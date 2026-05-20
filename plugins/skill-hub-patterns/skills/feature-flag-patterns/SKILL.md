---
name: feature-flag-patterns
description: "Feature flag lifecycle, SDK integration, targeting rules, gradual rollout, experimentation, and stale-flag cleanup. Use when implementing trunk-based development with flags or adding gradual rollout to a new feature."
metadata:
  domain: software-engineering
  triggers: feature flag, feature toggle, gradual rollout, LaunchDarkly, OpenFeature, Unleash, Split, A/B test, canary release, percentage rollout, trunk-based development, stale flags
  role: senior-engineer
  scope: implementation
---

## Role

You are a senior engineer who treats feature flags as a first-class engineering concern. You design flags with clear types, explicit lifecycle stages, and automatic cleanup gates — so flags never become permanent technical debt.

## When to Use

- Merging incomplete features to trunk without exposing them to users
- Implementing a gradual or percentage-based rollout
- Running an A/B or multivariate experiment
- Creating an operational kill switch for a risky change
- Auditing and cleaning up stale flags post-launch

## Core Workflow

### 1. Flag Type Taxonomy

Choose the right flag type before writing any code:

| Type | Purpose | Owner | Expected Lifetime |
|------|---------|-------|-------------------|
| **Release** | Hide incomplete feature during development | Engineering | Days to weeks |
| **Experiment** | A/B test or multivariate test | Product/Data | Duration of experiment |
| **Ops** | Kill switch, circuit breaker for a risky rollout | Engineering/SRE | Indefinite until stable |
| **Permission** | Gate access by user tier, plan, or role | Product | Long-lived / permanent |

Naming convention: `{type}_{team}_{feature}_{action}`
Examples: `release_equity_grant_export`, `experiment_pricing_annual_cta`, `ops_notifications_email_v2`

### 2. Trunk-Based Development with Flags

```
main branch (always deployable)
  └─ feature lives behind flag from day 1
  └─ merge small, daily increments
  └─ flag = OFF in prod until ready
  └─ flag = ON for internal testing
  └─ gradual rollout → 100% → flag removal
```

Rules:
- Create the flag in the flag service **before** writing the first line of flagged code
- Always default to the safe/off state — new flags default OFF in production
- Set flag to ON in staging/dev environments automatically via environment targeting
- Never use a flag to disable already-launched, stable features (that's config, not a flag)

### 3. Gradual Rollout Strategies

**Percentage rollout** (simplest):
```
0% → 1% → 5% → 20% → 50% → 100%
```
Monitor error rates and key metrics at each stage before advancing. Hold for at least one full traffic cycle (e.g., 24h to cover daily patterns).

**User segment targeting**:
- Internal employees first (dogfooding)
- Beta users / opt-in cohort
- Specific geography or plan tier
- Remaining users

**Sticky assignment**: ensure a user always gets the same variant within a session (hash user ID, not request ID).

**Gradual rollout checkpoints**:
1. Enable for internal users → verify no errors
2. Enable for 1% → watch metrics for 24h
3. Advance to 10%, 50%, 100% → remove flag after stable at 100% for one full release cycle

### 4. Testing with Flags

Every flag must be tested in all combinations relevant to the code path:
- **All-off**: test baseline (no flagged code active)
- **All-on**: test fully enabled path
- **Conflicting flags**: if two flags interact, test their combinations explicitly

Avoid flag spaghetti: if you need >3 boolean combinations to test a feature, your flag design is too granular.

For unit tests: inject flags as a dependency (don't call the flag SDK directly from business logic):
```python
# Good: flag value injected
def process_export(data, use_new_format: bool):
    ...

# Bad: flag SDK called deep in business logic
def process_export(data):
    if flag_client.is_enabled('release_equity_grant_export'):
        ...
```

### 5. Flag Lifecycle Management and Cleanup

Every flag must have a **sunset date** set at creation. Default: 30 days for release flags.

Cleanup workflow:
1. Flag reaches 100% rollout and is stable for one release cycle
2. Remove all flag evaluation code and both code branches
3. Delete the flag from the flag service
4. Verify no compile errors / test failures
5. PR title: `chore: remove feature flag {flag_name}`

Tracking: maintain a `feature-flags.md` or Jira label with: flag name, owner, created date, target removal date, current state.

### 6. Common Pitfalls

**Flag debt (permanent flags)**: release flags not removed after launch accumulate as hidden complexity. Every flag in the codebase is a branch you must test.

**Flag in the wrong layer**: don't put flag evaluations in database queries, background jobs, or shared utilities — only in the application layer where the user experience diverges.

**Missing default**: always specify what happens when the flag service is unreachable — default to the safe/existing behavior, never fail open.

**Bootstrapping race**: don't read flags before the SDK has initialized — cache the result or block startup until flags are loaded.

**A/B test leakage**: if the control and treatment groups share mutable state (same DB rows, same cache keys), the experiment is invalid.

### 7. Key Rules

- Every flag has a type, an owner, and a sunset date — set all three at creation
- Business logic never calls the flag SDK directly — inject the resolved boolean
- Default value is always the safe, pre-flag behavior
- Remove flags on schedule — flag removal is a feature, not cleanup
- Never use a feature flag as a configuration system (use env vars or a config service instead)
