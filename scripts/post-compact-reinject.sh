#!/usr/bin/env bash
# PostCompact hook — outputs recovery context so Claude re-reads it.
#
# After compaction, Claude's prior context is summarized and detail is lost.
# This hook prints the recovery file path so Claude knows to read it.
# It also logs compaction analytics (skills used, duration estimate).

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd','unknown'))" 2>/dev/null || echo "unknown")
TRANSCRIPT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('transcript_path',''))" 2>/dev/null || echo "")

RECOVERY_DIR="$HOME/.claude-work/compact-recovery"
RECOVERY_FILE="$RECOVERY_DIR/${SESSION_ID}.md"

# Log analytics (preserve existing post-compact.sh behavior)
SKILL_HUB_DIR="$HOME/dev/skill-hub"
LOG_DIR="$SKILL_HUB_DIR/logs/claude"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/${DATE}.log"

# Run session tracker (structured analytics with co-trigger detection)
TRACKER="$SKILL_HUB_DIR/scripts/session-tracker.py"
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] && [ -f "$TRACKER" ]; then
  python3 "$TRACKER" "$TRANSCRIPT" "$SESSION_ID" "$CWD" "compact" 2>/dev/null || true
fi

# Legacy compact log (simple text format for backward compat)
SKILLS_USED="none"
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  SKILLS_USED=$(python3 -c "
import sys, json
from pathlib import Path
skills = set()
try:
    with open(sys.argv[1]) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                content = entry.get('message', {}).get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict) or block.get('type') != 'tool_use': continue
                        name, inp = block.get('name',''), block.get('input',{})
                        if name == 'Read' and '.claude/skills/' in inp.get('file_path',''): skills.add(Path(inp['file_path']).parent.name)
                        elif name == 'Skill' and inp.get('skill',''): skills.add(inp['skill'])
            except: continue
except: pass
print(', '.join(sorted(skills)) if skills else 'none')
" "$TRANSCRIPT" 2>/dev/null || echo "none")
fi

printf -- "---\ntimestamp: %s\nsession_id: %s\ncwd: %s\nskills_used: %s\ntranscript: %s\n\n" \
  "$TIMESTAMP" "$SESSION_ID" "$CWD" "$SKILLS_USED" "$TRANSCRIPT" >> "$LOG_FILE"

# Output recovery prompt
if [ -f "$RECOVERY_FILE" ]; then
  echo "[PostCompact] Context was compacted. Recovery file: $RECOVERY_FILE"
  echo "[PostCompact] Read the recovery file above to restore working context."
else
  echo "[PostCompact] Context was compacted. No recovery file found."
fi
