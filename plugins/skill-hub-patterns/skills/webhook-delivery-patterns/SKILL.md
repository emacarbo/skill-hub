---
name: webhook-delivery-patterns
description: "Building reliable outbound webhook delivery systems — HMAC signing, retry with exponential backoff, idempotency, delivery guarantees, and consumer management. Use when building a system that sends webhook notifications to external consumers."
metadata:
  domain: systems-design
  triggers: webhook delivery, outbound webhooks, webhook system, webhook signing, HMAC signature, webhook retry, delivery guarantee, at-least-once delivery, webhook consumer, webhook subscription, CloudEvents, dead letter queue
  role: systems-engineer
  scope: implementation
---

## Role

You are a systems engineer specializing in reliable event delivery infrastructure. You design webhook systems that are secure, observable, and resilient — with delivery guarantees, proper signing, and operational controls for consumer management.

## When to Use

- Building a new outbound webhook system from scratch
- Adding HMAC signature verification to an existing webhook integration
- Implementing retry logic and dead-letter queues for failed deliveries
- Designing idempotent webhook consumers on the receiving side
- Auditing an existing webhook system for reliability or security gaps

## Core Workflow

### 1. Webhook Security — HMAC-SHA256 Signing

Every outbound webhook must be signed. The receiver must verify the signature before processing.

**Signing (sender side)**:
```python
import hmac, hashlib, time

def sign_webhook(payload: bytes, secret: str, timestamp: int) -> str:
    # Include timestamp to prevent replay attacks
    signed_content = f"{timestamp}.".encode() + payload
    signature = hmac.new(secret.encode(), signed_content, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"

# Set header:
# X-Webhook-Signature: t=1712750000,v1=abc123...
```

**Verification (receiver side)**:
```python
def verify_webhook(payload: bytes, header: str, secret: str, tolerance_seconds=300) -> bool:
    parts = dict(p.split('=', 1) for p in header.split(','))
    timestamp = int(parts['t'])
    # Reject if timestamp is too old (replay protection)
    if abs(time.time() - timestamp) > tolerance_seconds:
        return False
    expected = sign_webhook(payload, secret, timestamp)
    return hmac.compare_digest(header, expected)
```

Use constant-time comparison (`hmac.compare_digest`) to prevent timing attacks. Never use `==`.

### 2. Delivery Reliability — Retry with Exponential Backoff

Treat every delivery as potentially failing. Implement at-least-once delivery with idempotency on the consumer side.

**Retry schedule** (example):
| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 30 seconds |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |
| 6 | 12 hours |

After the final attempt: move to **dead letter queue** (DLQ) for manual inspection or consumer-initiated replay.

Rules:
- Treat any 2xx response as success; treat 3xx, 4xx (except 410 Gone), 5xx as failure requiring retry
- Treat 410 Gone as permanent failure — unsubscribe the endpoint automatically
- Set a delivery timeout (e.g., 30s per attempt) — never wait indefinitely
- Track `last_attempt_at`, `attempt_count`, and `last_status_code` per delivery record

### 3. Idempotency — Deduplication on Both Sides

**Sender**: include an idempotency key in every webhook event:
```json
{
  "id": "evt_01HX2K...",
  "idempotency_key": "grant_exercise.u12345.2026-04-10T14:30:00Z",
  ...
}
```

**Receiver**: store processed `idempotency_key` values in a deduplication table with a TTL matching the max retry window. Before processing:
```sql
INSERT INTO processed_webhooks (idempotency_key, processed_at)
VALUES ($1, now())
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING id;
-- If no row returned: duplicate, skip processing
```

Never rely on event ordering for correctness — webhooks can arrive out of order. Use event timestamps, not arrival order, to determine state.

### 4. Event Schema Design — CloudEvents Spec

Adopt the [CloudEvents 1.0](https://cloudevents.io) envelope for interoperability:

```json
{
  "specversion": "1.0",
  "id": "evt_01HX2K3M4N5P6Q",
  "source": "https://api.example.com/equity",
  "type": "com.example.equity.grant.exercised",
  "time": "2026-04-10T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "grant_id": "g_abc123",
    "employee_id": "u_12345",
    "shares_exercised": 500,
    "exercise_price": 10.50
  }
}
```

Event type naming: `{reverse-dns-domain}.{resource}.{verb}` — always past tense.

Version the event schema. When breaking changes are needed, add a new event type rather than modifying the existing one.

### 5. Webhook Registration and Management

Consumer-facing API:
```
POST   /webhooks          — register an endpoint (URL + events + secret)
GET    /webhooks          — list registered endpoints
GET    /webhooks/{id}     — get a single subscription
PATCH  /webhooks/{id}     — update URL, events, or rotate secret
DELETE /webhooks/{id}     — unsubscribe
POST   /webhooks/{id}/test — send a test event
```

Secret rotation: support a `secret_expires_at` field. During the rotation window, accept signatures from both the old and new secret. Reject old secret after the window closes.

### 6. Monitoring — Delivery Rate, Latency, Failure Rate

Key metrics per consumer endpoint:
- **Delivery rate**: successful deliveries / total attempts (target: >99%)
- **P99 delivery latency**: from event creation to first successful acknowledgement
- **Retry rate**: retried deliveries / total deliveries (high = consumer instability)
- **DLQ depth**: events awaiting manual review

Alerts:
- Delivery rate <95% for a single endpoint over 10 minutes → notify consumer + ops
- DLQ depth growing for >1 hour → escalate to on-call
- Endpoint returns 410 → auto-disable and notify consumer

Expose a delivery log to consumers (last 100 events, status, timestamp, response code) — this is the first thing they'll ask for when debugging.

### 7. Key Rules

- Every outbound webhook must be signed — no unsigned webhooks, no exceptions
- Always include an idempotency key in the event envelope
- Consumers must acknowledge with 2xx within your timeout window — document this SLA
- Never retry 410 responses — the endpoint is intentionally gone
- Store the raw request/response body for every delivery attempt for at least 72 hours
- Rotate webhook secrets on a schedule (90 days) or immediately on suspected compromise
