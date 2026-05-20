---
name: translate
description: >
  Use when the user asks to translate text between languages — triggers on the word "translate"
  or phrases like "translate to X", "render in Italian", "in Spanish please", "how do you say X in Y".
  Offloads translation to a local Ollama model (gemma4:26b) instead of spending Claude tokens on it.
  Do NOT use for code identifier renaming, code comments that are part of a refactor, or tasks
  where translation is incidental to a larger code change Claude is performing.
user-invocable: true
allowed_tools: ["Bash", "Read"]
---

# Translate — offload to local LLM

## Why this skill exists

Translation is bulk text work with well-understood quality floors. Running it through Claude
burns API tokens for something a local model handles fine. This skill routes translation
requests to Ollama and returns the result.

## When to activate

Activate when the user's request is primarily translation. Examples:
- "Translate this paragraph to Italian"
- "How do you say 'deadline' in German?"
- "Render the README in Spanish"
- "Translate: <text>"

Do NOT activate when:
- The user is refactoring code and translation is a side task
- The text is ambiguous and needs Claude's judgment (e.g., choosing tone, localizing idioms for a product)
- The user explicitly wants Claude to do it

## Execution

### Step 1 — identify the source text and target language

The user will provide both. If the target language is missing, ASK before running.
Never guess the target language.

### Step 2 — pick the model

**Default**: `gemma4:e4b` — fast, ~9.6 GB, handles all major European languages (ES/DE/FR/IT/PT)
well for plain text.

**Step up to `gemma4:26b` when ANY of these apply**:
- Text is ≤20 words AND looks like a proverb, idiom, aphorism, or saying
- Source is literary/poetic
- Target is a low-resource language (Welsh, Swahili, Kazakh, etc.)
- The user explicitly asks for the big model
- User complains that a prior e4b translation lost nuance

Rationale: e4b misses idiomatic English equivalents for proverbs (e.g., it translates
"A caval donato non si guarda in bocca" literally as "A gift is not judged by its appearance"
instead of "Don't look a gift horse in the mouth"). 26b reliably catches these.

**Prompt biasing** (use for both models on idiomatic text):
Include in the prompt: *"For proverbs and idioms, prefer the natural English equivalent."*
This doesn't rescue e4b when it lacks the knowledge, but helps the 26b produce the idiomatic form.

**Thinking-mode quirk**: `/no_think` works on e4b but is ignored by 26b — the 26b will
always stream its reasoning before the final answer. This is cosmetic; the final line is
still the correct translation. When piping 26b output, grep for the last non-empty line.

### Step 3 — call Ollama via Bash

**Always append `/no_think`** to suppress reasoning-mode output. Gemma 4 dumps chain-of-thought
by default, which wastes time and pollutes stdout.

For short plain text (fits on the command line):
```bash
ollama run gemma4:e4b "Translate the following to <LANG>. Output ONLY the translation, no commentary. /no_think

<TEXT>"
```

For idioms/proverbs/aphorisms (use 26b):
```bash
ollama run gemma4:26b "Translate the following to <LANG>. For proverbs and idioms, prefer the natural English equivalent. Output ONLY the translation.

<TEXT>" | tail -n 1
```
(The `tail -n 1` strips the unavoidable reasoning dump from 26b; the last line is the answer.)

For longer text (paragraphs, files), pipe it in:
```bash
cat /path/to/file.txt | ollama run gemma4:e4b "Translate to <LANG>. Output only the translation. /no_think"
```

For very long documents, read the file with the Read tool first, then pass chunks via stdin.
Do NOT read a huge file into context just to translate it — that defeats the purpose.

### Step 4 — present the result

Return the translation directly. Do not summarize, do not add commentary unless the user asked
for something else alongside (e.g., "translate and explain the grammar").

If the local model output looks clearly wrong (empty, error, obvious garbage), fall back to
doing the translation yourself and note the fallback to the user.

## Quality notes

- `gemma4:e4b` handles Romance languages (IT/ES/FR/PT) and German at near-native quality.
- For low-resource languages (e.g., Welsh, Swahili, Kazakh), step up to `gemma4:26b`, or
  recommend installing `aya-expanse:8b` (specialist-trained on 23 languages).
- If the user is translating technical/legal/medical text with strict terminology, warn them
  that a local general-purpose model may miss domain nuances.

## Anti-patterns

- Don't load the translation into your own context and re-output it verbatim — that wastes the
  offload. Run Ollama, return its output.
- Don't chain multiple Ollama calls when one batched call suffices.
- Don't silently swap to Claude translation without telling the user.
