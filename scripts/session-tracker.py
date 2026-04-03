#!/usr/bin/env python3
"""
PostCompact / SessionEnd analytics — extracts skill usage, context pressure,
and trigger co-occurrence data from Claude Code transcripts.

Called by post-compact-reinject.sh. Writes structured logs to:
  ~/dev/skill-hub/logs/claude/sessions/<date>.jsonl   (one JSON line per session event)
  ~/dev/skill-hub/logs/claude/skills-usage.jsonl      (running skill usage ledger)

Usage:
  python3 session-tracker.py <transcript_path> <session_id> <cwd> <event_type>
  event_type: "compact" | "session_end"
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

SKILL_HUB = Path.home() / "dev" / "skill-hub"
LOG_DIR = SKILL_HUB / "logs" / "claude"
SESSIONS_DIR = LOG_DIR / "sessions"
USAGE_FILE = LOG_DIR / "skills-usage.jsonl"


def parse_transcript(transcript_path: str) -> dict:
    """Extract skill usage and context signals from a transcript."""
    skills_read = Counter()       # skills loaded via Read tool
    skills_invoked = Counter()    # skills invoked via Skill tool
    tool_calls = Counter()        # tool call counts by name
    skill_files_read = []         # ordered list of skill file reads
    total_lines = 0
    compaction_count = 0

    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_lines += 1
                try:
                    entry = json.loads(line)
                    content = entry.get("message", {}).get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if not isinstance(block, dict):
                                continue
                            if block.get("type") != "tool_use":
                                continue
                            name = block.get("name", "")
                            inp = block.get("input", {})
                            tool_calls[name] += 1

                            if name == "Read":
                                path = inp.get("file_path", "")
                                if ".claude/skills/" in path:
                                    skill_name = Path(path).parts
                                    # Extract skill dir name
                                    for i, part in enumerate(skill_name):
                                        if part == "skills" and i + 1 < len(skill_name):
                                            s = skill_name[i + 1]
                                            skills_read[s] += 1
                                            skill_files_read.append(s)
                                            break
                                elif "general_skills/" in path:
                                    stem = Path(path).stem
                                    skills_read[stem] += 1
                                    skill_files_read.append(stem)

                            elif name == "Skill":
                                skill = inp.get("skill", "")
                                if skill:
                                    skills_invoked[skill] += 1

                    # Detect compaction markers
                    role = entry.get("message", {}).get("role", "")
                    if role == "system":
                        text = str(content) if isinstance(content, str) else str(content)
                        if "compact" in text.lower() or "summary" in text.lower():
                            compaction_count += 1

                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
    except Exception:
        pass

    return {
        "skills_read": dict(skills_read),
        "skills_invoked": dict(skills_invoked),
        "tool_calls": dict(tool_calls),
        "skill_load_order": skill_files_read,
        "transcript_lines": total_lines,
        "total_tool_calls": sum(tool_calls.values()),
        "compaction_markers": compaction_count,
    }


def detect_co_triggers(skill_load_order: list) -> list:
    """Find skills that loaded together (within 5 tool calls of each other)."""
    co_triggers = []
    for i, skill_a in enumerate(skill_load_order):
        for j in range(i + 1, min(i + 6, len(skill_load_order))):
            skill_b = skill_load_order[j]
            if skill_a != skill_b:
                pair = tuple(sorted([skill_a, skill_b]))
                if pair not in co_triggers:
                    co_triggers.append(pair)
    return [list(p) for p in co_triggers]


def main():
    if len(sys.argv) < 5:
        print("Usage: session-tracker.py <transcript> <session_id> <cwd> <event_type>")
        sys.exit(1)

    transcript_path = sys.argv[1]
    session_id = sys.argv[2]
    cwd = sys.argv[3]
    event_type = sys.argv[4]

    now = datetime.now(timezone.utc).isoformat()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Parse transcript
    data = parse_transcript(transcript_path)
    co_triggers = detect_co_triggers(data["skill_load_order"])

    # Session event log
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    session_event = {
        "timestamp": now,
        "session_id": session_id,
        "event": event_type,
        "cwd": cwd,
        "skills_read": data["skills_read"],
        "skills_invoked": data["skills_invoked"],
        "skill_count": len(data["skills_read"]),
        "co_triggers": co_triggers,
        "total_tool_calls": data["total_tool_calls"],
        "transcript_lines": data["transcript_lines"],
        "compaction_markers": data["compaction_markers"],
    }

    session_log = SESSIONS_DIR / f"{date_str}.jsonl"
    with open(session_log, "a") as f:
        f.write(json.dumps(session_event) + "\n")

    # Skills usage ledger (append one entry per skill used)
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    all_skills = set(data["skills_read"].keys()) | set(data["skills_invoked"].keys())
    with open(USAGE_FILE, "a") as f:
        for skill in sorted(all_skills):
            entry = {
                "timestamp": now,
                "skill": skill,
                "session_id": session_id,
                "reads": data["skills_read"].get(skill, 0),
                "invocations": data["skills_invoked"].get(skill, 0),
                "cwd": cwd,
            }
            f.write(json.dumps(entry) + "\n")

    # Print summary for hook output
    skill_list = ", ".join(sorted(all_skills)) if all_skills else "none"
    print(f"[SessionTracker] {len(all_skills)} skills used: {skill_list}")
    if co_triggers:
        print(f"[SessionTracker] Co-triggers: {co_triggers[:5]}")


if __name__ == "__main__":
    main()
