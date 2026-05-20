#!/usr/bin/env python3
"""PostToolUse hook: track skill invocations.

Three outputs per invocation:
1. Updates last-used date in manifest.yaml (legacy).
2. Appends a daily plain-text line to usage.log (legacy).
3. Appends a timestamped JSONL entry to ~/.claude/logs/skill-invocations.jsonl
   with source attribution (direct / router-suggested / do-routed) computed
   by cross-referencing the router log and recent invocations.

Why: the legacy log only captured skill name + date — no source, no granularity.
The new log lets skill-eval analyze invocation health (which routes work,
which skills are dormant, which router suggestions Claude ignores).
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "manifest.yaml"
LOG = Path(__file__).resolve().parent.parent / "usage.log"

INVOCATIONS_LOG = Path.home() / ".claude" / "logs" / "skill-invocations.jsonl"
ROUTER_LOG = Path.home() / ".claude" / "logs" / "skill-routing.jsonl"
SOURCE_WINDOW_SECS = 120  # how far back to look for a triggering event


def log(msg: str) -> None:
    with open(LOG, "a") as f:
        f.write(f"{date.today()} {msg}\n")


def update_manifest(skill_name: str, today: str) -> bool:
    """Update last_used.claude for the matching skill in manifest.yaml.

    Uses plain string manipulation to avoid pyyaml reformatting the entire file.
    Returns True if updated, False if skill not found.
    """
    text = MANIFEST.read_text()
    lines = text.split("\n")

    # Normalize: "financial-analysis:comps" → "comps"
    base_name = skill_name.split(":")[-1] if ":" in skill_name else skill_name

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped in (f"name: {base_name}", f"- name: {base_name}"):
            # Found the skill — scan forward for last_used.claude
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("- name:"):
                if lines[j].strip() == "claude: null" or lines[j].strip().startswith("claude: '"):
                    indent = lines[j][: len(lines[j]) - len(lines[j].lstrip())]
                    lines[j] = f"{indent}claude: '{today}'"
                    MANIFEST.write_text("\n".join(lines))
                    return True
                j += 1
            return False
        i += 1
    return False


def _read_last_jsonl(path: Path, n: int = 30) -> list[dict]:
    """Read the last N JSONL entries from path. Returns [] on any error."""
    if not path.exists():
        return []
    try:
        with open(path) as f:
            lines = f.readlines()[-n:]
        entries: list[dict] = []
        for line in lines:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        return entries
    except Exception:
        return []


def _base_name(skill_name: str) -> str:
    return skill_name.split(":")[-1] if ":" in skill_name else skill_name


def detect_source(skill_name: str, now_ts: float) -> dict:
    """Determine what triggered this invocation.

    Returns {"source": "...", "evidence": {...}}. Source is one of:
    - "router-suggested": router log within SOURCE_WINDOW_SECS proposed this skill.
    - "do-routed": a prior `do` skill invocation is within the window.
    - "direct": no recent attributable trigger.
    """
    base = _base_name(skill_name)

    # Router-suggested?
    for entry in reversed(_read_last_jsonl(ROUTER_LOG, n=20)):
        ts = entry.get("ts", 0)
        if now_ts - ts > SOURCE_WINDOW_SECS:
            break
        matched = set(entry.get("regex_matches") or []) | set(entry.get("haiku_matches") or [])
        matched_bases = {_base_name(m) for m in matched}
        if base in matched_bases:
            return {
                "source": "router-suggested",
                "evidence": {
                    "router_ts": ts,
                    "category": entry.get("category"),
                    "regex": base in {_base_name(m) for m in entry.get("regex_matches") or []},
                    "haiku": base in {_base_name(m) for m in entry.get("haiku_matches") or []},
                },
            }

    # /do-routed?
    for entry in reversed(_read_last_jsonl(INVOCATIONS_LOG, n=10)):
        ts = entry.get("ts", 0)
        if now_ts - ts > SOURCE_WINDOW_SECS:
            break
        prior_skill = entry.get("skill", "")
        if _base_name(prior_skill) == "do" and base != "do":
            return {"source": "do-routed", "evidence": {"do_ts": ts}}

    return {"source": "direct", "evidence": {}}


def append_invocation_log(skill_name: str, source_info: dict, session_id: str | None) -> None:
    try:
        INVOCATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": time.time(),
            "skill": skill_name,
            "source": source_info.get("source", "unknown"),
            "evidence": source_info.get("evidence", {}),
            "session_id": session_id,
        }
        with open(INVOCATIONS_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("skill", "")
    if not skill_name:
        return

    now_ts = time.time()
    source_info = detect_source(skill_name, now_ts)
    session_id = data.get("session_id")
    append_invocation_log(skill_name, source_info, session_id)

    today = str(date.today())
    updated = update_manifest(skill_name, today)
    status = "updated" if updated else "not-found"
    log(f"skill={skill_name} status={status} source={source_info.get('source')}")


if __name__ == "__main__":
    main()
