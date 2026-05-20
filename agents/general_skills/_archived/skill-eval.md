---
name: skill-eval
description: >
  Evaluate skill quality pre-swap and monitor skill health post-swap.
  Covers staging evaluation, post-swap 2-week monitoring, usage analytics,
  false-positive detection, and quality flagging.
triggers: [skill eval, evaluate skill, review staged skill, skill health, skill report, /skill-eval]
---

# Skill Evaluation & Health Monitoring

## Part 1: Pre-Swap Evaluation (Staging -> Promoted)

Use when evaluating a candidate skill before adding it to the library.

### Steps

1. **Read the skill file** from `staging/` or the source URL
2. **Check relevance** — match skill tags against active stack (Python, TypeScript/React, SQL/dbt)
3. **Check quality:**
   - Well-structured with clear sections?
   - Actionable instructions (not vague advice)?
   - No hallucinated tool names or APIs?
   - Code examples are correct and runnable?
4. **Check overlap** — does a similar skill exist in `general_skills/`?
   - If overlap > 70%: reject (absorbed by existing cluster)
   - If overlap 30-70%: consider merging into existing cluster
   - If overlap < 30%: accept as standalone
5. **Check trigger conflicts** — would this skill's triggers fire on the same prompts as an existing skill?

### Decision

| Verdict | Action |
|---------|--------|
| Accept | Move to `general_skills/`, update consolidation-map if cluster |
| Merge | Fold unique content into existing cluster skill |
| Reject | Note reason, do not add |

### Evaluation Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| Stack relevance | Directly useful for Python, React/TS, SQL/dbt, or infra tooling | Tangentially related or wrong stack entirely |
| Usage prediction | Expected weekly+ use in active projects | Monthly-or-less use (reject unless domain-critical) |
| Quality | Clear, actionable, correct examples | Vague, broken, or hallucinated |
| Uniqueness | <30% overlap with existing skills | >30% overlap (must merge, not add standalone) |
| Size | Full file ≤10 KB, stub ≤600 bytes | Oversized — trim or split before promoting |
| Context budget | Library total (stubs) stays under 25 KB (~6K tokens) | Adding this skill exceeds budget — remove one first |
| Safety | No destructive operations without confirmation | Blind deletes, force pushes |
| Trigger isolation | Distinct triggers from existing skills | Same triggers as existing cluster |

### Token ROI Check

Before accepting, estimate the cost-benefit:
- **Cost**: stub size in bytes × number of API calls per session (assume 50)
- **Value**: how often will this skill prevent a mistake or save manual explanation?
- Rule of thumb: if you'd need to explain the same thing 2+ times/week without the skill, it pays for itself

---

## Part 2: Post-Swap Health Monitoring

Use during the 2-week evaluation period after swapping to the new skill library.
Reads data from `logs/claude/sessions/*.jsonl` and `logs/claude/skills-usage.jsonl`
(written by `session-tracker.py` on every compaction and session end).

### Run: `/skill-eval health`

Produces a health report covering three dimensions:

### Dimension 1: Context Pressure

**Data source:** `logs/claude/sessions/*.jsonl` — `skill_count` and `compaction_markers` per session.

| Metric | Healthy | Warning | Action |
|--------|---------|---------|--------|
| Skills loaded per session | 1-3 | 4-6 | >6: check trigger deconfliction |
| Compaction events per session | 0-1 | 2 | >2: skills are consuming too much context |
| Avg transcript lines before compaction | >500 | 300-500 | <300: skills loading too early |

**Check:**
```bash
# Count avg skills per session (last 7 days)
cat ~/dev/skill-hub/logs/claude/sessions/*.jsonl | \
  python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin]; print(f'Avg skills/session: {sum(d[\"skill_count\"] for d in data)/len(data):.1f}')"
```

### Dimension 2: False-Positive Triggers (Co-Trigger Analysis)

**Data source:** `logs/claude/sessions/*.jsonl` — `co_triggers` field.

When two large skills load together repeatedly, one is likely a false positive.

| Signal | Meaning | Action |
|--------|---------|--------|
| Same pair co-triggers 3+ times in a week | Trigger overlap | Tighten triggers on the less relevant skill |
| Cluster + standalone co-trigger | Standalone may be redundant | Check if standalone adds value over cluster |
| 3+ skills co-trigger on single session | Ambiguous prompt or bad triggers | Review which skill actually answered the question |

**Check:**
```bash
# Find most common co-trigger pairs
cat ~/dev/skill-hub/logs/claude/sessions/*.jsonl | \
  python3 -c "
import sys,json
from collections import Counter
pairs = Counter()
for line in sys.stdin:
    d = json.loads(line)
    for pair in d.get('co_triggers', []):
        pairs[tuple(sorted(pair))] += 1
for pair, count in pairs.most_common(10):
    print(f'  {count}x  {pair[0]} + {pair[1]}')
"
```

### Dimension 3: Skill Usage & Staleness

**Data source:** `logs/claude/skills-usage.jsonl`

| Metric | Healthy | Warning | Action |
|--------|---------|---------|--------|
| Skill used in last 14 days | Active | — | Keep |
| Skill not used in 14-30 days | Stale | Check if relevant to stack | Keep if domain-critical |
| Skill not used in 30+ days | Dead | Not in active stack | Candidate for removal |
| Community standalone never used | Untested | May be irrelevant | Remove after 30 days unused |

**Check:**
```bash
# Skills ranked by usage (last 14 days)
cat ~/dev/skill-hub/logs/claude/skills-usage.jsonl | \
  python3 -c "
import sys,json
from collections import Counter
from datetime import datetime, timedelta, timezone
cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
usage = Counter()
for line in sys.stdin:
    d = json.loads(line)
    if d['timestamp'] >= cutoff:
        usage[d['skill']] += d['reads'] + d['invocations']
for skill, count in usage.most_common(20):
    print(f'  {count:3d}  {skill}')
"
```

### Dimension 4: Quality Flags

Track skills that produced bad advice or needed correction mid-session.

**Manual process** (no automation yet):
- After a session where a skill gave wrong advice, log it:
  ```bash
  echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"<name>","issue":"<description>","severity":"<low|medium|high>"}' \
    >> ~/dev/skill-hub/logs/claude/quality-flags.jsonl
  ```
- Review quality flags weekly during `/skill-sync`

---

## Part 3: Health Report Format

```
=== Skill Health Report (2-week post-swap) ===
Period: 2026-04-03 to 2026-04-17

CONTEXT PRESSURE
  Avg skills/session: 2.3 (healthy)
  Avg compactions/session: 0.8 (healthy)
  Sessions hitting >6 skills: 2/47 (4%)

FALSE POSITIVES
  Top co-trigger pairs:
    5x  python-web-frameworks + testing-qa-suite (expected — Django + tests)
    3x  react-development + frontend-ui-ux (review — may need tighter triggers)
    2x  database-pro + data-engineering-pro (expected — SQL + dbt)

USAGE (top 10)
    34  testing-qa-suite
    28  python-core
    22  react-development
    19  architecture-planning
    15  code-review-suite
    ...

STALE (0 uses in 14 days)
    antigravity-biopython (never used — remove?)
    antigravity-scanpy (never used — remove?)
    wshobson-game-development (never used — remove?)

QUALITY FLAGS
    1x  antigravity-django-perf-review — suggested deprecated Django API (medium)

RECOMMENDATIONS
  - Tighten triggers on react-development vs frontend-ui-ux
  - Remove 3 unused community standalones
  - Review antigravity-django-perf-review for outdated APIs
```
