---
name: cache-invalidation-patterns
description: "Cache invalidation strategies, write policies, stampede prevention, TTL design, and event-driven invalidation. Use when adding caching to any layer (API, DB query, computed results) to avoid stale-data bugs and performance regressions."
metadata:
  domain: systems-design
  triggers: cache invalidation, stale data, cache strategy, write-through, write-behind, write-around, cache stampede, thundering herd, TTL strategy, cache eviction, Redis cache, L1 L2 cache
  role: systems-engineer
  scope: implementation
---

## Role

You are a systems engineer specializing in distributed caching. You design cache layers that are fast, consistent, and operationally observable — and you prevent the classic failure modes (stampedes, stale reads, unbounded memory growth) before they hit production.

## When to Use

- Adding a cache to reduce DB load or API latency
- Debugging stale-data bugs after a cache was introduced
- Designing invalidation logic for a new write path
- Choosing between TTL-based and event-based invalidation
- Reviewing a caching implementation for correctness under concurrency

## Core Workflow

### 1. Choose a Write Policy First

| Strategy | How it works | Use when |
|----------|-------------|----------|
| **Write-through** | Write to cache + DB synchronously | Read-heavy, strong consistency required |
| **Write-behind** | Write to cache; async flush to DB | Write-heavy, eventual consistency acceptable |
| **Write-around** | Write directly to DB, skip cache | Infrequently-read write-heavy data |
| **Read-through** | Cache fetches from DB on miss | Application doesn't manage cache population |

Write-through is the safe default. Write-behind trades consistency for throughput — use it only when you can tolerate data loss on cache node failure.

### 2. TTL Management and Expiration Policies

- Set TTLs based on data change frequency, not instinct:
  - User session data: 30–60 minutes (sliding window)
  - Catalog / reference data: 5–30 minutes
  - Real-time metrics: 5–30 seconds
  - Static content: hours to days with versioned keys
- Use **jitter** on TTLs to prevent coordinated expiration:
  ```
  ttl = base_ttl + random(0, base_ttl * 0.1)
  ```
- For sliding expiration: reset TTL on every read (`EXPIRE key ttl` after `GET`)
- Avoid TTL = 0 (no expiry) for computed values — they become stale permanently

### 3. Cache Stampede Prevention

A stampede occurs when many requests simultaneously miss a cold or just-expired key and all hit the DB at once.

**Locking (mutex)**:
```
value = cache.get(key)
if value is None:
    lock = acquire_lock(key, timeout=5s)
    if lock:
        value = db.fetch(key)
        cache.set(key, value, ttl)
        release_lock(key)
    else:
        # Another worker is populating — wait and retry
        sleep(50ms)
        value = cache.get(key)
```

**Probabilistic early expiration (XFetch)**:
```
# Recompute before TTL expires, with probability proportional to cost
remaining_ttl = cache.ttl(key)
if remaining_ttl < compute_time * beta * log(random()):
    # probabilistically refresh now
    value = db.fetch(key)
    cache.set(key, value, ttl)
```

**Stale-while-revalidate**: return the stale value immediately, refresh in the background. Best for non-critical display data.

### 4. Cache Invalidation Patterns

**Time-based (TTL)**: simple, no coordination needed. Accepts bounded staleness.

**Event-based (push invalidation)**: listen for write events and delete/update affected keys immediately.
```
# On write event (e.g., user profile updated):
cache.delete(f"user:{user_id}:profile")
cache.delete(f"user:{user_id}:permissions")
```

**Version-based (cache busting)**: embed a version token in the key. Old keys expire naturally; no explicit invalidation needed.
```
key = f"product:{product_id}:v{product.version}"
```

**Tag-based invalidation**: associate multiple keys with a tag, then invalidate all by tag.
- Supported by Varnish, Fastly, and some Redis patterns (maintain a tag→key set)

Choose: event-based for low latency requirements, TTL for simplicity, version-based for immutable content.

### 5. Multi-Layer Caching (L1 + L2)

```
Request → L1 (in-process, local memory) → L2 (Redis, distributed) → DB
```

- L1 is fastest (nanoseconds) but local to one instance — stale data is per-instance
- L2 is shared across instances — consistent but adds network hop
- Keep L1 TTLs much shorter than L2 (L1: 1–5s, L2: 60s+) to bound inconsistency
- On a write: invalidate L2 first, then let L1 expire naturally (or invalidate via pub/sub broadcast)
- Never cache mutable user-specific data in L1 across requests in stateless services

### 6. Cache Key Design and Namespacing

```
namespace:version:entity_type:id[:qualifier]
# Examples:
api:v1:user:12345
api:v1:user:12345:permissions
api:v1:product:sku:ABC123:price:USD
```

Rules:
- Always include a namespace to prevent key collisions across services sharing a Redis cluster
- Include a version prefix to enable instant full-cache invalidation (bump the version)
- Keep keys short — Redis stores keys as strings; long keys waste memory
- Never embed user-supplied strings in keys without sanitization (colon injection)

### 7. Monitoring Cache Health

Key metrics to track:
- **Hit rate**: (hits / (hits + misses)) — target >80% for steady-state caches
- **Eviction rate**: high evictions = cache too small for working set; increase memory or reduce TTL
- **Miss latency vs hit latency**: if miss latency spikes, the DB is under stampede pressure
- **Key count by pattern**: detect unbounded key growth (missing TTLs, key explosion)

Alerts:
- Hit rate drops >10% in 5 minutes → probable cache invalidation bug or deployment
- Eviction rate >5% of ops → memory pressure, risk of stampede
- P99 miss latency >2× normal → downstream DB under stress

### 8. Key Rules

- Every cached value must have a TTL — no exceptions for mutable data
- Always test cache invalidation, not just cache population
- Never cache authorization decisions for longer than the session TTL
- Document the acceptable staleness window for every cached data type
- When in doubt between TTL and event-based: start with TTL, add events when staleness is measured as a real problem
