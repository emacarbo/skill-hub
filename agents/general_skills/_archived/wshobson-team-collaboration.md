---
name: wshobson-team-collaboration
description: Team collaboration patterns for DX optimization, GitHub issue resolution, and async standup workflows
---

# Team Collaboration

Covers developer experience optimization (onboarding, tooling, workflows), systematic GitHub issue resolution (triage, TDD, PR creation), and async-first standup note generation from Git/Jira/Obsidian.

## Key Patterns

- **DX onboarding < 5 minutes** -- automate deps, intelligent defaults, helpful error messages
- **Issue triage by priority** -- P0 (production breaking), P1 (major broken), P2 (minor, workaround exists), P3 (cosmetic/enhancement)
- **Root cause with git bisect** -- `git bisect start && git bisect bad HEAD && git bisect good <tag>` to find regression commit
- **Branch naming** -- `fix/issue-123-description`, `feature/issue-456-description`, `hotfix/issue-789-critical`
- **TDD for every fix** -- write failing test first, implement fix, verify green, check coverage
- **Atomic commits** -- `git add -p` for partial staging; one logical change per commit
- **PR links issue** -- `Fixes #123` in PR body auto-closes issue on merge
- **Async standup format** -- Yesterday (delivered value) / Today (specific outcomes) / Blockers (actionable, tagged)
- **Blocker escalation** -- include: description, blocked since, impact, what you need, from whom, what you tried
- **AI-assisted standup** -- parse git log + Jira tickets + Obsidian tasks; group commits by feature; human review before posting

## Quick Reference

### GitHub issue resolution workflow

```bash
# 1. Triage
gh issue view $ID --comments --json title,body,labels

# 2. Branch
git checkout -b fix/issue-${ID}-short-description

# 3. Investigate
git log --oneline --grep="component" -20
rg "functionName" --type py -A 3

# 4. Write failing test, then implement fix

# 5. Commit
git add -p
git commit -m "fix(auth): validate token expiry (#${ID})"

# 6. Create PR
gh pr create \
  --title "Fix #${ID}: description" \
  --body "Fixes #${ID}
## Changes
- ...
## Testing
- [x] Unit tests added
- [x] All tests pass" \
  --assignee @me
```

### Async standup template

```markdown
## Yesterday
- Shipped X (JIRA-123) -- deployed to production, monitoring green
- Fixed Y affecting Z users -- PR #456 merged

## Today
- Continue JIRA-789 -- target: API integration complete by EOD
- Code review PR #012 for @teammate

## Blockers
- **Need:** staging DB refresh for integration tests
  - **From:** @devops | **Impact:** can't test full flow
  - **Workaround:** mock data (lower confidence)
```

### DX optimization checklist

```
[ ] Clone-to-running-app in < 5 minutes
[ ] Single command for deps install + DB setup + seed data
[ ] Pre-commit hooks (lint, format, type-check)
[ ] Useful error messages in dev scripts
[ ] IDE config committed (.vscode/settings.json, .editorconfig)
[ ] Makefile or package.json scripts for common tasks
[ ] Troubleshooting section in README
```

## When to Use

- Setting up or improving developer onboarding and tooling
- Resolving GitHub issues systematically (triage through PR and verification)
- Generating daily standup notes from commits, tickets, and notes
- Structuring async team communication for remote/distributed teams
- Escalating blockers with actionable context
