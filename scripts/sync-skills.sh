#!/bin/bash
# Sync general_skills/ → ~/.claude/skills/ AND plugin skill dirs.
#
# For each .md file in general_skills/, deploys a FULL copy to:
#   ~/.claude/skills/<name>/SKILL.md
#   ~/dev/skill-hub/plugins/<plugin>/skills/<name>/SKILL.md  (if present)
#
# The previous stub-generation step (scripts/generate-stubs.py) was archived —
# disk savings were negligible (~15KB/skill) and the truncated descriptions
# hurt skill invocation. Full content lives at deployed paths now.
#
# Preserves Citadel orchestration directories (do, marshal, archon, fleet, etc.)
# that have multi-file structures.
#
# Usage: ./sync-skills.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GENERAL_SKILLS="$REPO_ROOT/agents/general_skills"
SKILLS_DIR="$HOME/.claude/skills"
DRY_RUN="${1:-}"

# --- Enforcement gate: run pre-sync validation ---
# This blocks the sync if stack relevance, budget, or cap checks fail.
# Cannot be skipped — if the validator doesn't exist, sync refuses to run.
VALIDATOR="$SCRIPT_DIR/pre-sync-validate.sh"
if [ ! -x "$VALIDATOR" ]; then
  echo "ERROR: pre-sync-validate.sh not found or not executable at $VALIDATOR"
  echo "       Sync cannot proceed without validation."
  exit 1
fi

echo "=== Running pre-sync validation ==="
if ! bash "$VALIDATOR"; then
  echo ""
  echo "Sync BLOCKED by validation. Fix errors above first."
  exit 1
fi
echo ""

# Citadel orchestration skills to NEVER overwrite — they have multi-file
# directory structures (SKILL.md + sub-agents + references) that our flat
# files cannot replace.
PRESERVE=(
  "do" "marshal" "archon" "fleet" "architect" "autopilot"
  "configure-ecc" "continuous-learning-v2" "create-app" "create-skill"
  "design" "experiment" "live-preview" "postmortem" "qa" "research"
  "research-fleet" "review" "scaffold" "session-handoff" "setup"
  "systematic-debugging" "test-gen" "doc-gen" "refactor"
)

# Lifecycle/meta files to skip (not skills)
SKIP=(
  "consolidation-map" "skill-consolidate" "skill-discover"
  "skill-eval" "skill-promote" "skill-sync" "post-compact"
)

is_preserved() {
  local name="$1"
  for p in "${PRESERVE[@]}"; do
    [[ "$name" == "$p" ]] && return 0
  done
  return 1
}

is_skipped() {
  local name="$1"
  for s in "${SKIP[@]}"; do
    [[ "$name" == "$s" ]] && return 0
  done
  return 1
}

created=0
skipped=0
preserved=0

for md_file in "$GENERAL_SKILLS"/*.md; do
  name=$(basename "$md_file" .md)

  if is_skipped "$name"; then
    skipped=$((skipped + 1))
    continue
  fi

  if is_preserved "$name"; then
    echo "PRESERVE $name (Citadel orchestration)"
    preserved=$((preserved + 1))
    continue
  fi

  target_dir="$SKILLS_DIR/$name"

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "WOULD CREATE $target_dir/SKILL.md → $md_file"
    created=$((created + 1))
    continue
  fi

  # Remove old directory/symlink if it exists
  if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then
    rm -rf "$target_dir"
  fi

  # Minimum-content check: skip files with fewer than 20 lines (likely stubs).
  source_file="$md_file"
  line_count=$(wc -l < "$source_file")
  if [ "$line_count" -lt 20 ]; then
    echo "[WARN] Skipping $name: only $line_count lines (likely a stub, minimum 20 required)"
    continue
  fi

  # Copy the full source content to the deployed SKILL.md.
  # Full content (5-30KB/skill) is trivial disk-wise; rich descriptions and
  # bodies give Claude better invocation signals and direct skill access.
  mkdir -p "$target_dir"
  if ! cp "$source_file" "$target_dir/SKILL.md"; then
    echo "[ERROR] Copy failed for $name, skipping"
    continue
  fi
  echo "CREATE $name (full)"

  # Propagate the full copy to every plugin that owns this skill, so plugin
  # consumers (not just ~/.claude/skills/) get the same canonical content.
  for plugin_dir in "$HOME"/dev/skill-hub/plugins/*/skills/"$name"; do
    if [ -d "$plugin_dir" ]; then
      cp "$source_file" "$plugin_dir/SKILL.md"
    fi
  done

  created=$((created + 1))
done

echo ""
echo "=== Sync complete ==="
echo "Created/updated: $created"
echo "Preserved (Citadel): $preserved"
echo "Skipped (lifecycle): $skipped"
echo "Total in ~/.claude/skills/: $(ls "$SKILLS_DIR" | wc -l | tr -d ' ')"
