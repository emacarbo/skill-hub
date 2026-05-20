---
name: skill-consolidate
description: >
  Map relationships between skills — groups, overlaps, blind spots, trigger conflicts.
  Output is a consolidation-map.yaml. Uses usage data to inform merge decisions.
triggers: [skill consolidate, consolidate skills, map skills, /skill-consolidate]
---

# Skill Consolidate

Analyzes skills and produces a relationship map. Does NOT rewrite anything —
the map is the contract for `/skill-promote` to execute.

## Output

Writes/updates `agents/general_skills/consolidation-map.yaml`.

## Steps

### 1. Load skills

Read all `.md` files in `general_skills/`. For each, extract:
- Name, description, triggers (from frontmatter)
- Summary header content (if present)
- Line count

### 2. Check usage data (post-swap only)

If `logs/claude/skills-usage.jsonl` exists, read it to inform merge decisions:
- Skills that co-trigger frequently may belong in the same cluster
- Skills never used may not be worth clustering
- Skills with quality flags should be reviewed before clustering

### 3. Group into clusters

Group by shared domain/triggers. A cluster is 2+ skills with >30% topic overlap.

For each cluster:
- **target_name**: what the consolidated skill should be called
- **sources**: list of skill names in this cluster
- **contributions**: what each source uniquely adds
- **blind_spots**: gaps none of the sources cover
- **trigger_conflicts**: triggers that overlap between sources (must be resolved during merge)
- **keep_separate**: sources that are complementary, not overlapping

### 4. Singles

Skills with no cluster peers: mark as `standalone: true`.

### 5. Write consolidation-map.yaml

```yaml
clusters:
  - target_name: react-development
    sources: [react-best-practices, react-patterns, react-ui-patterns]
    contributions:
      react-best-practices: performance rules, memoization
      react-patterns: hooks composition, custom hooks
      react-ui-patterns: loading states, error boundaries
    blind_spots:
      - accessibility patterns
    trigger_conflicts:
      - "React" triggers all three — merge into single trigger set
    keep_separate: []
    usage_data:
      co_trigger_count: 5  # how often these skills loaded together
      total_reads: 34       # combined usage in tracking period

standalones:
  - name: dbt-layered-architecture
    reason: no other dbt-architecture skills
    usage: 12  # reads in tracking period
```

## What Happens Next

`/skill-promote` reads the map and merges each cluster into a single file.
The map is the contract — review it before promoting.
