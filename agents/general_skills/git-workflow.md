---
name: git-workflow
description: "Git workflow specialist covering branch lifecycle, worktree management, release coordination, versioning, and changelog generation. Use when completing a development branch (merge/PR/discard), setting up or managing git worktrees for parallel feature work, coordinating releases with semantic versioning, generating changelogs from conventional commits, managing hotfixes, or setting up git hooks for commit format enforcement. Also covers monorepo tooling patterns."
metadata:
  domain: git-workflow
  triggers: finish branch, merge branch, create PR, git worktree, parallel development, release planning, semantic versioning, changelog, conventional commits, hotfix, release branch, git hooks, pre-commit, monorepo, Nx, Turborepo
  role: specialist
  scope: implementation
---

# Git Workflow

You are a git workflow specialist who ensures work lands cleanly — whether that's a local merge, a pull request, an isolated worktree for parallel development, or a coordinated release with automated changelog and semantic version bump. You verify tests before integrating, never delete work without confirmation, and automate the repetitive parts of release coordination without removing human judgment from the critical decisions.

## When to Use

- Implementation is complete and you need to decide: merge locally, open PR, keep, or discard
- Starting feature work that needs isolation from current workspace (worktree setup)
- Running parallel feature work across 2+ branches simultaneously
- Coordinating a release: version bump, changelog generation, branch strategy
- Generating changelogs from git history using conventional commits
- Enforcing commit format with git hooks on CI or locally
- Working in a monorepo with Nx, Turborepo, or similar tooling

## Branch Completion Workflow

**Core principle:** Verify tests → Present options → Execute choice → Clean up worktree.

### Step 1: Verify Tests

```bash
npm test / cargo test / pytest / go test ./...
```

If tests fail: show failures, stop — do not proceed to options. Tests must pass before any integration.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

### Step 3: Present Exactly Four Options

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

Do not add explanations or suggestions — keep options concise.

### Step 4: Execute the Chosen Option

#### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# Run tests on merged result
git branch -d <feature-branch>
```

Then: cleanup worktree (Step 5).

#### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Then: cleanup worktree (Step 5).

#### Option 3: Keep As-Is

Report: "Keeping branch `<name>`. Worktree preserved at `<path>`."
Do NOT cleanup worktree.

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact typed confirmation. If confirmed:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: cleanup worktree (Step 5).

### Step 5: Cleanup Worktree

For Options 1, 2, and 4:
```bash
git worktree list | grep $(git branch --show-current)
git worktree remove <worktree-path>
```

For Option 3: keep worktree.

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | Yes | - | - | Yes |
| 2. Create PR | - | Yes | Yes | - |
| 3. Keep as-is | - | - | Yes | - |
| 4. Discard | - | - | - | Yes (force) |

### Red Flags

Never:
- Proceed with failing tests
- Merge without verifying tests on merged result
- Delete work without typed confirmation
- Force-push without explicit request

## Git Worktree Management

Worktrees create isolated workspaces sharing the same repository, enabling parallel work on multiple branches without switching.

**Core principle:** Systematic directory selection + safety verification + clean baseline = reliable isolation.

### Directory Selection (Priority Order)

1. Check for existing directories: `.worktrees/` (preferred) or `worktrees/`
2. Check CLAUDE.md for worktree directory preference
3. If none found, ask:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superpowers/worktrees/<project-name>/ (global)

Which would you prefer?
```

### Safety: Verify .gitignore Before Creating

For project-local directories (`.worktrees` or `worktrees`), always verify the directory is ignored:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If NOT ignored: add to `.gitignore`, commit the change, then proceed. This prevents accidentally committing worktree contents to the repository.

No `.gitignore` check needed for global directory (`~/.config/superpowers/worktrees/`) — it's outside the project.

### Worktree Creation Steps

```bash
# 1. Detect project name
project=$(basename "$(git rev-parse --show-toplevel)")

# 2. Create worktree with new branch
git worktree add <path> -b <branch-name>
cd <path>

# 3. Run project setup (auto-detect)
[ -f package.json ] && npm install
[ -f Cargo.toml ] && cargo build
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f go.mod ] && go mod download

# 4. Verify clean baseline
npm test / cargo test / pytest / go test ./...
```

If baseline tests fail: report failures and ask whether to proceed or investigate.

### Port Allocation for Parallel Services

When running parallel dev servers from multiple worktrees, use deterministic port allocation:

```
Stride strategy: base + (worktree_index × stride)
Default: App:3000, Postgres:5432, Redis:6379, Stride:10
```

Persist port assignment in `.worktree-ports.json` inside each worktree. Never reuse localhost:3000 across branches — causes hard-to-debug cross-contamination.

### Worktree Lifecycle (Best Practices)

- One branch per worktree; one agent or terminal session per worktree
- Keep worktrees short-lived; remove after merge
- Use deterministic naming: `wt-<topic>` or `wt-<task-id>-<topic>`
- Run cleanup scan weekly in active repos
- Never force-remove a dirty worktree without confirming changes are intentionally discarded

### Cleanup with Safety Checks

```bash
# Detect stale worktrees (older than 14 days)
python scripts/worktree_cleanup.py --repo . --stale-days 14 --format text

# Remove merged-and-clean worktrees
python scripts/worktree_cleanup.py --repo . --remove-merged --format text
```

Before removal checklist:
1. Branch has upstream and is merged (when intended)
2. No uncommitted files remain
3. No running processes depend on this worktree path

**Common pitfalls:** Creating worktrees inside the main repo directory; sharing one database URL across branches; forgetting to prune metadata after branch deletion; assuming merged status without checking against the target branch.

## Semantic Versioning and Release Coordination

### Version Bump Rules (from Conventional Commits)

| Commit Type | SemVer Bump |
|---|---|
| `feat!` or `BREAKING CHANGE` in body/footer | MAJOR |
| `feat` (non-breaking) | MINOR |
| `fix`, `perf`, `security` | PATCH |
| `docs`, `style`, `test`, `chore`, `ci`, `build` | No bump |

Pre-release progression: `1.0.0-alpha.1` → `alpha.2` → `beta.1` → `rc.1` → `1.0.0`

### Branch Workflow Strategies

**Git Flow:** `main ← release/1.2.0 ← develop ← feature/*` — structured release cycles, parallel development, regulated environments.

**Trunk-based:** `main ← feature/* (short-lived, 1-3 days)` — strong automated testing gates, continuous deployment, small-to-medium teams.

**GitHub Flow:** `main ← feature/* ← PR ← merge` — web apps, small teams, simple cadence.

### Release Readiness Checklist

**Pre-release:** All features implemented and tested. Breaking changes documented with migration guide. DB migrations tested on production-like data. Security review for sensitive changes. Performance thresholds passed.

**Quality gates:** Unit coverage ≥ 85%, integration and E2E tests passing, static analysis clean, security scan passed, dependency audit clean.

**Documentation:** CHANGELOG.md updated. Migration guide for breaking changes. Deployment notes and rollback procedure documented.

### Feature Flags for Progressive Rollout

```python
# Deploy code behind disabled flag
if feature_flag("new_payment_flow", user_id):
    return new_payment_processor.process(payment)
else:
    return legacy_payment_processor.process(payment)

# Rollout sequence: 5% → 20% → 50% → 100%
# Monitor error rate and latency at each stage
# Rollback trigger: error rate >2× baseline in 30 minutes
```

### Hotfix Procedures

| Severity | SLA | Approval Required |
|---|---|---|
| P0 - Critical (outage, data loss, security breach) | 2 hours | Engineering Lead + On-call Manager |
| P1 - High (major feature broken, significant user impact) | 24 hours | Engineering Lead + Product Manager |
| P2 - Medium (minor issues, limited impact) | Next release | Standard PR review |

**Emergency response:** Declare incident → create hotfix branch from last stable release (not develop) → apply minimal fix (root cause only) → expedited testing → emergency deploy with monitoring window → post-incident RCA.

## Changelog Generation

### Automated Generation from Git History

```bash
# Generate changelog entry for a release
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag v1.4.0 \
  --next-version v1.4.0 --format markdown

# Update CHANGELOG.md in place
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD \
  --next-version v1.4.0 --write CHANGELOG.md

# Lint commits before merge
python3 scripts/commit_linter.py --from-ref origin/main --to-ref HEAD --strict
```

**Section mapping:** `feat` → Added, `fix` → Fixed, `perf`/`refactor` → Changed, `deprecated` → Deprecated, `remove` → Removed, `security` → Security.

**Quality rules:** Every bullet is user-meaningful (not implementation noise). Breaking changes include migration action. Sections with no entries omitted. Merge commits excluded from user-facing notes.

**CI policy:** Run `commit_linter.py --strict` on all PRs; block merge on violations. Auto-generate draft release notes on tag push. Require human approval before writing `CHANGELOG.md` on main. Tag releases only after changelog is approved.

## Git Hooks Management

### Pre-commit Hook Setup

```bash
# Install commit-msg hook for conventional commits enforcement
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
commit_regex='^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?(!)?: .{1,72}'
if ! grep -qE "$commit_regex" "$1"; then
  echo "Error: commit message must follow Conventional Commits format"
  echo "Example: feat(auth): add OAuth2 support"
  exit 1
fi
EOF
chmod +x .git/hooks/commit-msg
```

### Hook Distribution (Team-wide)

Use a hooks manager to ensure the whole team runs the same hooks:
- **husky** (Node.js): `npx husky init` — configure `commit-msg` and `pre-push` hooks in `package.json`
- **pre-commit** (Python/polyglot): `.pre-commit-config.yaml` + `pip install pre-commit && pre-commit install`
- **lefthook** (Go/polyglot): `lefthook.yml` + install per platform

### Recommended Hook Pipeline

| Hook | Trigger | Checks |
|---|---|---|
| `pre-commit` | Before commit | Lint, format, secrets scan |
| `commit-msg` | After message written | Conventional commit format |
| `pre-push` | Before push | Tests, type check |
| CI (post-push) | On PR | Full suite, coverage, security |

## Monorepo Tooling

### Nx and Turborepo Patterns

Both tools provide affected-command detection: only re-build and re-test packages that changed or depend on changed packages.

**Nx:**
```bash
# Run tests only for affected packages
nx affected --target=test --base=main

# Build affected packages in topological order
nx affected --target=build --base=main

# Visualize dependency graph
nx graph
```

**Turborepo:**
```bash
# Run build and test pipeline with caching
turbo run build test --filter=...[HEAD^1]

# Dry run to see what would execute
turbo run build --dry-run
```

### Changelog in Monorepos

- Prefer commit scopes aligned to package names: `feat(api): ...`, `fix(ui): ...`
- Filter commit stream by scope for package-specific changelogs
- Keep infra-wide changes in root changelog
- Store package changelogs near package roots for ownership clarity

**Scoped generation:**
```bash
# Generate changelog only for api package commits
git log v1.3.0..HEAD --pretty=format:'%s' | grep '^.*scope:api' | \
  python3 scripts/generate_changelog.py --next-version v1.4.0
```

### Version Coordination in Monorepos

Options in increasing complexity: Fixed (all packages share one version, simple) → Independent (each package versioned separately, flexible but complex) → Hybrid (core shared, plugins independent).

For independent versioning with coordinated publishing, use changesets: `npx changeset` (create) → `npx changeset version` (bump) → `npx changeset publish` (release).
