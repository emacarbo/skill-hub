---
name: skill-discover
description: >
  Analyze session context and usage data to detect skill gaps.
  Uses co-trigger data and manual patterns to find what's missing.
triggers: [skill discover, discover skills, find skills, what skills do I need, /skill-discover]
---

# Skill Discover

Identifies skill gaps by analyzing current work context, usage analytics,
and repeated manual patterns.

## Gap Detection Methods

### 1. Session Context Analysis

Look at the current conversation:
- What is the user working on?
- Which tools were called repeatedly without skill guidance?
- Did the user explain something step-by-step that a skill could automate?
- Were there repeated corrections ("no, do it this way") that indicate missing conventions?

### 2. Usage Analytics (Post-Swap)

Read `logs/claude/sessions/*.jsonl`:
- **High tool-call sessions with no skills loaded**: the user did complex work without skill guidance — potential gap
- **Sessions with quality flags**: the skill gave bad advice — might need a better skill or an update
- **Repeated manual patterns**: same sequence of tool calls across multiple sessions without a skill

### 3. Blind Spot Check

Cross-reference the active tech stack against installed skills:

| Stack component | Expected skills | Check |
|-----------------|----------------|-------|
| Python | python-core, python-web-frameworks | installed? |
| TypeScript/React | typescript-javascript, react-development | installed? |
| SQL/dbt | database-pro, data-engineering-pro, dbt-layered-architecture | installed? |
| Testing | testing-qa-suite | installed? |
| Security | security-guardian | installed? |
| Git workflow | git-workflow | installed? |
| API design | api-design-pro | installed? |

### 4. Community Search (for confirmed gaps)

For each confirmed gap, search in order:
1. `general_skills/` — already in library but not installed?
2. GitHub: `claude-code skill <topic>` or `claude skill <topic>`
3. Known skill repos in `~/dev/`:
   - `~/dev/claude-skills/`
   - `~/dev/antigravity-awesome-skills/`
   - `~/dev/alirezarezvani-claude-skills/`
   - `~/dev/wshobson-agents/`

## Output

For each gap:
- **Gap**: what's missing
- **Found**: skill name + source (or "not found")
- **Action**: add to general_skills | merge into existing cluster | build from scratch | not worth it

Only flag gaps that would save real time or prevent real mistakes.
