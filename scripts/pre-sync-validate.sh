#!/bin/bash
# pre-sync-validate.sh — Enforcement gate before sync-skills.sh
#
# Checks:
#   1. Context budget: total stub/skill size must stay under MAX_CONTEXT_BYTES
#   2. Skill cap: total count must stay under MAX_SKILLS
#   3. Stack relevance: each skill must match at least one active_tag
#
# Exits non-zero if ANY check fails. sync-skills.sh calls this before syncing.
#
# Usage: ./pre-sync-validate.sh [skill-list-file]
#   If no file given, validates all .md files in general_skills/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GENERAL_SKILLS="$REPO_ROOT/agents/general_skills"
STACK_CONTEXT="$REPO_ROOT/stack-context.yaml"
STUBS_DIR="$HOME/.claude/skills"

# --- Thresholds ---
MAX_CONTEXT_BYTES=25000    # 25 KB for stubs (~6K tokens)
MAX_SKILLS=70              # Hard cap (25 Citadel + 45 general)
MAX_SKILL_SIZE=10240       # 10 KB per skill file

# --- Deny-list: stack keywords NOT in use ---
# Matched against SKILL NAME only (not content — too many false positives).
# A skill named "django-perf-review" is definitely about Django.
# A skill named "testing-qa-suite" that mentions Django in an example is not.
DENY_NAME_TAGS="django|rails|ruby|laravel|php|java-|spring-|kotlin|android|swift-|ios-|rust-|golang|nestjs|hono|bun-|prisma|drizzle|angular|vue-|svelte|flutter|dart-|cpp-|perl-|elixir|erlang|scala|clojure|haskell"

# --- Lifecycle/meta files to skip ---
SKIP_NAMES="consolidation-map skill-consolidate skill-discover skill-eval skill-promote skill-sync post-compact"

# --- Citadel skills to skip ---
PRESERVE_NAMES="do marshal archon fleet architect autopilot configure-ecc continuous-learning-v2 create-app create-skill design experiment live-preview postmortem qa research research-fleet review scaffold session-handoff setup systematic-debugging test-gen doc-gen refactor"

is_skipped() {
  local name="$1"
  for s in $SKIP_NAMES $PRESERVE_NAMES; do
    [[ "$name" == "$s" ]] && return 0
  done
  return 1
}

# --- Validation ---
errors=0
warnings=0
total_size=0
skill_count=0
failed_skills=""
SKIP_LIST=""

for md_file in "$GENERAL_SKILLS"/*.md; do
  name=$(basename "$md_file" .md)
  is_skipped "$name" && continue

  skill_count=$((skill_count + 1))
  size=$(wc -c < "$md_file")

  # Check 1: Individual skill size
  if [ "$size" -gt "$MAX_SKILL_SIZE" ]; then
    echo "WARN  $name: ${size}B exceeds ${MAX_SKILL_SIZE}B limit (will need trimming or stub)"
    warnings=$((warnings + 1))
  fi

  total_size=$((total_size + size))

  # Check 2: Stack relevance — skill name must not match a denied stack
  # Only checks the skill NAME, not file content (content has too many false positives)
  skill_name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
  matched_tag=$(echo "$skill_name_lower" | grep -oiE "$DENY_NAME_TAGS" | head -1 || true)
  if [ -n "$matched_tag" ]; then
    echo "WARN  $name: skill name matches denied stack '$matched_tag' — will be skipped"
    warnings=$((warnings + 1))
    SKIP_LIST="$SKIP_LIST $name"
  fi
done

# Check 3: Count against Citadel skills
citadel_count=$(echo $PRESERVE_NAMES | wc -w | tr -d ' ')
total_with_citadel=$((skill_count + citadel_count))

echo ""
echo "=== Pre-Sync Validation ==="
echo "General skills:  $skill_count"
echo "Citadel skills:  $citadel_count"
echo "Total:           $total_with_citadel / $MAX_SKILLS"
echo "Total file size: $total_size bytes (budget: $MAX_CONTEXT_BYTES for stubs)"
echo ""

if [ "$total_with_citadel" -gt "$MAX_SKILLS" ]; then
  echo "WARN  Skill soft cap exceeded: $total_with_citadel > $MAX_SKILLS"
  echo "      Exceeding cap is OK for new stacks — but verify stub budget stays under ${MAX_CONTEXT_BYTES}B"
  warnings=$((warnings + 1))
fi

if [ -n "$SKIP_LIST" ]; then
  echo "SKIP_LIST:$SKIP_LIST"
fi

valid_skills=$((skill_count - $(echo $SKIP_LIST | wc -w | tr -d ' ')))

if [ "$valid_skills" -le 0 ]; then
  echo ""
  echo "BLOCKED: no valid skills to sync after applying deny-list"
  exit 1
fi

if [ "$warnings" -gt 0 ]; then
  echo "PASSED with $warnings warning(s) — stubs will compress oversized skills"
else
  echo "PASSED — all checks clean"
fi
exit 0
