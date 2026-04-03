---
name: productivity-learning
description: >
  Unified productivity-learning skill. Extract content from any source (YouTube, article, PDF),
  transform it into actionable Ship-Learn-Next quests with spaced repetition, and unblock stuck
  actions. Activate when user says "learn-this <URL>", "weave <URL>", "extract <URL>",
  "unblock", "I'm stuck on...", or asks to make content actionable.
allowed-tools: Bash,Read,Write
sources:
  - article-extractor
  - learn-this
  - ship-learn-next
  - unblock-action
  - youtube-transcript
---


<!-- SUMMARY
Scope: Content extraction, learning plans, action unblocking, spaced repetition, Zettelkasten
Capabilities: YouTube/article extraction, ship-learn-next quests, 2-min unblocking, retention tracking
Not for: Documentation (use documentation-suite), skill creation (use writing-skills standalone)
END SUMMARY -->

# Productivity Learning

End-to-end pipeline: **Extract** content, **Plan** actionable quests, **Retain** through
spaced repetition, and **Unblock** when stuck.

---

## 1. Trigger Detection

| User says | Mode |
|-----------|------|
| `learn-this <URL>`, `weave <URL>`, `extract and plan <URL>` | Full pipeline (extract + plan) |
| `extract <URL>`, `download article/transcript <URL>` | Extract only |
| `make this actionable`, `turn into a plan` + file/text | Plan only |
| `unblock`, `unstick`, `I'm stuck on...` | Unblock action |
| `review reps`, `what's due?`, `retention check` | Spaced repetition review |

---

## 2. Content Extraction

### 2.1 Detect Content Type

```bash
URL="$1"
if [[ "$URL" =~ youtube\.com/watch || "$URL" =~ youtu\.be/ || "$URL" =~ youtube\.com/shorts ]]; then
    CONTENT_TYPE="youtube"
elif [[ "$URL" =~ \.pdf$ ]] || curl -sI "$URL" | grep -iq "content-type: application/pdf"; then
    CONTENT_TYPE="pdf"
else
    CONTENT_TYPE="article"
fi
```

### 2.2 YouTube Transcript

**Prerequisites**: `yt-dlp` (install via `brew install yt-dlp` or `pip3 install yt-dlp`).

1. Check installation: `command -v yt-dlp`
2. List available subtitles: `yt-dlp --list-subs "$URL"`
3. Download (priority order):
   - Manual subs: `yt-dlp --write-sub --skip-download --sub-langs en --output "temp_transcript" "$URL"`
   - Auto-generated: `yt-dlp --write-auto-sub --skip-download --sub-langs en --output "temp_transcript" "$URL"`
   - Last resort: Whisper transcription (confirm with user first -- show audio size)
4. Get title: `VIDEO_TITLE=$(yt-dlp --print "%(title)s" "$URL" | tr '/' '_' | tr ':' '-' | tr '?' '' | tr '"' '')`
5. Deduplicate VTT to plain text:

```bash
python3 -c "
import sys, re
seen = set()
with open('temp_transcript.en.vtt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('WEBVTT') and not line.startswith('Kind:') \
           and not line.startswith('Language:') and '-->' not in line:
            clean = re.sub('<[^>]*>', '', line)
            clean = clean.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
            if clean and clean not in seen:
                print(clean)
                seen.add(clean)
" > "\${VIDEO_TITLE}.txt"
rm -f temp_transcript*.vtt
```

### 2.3 Article Extraction

**Tool priority**: `reader` (Mozilla Readability) > `trafilatura` > curl fallback.

| Tool | Install | Extract command |
|------|---------|----------------|
| reader | `npm i -g @mozilla/readability-cli` | `reader "$URL" > temp_article.txt` |
| trafilatura | `pip3 install trafilatura` | `trafilatura --URL "$URL" --output-format txt --no-comments > temp_article.txt` |
| fallback | none | curl + Python HTMLParser (strips script/style/nav/header/footer/aside) |

Title extraction per tool:
- reader: `head -n 1 temp_article.txt | sed 's/^# //'`
- trafilatura: `trafilatura --URL "$URL" --json | python3 -c "import json,sys; print(json.load(sys.stdin).get('title','Article'))"`
- fallback: `curl -s "$URL" | grep -oP '<title>\K[^<]+' | head -n 1`

Clean filename: `FILENAME=$(echo "$TITLE" | tr '/:?\"<>|' '-------' | cut -c 1-80 | sed 's/ *$//')`.

### 2.4 PDF Extraction

1. Download: `curl -L -o "$PDF_FILENAME" "$URL"`
2. Extract text: `pdftotext "$PDF_FILENAME" "${PDF_FILENAME%.pdf}.txt"` (requires poppler: `brew install poppler`)
3. If pdftotext unavailable, use the Read tool on the downloaded PDF directly.

### 2.5 After Extraction

- Verify file has content (non-empty)
- Show preview: first 10 lines
- Report: tool used, word count, file location
- Clean up temp files

---

## 3. Ship-Learn-Next Action Planning

Core principle: **100 reps beats 100 hours of study. Learning = doing better, not knowing more.**

### 3.1 Extract Core Lessons

From the extracted content, identify:
- **Actionable principles** (what can be practiced)
- **Concrete techniques** (specific methods mentioned)
- **Examples/case studies** (real implementations to replicate)

Skip: pure theory, "nice to know", anything not directly actionable.

### 3.2 Define the Quest

Ask the user:
1. "Based on this content, what do you want to achieve in 4-8 weeks?"
2. "What would success look like? Be specific."
3. "What concrete thing could you build/create/ship?"

Good quest: "Ship 10 cold outreach messages and get 2 responses"
Bad quest: "Learn about sales" (too vague -- push for a noun/artifact)

### 3.3 Design Rep 1 (Smallest Shippable Version)

Must be:
- Completable in 1-7 days
- Produces a real artifact (code, content, deployed thing)
- Small enough to not intimidate, big enough to learn from

### 3.4 Plan Structure

```markdown
# Ship-Learn-Next Quest: [Title]

## Quest Overview
**Goal**: [4-8 week target]
**Source**: [URL/content that inspired this]
**Core Lessons**: [3-5 actionable takeaways]

---

## Rep 1: [Specific Shippable Goal]
**Ship Goal**: [Concrete deliverable]
**Timeline**: [This week / by DATE]
**Success Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

**What You'll Practice** (from the content):
- [Skill/concept 1]
- [Skill/concept 2]

**Action Steps**:
1. [Concrete step]
2. [Concrete step]
3. Ship it (publish/deploy/share)

**Minimal Resources** (only for this rep):
- [Reference if truly needed]

**After Shipping -- Reflection**:
- What actually happened?
- What worked? What didn't?
- What surprised you?
- Rate this rep: _/10
- One thing to try differently next time?

---

## Rep 2: [Next Iteration]
**Builds on**: Rep 1 learnings
**New element**: [One new challenge/skill]
**Ship goal**: [Next deliverable]

## Rep 3-5: Future Path
**Rep 3**: [Brief description]
**Rep 4**: [Brief description]
**Rep 5**: [Brief description]
*(Details evolve based on Reps 1-2)*
```

### 3.5 Save and Present

- Filename: `Ship-Learn-Next Plan - [Brief Quest Title].md`
- Show quest overview and Rep 1 details
- Ask: "When will you ship Rep 1?"
- Ask: "What might stop you? How will you handle it?"

### 3.6 Anti-Patterns

- Do NOT create a study plan (create a SHIP plan)
- Do NOT list all resources to consume
- Do NOT let planning replace doing
- Do NOT accept vague goals -- always push for artifact + deadline

---

## 4. Unblock Action

2-minute facilitation for stuck tasks. Direct, no fluff, Socratic but fast.

### 4.1 Flow (3 Back-and-Forths Max)

**Step 1 -- Clarify output**: Ask ONE question:
> "When this is DONE -- what exists that doesn't exist now? A document? A sent message? A deployed feature? A decision?"

Push for a **noun** (artifact), not a feeling.

**Step 2 -- Scope to today**: If bigger than a day:
> "That's multi-day. What piece can you FINISH today?"

Find a completable sub-output, not "start working on it".

**Step 3 -- Best-option check**:
> "Is this the BEST thing you could work on right now, or is there something higher-leverage you're avoiding?"

**Step 4 -- Next physical action**:
> "What's the very first thing you'd do? Open what app, write what sentence, message whom?"

Must be **verb + object**: "Open Figma and sketch the layout", not "think about it".

**Step 5 -- Output action card**:

```markdown
## Unblocked

**Output:** [concrete deliverable]
**Today's scope:** [day-sized slice]
**Next action:** [verb + object -- literal first step]
**Safe to try?** Yes -- [one-line confirmation]
```

### 4.2 Style Rules
- Skip steps the user already answered
- If the task is already clear and day-sized, jump straight to next action
- No motivational fluff
- Match the user's language

---

## 5. Spaced Repetition and Retention

Track and reinforce learning across quests using expanding review intervals.

### 5.1 Review Schedule

After a rep is shipped, schedule retention checks:

| Review | Interval | Focus |
|--------|----------|-------|
| R1 | 1 day after shipping | Quick recall: what did you learn? |
| R2 | 3 days | Apply the lesson in a different context |
| R3 | 7 days | Teach it: explain to someone or write it up |
| R4 | 14 days | Stress test: use under pressure or combine with another skill |
| R5 | 30 days | Integrate: how has this changed your default behavior? |

### 5.2 Retention Log Format

Maintain a retention log file per user (append-only):

```markdown
# Retention Log

## [Quest Title] -- Rep [N]
**Shipped**: YYYY-MM-DD
**Core lesson**: [one-line summary]
**Reviews**:
- [ ] R1 (YYYY-MM-DD): _
- [ ] R2 (YYYY-MM-DD): _
- [ ] R3 (YYYY-MM-DD): _
- [ ] R4 (YYYY-MM-DD): _
- [ ] R5 (YYYY-MM-DD): _
```

File location: `retention-log.md` in the same directory as the quest plan.

### 5.3 Review Prompt

When a review is due (user says "review reps" or "what's due?"):

1. Read the retention log
2. Find entries with unchecked reviews where the date has passed
3. For each due review, prompt based on review type:
   - **R1 (Recall)**: "What was the core lesson from [quest/rep]? No peeking."
   - **R2 (Apply)**: "How could you apply [lesson] to something you're working on now?"
   - **R3 (Teach)**: "Explain [lesson] as if teaching a junior colleague. Write 3-5 sentences."
   - **R4 (Stress)**: "Where would [lesson] break down? What's the edge case?"
   - **R5 (Integrate)**: "Has [lesson] changed how you work day-to-day? How?"
4. Record the user's response in the log
5. If the user struggles, suggest re-doing a lighter version of the rep

---

## 6. Personal Knowledge Management (Zettelkasten)

Connect learnings into a growing knowledge graph using atomic notes.

### 6.1 When to Create Notes

After completing any rep or review, offer:
> "Want me to create a knowledge note from this lesson?"

### 6.2 Note Format

Each note is one atomic idea. Store in a `knowledge/` directory alongside quest plans.

```markdown
# [YYYYMMDDHHMMSS] [Concise Title]

**Source**: [Quest name, rep number, or URL]
**Tags**: #[domain] #[concept] #[technique]

## Idea
[One paragraph: the atomic insight in your own words]

## Evidence
[What happened when you applied this -- concrete result from a rep]

## Connections
- Links to [[other note titles]] that relate
- Contradicts / extends / supports [other idea]

## Open Questions
- [What you still don't know or want to test]
```

### 6.3 Linking Conventions

- Use `[[Title]]` wiki-link syntax for cross-references
- When creating a new note, scan existing notes for related titles and add bidirectional links
- Tags follow the format `#domain-concept` (kebab-case)

### 6.4 Periodic Review

When user asks "review knowledge" or "connect notes":
1. Read all notes in `knowledge/`
2. Identify clusters (notes with shared tags or links)
3. Surface unlinked notes that share concepts
4. Suggest new connections: "Note A and Note B both discuss [concept] -- should they link?"
5. Highlight orphan notes (no connections) for potential linking or archiving

---

## 7. Error Handling

| Problem | Resolution |
|---------|------------|
| Tool not installed (yt-dlp, reader, trafilatura) | Try next in priority; offer install command |
| Paywall / login required | Inform user: "This URL requires authentication. Cannot extract." |
| No subtitles on YouTube | Offer Whisper transcription with size/duration warning |
| Empty extraction result | Try fallback method; do NOT proceed to planning on empty content |
| Invalid URL | Validate format; try with/without www; check redirects |
| PDF without pdftotext | Use Read tool on the PDF directly |

---

## 8. Output Conventions

### File Naming
- Transcripts/articles: `[Clean Title].txt`
- Quest plans: `Ship-Learn-Next Plan - [Brief Quest Title].md`
- Retention logs: `retention-log.md`
- Knowledge notes: `knowledge/[YYYYMMDDHHMMSS] [Title].md`

### Progress Reporting

After extraction:
```
Content Extracted:
  Type: [youtube/article/pdf]
  Title: [title]
  Saved to: [path]
  Words: [count]
```

After planning:
```
Action Plan Created:
  Quest: [title]
  Saved to: [path]
  Rep 1 due: [date]
```

### Closing Prompts
- Full pipeline: "When will you ship Rep 1?"
- Extract only: "Want me to create a Ship-Learn-Next plan from this?"
- Unblock: Action card (no further prompting needed)
- Review: Update retention log and suggest next review date
