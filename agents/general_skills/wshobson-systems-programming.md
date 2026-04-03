---
name: wshobson-systems-programming
description: Systems programming patterns for Go concurrency, Rust async, memory safety (C/C++/Rust), and RAII
---

# Systems Programming

Covers Go concurrency (goroutines, channels, errgroup), Rust async patterns (Tokio, channels, streams), and cross-language memory safety (RAII, ownership, smart pointers, bounds checking).

## Key Patterns

- **Go: "Share memory by communicating"** -- prefer channels over mutexes; use `errgroup` for concurrent operations with error propagation
- **Go worker pool** -- buffered job channel + N goroutines + WaitGroup + context cancellation
- **Go graceful shutdown** -- `signal.Notify` + context cancel + `wg.Wait()` with timeout
- **Go race detection** -- always run `go test -race ./...` in CI
- **Rust: async is lazy** -- futures do nothing until polled; use `tokio::spawn` or `JoinSet` for concurrency
- **Rust channels** -- `mpsc` (multi-producer), `broadcast` (multi-consumer), `oneshot` (single response), `watch` (latest value)
- **Rust graceful shutdown** -- `CancellationToken` + `tokio::select!` + `signal::ctrl_c()`
- **RAII everywhere** -- tie resource lifetime to scope (C++ destructors, Rust `Drop`, Go `defer`)
- **Smart pointers** -- `unique_ptr` (sole owner), `shared_ptr` (refcounted), `weak_ptr` (break cycles)
- **Rust ownership** -- move by default, borrow with `&`/`&mut`, lifetimes for references in structs

## Quick Reference

### Go: Worker pool with context

```go
func WorkerPool(ctx context.Context, n int, jobs <-chan Job) <-chan Result {
    results := make(chan Result, len(jobs))
    var wg sync.WaitGroup
    for i := 0; i < n; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                select {
                case <-ctx.Done():
                    return
                default:
                    results <- process(job)
                }
            }
        }()
    }
    go func() { wg.Wait(); close(results) }()
    return results
}
```

### Rust: Concurrent tasks with JoinSet

```rust
async fn fetch_all(urls: Vec<String>) -> Vec<String> {
    let mut set = JoinSet::new();
    for url in urls {
        set.spawn(async move { fetch(&url).await });
    }
    let mut results = Vec::new();
    while let Some(res) = set.join_next().await {
        if let Ok(Ok(data)) = res { results.push(data); }
    }
    results
}
```

### Memory bug prevention cheat sheet

| Bug              | C prevention         | C++ prevention     | Rust prevention       |
|------------------|---------------------|--------------------|----------------------|
| Use-after-free   | goto cleanup        | unique_ptr / RAII  | Ownership + borrow   |
| Double-free      | NULL after free     | Smart pointers     | Compiler enforced     |
| Memory leak      | goto cleanup        | RAII destructors   | Drop trait            |
| Buffer overflow  | Manual bounds check | .at() / span       | Default bounds check  |
| Data race        | pthread_mutex       | shared_mutex       | Send + Sync traits    |

### Debugging tools

```bash
go test -race ./...                        # Go race detector
clang++ -fsanitize=address -g source.cpp   # AddressSanitizer
valgrind --leak-check=full ./program       # Memory leak check
cargo +nightly miri run                    # Rust UB detector
```

## When to Use

- Building concurrent Go services (worker pools, pipelines, graceful shutdown)
- Writing async Rust network services with Tokio
- Choosing between channels, mutexes, and atomics for shared state
- Implementing safe resource management in C/C++/Rust
- Debugging race conditions or memory safety issues
