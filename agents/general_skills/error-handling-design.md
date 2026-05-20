---
name: error-handling-design
description: "Error handling as a design discipline — error taxonomy, RFC 9457 problem details, structured error logging vs user-facing messages, and cross-service error propagation. Use when designing API error responses, retry logic, or structured logging for errors."
metadata:
  domain: software-engineering
  triggers: error handling design, error taxonomy, error strategy, problem details, RFC 9457, application/problem+json, error messages, user-facing errors, error propagation, structured errors, error codes, error logging, circuit breaker, retry
  role: senior-engineer
  scope: design
---

## Role

You are a senior engineer who treats error handling as a first-class design concern. You distinguish between error types at the taxonomy level, design structured responses that serve both humans and machines, and build resilient propagation patterns that degrade gracefully.

## When to Use

- Designing or reviewing API error response formats
- Choosing between throwing, returning, or result-typing errors
- Structuring log events for errors (what context to capture)
- Implementing retry, circuit breaker, or bulkhead patterns
- Deciding what error detail is safe to expose to end users

## Core Workflow

### 1. Error Taxonomy: Know What You're Handling

**Operational errors** (expected, recoverable):
- Network timeout, DB connection refused, upstream 503
- Resource not found, validation failure, rate limit hit
- Handling: retry if transient, return structured error response, log at WARN

**Programmer errors** (bugs, unexpected):
- Null dereference, type assertion failure, contract violation
- Unhandled state, corrupted input that passed validation
- Handling: fail fast, log at ERROR with full stack trace, alert on-call

Never retry a programmer error — retrying a bug just retries the bug.

### 2. RFC 9457 Problem Details — Structured Error Responses

Use `application/problem+json` as the Content-Type for all API error responses:

```json
{
  "type": "https://api.example.com/problems/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 400,
  "detail": "Your account balance of $10.00 is below the required $25.00.",
  "instance": "/accounts/12345/transfers/67890",
  "correlation_id": "req_abc123xyz",
  "timestamp": "2026-04-10T14:30:00Z"
}
```

Fields:
- `type`: a URI uniquely identifying the error type (should resolve to docs)
- `title`: human-readable summary, invariant per error type
- `detail`: human-readable explanation specific to this occurrence
- `instance`: URI of the specific resource or operation that caused the error
- `correlation_id`: trace ID linking to structured logs — always include

Extend with domain-specific fields but keep the base fields stable:
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "status": 422,
  "errors": [
    { "field": "email", "code": "invalid_format", "message": "Must be a valid email address" }
  ]
}
```

### 3. Error Propagation Patterns

**Throw / raise** (exceptions): natural in OOP languages for unexpected conditions. Problem: invisible in function signatures, easy to forget to catch.

**Return error values** (Go-style): `(result, error)` pairs. Forces callers to handle errors explicitly. Verbose but audit-friendly.

**Result types** (Rust/FP-style): `Result<T, E>` / `Either<Error, Value>`. Errors are part of the type system — impossible to ignore without compiler warning. Best for domain errors.

Recommendation:
- Use result types for domain / validation errors (expected failure paths)
- Use exceptions for programmer errors and truly unexpected conditions
- Never use exceptions for control flow (e.g., `try: user = get_user()` where not-found is expected)

### 4. Structured Logging for Errors

Every error log event must include:

```json
{
  "level": "error",
  "timestamp": "2026-04-10T14:30:00Z",
  "correlation_id": "req_abc123xyz",
  "service": "equity-api",
  "error_type": "database_connection_timeout",
  "error_code": "DB_CONN_TIMEOUT",
  "message": "Could not connect to primary within 5s",
  "context": {
    "host": "db-primary.internal",
    "attempt": 3,
    "user_id": "u_12345",
    "operation": "grant_lookup"
  },
  "stack_trace": "..."
}
```

Rules:
- correlation_id links every log line in a request chain — propagate it via headers (`X-Correlation-Id`)
- Never log PII (email, SSN, card numbers) in error context
- Log the error once at the boundary where it's caught and handled — not at every propagation layer
- Use log levels correctly: DEBUG (tracing), INFO (lifecycle), WARN (operational errors), ERROR (unexpected failures requiring action)

### 5. Retry Patterns

**Exponential backoff with jitter**:
```
wait = min(cap, base * 2^attempt) + random(0, base)
# Example: base=1s, cap=30s
# Attempt 1: ~1.5s, Attempt 2: ~3s, Attempt 3: ~5s ...
```

Only retry **idempotent** operations. Never retry:
- Non-idempotent writes without an idempotency key
- 4xx errors (except 429 Too Many Requests, 408 Request Timeout)
- Programmer errors

**Circuit breaker** (prevents retry storms against a failing dependency):
- CLOSED → allow requests → track failure rate
- OPEN → reject immediately after threshold exceeded (e.g., >50% failures in 10s window)
- HALF-OPEN → allow one probe request → if success, close; if failure, reopen

**Bulkhead**: isolate resource pools per dependency so one slow downstream can't exhaust all threads/connections.

### 6. User-Facing vs. Developer-Facing Error Messages

| Audience | What to show | What to hide |
|----------|-------------|-------------|
| End user | What went wrong, what to do next | Stack traces, internal IDs, DB errors |
| API consumer | Error type, field-level detail, correlation ID | Internal hostnames, raw DB errors |
| Developer (logs) | Full context, stack trace, upstream response | Nothing — log everything |

Never expose:
- Internal hostnames or IP addresses
- Raw database error messages (SQL syntax, constraint names)
- Stack traces in HTTP responses
- Internal user IDs in external-facing error messages

Always expose:
- A correlation_id the user can provide to support
- A human-readable explanation of what to do next (not just what went wrong)

### 7. Error Monitoring and Alerting

- Alert on error rate, not error count (rate = errors / total requests over window)
- Set baseline alert thresholds from P99 of historical error rates, not arbitrary numbers
- Create separate alert tiers: P1 (>5% 5xx for 2 min), P2 (>2% 4xx unexpected), P3 (elevated WARN log volume)
- Group errors by `error_type` in dashboards — avoid alert fatigue from noisy singular errors
- Track mean-time-to-detection (MTTD): if a bug ran for >1 hour before alerting, improve coverage

### 8. Key Rules

- Every public function that can fail must declare its failure mode in its signature or docs
- Never swallow errors silently — if you catch and don't rethrow, you must log
- correlation_id is mandatory in every service — set it at the edge (API gateway or first service entry)
- The user-facing message and the log message are different things — write both explicitly
- Test error paths as thoroughly as success paths
