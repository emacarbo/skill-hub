#!/usr/bin/env python3
"""UserPromptSubmit hook for automatic skill triggering.

Runs two routers in parallel on every user prompt:
- Path A (regex): match prompt against `triggers:` keywords pulled from
  SKILL.md frontmatter. Fast (~5ms), free, deterministic.
- Path B (Haiku): call `claude --print --model haiku-4.5` as a subprocess
  to do fuzzy intent matching. Slower (~800ms), uses the Claude Code
  subscription (no API key), recursion-guarded via env var.

Both results are merged and injected as a system reminder. Each prompt's
result is logged to ~/.claude/logs/skill-routing.jsonl with a category
label so the regex layer can be expanded over time from the "haiku-only"
log entries until Haiku rarely fires.

Why: descriptions alone don't trigger reliably across 80+ skills. This
hook makes invocation deterministic-first, fuzzy-fallback.

Deps: PyYAML (already installed), local `claude` CLI binary.

Sticky re-injection depends on `session_id` being present in the
UserPromptSubmit hook payload. If Claude Code ever omits this field
(version drift, alternate hook variants, replay tooling), sticky
silently degrades to off — the original stateless behavior. Look for
`hook_input.get("session_id")` to confirm the dependency at the
extraction point.
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HOME = Path.home()
LOG_DIR = HOME / ".claude" / "logs"
LOG_FILE = LOG_DIR / "skill-routing.jsonl"
INDEX_CACHE = HOME / ".claude" / "hooks" / "skill-router-index.json"
INDEX_CACHE_TTL_SECS = 3600

CLAUDE_BIN = str(HOME / ".local" / "bin" / "claude")
# Match the user's `claude-work` alias: `CLAUDE_CONFIG_DIR=~/.claude-work command claude`
CLAUDE_CONFIG_DIR = str(HOME / ".claude-work")
HAIKU_MODEL = "claude-haiku-4-5-20251001"
HAIKU_TIMEOUT_SECS = 20

PROMPT_PREVIEW_MAX = 500
MAX_INJECTED_SKILLS = 3
SKIP_IF_PROMPT_SHORTER_THAN = 12
SKIP_PROMPTS = {
    "ok", "okay", "yes", "yeah", "yep", "no", "nope", "continue", "go",
    "stop", "cancel", "next", "done", "thanks", "thank you", "got it",
    "proceed", "go ahead", "do it", "let's go", "sounds good",
    "ship it", "lgtm", "looks good", "please proceed", "yes please",
    "yes do it", "yes proceed",
}

RECURSION_GUARD_ENV = "CLAUDE_SKILL_ROUTING_ACTIVE"
DISABLE_ENV = "SKILL_ROUTER_DISABLED"
HAIKU_DISABLE_ENV = "SKILL_ROUTER_HAIKU_DISABLED"

# Sticky re-injection: when a follow-up prompt has no signal of its own
# (short ack like "proceed", or both routers return zero), re-inject the
# skills that last routed in this session so the assistant keeps context.
STICKY_DISABLE_ENV = "SKILL_ROUTER_STICKY_DISABLED"
STICKY_TTL_SECS = int(os.environ.get("SKILL_ROUTER_STICKY_TTL_SECS", "900"))
SESSION_STATE_DIR = HOME / ".claude" / "hooks" / "sessions"
STICKY_PRUNE_PROBABILITY = float(
    os.environ.get("SKILL_ROUTER_STICKY_PRUNE_PROBABILITY", "0.02")
)


# ---------------------------------------------------------------------------
# Skill index
# ---------------------------------------------------------------------------

def discover_skill_md_paths() -> list[Path]:
    paths: list[Path] = []
    base = HOME / ".claude" / "skills"
    if base.exists():
        paths.extend(base.glob("*/SKILL.md"))
    plugin_base = HOME / "dev" / "skill-hub" / "plugins"
    if plugin_base.exists():
        for plugin in plugin_base.iterdir():
            if plugin.is_dir():
                paths.extend(plugin.glob("skills/*/SKILL.md"))
    return paths


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def normalize_triggers(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        return [t.strip() for t in raw.split(",") if t.strip()]
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]
    return []


def build_index() -> list[dict]:
    skills: list[dict] = []
    for path in discover_skill_md_paths():
        try:
            fm = parse_frontmatter(path.read_text(errors="ignore"))
        except Exception:
            continue
        name = fm.get("name")
        if not name:
            continue
        desc = (fm.get("description") or "").strip().replace("\n", " ")
        triggers = normalize_triggers(fm.get("triggers"))
        metadata = fm.get("metadata") or {}
        if isinstance(metadata, dict):
            triggers.extend(normalize_triggers(metadata.get("triggers")))
        # Dedupe, drop empties
        seen, deduped = set(), []
        for t in triggers:
            tl = t.lower()
            if tl and tl not in seen:
                seen.add(tl)
                deduped.append(t)
        # Broad-match modes: skill opts in via `match_modes:` in frontmatter
        # (or under metadata.match_modes). Recognized modes: "questions",
        # "decisions", "exploration". A skill with mode X fires on any prompt
        # whose shape matches X, in addition to its keyword triggers.
        match_modes = normalize_triggers(fm.get("match_modes"))
        if isinstance(metadata, dict):
            match_modes.extend(normalize_triggers(metadata.get("match_modes")))
        match_modes = [m.lower() for m in match_modes]
        # Per-skill sticky opt-out. Default True. Skills where wrong activation
        # is costly (destructive ops, narrow one-shots) can set `sticky: false`.
        sticky_raw = fm.get("sticky")
        if sticky_raw is None and isinstance(metadata, dict):
            sticky_raw = metadata.get("sticky")
        sticky = False if sticky_raw is False else True
        skills.append({
            "name": name,
            "triggers": deduped,
            "description": desc,
            "match_modes": match_modes,
            "sticky": sticky,
        })
    return skills


def load_index() -> list[dict]:
    try:
        if INDEX_CACHE.exists():
            age = time.time() - INDEX_CACHE.stat().st_mtime
            if age < INDEX_CACHE_TTL_SECS:
                return json.loads(INDEX_CACHE.read_text())
    except Exception:
        pass
    skills = build_index()
    try:
        INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_CACHE.write_text(json.dumps(skills))
    except Exception:
        pass
    return skills


# ---------------------------------------------------------------------------
# Pattern detectors (for broad match_modes)
# ---------------------------------------------------------------------------

QUESTION_STARTERS = {
    "how", "what", "why", "should", "shall", "could", "would",
    "can", "is", "are", "do", "does", "where", "when", "who", "which",
    "any", "anyone",
}

DECISION_PHRASES = (
    "should we", "should i", "decide between", "trade-off", "tradeoff",
    "tradeoffs", "which approach", "which option", "what's the best",
    "best approach", "best way", "pros and cons", "vs ", " vs.",
    "compare", "alternatives",
)

EXPLORATION_PHRASES = (
    "i'm thinking", "i was thinking", "i wonder", "wondering",
    "exploring", "let's brainstorm", "let's think", "what if",
    "could we", "could i", "maybe we", "what's possible",
    "ideating", "kicking around",
)


def detect_pattern_modes(prompt: str) -> set[str]:
    """Return set of broad-match modes the prompt matches."""
    stripped = prompt.strip()
    if not stripped:
        return set()
    lower = stripped.lower()
    modes: set[str] = set()

    # questions
    if stripped.endswith("?"):
        modes.add("questions")
    else:
        first_word = lower.split()[0] if lower.split() else ""
        if first_word in QUESTION_STARTERS:
            modes.add("questions")

    # decisions
    for phrase in DECISION_PHRASES:
        if phrase in lower:
            modes.add("decisions")
            break

    # exploration
    for phrase in EXPLORATION_PHRASES:
        if phrase in lower:
            modes.add("exploration")
            break

    return modes


# ---------------------------------------------------------------------------
# Path A — regex
# ---------------------------------------------------------------------------

def regex_match(prompt_lower: str, skills: list[dict]) -> list[str]:
    matches: list[str] = []
    pattern_modes = detect_pattern_modes(prompt_lower)
    for skill in skills:
        # Broad-match first: if skill opts into a mode the prompt has, match it
        # without needing a keyword hit.
        if pattern_modes and any(m in pattern_modes for m in skill.get("match_modes", [])):
            matches.append(skill["name"])
            continue
        for trig in skill["triggers"]:
            t = trig.lower().strip()
            if not t or len(t) < 3:
                continue
            if " " in t or "/" in t or "-" in t or "." in t:
                if t in prompt_lower:
                    matches.append(skill["name"])
                    break
            else:
                if re.search(r"\b" + re.escape(t) + r"\b", prompt_lower):
                    matches.append(skill["name"])
                    break
    return matches


# ---------------------------------------------------------------------------
# Path B — Haiku via CLI
# ---------------------------------------------------------------------------

def haiku_match(prompt: str, skills: list[dict], cwd: str | None) -> list[str]:
    if os.environ.get(HAIKU_DISABLE_ENV) == "1":
        return []
    if not Path(CLAUDE_BIN).exists():
        return []
    catalog_lines: list[str] = []
    for skill in skills:
        desc = skill["description"][:200]
        catalog_lines.append(f"- {skill['name']}: {desc}")
    catalog = "\n".join(catalog_lines)

    cwd_line = f"<cwd>{cwd}</cwd>\n\n" if cwd else ""

    routing_prompt = (
        "You are a deterministic skill router. The user just sent this prompt "
        "while working in the following directory (consider the path as additional "
        "context — e.g. a path like `/my-api-server` suggests API/backend skills, "
        "`/my-data-pipeline` suggests data/SQL skills):\n\n"
        f"{cwd_line}"
        f"<user_prompt>\n{prompt}\n</user_prompt>\n\n"
        "Below are available skills. Return ONLY a JSON object with a 'matches' "
        "array listing skill names (exactly as written below) that should be "
        "invoked for this prompt. Include a skill only if the user's intent "
        "(or the working directory) clearly aligns with the skill's purpose. "
        "Return an empty array if no skill matches. Do NOT include explanation, "
        "only the JSON.\n\n"
        f"<skills>\n{catalog}\n</skills>"
    )

    env = {
        **os.environ,
        RECURSION_GUARD_ENV: "1",
        "CLAUDE_CONFIG_DIR": CLAUDE_CONFIG_DIR,
    }
    schema = (
        '{"type":"object","properties":{"matches":{"type":"array","items":'
        '{"type":"string"}}},"required":["matches"]}'
    )
    try:
        result = subprocess.run(
            [
                CLAUDE_BIN, "--print",
                "--output-format", "json",
                "--model", HAIKU_MODEL,
                "--disable-slash-commands",
                "--json-schema", schema,
                routing_prompt,
            ],
            env=env,
            timeout=HAIKU_TIMEOUT_SECS,
            capture_output=True,
            text=True,
        )
    except (subprocess.TimeoutExpired, Exception):
        return []
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout.strip())
        # When --json-schema is set, the parsed object lives under structured_output.
        structured = data.get("structured_output") or {}
        return structured.get("matches", []) or []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------

def categorize(regex_set: set[str], haiku_set: set[str]) -> str:
    if not regex_set and not haiku_set:
        return "both-empty"
    if regex_set == haiku_set:
        return "both-agree"
    if regex_set and not haiku_set:
        return "regex-only"
    if haiku_set and not regex_set:
        return "haiku-only"
    if haiku_set > regex_set:
        return "haiku-superset"
    if regex_set > haiku_set:
        return "regex-superset"
    return "partial-overlap"


# ---------------------------------------------------------------------------
# Sticky session state
# ---------------------------------------------------------------------------

def session_state_path(session_id: str) -> Path:
    return SESSION_STATE_DIR / f"{session_id}.json"


def load_session_state(session_id: str) -> dict | None:
    """Return the saved routing for this session if it's still fresh, else None."""
    try:
        path = session_state_path(session_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        ts = float(data.get("last_routed_at") or 0)
        if time.time() - ts > STICKY_TTL_SECS:
            return None
        return data
    except Exception:
        return None


def save_session_state(
    session_id: str, skills: list[str], category: str
) -> None:
    """Atomically write the session's last successful routing."""
    if not session_id or not skills:
        return
    try:
        SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": session_id,
            "last_skills": skills,
            "last_routed_at": time.time(),
            "last_category": category,
        }
        # Write to a tempfile in the same dir, then atomically rename.
        # os.replace is atomic on POSIX — readers either see the prior file
        # or the new one, never a partial write.
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=str(SESSION_STATE_DIR),
            prefix=f".{session_id}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        os.replace(tmp_path, session_state_path(session_id))
    except Exception:
        pass


def prune_stale_sessions() -> None:
    """Delete session state files older than 4× TTL. Runs probabilistically."""
    try:
        if not SESSION_STATE_DIR.exists():
            return
        cutoff = time.time() - (STICKY_TTL_SECS * 4)
        for f in SESSION_STATE_DIR.glob("*.json"):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
            except Exception:
                continue
    except Exception:
        pass


def sticky_reinject(
    session_id: str | None, known_names: set[str]
) -> list[str]:
    """Return prior session skills that are still valid in the live index.

    Empty list means: no sticky available. Filters against `known_names`
    so renamed/deleted skills don't get injected.
    """
    if not session_id:
        return []
    if os.environ.get(STICKY_DISABLE_ENV) == "1":
        return []
    state = load_session_state(session_id)
    if not state:
        return []
    last_skills = state.get("last_skills") or []
    return [s for s in last_skills if s in known_names]


# ---------------------------------------------------------------------------
# Reminder construction
# ---------------------------------------------------------------------------

def build_reminder(top: list[str], source: str = "router") -> str:
    """Compose the additionalContext string for injection.

    `source="router"` uses the fresh-match phrasing.
    `source="sticky"` makes it explicit that context is carried over.
    """
    prefix = ""
    if source == "sticky":
        prefix = (
            "Continuing from earlier routing in this session. The user's "
            "current prompt is short/empty of new signal — the assistant "
            "should treat it as a follow-up to the prior topic. "
        )

    if len(top) == 1:
        return (
            f"{prefix}Skill router matched the user's prompt to: {top[0]}. "
            f"Strongly consider invoking Skill(skill=\"{top[0]}\") before "
            f"responding if the user's intent matches the skill's purpose. "
            f"Override if the prompt only incidentally mentions a trigger keyword."
        )

    # Multiple skills matched the same prompt. They may be designed to
    # complement each other (e.g., code-review-suite + adversarial-review
    # both fire on /review — defect-finding paired with design-challenge).
    # Suggest evaluating the chain, not just the top one.
    chain = ", ".join(f"Skill(skill=\"{s}\")" for s in top)
    return (
        f"{prefix}Skill router matched the user's prompt to {len(top)} skills: "
        f"{', '.join(top)}. These may be designed to fire as a chain — "
        f"e.g. defect-finding paired with design-challenge, or research "
        f"paired with planning. Evaluate whether the user's intent "
        f"warrants invoking the full chain: {chain}. If only one "
        f"applies, start with the most specific match. If the prompt "
        f"only incidentally mentions a trigger keyword, override and skip."
    )


def emit_sticky_injection(skills: list[str]) -> None:
    """Print the hookSpecificOutput JSON for a sticky (carried-over) routing.

    Named explicitly so future callers don't accidentally use this for
    fresh router matches — the reminder text is sticky-specific.
    """
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": build_reminder(skills, source="sticky"),
        }
    }
    print(json.dumps(output))


def write_log_entry(entry: dict) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Skip conditions
# ---------------------------------------------------------------------------

def should_skip(prompt: str) -> str | None:
    if os.environ.get(DISABLE_ENV) == "1":
        return "disabled"
    if os.environ.get(RECURSION_GUARD_ENV) == "1":
        return "recursion-guard"
    stripped = (prompt or "").strip()
    if not stripped:
        return "too-short"
    # Slash-command check must come BEFORE too-short: many slash commands are
    # under the 12-char minimum (e.g., "/review" is 7 chars) but we still want
    # to log them as slash-command for observability.
    if stripped.startswith("/"):
        return "slash-command"
    # Ack-word check must come BEFORE too-short: most acks ("proceed", "lgtm",
    # "do it") are under 12 chars, so the length check would mis-categorize
    # them as too-short. Reversing the order surfaces vocabulary-driven sticky
    # vs length-driven sticky distinctly in the log.
    if stripped.lower() in SKIP_PROMPTS:
        return "ack-word"
    if len(stripped) < SKIP_IF_PROMPT_SHORTER_THAN:
        return "too-short"
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    raw_stdin = sys.stdin.read()
    try:
        hook_input = json.loads(raw_stdin)
    except Exception:
        sys.exit(0)
    prompt = hook_input.get("prompt") or ""
    cwd = hook_input.get("cwd") or None
    session_id = hook_input.get("session_id") or None

    # Probabilistic housekeeping: keep the sessions/ dir from growing unbounded.
    if random.random() < STICKY_PRUNE_PROBABILITY:
        prune_stale_sessions()

    skip_reason = should_skip(prompt)
    if skip_reason:
        # Log slash commands so the router log is a complete record of user
        # prompts (useful for plan-adherence analysis: did the plan call for
        # /X and did the user actually run it?). Other skip reasons stay silent.
        if skip_reason == "slash-command":
            write_log_entry({
                "ts": time.time(),
                "prompt": prompt[:PROMPT_PREVIEW_MAX],
                "cwd": cwd,
                "regex_matches": [],
                "haiku_matches": [],
                "category": "slash-command",
            })
            sys.exit(0)

        # Sticky re-injection: when the prompt would have produced no
        # injection today (ack-word or too-short), reuse the session's
        # last successful routing if it's still fresh. Strictly additive:
        # the original silent-exit path is preserved when there's no state.
        if skip_reason in {"ack-word", "too-short"} and session_id:
            skills_index = load_index()
            if skills_index:
                known_names = {s["name"] for s in skills_index}
                sticky_skills = sticky_reinject(session_id, known_names)
                if sticky_skills:
                    top = sticky_skills[:MAX_INJECTED_SKILLS]
                    emit_sticky_injection(top)
                    # Distinguish vocabulary-driven sticky from length-driven
                    # sticky in the log — helps diagnose "why does sticky
                    # fire so much" without re-deriving from the prompt.
                    sticky_category = (
                        "sticky-ack-word"
                        if skip_reason == "ack-word"
                        else "sticky-too-short"
                    )
                    write_log_entry({
                        "ts": time.time(),
                        "prompt": prompt[:PROMPT_PREVIEW_MAX],
                        "cwd": cwd,
                        "regex_matches": [],
                        "haiku_matches": [],
                        "category": sticky_category,
                        "sticky_used": True,
                        "sticky_skills": top,
                    })
        sys.exit(0)

    skills = load_index()
    if not skills:
        sys.exit(0)

    prompt_lower = prompt.lower()

    with ThreadPoolExecutor(max_workers=2) as ex:
        regex_future = ex.submit(regex_match, prompt_lower, skills)
        haiku_future = ex.submit(haiku_match, prompt, skills, cwd)
        regex_matches = regex_future.result()
        haiku_matches = haiku_future.result()

    known_names = {s["name"] for s in skills}
    haiku_matches = [m for m in haiku_matches if m in known_names]

    regex_set = set(regex_matches)
    haiku_set = set(haiku_matches)
    all_matches_ordered = list(dict.fromkeys(regex_matches + haiku_matches))
    category = categorize(regex_set, haiku_set)

    # Sticky fallback: fresh routing produced nothing, but we have a recent
    # routing for this session. Inject that instead of staying silent.
    if not all_matches_ordered and session_id:
        sticky_skills = sticky_reinject(session_id, known_names)
        if sticky_skills:
            top = sticky_skills[:MAX_INJECTED_SKILLS]
            emit_sticky_injection(top)
            write_log_entry({
                "ts": time.time(),
                "prompt": prompt[:PROMPT_PREVIEW_MAX],
                "cwd": cwd,
                "regex_matches": [],
                "haiku_matches": [],
                "category": "sticky-fallback",
                "sticky_used": True,
                "sticky_skills": top,
            })
            sys.exit(0)

    write_log_entry({
        "ts": time.time(),
        "prompt": prompt[:PROMPT_PREVIEW_MAX],
        "cwd": cwd,
        "regex_matches": sorted(regex_set),
        "haiku_matches": sorted(haiku_set),
        "category": category,
    })

    if all_matches_ordered:
        top = all_matches_ordered[:MAX_INJECTED_SKILLS]
        reminder = build_reminder(top, source="router")
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": reminder,
            }
        }
        print(json.dumps(output))

        # Persist this routing so a follow-up ack-word / both-empty prompt
        # in the same session can re-inject. Filter out skills with
        # `sticky: false` in their frontmatter (default is true).
        if session_id:
            sticky_set = {s["name"] for s in skills if s.get("sticky", True)}
            sticky_top = [s for s in top if s in sticky_set]
            if sticky_top:
                save_session_state(session_id, sticky_top, category)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
