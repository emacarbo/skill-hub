---
description: Git workflow — branch completion, PR authoring, changelog, release management, worktrees.
---

# /git — Git Workflow

Read the **git-workflow** skill from `~/dev/skill-hub/agents/general_skills/git-workflow.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `finish` | Branch completion | 4-option flow: merge / PR / keep / discard |
| `pr` | Pull request | Analyze commits, draft PR title + body, push + create |
| `changelog` | Changelog | Generate changelog from conventional commits |
| `release <version>` | Release | Version bump, changelog, tag, release notes |
| `worktree <name>` | Worktree | Create isolated worktree with safety checks |
| *(no args)* | Status | Show branch, uncommitted changes, ahead/behind remote |

## Conventions

- Commit format: `<type>: <description>` (feat, fix, refactor, docs, test, chore, perf, ci)
- Branch naming: `<type>/<ticket-or-slug>` (e.g., `feat/equity-reallocation`)
- PR size target: < 400 lines changed
