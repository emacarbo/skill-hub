---
name: skill-promote
description: >
  Promote a skill to the next pipeline stage, run sync, and register in
  usage tracking. Handles both cluster merges and standalone promotions.
triggers: [skill promote, promote skill, ship skill, /skill-promote]
---

# Skill Promote

Moves a skill forward in the pipeline, syncs to `~/.claude/skills/`, and
registers it for usage tracking.

## Promotion Paths

### Cluster merge (skill belongs to a consolidation-map cluster)

1. Read `consolidation-map.yaml` — find the target cluster
2. Read ALL source files for that cluster
3. Write ONE merged file to `general_skills/<target_name>.md`:
   - Union of all sections (no redundancy)
   - Fill any `blind_spots` from the map
   - Add summary header (`<!-- SUMMARY -->`) for lazy-loading
   - Add distinct trigger keywords (check existing clusters for conflicts)
4. Run `scripts/sync-skills.sh` to create/update the symlink

### Standalone promotion (no cluster)

1. Read the skill file
2. Write to `general_skills/<skill-name>.md`
3. Run `scripts/sync-skills.sh` to create the symlink

### Post-Promotion

After any promotion:
1. Verify symlink: `ls -la ~/.claude/skills/<name>/SKILL.md`
2. Log the promotion event for tracking:
   ```bash
   echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"<name>","action":"promoted","source":"<source>"}' \
     >> ~/dev/skill-hub/logs/claude/promotions.jsonl
   ```
3. The skill will appear in usage analytics after its first use

## Promotion Gates (ALL must pass)

### Gate 1: Size Cap
- Full skill file: **≤10 KB**
- Generated stub: **≤600 bytes**
- If over: trim, split, or reject

### Gate 2: Context Budget
- Total library stubs must stay **under 25 KB (~6K tokens)**
- Check: `du -cb ~/.claude/skills/*/SKILL.md | tail -1`
- If adding this skill exceeds budget: identify a removal candidate first

### Gate 3: Library Cap — 1-in-1-out
- Hard cap: **70 skills** (25 Citadel + 45 general)
- If at capacity, must remove or merge an existing skill before adding
- Prefer removing lowest-usage skill (check `logs/claude/skills-usage.jsonl`)

### Gate 4: Consolidation-First
- If **≥30% overlap** with an existing skill → **must merge**, not add standalone
- Check: `grep -l '<key concept>' ~/dev/skill-hub/agents/general_skills/*.md`
- Merging into an existing skill does NOT count against the cap

### Gate 5: Trigger Deconfliction (Mandatory)

Before promoting, check that the skill's triggers don't overlap with existing skills:

```bash
# Find trigger conflicts
grep -l '<keyword>' ~/dev/skill-hub/agents/general_skills/*.md
```

If overlap found:
- Narrow the new skill's triggers to be more specific
- Or add a `Not for:` line to the summary header of both skills
