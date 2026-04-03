---
name: skill-sync
description: Audit the skill pipeline for staleness, drift, and missing symlinks
triggers: [skill sync, sync skills, audit skills, check skills, /skill-sync]
---

# Skill Sync

Run this periodically (suggested: weekly) to keep the pipeline healthy.

## Checks

### 1. Staleness
Read `manifest.yaml` and flag any skill where:
- `last_used.claude` or `last_used.codex` is older than 30 days → candidate for removal
- `date_updated` is older than 90 days and `source_url` is a GitHub repo → check if upstream has changed

### 2. GitHub upstream check
For each skill in `staging/` or `promoted/` whose manifest entry has a `source_url`:
- Fetch the raw SKILL.md from the source URL
- Diff against our local copy in staging/
- If upstream changed: show the diff and ask whether to pull the update into our version

This is safe because we copy (never sync) — upstream changes never touch our `general_skills/` or agent files automatically. You decide what to absorb.

### 3. Agent drift
For each skill with `status: agent-ready`:
- Verify the file exists in `agents/claude/` or `agents/codex/`
- Verify the symlink exists in `~/.claude/skills/` (for Claude skills)
- If symlink is broken or missing → flag for re-linking

### 3. Manifest gaps
- Skills in `agents/general_skills/` with no manifest entry → add entries with `status: general`
- Skills in `staging/` older than 14 days with no evaluation → flag for eval or cleanup

## Output

Produce a short report:
```
STALE (unused 30+ days): [list]
DRIFT (file/symlink mismatch): [list]
MANIFEST GAPS: [list]
READY FOR REMOVAL: [list]
```

Ask user to confirm before removing anything.
