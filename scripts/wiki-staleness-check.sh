#!/bin/bash
# Stop hook: check if .context/wiki/ is stale relative to git HEAD.
# Writes .context/wiki/.stale if the wiki's git_rev is behind HEAD.
# Designed to be fast (<50ms) with zero dependencies beyond git + python3.

set -euo pipefail

# Read CWD from hook stdin JSON (Stop hooks receive session context)
CWD=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null || echo "")
[ -z "$CWD" ] && exit 0

# Walk upward to find project root (.git)
PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ]; do
  [ -d "$PROJECT_ROOT/.git" ] && break
  PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done
[ ! -d "$PROJECT_ROOT/.git" ] && exit 0

META="$PROJECT_ROOT/.context/wiki/.wiki-meta.json"
[ ! -f "$META" ] && exit 0

# Read wiki's git rev
WIKI_REV=$(python3 -c "import json; print(json.load(open('$META')).get('git_rev',''))" 2>/dev/null || echo "")
[ -z "$WIKI_REV" ] && exit 0

# Compare to HEAD
HEAD_REV=$(git -C "$PROJECT_ROOT" rev-parse HEAD 2>/dev/null || echo "")
[ -z "$HEAD_REV" ] && exit 0
[ "$WIKI_REV" = "$HEAD_REV" ] && exit 0

# Count commits since wiki build
COMMITS_BEHIND=$(git -C "$PROJECT_ROOT" rev-list --count "$WIKI_REV..HEAD" 2>/dev/null || echo "0")
[ "$COMMITS_BEHIND" = "0" ] && exit 0

# Write stale flag
STALE_FILE="$PROJECT_ROOT/.context/wiki/.stale"
python3 -c "
import json
from datetime import datetime, timezone
json.dump({
    'stale_since': datetime.now(timezone.utc).isoformat(),
    'wiki_rev': '$WIKI_REV',
    'head_rev': '$HEAD_REV',
    'commits_behind': $COMMITS_BEHIND
}, open('$STALE_FILE', 'w'), indent=2)
"

exit 0
