---
name: wshobson-multi-platform-apps
description: Multi-platform app development patterns for backend APIs, Flutter, React/Next.js, iOS, and React Native
---

# Multi-Platform Apps

Reference for building cross-platform applications spanning backend architecture (REST/GraphQL/gRPC), Flutter, React/Next.js frontend, native iOS (Swift/SwiftUI), and React Native. Covers API design, state management, resilience, and platform-specific patterns.

## Key Patterns

- **API-first design** -- define contracts (OpenAPI / GraphQL schema) before implementation; generate client SDKs
- **Backend-for-Frontend (BFF)** -- create client-specific backends to aggregate and shape data per platform
- **Resilience built-in** -- circuit breakers, exponential backoff with jitter, timeout propagation, bulkhead isolation
- **Observability as first-class** -- structured logging with correlation IDs, RED metrics (Rate/Errors/Duration), distributed tracing via OpenTelemetry
- **Event-driven decoupling** -- prefer async messaging (Kafka, SQS) between services; use sagas for distributed transactions
- **Flutter: Riverpod + Clean Architecture** -- feature-driven modules, const constructors, typed state management
- **React: Server Components + Checkout Sessions** -- prefer RSC for data fetching, Zustand/Jotai for client state, Suspense boundaries
- **iOS: SwiftUI-first with UIKit bridge** -- @Observable macro, async/await networking, SwiftData for persistence
- **React Native: New Architecture** -- Fabric renderer, TurboModules, Hermes engine; Expo for managed builds
- **Offline-first data sync** -- local DB (SQLite/Hive/SwiftData) + conflict resolution + background sync

## Quick Reference

### Backend API checklist

```
[ ] OpenAPI/GraphQL schema defined and versioned
[ ] Authentication (OAuth 2.0 / JWT) with refresh tokens
[ ] Rate limiting (token bucket) on all endpoints
[ ] Input validation at boundary (schema-based)
[ ] Pagination (cursor-based preferred)
[ ] CORS configured for known origins
[ ] Webhook delivery with HMAC signature + retry + idempotency key
[ ] Health check endpoints (liveness + readiness)
[ ] Structured JSON logging with request correlation ID
[ ] Graceful shutdown handling
```

### State management decision matrix

| Complexity | Flutter      | React           | iOS              | React Native     |
|------------|-------------|-----------------|------------------|------------------|
| Simple     | Provider    | useState/Context| @State/@Binding  | useState/Context |
| Medium     | Riverpod    | Zustand/Jotai   | @Observable      | Zustand          |
| Complex    | Bloc        | Redux Toolkit   | TCA              | Redux Toolkit    |

### Cross-platform architecture layers

```
Presentation  ->  Domain (shared logic)  ->  Data (platform repos)
     |                    |                        |
  UI/Widgets       Use Cases / BLoC          API + Local DB
```

## When to Use

- Designing a backend API that serves multiple client platforms
- Choosing architecture and state management for a Flutter, React, iOS, or React Native app
- Implementing resilience patterns (circuit breaker, retry, timeout) in distributed systems
- Building offline-first mobile apps with sync
- Setting up cross-platform CI/CD and app store deployment
