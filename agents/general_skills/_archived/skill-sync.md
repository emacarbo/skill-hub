---
name: skill-sync
description: >
  Weekly audit of skill pipeline health — staleness, drift, symlink integrity,
  usage analytics, quality flags, and community standalone review.
triggers: [skill sync, sync skills, audit skills, check skills, weekly review, /skill-sync]
---

# Skill Sync (Weekly Audit)

Run weekly (suggested: Mondays) to keep the skill library healthy.
Combines pipeline integrity checks with post-swap monitoring data.

## Checks

### 1. Usage Analytics

Read `logs/claude/skills-usage.jsonl` and produce usage rankings.

```bash
# Skills used in last 7 days, ranked
python3 -c "
import sys, json
from collections import Counter
from datetime import datetime, timedelta, timezone
cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
usage = Counter()
for line in open('$HOME/dev/skill-hub/logs/claude/skills-usage.jsonl'):
    d = json.loads(line)
    if d['timestamp'] >= cutoff:
        usage[d['skill']] += d['reads'] + d['invocations']
print('=== Usage (last 7 days) ===')
for skill, count in usage.most_common():
    print(f'  {count:3d}  {skill}')
"
```

Flag:
- **Unused 30+ days**: candidate for removal (unless domain-critical)
- **Used only once**: might have been a false trigger — check co-trigger data
- **Top 5 most used**: these are load-bearing — protect from accidental changes

### 2. Staleness

For each skill in `general_skills/`:
- Check `git log --format=%ai -1 -- <file>` for last modification date
- If modified > 90 days ago AND unused in 30 days: **flag for review**
- Community standalones (alireza-/antigravity-/wshobson-) have no upstream sync — staleness is permanent unless we update manually

### 3. Co-Trigger Review

Read `logs/claude/sessions/*.jsonl` and identify problematic co-trigger pairs.

```bash
# Co-trigger pairs from last 7 days
python3 -c "
import sys, json
from collections import Counter
from datetime import datetime, timedelta, timezone
cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
pairs = Counter()
for line in open('$HOME/dev/skill-hub/logs/claude/sessions/' + datetime.now().strftime('%Y-%m-%d') + '.jsonl'):
    d = json.loads(line)
    if d['timestamp'] >= cutoff:
        for pair in d.get('co_triggers', []):
            pairs[tuple(sorted(pair))] += 1
print('=== Co-triggers (last 7 days) ===')
for pair, count in pairs.most_common(10):
    status = 'CHECK' if count >= 3 else 'ok'
    print(f'  {count}x  {pair[0]} + {pair[1]}  [{status}]')
"
```

Pairs with 3+ co-triggers in a week: review trigger keywords for overlap.

### 4. Quality Flags Review

Read `logs/claude/quality-flags.jsonl`:
- **High severity**: fix this week (update the skill or remove it)
- **Medium severity**: investigate, fix within 2 weeks
- **Low severity**: note for next review

### 5. Symlink Integrity

For each skill expected in `~/.claude/skills/`:
- Verify directory exists
- Verify `SKILL.md` symlink is not broken
- Verify symlink target file exists in `general_skills/`

```bash
# Check for broken symlinks
for d in ~/.claude/skills/*/; do
  skill="${d%/}"
  if [ -L "$skill" ]; then
    target=$(readlink "$skill")
    [ ! -e "$target" ] && echo "BROKEN: $skill -> $target"
  elif [ -L "$skill/SKILL.md" ]; then
    target=$(readlink "$skill/SKILL.md")
    [ ! -e "$target" ] && echo "BROKEN: $skill/SKILL.md -> $target"
  fi
done
```

### 6. Manifest Gaps

- Skills in `general_skills/` with no manifest entry: add entries
- Skills in manifest with `status: agent-ready` but no symlink: flag for re-linking
- Skills removed from `general_skills/` but still in manifest: clean up manifest

## Output Format

```
=== Skill Sync Report (YYYY-MM-DD) ===

USAGE (last 7 days)
  Top 5: [list with counts]
  Unused: [list]

CO-TRIGGERS
  Problematic pairs (3+ in week): [list]
  Expected pairs (known-good): [list]

QUALITY FLAGS
  Open: [count by severity]
  Resolved since last sync: [count]

STALENESS
  Stale (90+ days, unused 30+): [list]
  Community standalones never used: [list]

SYMLINKS
  Broken: [list]
  Missing: [list]

ACTIONS
  - [Specific action items with priority]
```

## Decision Framework

| Signal | Severity | Action |
|--------|----------|--------|
| Skill unused 30+ days, not domain-critical | Low | Remove |
| Skill unused 30+ days, domain-critical | None | Keep (insurance) |
| Co-trigger pair 3+ times/week | Medium | Tighten triggers on less relevant skill |
| Quality flag (high) | High | Fix or remove this week |
| Quality flag (medium) | Medium | Fix within 2 weeks |
| Broken symlink | High | Re-link immediately |
| Community standalone with quality flag | High | Remove — untested and buggy |
