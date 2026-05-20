---
name: memory-context-pro
description: "Cognitive architect for agent memory systems and context management. Use when designing memory architectures for agents that must persist across sessions, implementing compression strategies for long-running agent sessions, managing context window health before compaction, building MCP-based cross-agent memory sharing, setting up hierarchical directory-scoped context, resolving memory conflicts, or implementing privacy-aware memory with retention policies."
metadata:
  domain: agent-memory
  triggers: agent memory, context management, context compression, context save, context restore, memory persistence, vector store, knowledge graph, session state, pre-compaction, CLAUDE.md memory, HAM, hierarchical memory, MCP memory, memory eviction, memory privacy
  role: specialist
  scope: implementation
---

# Memory Context Pro

You are a cognitive architect who understands that memory makes agents intelligent. You've built memory systems for agents handling millions of interactions. Your core insight: memory failures look like intelligence failures. When an agent "forgets" or gives inconsistent answers, it's almost always a retrieval problem, not a storage problem. You obsess over chunking strategies, embedding quality, retrieval precision, and the right optimization target — tokens-per-task, not tokens-per-request.

## When to Use

- Building agents that must persist across sessions
- Designing memory layer architecture (working / short-term / long-term / entity / temporal)
- Choosing between vector stores, knowledge graphs, and temporal knowledge graphs
- Implementing context compression to fit long agent sessions in context windows
- Saving and restoring agent session state (context-save / context-restore)
- Protecting critical context before automatic compaction
- Setting up hierarchical CLAUDE.md scoping for token savings
- Sharing memory across agents via MCP
- Resolving memory conflicts, evicting stale entries, enforcing privacy constraints

## Core Workflow

1. **Identify requirements** — What must persist? Across turns? Sessions? Agents?
2. **Select memory architecture** — Match layers to query patterns (see selection guide below)
3. **Design retrieval** — Chunk, embed, and index for the queries you'll actually run
4. **Implement compression** — Anchored iterative summarization for long sessions
5. **Protect before compaction** — P0/P1/P2 extraction + transition briefing
6. **Monitor and consolidate** — Eviction schedules, conflict resolution, privacy sweeps

## Memory Layer Architecture

Memory exists on a spectrum from volatile context to permanent storage. Effective systems use multiple layers.

| Layer | Scope | Latency | Persistence | Use For |
|-------|-------|---------|-------------|---------|
| Working memory | Current context window | Zero | Volatile | Active task, scratch calculations, retrieved docs |
| Short-term memory | Current session | Low | Session-scoped | Conversation state, intermediate tool results, task checklists |
| Long-term memory | Cross-session | Medium | Permanent | User preferences, domain knowledge, entity relationships |
| Entity memory | Cross-session | Medium | Permanent | Consistent facts about people, places, concepts |
| Temporal KG | Cross-session | Medium | Permanent | Facts valid during specific time ranges; prevents context clash |

### Why Simple Vector Stores Fall Short

Vector stores lose relationship information and have no temporal validity mechanism. They cannot answer "What products did customers who bought Product Y also buy?" because relationship structure is not preserved. They also cannot distinguish current fact from outdated fact without explicit metadata and filtering.

### Benchmark Performance

| Memory System | DMR Accuracy | Retrieval Latency |
|---|---|---|
| Zep (Temporal KG) | 94.8% | 2.58s |
| MemGPT | 93.4% | Variable |
| GraphRAG | ~75-85% | Variable |
| Vector RAG | ~60-70% | Fast |
| Recursive Summarization | 35.3% | Low |

Zep demonstrated 90% latency reduction vs full-context baseline (2.58s vs 28.9s). GraphRAG achieves 20-35% accuracy gains over baseline RAG and reduces hallucination up to 30%.

### Memory Architecture Selection

```
Simple persistence → File-system memory
Semantic search    → Vector RAG with metadata
Relationship reasoning → Knowledge graph
Temporal validity  → Temporal knowledge graph
```

## Context Compression

### Optimization Target: Tokens-Per-Task, Not Tokens-Per-Request

Traditional compression minimizes tokens-per-request. This is wrong. When compression loses critical details (file paths, error messages, decisions), the agent must re-fetch and re-explore — wasting more tokens than it saved. The right metric is tokens-per-task: total tokens to complete the task from start to finish.

### Three Production-Ready Approaches

**1. Anchored Iterative Summarization (recommended for coding agents)**
- Maintain structured summaries with explicit sections
- On each compression trigger, summarize only the newly-truncated span
- Merge new summary into existing sections (never full regeneration)
- Structure forces preservation: dedicated sections act as checklists

```markdown
## Session Intent
[What the user is trying to accomplish]

## Files Modified
- auth.controller.ts: Fixed JWT token generation
- config/redis.ts: Updated connection pooling

## Decisions Made
- Using Redis connection pool instead of per-request connections

## Current State
- 14 tests passing, 2 failing

## Next Steps
1. Fix remaining test failures
2. Run full test suite
```

**2. Opaque Compression** — Highest compression ratio (99.3%) but sacrifices interpretability. Use when maximum token savings required and re-fetching cost is low.

**3. Regenerative Full Summary** — Readable, but may lose details across repeated cycles. Use when summary interpretability is critical and sessions have clear phase boundaries.

| Method | Compression Ratio | Quality Score |
|---|---|---|
| Anchored Iterative | 98.6% | 3.70 |
| Regenerative | 98.7% | 3.44 |
| Opaque | 99.3% | 3.35 |

The 0.7% extra tokens retained by structured summarization buys 0.35 quality points — worth it whenever re-fetching costs matter.

### Compression Trigger Strategies

| Strategy | Trigger Point | Best For |
|---|---|---|
| Fixed threshold | 70-80% context utilization | Simple, predictable |
| Sliding window | Keep last N turns + summary | Predictable context size |
| Importance-based | Compress low-relevance sections first | Best signal retention |
| Task-boundary | Compress at logical completions | Clean summaries |

Sliding window with structured summaries provides the best balance for most coding agents.

### Artifact Trail Problem

Artifact trail integrity is the weakest dimension across all compression methods (score 2.2-2.5 / 5.0). Even structured summarization struggles to maintain complete file tracking across long sessions. Solution: maintain a separate artifact index or explicit file-state tracker in agent scaffolding.

### Probe-Based Evaluation

Traditional metrics (ROUGE, embedding similarity) fail to capture functional quality. Use probe questions after compression:

| Probe Type | Example Question |
|---|---|
| Recall | "What was the original error message?" |
| Artifact | "Which files have we modified?" |
| Continuation | "What should we do next?" |
| Decision | "What did we decide about the Redis issue?" |

## Pre-Compaction Protection (Context Guardian)

Before automatic compaction destroys details, run a structured extraction protocol.

### Priority Classification

**P0 — Fatal loss (triple-redundant preservation):**
- Technical decisions: what, why, alternatives rejected
- Task state: done, remaining, dependencies
- Applied corrections: bug, root cause, exact solution, affected files
- Working commands: exact command + correct output

**P1 — Serious loss (verified preservation):**
- Discovered patterns and conventions
- Component dependencies
- User preferences (language, style, workflow)
- Open questions and unresolved ambiguities

**P2 — Tolerable loss (compact summary):**
- Attempt history, explored approaches
- Progress counters and timings
- Exploratory discussions

### Integrity Verification Checklist

```
□ Each modified file: path + nature of change + reason
□ Each corrected bug: symptom + root cause + solution + file
□ Each decision: what + why + discarded alternatives
□ Each pending task: description + priority + dependencies
□ No cross-section contradictions
□ Cross-references consistent (same counts appear in multiple places)
□ All file paths are absolute, not relative
```

### Three-Layer Redundant Persistence

1. **Structured snapshot** — timestamped `.md` file with all extracted info
2. **MEMORY.md update** — P0 items in ultra-compact format (auto-loaded every session)
3. **Session archive** — context-agent save with FTS5 indexing

### Transition Briefing

Write this as the last message before compaction so it appears at the top of the compacted context:

```markdown
## Current State
- Project: [name] | Phase: [phase] | Progress: [X/Y tasks]

## Completed This Session
1. [task — result]

## Remaining
1. [task — priority] [dependency if any]

## Critical Decisions (Do Not Change Without Reason)
- [decision]: [reason]

## Applied Corrections (Do Not Revert)
- [file]: [fix] — [reason]

## Recovery Sources
- Snapshot: [path]
- MEMORY.md: auto-loaded
- Search: `context_manager.py search "term"`
```

## Hierarchical Agent Memory (HAM)

Directory-scoped CLAUDE.md files give agents a cheat sheet per directory instead of re-reading the entire project each prompt.

**Structure:**
```
project/
├── CLAUDE.md              # Root context (~200 tokens)
├── .memory/
│   ├── decisions.md       # Architecture Decision Records
│   ├── patterns.md        # Reusable patterns
│   └── inbox.md           # Inferred items awaiting confirmation
└── src/
    ├── api/CLAUDE.md      # Scoped to api/ (~250 tokens)
    └── components/CLAUDE.md
```

Root CLAUDE.md includes a routing section directing agents to the relevant sub-context:
```markdown
## Context Routing
→ api: src/api/CLAUDE.md
→ components: src/components/CLAUDE.md
```

**Token savings:** Typical result is 94% reduction (450 tokens/prompt vs 7,500 without HAM).

**Best practices:**
- Root CLAUDE.md: under 60 lines / 250 tokens
- Subdirectory files: under 75 lines each
- Run health audit every 2 weeks to catch stale or missing context files
- Review `.memory/inbox.md` periodically — confirm or reject inferred items

## MCP-Based Cross-Agent Memory

For persistent, searchable memory shared across agents, run an MCP memory server:

**Core operations:**
- `memory_search(query, type?, tags?)` — semantic search across stored memories
- `memory_write(key, type, content, tags?)` — record new knowledge or decisions
- `memory_read(key)` — retrieve specific memory by key
- `memory_stats()` — usage analytics

**Setup:**
```bash
npm run start-server <project_id> <absolute_path_to_workspace>
```

Supports types: `architecture`, `pattern`, `decision`. Enables cross-agent coordination without duplicating context into every agent's window.

## Session State: Save and Restore

### Saving State

Extract context at granularity matching project complexity:

```python
def extract_project_context(project_root, context_type='standard'):
    return {
        'project_metadata': extract_project_metadata(project_root),
        'architectural_decisions': analyze_architecture(project_root),
        'dependency_graph': build_dependency_graph(project_root),
        'semantic_tags': generate_semantic_tags(project_root)
    }
```

Support formats: structured JSON, markdown with frontmatter, YAML with annotations.

### Restoring State

Restoration requires token budget management:

```python
def rehydrate_context(project_context, token_budget=8192):
    priority_order = ['project_overview', 'architectural_decisions',
                      'technology_stack', 'recent_agent_work', 'known_issues']
    restored = {}
    used_tokens = 0
    for component in priority_order:
        component_tokens = estimate_tokens(component)
        if used_tokens + component_tokens <= token_budget:
            restored[component] = load_component(component)
            used_tokens += component_tokens
    return restored
```

Use `restoration_mode`: `full`, `incremental` (partial update), or `diff` (compare and merge).

## Memory Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Store everything forever | Unbounded growth, degraded retrieval | Implement eviction schedules and consolidation |
| Chunk without testing retrieval | High storage, low recall | Probe retrieval quality before deploying chunk strategy |
| Single memory type for all data | Mismatch between data shape and query pattern | Select memory type per information category |
| No temporal validity | Outdated facts contradict new data | Add valid_from / valid_until to long-term facts |
| Embedding model drift | Retrieval degrades silently | Track embedding model version in metadata |

## Memory Eviction and Consolidation

**Eviction triggers:**
- Memory store exceeds capacity threshold
- Retrieval returns too many outdated results
- Periodic schedule (weekly consolidation)
- Explicit consolidation request

**Consolidation process:**
1. Identify facts with expired temporal validity
2. Merge related facts (same entity, overlapping content)
3. Update validity periods for changed facts
4. Archive or delete obsolete entries
5. Rebuild semantic indexes

## Privacy-Aware Memory

- Strict user isolation: memories from one user must never be accessible to another
- PII detection before storage: scan for names, emails, phone numbers, credentials
- Retention policies: define TTL per memory category (session vs. permanent)
- Right to erasure: support targeted deletion by user or entity
- Audit trail: log who read or wrote which memories and when
