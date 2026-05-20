---
name: skill-consolidate
description: "Use when you want to map how promoted skills relate — triggers on /skill-consolidate, \"consolidate skills\", \"map skill overlaps\", or \"which skills are redundant\". Produces consolidation-map.yaml that skill-promote reads when merging clusters. Run BEFORE promoting a cluster, not after."
triggers: [skill consolidate, consolidate skills, map skills, /skill-consolidate]
---

# Skill Consolidate

Analyzes promoted skills and produces a relationship map. Does NOT rewrite anything.
The agent reads this map when writing to agents/claude/ and merges the cluster in one pass.

## Output

Writes/updates `agents/general_skills/consolidation-map.yaml`.

## Steps

### 1. Load promoted skills
Read `manifest.yaml` — collect all entries with `status: promoted`.

### 2. Group into clusters
Group skills by shared `tech_stack_tags`. Within each tag group, identify sub-clusters
by semantic similarity (name + description). A cluster is 2+ skills that cover the same domain.

### 3. For each cluster: map relationships
Read the SKILL.md (or main file) for each skill in the cluster from `promoted/`.

For each cluster produce:
- **target_name**: what the consolidated skill should be called (descriptive, domain-scoped)
- **sources**: list of promoted skill names in this cluster
- **contributions**: for each source, one line of what it uniquely adds
- **blind_spots**: gaps none of the sources cover but the domain needs
- **keep_separate**: any sources that are complementary (not overlapping) and should stay as independent skills

### 4. Singles
Skills with no cluster peers stay as-is. Note them as `standalone: true` in the map.

### 5. Write consolidation-map.yaml
Append or update entries in `agents/general_skills/consolidation-map.yaml`.

## consolidation-map.yaml schema

```yaml
clusters:
  - target_name: react-development
    sources:
      - react-best-practices
      - react-patterns
      - react-ui-patterns
      - react-state-management
    contributions:
      react-best-practices: performance rules, memoization, render optimization
      react-patterns: hooks composition, custom hooks, render patterns
      react-ui-patterns: loading states, error boundaries, optimistic updates
      react-state-management: Zustand, Redux Toolkit, Jotai, React Query patterns
    blind_spots:
      - component testing patterns (none cover this)
      - accessibility in React components
    keep_separate: []

standalones:
  - name: dbt-transformation-patterns
    reason: no other dbt skills in promoted
```

## What happens next

When the agent runs `/skill-promote` for a cluster, it:
1. Reads `consolidation-map.yaml` for the target cluster
2. Reads all source SKILL.md files from `promoted/`
3. Writes ONE merged + agent-optimized file to `agents/claude/<target_name>.md`
4. Updates `manifest.yaml`: sources → `status: consolidated`, new entry → `status: agent-ready`

The map is the contract. The agent does the merge in a single rewrite pass.
