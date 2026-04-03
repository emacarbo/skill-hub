#!/usr/bin/env bash
# PostCompact hook — logs session metadata + skills used to skill-hub/logs/claude/
# Fires automatically after Claude Code compacts the conversation context.
#
# Input (stdin): JSON with session_id, cwd, transcript_path, hook_event_name

set -euo pipefail

SKILL_HUB_DIR="$HOME/dev/skill-hub"
LOG_DIR="$SKILL_HUB_DIR/logs/claude"
mkdir -p "$LOG_DIR"

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd','unknown'))" 2>/dev/null || echo "unknown")
TRANSCRIPT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('transcript_path',''))" 2>/dev/null || echo "")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/${DATE}.log"

# Parse transcript to find which skills were used since last compact
SKILLS_USED="none"
if [[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]]; then
  SKILLS_USED=$(python3 - "$TRANSCRIPT" <<'PYEOF'
import sys, json
from pathlib import Path

skills = set()
try:
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                content = entry.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict) or block.get("type") != "tool_use":
                            continue
                        name = block.get("name", "")
                        inp  = block.get("input", {})
                        # Read tool calls to ~/.claude/skills/
                        if name == "Read":
                            path = inp.get("file_path", "")
                            if ".claude/skills/" in path:
                                skills.add(Path(path).stem)
                        # Skill tool invocations
                        elif name == "Skill":
                            skill = inp.get("skill", "")
                            if skill:
                                skills.add(skill)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
except Exception:
    pass

print(", ".join(sorted(skills)) if skills else "none")
PYEOF
  )
fi

printf -- "---\ntimestamp: %s\nsession_id: %s\ncwd: %s\nskills_used: %s\ntranscript: %s\n\n" \
  "$TIMESTAMP" "$SESSION_ID" "$CWD" "$SKILLS_USED" "$TRANSCRIPT" >> "$LOG_FILE"
