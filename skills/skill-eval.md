---
name: skill-eval
description: Evaluate a skill in staging against the current tech stack and decide accept/reject
triggers: [skill eval, evaluate skill, review staged skill, /skill-eval]
---

# Skill Evaluation

Use this skill to evaluate a candidate skill in `skill-lifecycle/staging/` before promoting it.

## Steps

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

## Evaluation Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| Relevant to active stack | At least one tag matches | Completely unrelated |
| Quality | Clear, actionable instructions | Vague, broken, or hallucinated |
| Uniqueness | No duplicate in promoted/general | Duplicate exists |
| Safety | No destructive operations without confirmation | Blind deletes, force pushes |
