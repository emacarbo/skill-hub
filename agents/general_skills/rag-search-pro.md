---
name: rag-search-pro
description: "End-to-end RAG and vector search skill covering embeddings, chunking, vector DBs, hybrid search, retrieval pipelines, evaluation, GraphRAG, multi-modal RAG, and agentic RAG."
version: "1.0.0"
risk: low
source: consolidated
date_added: "2026-03-29"
upstream_skills:
  - antigravity-embedding-strategies
  - antigravity-hybrid-search-implementation
  - antigravity-similarity-search-patterns
  - alireza-rag-architect
  - wshobson-llm-application-dev
---


<!-- SUMMARY
Scope: RAG pipelines, embeddings, vector DBs, hybrid search, GraphRAG, evaluation
Capabilities: Embedding models, chunking strategies, HNSW tuning, RAGAS eval, agentic RAG
Not for: Agent architecture (use agent-engineering-pro), general AI (use standalone skills)
END SUMMARY -->

# RAG Search Pro

Comprehensive skill for designing, building, and optimizing Retrieval-Augmented Generation systems and vector search infrastructure.

## Use this skill when

- Choosing or comparing embedding models
- Designing chunking strategies for documents or code
- Standing up or tuning a vector database (Pinecone, Qdrant, pgvector, Weaviate, Chroma)
- Implementing hybrid search (dense + sparse fusion)
- Building full RAG pipelines with LangGraph / LangChain
- Applying query transformation (HyDE, multi-query, step-back)
- Evaluating retrieval quality (RAGAS, LLM-as-judge, IR metrics)
- Implementing GraphRAG with knowledge graphs
- Adding multi-modal retrieval (images, audio, video)
- Designing agentic RAG with iterative retrieval and self-reflection

## Do not use this skill when

- The task involves only prompt engineering without retrieval
- You need general LLM fine-tuning (not retrieval-specific)
- The problem is purely a keyword search without semantic needs

---

## 1. Embedding Models

### Model Selection Matrix

| Model | Dims | Max Tokens | Best For |
|-------|------|------------|----------|
| **voyage-3-large** | 1024 | 32000 | Claude apps (Anthropic recommended) |
| **voyage-code-3** | 1024 | 16000 | Code search |
| **text-embedding-3-large** | 3072 | 8191 | High accuracy (OpenAI) |
| **text-embedding-3-small** | 1536 | 8191 | Cost-effective (OpenAI) |
| **bge-large-en-v1.5** | 1024 | 512 | Open source, local |
| **all-MiniLM-L6-v2** | 384 | 256 | Fast, lightweight |
| **multilingual-e5-large** | 1024 | 512 | Multi-language |

### Dimension Guidance

- **128-384**: Fast retrieval, low memory. Simple domains, prototyping.
- **512-768**: Balanced. Good for most production apps.
- **1024-1536**: High quality. Complex domains, production RAG.
- **3072**: Maximum quality. Use Matryoshka dimension reduction when cost matters.

### Embedding Pipeline

```
Document -> Chunking -> Preprocessing -> Embedding Model -> Vector
               |              |                |
        [overlap, size]  [clean, norm]   [API or local]
```

### Key Practices

- **Match model to use case**: code vs prose vs multilingual.
- **Normalize embeddings** before cosine similarity.
- **Batch requests** (batch_size=100) for throughput.
- **Cache embeddings** to avoid recomputation.
- **Never mix models** in the same vector space.
- **Respect token limits** -- truncation silently loses information.

---

## 2. Chunking Strategies

### Strategy Selection

| Strategy | Preserves Semantics | Consistent Size | Best For |
|----------|-------------------|-----------------|----------|
| **Token-based** | Low | High | Uniform documents |
| **Sentence-based** | Medium | Medium | Narrative text, articles |
| **Recursive character** | Medium | Medium | General purpose (LangChain default) |
| **Semantic (embedding sim)** | High | Low | Long-form, research papers |
| **Markdown/header-aware** | High | Medium | Technical docs, wikis |
| **Code (tree-sitter)** | High | Low | Source code |

### Recommended Defaults

- **chunk_size**: 512-1000 tokens.
- **chunk_overlap**: 10-20% of chunk size (50-200 tokens).
- **Separators** (recursive): `["\n\n", "\n", ". ", " ", ""]`.

### Parent-Child Pattern

Use small chunks (400 tokens) for precise retrieval but return the parent chunk (2000 tokens) for full context. Implement with LangChain `ParentDocumentRetriever` or equivalent two-store approach.

---

## 3. Vector Databases

### Selection Guide

| Database | Type | Hybrid Search | Best For |
|----------|------|--------------|----------|
| **Pinecone** | Managed SaaS | Yes (sparse+dense) | Production, auto-scaling |
| **Qdrant** | Self-hosted / Cloud | Yes (named vectors) | High perf, Rust-based |
| **pgvector** | PostgreSQL extension | Yes (+ tsvector) | Existing Postgres infra, ACID |
| **Weaviate** | Self-hosted / Cloud | Yes (BM25+vector) | GraphQL API, multi-modal |
| **Chroma** | Embedded (SQLite) | No | Prototyping, local dev |

### Index Type Selection

```
< 10K vectors   ->  Flat (exact search, 100% recall)
10K - 1M        ->  HNSW
1M - 100M       ->  HNSW + Quantization (INT8 or PQ)
> 100M          ->  IVF + PQ  or  DiskANN
```

### HNSW Parameter Tuning

| Parameter | Default | Tune Up When | Tune Down When |
|-----------|---------|-------------|----------------|
| **M** | 16 | Need higher recall | Memory constrained |
| **efConstruction** | 100 | Build once, query many | Frequent rebuilds |
| **efSearch** | 50 | Target recall > 95% | Latency < 5ms required |

### Quantization Options

| Method | Bytes/Vector | Recall Impact | Use When |
|--------|-------------|---------------|----------|
| FP32 (none) | 4 x dims | Baseline | < 1M vectors |
| INT8 scalar | 1 x dims | ~1-2% loss | 1M-50M vectors |
| Product (PQ) | 32-64 total | ~5-10% loss | > 50M vectors, memory tight |
| Binary | dims/8 | ~10-15% loss | Billion-scale pre-filter |

---

## 4. Hybrid Search

### Architecture

```
Query -> +-- Dense search (embeddings)  -- Candidates --+
         |                                               |
         +-- Sparse search (BM25/tsvector) -- Candidates-+-> Fusion -> Rerank -> Results
```

### Fusion Methods

| Method | When to Use |
|--------|------------|
| **Reciprocal Rank Fusion (RRF)** | Default. No tuning needed. `score = sum(1/(k + rank))`, k=60. |
| **Linear combination** | When you have labeled data to tune alpha (vector_weight). |
| **Cross-encoder rerank** | Highest quality. Add as a second stage over RRF or linear. |

### RRF Implementation (Concise)

```python
from collections import defaultdict
from typing import List, Tuple

def rrf(
    result_lists: List[List[Tuple[str, float]]],
    k: int = 60,
    weights: List[float] | None = None,
) -> List[Tuple[str, float]]:
    weights = weights or [1.0] * len(result_lists)
    scores: dict[str, float] = defaultdict(float)
    for results, w in zip(result_lists, weights):
        for rank, (doc_id, _) in enumerate(results):
            scores[doc_id] += w / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Reranking

- **Cross-encoder**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast) or `bge-reranker-v2-m3` (multilingual).
- **Cohere Rerank API**: `rerank-english-v3.0`. Managed, low-latency.
- **LLM-based rerank**: Use Claude for complex domain-specific scoring when latency allows.
- **MMR (Maximal Marginal Relevance)**: Use when diversity matters. `lambda_mult=0.5` balances relevance and diversity.

---

## 5. RAG Pipeline

### Minimal LangGraph RAG

```python
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict

class RAGState(TypedDict):
    question: str
    context: list[Document]
    answer: str

llm = ChatAnthropic(model="claude-sonnet-4-6")
embeddings = VoyageAIEmbeddings(model="voyage-3-large")
vectorstore = PineconeVectorStore(index_name="docs", embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

rag_prompt = ChatPromptTemplate.from_template(
    """Answer based on the context. Cite sources with [1], [2]. If unsure, say so.

    Context:
    {context}

    Question: {question}"""
)

async def retrieve(state: RAGState) -> RAGState:
    docs = await retriever.ainvoke(state["question"])
    return {"context": docs}

async def generate(state: RAGState) -> RAGState:
    ctx = "\n\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(state["context"]))
    response = await llm.ainvoke(rag_prompt.format_messages(context=ctx, question=state["question"]))
    return {"answer": response.content}

builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
rag_chain = builder.compile()
```

### Query Transformation Techniques

| Technique | Approach | When to Use |
|-----------|----------|------------|
| **HyDE** | LLM generates hypothetical answer; embed that instead of query | Query/document style mismatch |
| **Multi-query** | LLM generates 3-5 query variations; merge retrieved results | Ambiguous or broad queries |
| **Step-back** | Generate a broader version of a specific query | Specific questions needing general context |
| **Query decomposition** | Break complex query into sub-questions | Multi-hop reasoning |

### Context Window Optimization

- **Relevance ordering**: Most relevant chunks first.
- **Diversity**: Deduplicate near-identical chunks.
- **Token budget**: Fit within model context; truncate lowest-relevance chunks.
- **Compression**: Use `LLMChainExtractor` to extract only relevant sentences from each chunk.
- **Hierarchical**: Include summary chunks before detailed ones.

---

## 6. Evaluation

### Retrieval Metrics (IR)

| Metric | Measures | Target |
|--------|---------|--------|
| **Precision@K** | Relevant in top K / K | > 0.7 |
| **Recall@K** | Retrieved relevant / total relevant | > 0.8 |
| **MRR** | 1/rank of first relevant result | > 0.8 |
| **NDCG@K** | Position-weighted relevance | > 0.8 |

### RAG Quality Metrics (RAGAS Framework)

| Metric | Measures | Target |
|--------|---------|--------|
| **Faithfulness** | Answer grounded in context | > 0.9 |
| **Answer relevance** | Answer addresses the question | > 0.85 |
| **Context relevance** | Retrieved context relevant to query | > 0.8 |
| **Correctness** | Factual accuracy vs ground truth | > 0.85 |

### LLM-as-Judge

Use Claude (Sonnet or Opus) to evaluate along three axes:
- **Accuracy** (1-10): factual correctness.
- **Helpfulness** (1-10): addresses the question.
- **Groundedness** (0-1): every claim supported by retrieved context.

Use pairwise comparison when A/B testing two pipeline configurations.

### Operational Monitoring

Track continuously in production:
- Query latency (p50, p95, p99).
- Retrieval recall (sampled).
- Generation faithfulness (sampled LLM-as-judge).
- Embedding + vector DB costs.

---

## 7. GraphRAG

Knowledge graph-augmented retrieval for complex, relational questions.

### When to Use

- Multi-hop reasoning ("What companies did the CEO's co-founders start?")
- Entity-centric queries over structured relationships
- Corpus with dense cross-references (legal, biomedical, organizational)

### Architecture

```
Documents -> Entity extraction (LLM) -> Knowledge Graph (Neo4j / NetworkX)
                                              |
Query -> Entity linking -> Graph traversal -> Subgraph context
                                              |
                              Merged with vector-retrieved chunks -> LLM -> Answer
```

### Implementation Pattern

1. **Extract entities and relations** from chunks using Claude with structured output (Pydantic schema: `subject, predicate, object, source_chunk_id`).
2. **Store in graph DB** (Neo4j with `MERGE` for deduplication) or in-memory (NetworkX for prototyping).
3. **At query time**:
   - Extract query entities.
   - Traverse graph (1-2 hops) to collect related subgraph.
   - Combine graph context with top-K vector-retrieved chunks.
   - Feed merged context to LLM for generation.

### Community Detection (Microsoft GraphRAG pattern)

For corpus-level summarization:
1. Build entity graph from entire corpus.
2. Run Leiden community detection to identify topic clusters.
3. Generate community summaries at multiple hierarchy levels.
4. At query time, route to relevant communities before retrieving individual chunks.

---

## 8. Multi-Modal RAG

Extend retrieval beyond text to images, audio, and video.

### Image RAG

| Approach | How | Pros | Cons |
|----------|-----|------|------|
| **Caption + embed** | Generate captions with vision LLM, embed captions | Simple, works with text pipeline | Loses visual detail |
| **CLIP embeddings** | Embed images and text into shared space | Native cross-modal search | Coarser semantics |
| **Multi-vector** | Store both caption embedding and image embedding per doc | Best recall | Double storage cost |

### Implementation Pattern (Caption-based)

1. **Ingest**: For each image/figure, call Claude vision to generate a detailed caption.
2. **Chunk**: Treat caption as a text chunk; attach image URL/path as metadata.
3. **Retrieve**: Standard vector search over captions.
4. **Generate**: Include both caption and image (base64 or URL) in the LLM prompt for grounded answers.

### Audio / Video RAG

1. **Transcribe**: Whisper or cloud STT to get timestamped text.
2. **Chunk by segments**: Use silence detection or topic shifts, not fixed windows.
3. **Embed and index** text chunks; attach timestamps as metadata.
4. **At generation**: Provide transcript context plus timestamp links for source attribution.

---

## 9. Agentic RAG

Autonomous retrieval agents that decide when, what, and how to retrieve.

### When to Use

- User questions require dynamic retrieval decisions (some need search, some do not).
- Multi-step research tasks where initial retrieval informs follow-up queries.
- Quality-critical applications that benefit from self-verification.

### Core Pattern: Retrieve-Reflect-Retry

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class AgenticRAGState(TypedDict):
    question: str
    context: list
    answer: str
    is_sufficient: bool
    attempts: int

async def retrieve(state: AgenticRAGState) -> AgenticRAGState:
    """Retrieve relevant documents."""
    docs = await retriever.ainvoke(state["question"])
    return {"context": docs, "attempts": state.get("attempts", 0) + 1}

async def grade_context(state: AgenticRAGState) -> AgenticRAGState:
    """LLM judges whether retrieved context is sufficient."""
    prompt = f"""Given the question and context, is the context sufficient to answer?
    Question: {state['question']}
    Context: {state['context'][:3]}
    Respond with only YES or NO."""
    response = await llm.ainvoke(prompt)
    return {"is_sufficient": "YES" in response.content.upper()}

async def refine_query(state: AgenticRAGState) -> AgenticRAGState:
    """Rewrite query for better retrieval."""
    prompt = f"Rewrite this question for better search results: {state['question']}"
    response = await llm.ainvoke(prompt)
    return {"question": response.content}

async def generate(state: AgenticRAGState) -> AgenticRAGState:
    ctx = "\n".join(d.page_content for d in state["context"])
    response = await llm.ainvoke(f"Answer based on context:\n{ctx}\n\nQ: {state['question']}")
    return {"answer": response.content}

def should_retry(state: AgenticRAGState) -> Literal["refine", "generate"]:
    if not state["is_sufficient"] and state["attempts"] < 3:
        return "refine"
    return "generate"

builder = StateGraph(AgenticRAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("grade", grade_context)
builder.add_node("refine", refine_query)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "grade")
builder.add_conditional_edges("grade", should_retry, {"refine": "refine", "generate": "generate"})
builder.add_edge("refine", "retrieve")
builder.add_edge("generate", END)
agentic_rag = builder.compile()
```

### Advanced Agentic Patterns

| Pattern | Description |
|---------|------------|
| **Tool-selection agent** | ReAct agent with retriever as one of several tools; decides when to search vs answer from memory. |
| **Multi-source routing** | Agent routes queries to different retrievers (web, internal docs, SQL DB) based on intent classification. |
| **Iterative decomposition** | Agent breaks complex question into sub-questions, retrieves for each, synthesizes. |
| **Self-RAG** | After generation, agent retrieves again to fact-check its own answer; revises if contradictions found. |
| **Adaptive retrieval** | Agent adjusts k, filters, and reranking strategy based on query complexity (simple=k:2, complex=k:10+rerank). |

---

## 10. Production Checklist

### Before Deploying

- [ ] Chunking strategy validated on representative documents
- [ ] Embedding model benchmarked on domain-specific queries
- [ ] Vector index parameters tuned (HNSW M, ef, quantization)
- [ ] Hybrid search weights calibrated on evaluation set
- [ ] Reranker added if precision is critical
- [ ] Evaluation suite (RAGAS + IR metrics) running on test set
- [ ] Caching layer for embeddings and frequent queries
- [ ] Fallback mechanism if retrieval fails (graceful degradation)
- [ ] Guardrails: PII filtering, injection prevention, hallucination detection
- [ ] Monitoring: latency, recall, faithfulness, cost dashboards
- [ ] Document refresh pipeline (incremental re-embedding of changed docs)

### Cost Optimization

- **Batch embed** changed documents only; skip unchanged.
- **Use Matryoshka dimension reduction** (e.g., 3072 -> 512) when marginal recall loss is acceptable.
- **Quantize vectors** (INT8) to cut storage 4x.
- **Semantic caching**: cache results for semantically similar queries (cosine > 0.95).
- **Route simple queries** to cheaper/faster retrieval paths.

---

## References

- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) -- embedding model benchmarks
- [RAGAS](https://docs.ragas.io/) -- RAG evaluation framework
- [LangGraph docs](https://langchain-ai.github.io/langgraph/) -- agent orchestration
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) -- knowledge graph RAG
- [RRF Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) -- reciprocal rank fusion
- [Pinecone](https://docs.pinecone.io/) | [Qdrant](https://qdrant.tech/documentation/) | [pgvector](https://github.com/pgvector/pgvector) | [Weaviate](https://weaviate.io/developers/weaviate)