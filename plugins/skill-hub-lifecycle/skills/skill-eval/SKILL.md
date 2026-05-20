---
name: skill-eval
description: "Use when evaluating skills — either (a) a staged candidate before promoting it, or (b) the invocation health of installed skills based on router + invocation logs. Triggers on /skill-eval, \"evaluate skill\", \"review staged skill\", \"audit skill invocations\", \"check skill routing\", \"why isn't skill X being invoked\", or \"expand skill triggers\". Run BEFORE skill-promote (mode A), or weekly to keep the regex router catching up to Haiku (mode B)."
triggers: [skill eval, evaluate skill, review staged skill, /skill-eval, audit skill invocations, check skill routing, expand triggers, why isn't skill being invoked, skill health, router gaps]
---

# Skill Evaluation

Two modes — pick based on the user's request:

- **Mode A — Candidate eval**: a new skill is in `skill-lifecycle/staging/` and you need accept/reject decision before promotion.
- **Mode B — Invocation health**: installed skills already exist; look at how well they're being invoked (router log + usage log) and recommend improvements.

If the user's request doesn't clearly pick one, ask which mode. Default to Mode B if they mention "router", "invocation", "triggers", "audit", or "health".

---

## Mode A — Candidate Eval

For a candidate skill in `skill-lifecycle/staging/`.

### Steps

1. **Read the skill file** from `staging/`
2. **Check relevance** — read `~/dev/skill-hub/stack-context.yaml` and match skill tags against `active_tags`. At least one match required.
3. **Check quality** — is it well-structured, clear instructions, no hallucinated tool names?
4. **Check overlap** — does a similar skill already exist in `general_skills/` or `agents/claude/`? Check `manifest.yaml`.
5. **Decision**

### Accept → Promoted
- Move file to `skill-lifecycle/promoted/`
- Add entry to `manifest.yaml` with `status: promoted`
- Note `tech_stack_tags` and `compatible_agents`

### Reject
- Move file to `skill-lifecycle/rejected/`
- Add entry to `manifest.yaml` with `status: rejected` and `rejection_reason`

### Evaluation Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| Relevant to active stack | At least one tag matches | Completely unrelated |
| Quality | Clear, actionable instructions | Vague, broken, or hallucinated |
| Uniqueness | No duplicate in promoted/general | Duplicate exists |
| Safety | No destructive operations without confirmation | Blind deletes, force pushes |

---

## Mode B — Invocation Health Review

Reads two logs to surface which skills are working and which are dormant or invisible to the router. Used as the weekly checkpoint for the regex+Haiku distillation loop.

### Inputs

- `~/.claude/logs/skill-routing.jsonl` — one row per non-trivial user prompt. Each row carries `regex_matches`, `haiku_matches`, and a `category` (`both-agree`, `regex-only`, `haiku-only`, `haiku-superset`, `both-empty`, `regex-superset`, `partial-overlap`).
- `~/.claude/logs/skill-invocations.jsonl` — one row per actual `Skill(skill=X)` call, with `source` attribution (`direct`, `router-suggested`, `do-routed`).

### Steps

1. **Define the window** — default last 7 days unless the user specifies otherwise (`--since 14d`, `--all`).

2. **Per-skill aggregate**:
   ```
   For each skill seen in either log over the window:
     n_router_suggested   = count of routing rows that matched this skill
     n_router_regex       = ditto but specifically from regex_matches
     n_router_haiku       = ditto but specifically from haiku_matches
     n_invoked            = count of invocations from skill-invocations.jsonl
     n_invoked_direct     = ditto where source == "direct"
     n_invoked_router     = ditto where source == "router-suggested"
     n_invoked_do         = ditto where source == "do-routed"
     follow_through_rate  = n_invoked_router / n_router_suggested
   ```

3. **Surface five tables**, in this order:

   **Table 1 — Router gaps (`haiku-only` / `haiku-superset`)**. Prompts where Haiku caught a skill the regex missed. THE most important section — drives trigger expansion.
   For each such (prompt, skill) pair, propose 1-3 new trigger phrases to add to that skill's `triggers:` YAML field. Show the user the diff before applying.

   **Table 2 — Dormant skills**. Skills with zero invocations in the window. Either (a) descriptions/triggers are invisible to Claude even when relevant, or (b) the user genuinely doesn't need them. Suggest deletion candidates for the second case.

   **Table 3 — Suggested but ignored**. High `n_router_suggested` but low `follow_through_rate` (<30%). The router is firing but Claude isn't running the skill — meaning either the suggestion is wrong (router false positive) or the skill itself is unhelpful. Investigate.

   **Table 4 — Source mix**. For each skill: `direct / router / /do` invocation split. Reveals usage patterns — heavily-direct means the user types it; heavily-router means the hook drives it; heavily-do means /do is the entry point.

   **Table 5 — Cost**. Estimate Haiku spend over the window (~$0.03 per Haiku call × `haiku_match_count`). Flag if approaching the user's stated budget.

4. **Propose actions** at the end:
   - Trigger expansions (with concrete YAML edits to apply)
   - Skill deletions (with confirmation prompt)
   - Whether to disable Haiku now that regex catches enough (target: `haiku-only` < 10% of matched prompts)
   - Whether to keep Haiku on if `haiku-only` is still high

5. **Wait for confirmation** before editing any SKILL.md trigger fields. Show the diff.

### Quality bar for new trigger phrases

When proposing trigger additions:
- 2–6 words, lowercase, natural phrasing
- Use the user's actual words from the `haiku-only` prompts (not paraphrases)
- Avoid single common words ("test", "data") that match everything
- Prefer multi-word phrases or compound terms ("slow query", "explain analyze")
- Never propose a phrase that would also match unrelated prompts — if uncertain, leave it out

### Output format

Report markdown, terminal-friendly. For trigger proposals, show one block per skill:

```
### postgres-patterns
Currently triggers on: ["postgres", "RLS policy", "EXPLAIN ANALYZE"]
Haiku caught the user saying: "this query takes forever", "I need to add an index", "why is the join slow"
Proposed additions: ["query takes forever", "add an index", "join slow"]
Apply? [y/n/edit]
```
