---
name: skill-promote
description: "Use when moving a skill from staging to promoted, or from promoted to agents/claude/ — triggers on /skill-promote, \"promote skill\", \"ship skill\", or \"merge skill cluster\". Updates manifest.yaml and writes merged Claude-optimized files. Run skill-eval first, and skill-consolidate if merging a cluster."
triggers: [skill promote, promote skill, ship skill, /skill-promote]
---

# Skill Promote

Moves a skill forward in the pipeline and keeps `manifest.yaml` in sync.

## Promotion Paths

### Cluster → agents/claude (standard path via consolidation map)
Use for any skill that belongs to a cluster in `consolidation-map.yaml`.

1. Read `agents/general_skills/consolidation-map.yaml` — find the target cluster
2. Read ALL source SKILL.md files from `skill-lifecycle/promoted/` for that cluster
3. **Write ONE merged + Claude-optimized file** to `agents/claude/<target_name>.md`
   - Union of all sections from sources (no redundancy)
   - Fill any `blind_spots` listed in the map
   - Claude Code conventions: concise, directive, tool names, project-specific references
4. Update `manifest.yaml`:
   - Each source skill: `status: consolidated`, `consolidated_into: <target_name>`
   - New entry: `status: agent-ready`, `consolidated_from: [sources]`

### Standalone → agents/claude (single skill, no cluster)
Use for skills marked `standalone: true` in the consolidation map.

1. Read the skill from `skill-lifecycle/promoted/`
2. **Rewrite for Claude** in one pass
3. Write to `agents/claude/<skill-name>.md`
4. Update `manifest.yaml`: `status: agent-ready`

### Symlink to agent
Once a skill is in `agents/claude/`, symlink it:
```bash
ln -s ~/dev/skill-hub/agents/claude/<skill>.md ~/.claude/skills/<skill>.md
```
Update `manifest.yaml` with `last_used.claude` date.
