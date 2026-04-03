---
name: skill-discover
description: Analyze recent session context to detect skill gaps and search for candidates
triggers: [skill discover, discover skills, find skills, what skills do I need, /skill-discover]
---

# Skill Discover

Analyzes the current conversation and project context to identify skill gaps,
then searches for candidates in known marketplaces.

## Steps

### 1. Context Analysis
Look at:
- The current working directory and tech stack
- Recent tasks performed in this session
- Any repeated patterns: "I had to do X manually", "there's no skill for Y", tool calls that took many steps

Identify gaps: things that were done step-by-step that a skill could automate.

### 2. Check existing coverage
Before flagging a gap, check `manifest.yaml` — the skill may already exist in `promoted/` or `general_skills/`.

### 3. Search marketplace
For each confirmed gap, search these sources in order:
1. `skill-lifecycle/promoted/` — already evaluated and waiting
2. GitHub: search `claude-code skill <topic>` or `claude skill <topic>`
3. Known skill repos (already cloned in `~/dev/`):
   - `~/dev/claude-skills/`
   - `~/dev/antigravity-awesome-skills/`
   - `~/dev/alirezarezvani-claude-skills/`
   - `~/dev/wshobson-agents/`
   - `~/dev/superpowers/`

### 4. Recommend
For each gap, return:
- **Gap**: what's missing
- **Found**: skill name + source (or "not found")
- **Action**: copy to staging | build from scratch | not worth it

Only flag gaps that came up more than once or would save significant manual work.
