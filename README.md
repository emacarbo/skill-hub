# skill-hub

Central registry and lifecycle manager for all agent skills.

## Pipeline

```
GitHub / marketplace
    ↓  copy raw (never sync)
skill-lifecycle/staging/        ← under evaluation
    ↓  /skill-eval → accept
skill-lifecycle/promoted/       ← accepted individual skills
    ↓  /skill-consolidate → maps clusters, overlaps, blind spots
agents/general_skills/
  └─ consolidation-map.yaml     ← relationship contract (no rewrites here)
    ↓  /skill-promote → agent reads map + sources, writes ONE merged file
agents/claude/                  ← Claude-optimized, merged (real files)
agents/codex/                   ← Codex-optimized, merged (real files)
    ↓  symlink
~/.claude/skills/               ← what Claude actually reads
```

Rejected skills go to `skill-lifecycle/rejected/` with a reason logged in `manifest.yaml`.
`general_skills/` houses the lifecycle skills and `consolidation-map.yaml` — no rewrites, no copies.
The agent does one single rewrite pass (merge + optimize) directly into `agents/claude/`.

## Lifecycle Skills

| Skill | Purpose |
|-------|---------|
| `/skill-eval` | Evaluate a staged skill against the current tech stack |
| `/skill-consolidate` | Merge 2+ similar promoted skills into one canonical skill, write to general_skills |
| `/skill-promote` | Move a single promoted skill to general_skills (when no consolidation needed) |
| `/skill-sync` | Check staleness and agent drift across all promoted/general skills |
| `/skill-discover` | Analyze recent session context and suggest skill gaps |

## Logs

`logs/claude/` and `logs/codex/` contain daily compaction logs written by the
`PostCompact` hook. Each entry records the session timestamp, working directory,
and transcript path — giving visibility into which projects are active and when
skills were last exercised.

## Manifest

`manifest.yaml` is the single source of truth for every skill's status, origin,
tech stack compatibility, last-used dates, and rejection reasons.

## Rules

- **Never sync** from source repos — always copy. We own what's in this repo.
- `general_skills/` is agent-agnostic. Never put agent-specific formatting there.
- Agent folders (`claude/`, `codex/`) contain real files, not symlinks to general_skills.
- Only symlink at the very end: agent folder → `~/.claude/skills/` (or equivalent).
- Update `manifest.yaml` at every stage transition.
