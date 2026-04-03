#!/usr/bin/env bash
# PreCompact hook — dumps working state to a recovery file before compaction.
#
# Captures:
#   1. Active git branch + uncommitted changes summary
#   2. Files modified in this session (from git diff)
#   3. Active campaign/fleet session status
#   4. Task list snapshot (if tasks exist)
#   5. Last 5 tool calls from transcript (what was Claude doing?)
#
# Output: ~/.claude-work/compact-recovery/<session-id>.md
# The PostCompact hook reads this and re-injects it.

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd','unknown'))" 2>/dev/null || echo "unknown")
TRANSCRIPT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('transcript_path',''))" 2>/dev/null || echo "")

RECOVERY_DIR="$HOME/.claude-work/compact-recovery"
mkdir -p "$RECOVERY_DIR"

RECOVERY_FILE="$RECOVERY_DIR/${SESSION_ID}.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

{
  echo "# Compact Recovery — $TIMESTAMP"
  echo ""
  echo "Session: $SESSION_ID"
  echo "CWD: $CWD"
  echo ""

  # 1. Git state
  echo "## Git State"
  if cd "$CWD" 2>/dev/null && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Branch: $(git branch --show-current 2>/dev/null || echo 'detached')"
    STAGED=$(git diff --cached --stat 2>/dev/null || echo "none")
    UNSTAGED=$(git diff --stat 2>/dev/null || echo "none")
    UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | head -10)
    echo "### Staged"
    echo "\`\`\`"
    echo "${STAGED:-none}"
    echo "\`\`\`"
    echo "### Unstaged"
    echo "\`\`\`"
    echo "${UNSTAGED:-none}"
    echo "\`\`\`"
    if [ -n "$UNTRACKED" ]; then
      echo "### Untracked (first 10)"
      echo "\`\`\`"
      echo "$UNTRACKED"
      echo "\`\`\`"
    fi
  else
    echo "Not a git repo or could not access CWD."
  fi
  echo ""

  # 2. Active campaigns/fleet sessions
  echo "## Active Campaigns"
  PLANNING_DIR="$CWD/.planning"
  if [ -d "$PLANNING_DIR/campaigns" ]; then
    grep -rl "Status: active" "$PLANNING_DIR/campaigns/" 2>/dev/null | while read -r f; do
      echo "- $(basename "$f"): active"
      head -5 "$f" 2>/dev/null | sed 's/^/  /'
    done
  else
    echo "No campaigns directory."
  fi
  echo ""

  if [ -d "$PLANNING_DIR/fleet" ]; then
    echo "## Fleet Sessions"
    grep -rl "status: active\|needs-continue" "$PLANNING_DIR/fleet/" 2>/dev/null | while read -r f; do
      echo "- $(basename "$f")"
      head -5 "$f" 2>/dev/null | sed 's/^/  /'
    done
  fi
  echo ""

  # 3. Recent tool calls from transcript (what was Claude working on?)
  echo "## Recent Activity (last 10 tool calls)"
  if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
    python3 - "$TRANSCRIPT" <<'PYEOF'
import sys, json

calls = []
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
                        inp = block.get("input", {})
                        # Summarize each tool call
                        if name == "Read":
                            calls.append(f"Read: {inp.get('file_path', '?')}")
                        elif name == "Edit":
                            calls.append(f"Edit: {inp.get('file_path', '?')}")
                        elif name == "Write":
                            calls.append(f"Write: {inp.get('file_path', '?')}")
                        elif name == "Bash":
                            cmd = inp.get("command", "?")[:80]
                            calls.append(f"Bash: {cmd}")
                        elif name == "Grep":
                            calls.append(f"Grep: {inp.get('pattern', '?')} in {inp.get('path', 'cwd')}")
                        elif name == "Agent":
                            calls.append(f"Agent: {inp.get('description', '?')}")
                        elif name == "Skill":
                            calls.append(f"Skill: {inp.get('skill', '?')}")
                        else:
                            calls.append(f"{name}")
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
except Exception:
    pass

# Last 10
for c in calls[-10:]:
    print(f"- {c}")
if not calls:
    print("(no tool calls found)")
PYEOF
  else
    echo "(no transcript available)"
  fi
  echo ""

  # 4. Tasks snapshot
  echo "## Tasks"
  TASKS_DIR="$HOME/.claude-work/tasks"
  if [ -d "$TASKS_DIR" ]; then
    find "$TASKS_DIR" -name "*.json" -newer "$RECOVERY_DIR" -mmin -120 2>/dev/null | head -5 | while read -r f; do
      python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    status = d.get('status', '?')
    title = d.get('title', d.get('description', '?'))[:80]
    print(f'- [{status}] {title}')
except: pass
" "$f" 2>/dev/null
    done
  fi
  echo ""

  echo "---"
  echo "**Re-read this file after compaction to restore working context.**"

} > "$RECOVERY_FILE"

echo "[PreCompact] Recovery state saved to $RECOVERY_FILE"
