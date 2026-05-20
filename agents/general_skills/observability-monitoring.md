---
name: observability-monitoring
description: "Comprehensive observability specialist covering the three pillars (metrics, logs, traces), SLI/SLO/error budget design, alerting architecture, dashboard design, incident command, and load testing. Use when setting up application monitoring, adding observability to services, designing SLI/SLO frameworks, debugging production issues with logs/metrics/traces, tuning alerting to reduce fatigue, running load tests, profiling performance bottlenecks, managing incident response, or optimizing observability costs."
license: MIT
metadata:
  domain: devops
  triggers: monitoring, observability, logging, metrics, tracing, alerting, Prometheus, Grafana, OpenTelemetry, DataDog, APM, SLI, SLO, error budget, burn rate, k6, load testing, profiling, capacity planning, incident response, incident commander, MTTD, MTTR, synthetic monitoring, business metrics, cardinality, log sampling
  role: specialist
  scope: implementation
  related-skills: devops-infrastructure, sre-engineer, debugging-master
---

# Observability & Monitoring Specialist

Observability and performance specialist implementing the full stack: metrics, logs, traces, SLI/SLO frameworks, alerting, incident response, and load testing.

## When to Use

- Instrumenting services with Prometheus metrics, structured logs, or OpenTelemetry traces
- Designing SLI/SLO frameworks and error budget policies
- Building dashboards using RED (Rate/Errors/Duration) or USE (Utilization/Saturation/Errors) methods
- Writing alerting rules — threshold, burn rate, anomaly detection
- Reducing alert fatigue through noise suppression and grouping
- Running load tests with k6 or Artillery; profiling CPU/memory bottlenecks
- Managing incidents: severity triage, stakeholder communication, blameless postmortems
- Controlling observability costs: log volume, metric cardinality, trace sampling
- Business-level observability: feature adoption, revenue correlation, SLA reporting

## Core Workflow

1. **Assess** — Identify SLIs, critical user journeys, and business metrics to protect
2. **Instrument** — Add structured logging, Prometheus metrics, and OTel traces
3. **Collect** — Configure aggregation (Prometheus scrape, log shipper, OTLP endpoint); verify data arrives before proceeding
4. **Visualize** — Build dashboards with drill-down hierarchy: overview → service → component → instance
5. **Alert** — Define SLO burn rate + symptom-based alerts; validate no false-positive flood before shipping

## Instrumentation Examples

### Structured Logging (Node.js / Pino)

```js
import pino from 'pino';
const logger = pino({ level: 'info' });

// Good: structured fields with correlation ID
logger.info({ requestId: req.id, userId: req.user.id, durationMs: elapsed }, 'order.created');

// Bad: string interpolation, no correlation
console.log(`Order created for user ${userId}`);
```

Never log passwords, tokens, or PII. Use log sampling for high-volume DEBUG output to control ingestion cost.

### Prometheus Metrics (Node.js)

```js
import { Counter, Histogram, register } from 'prom-client';

const httpRequests = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request latency',
  labelNames: ['method', 'route'],
  buckets: [0.05, 0.1, 0.3, 0.5, 1, 2, 5],
});

app.use((req, res, next) => {
  const end = httpDuration.startTimer({ method: req.method, route: req.path });
  res.on('finish', () => {
    httpRequests.inc({ method: req.method, route: req.path, status: res.statusCode });
    end();
  });
  next();
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### OpenTelemetry Tracing (Node.js)

```js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { trace, SpanStatusCode } from '@opentelemetry/api';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://jaeger:4318/v1/traces' }),
});
sdk.start();

const tracer = trace.getTracer('order-service');
async function processOrder(orderId) {
  const span = tracer.startSpan('order.process');
  span.setAttribute('order.id', orderId);
  try {
    const result = await db.saveOrder(orderId);
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (err) {
    span.recordException(err);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw err;
  } finally {
    span.end();
  }
}
```

## SLI / SLO / Error Budget Design

Define SLIs as measurable signals of user experience: availability, latency (P95/P99), error rate. Set SLOs collaboratively with product — targets that trigger error budget burn alerts, not just aspirational numbers.

```yaml
# Error budget burn rate alert (multi-window)
groups:
  - name: slo.rules
    rules:
      # Fast burn: 2% of monthly budget consumed in 1 hour
      - alert: ErrorBudgetFastBurn
        expr: |
          (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) > (14.4 * 0.001)
          and
          (rate(http_requests_total{status=~"5.."}[1h]) / rate(http_requests_total[1h])) > (14.4 * 0.001)
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "SLO fast burn — error budget depleting rapidly"

      # Slow burn: 10% of budget in 3 days
      - alert: ErrorBudgetSlowBurn
        expr: |
          (rate(http_requests_total{status=~"5.."}[6h]) / rate(http_requests_total[6h])) > 0.001
          and
          (rate(http_requests_total{status=~"5.."}[3d]) / rate(http_requests_total[3d])) > 0.001
        for: 15m
        labels: { severity: warning }

      # Threshold-based alert for reference
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Error rate above 5% on {{ $labels.route }}"
```

## Alerting Architecture

### Alert Design Principles

- Alert on **symptoms** (user-visible impact), not causes (high CPU that doesn't affect users)
- Every alert must be **actionable** and link to a runbook
- Use **multi-window** logic to avoid flapping: `avg_over_time(up[2m]) == 0 AND avg_over_time(up[10m]) < 0.8`
- Use **hysteresis**: fire at 5% error rate, auto-resolve only when it drops below 3%
- Use **inhibit rules** to suppress child alerts when parent (e.g., `ServiceDown`) is already firing
- Apply **grouping** (`group_wait: 30s`, `group_interval: 2m`) to batch related notifications
- Set `repeat_interval: 1h` to re-notify on unresolved alerts without spamming

**Alert fatigue prevention:** Measure alert precision (true positives / total alerts) and time-to-acknowledgement. Quarterly review of alerts that fired without resulting in incidents — tune or retire them.

**Alert severity tiers:** Critical (SLO burn, service down, data loss risk) → Warning (approaching threshold, non-user-facing degradation) → Info (deployment notifications, capacity triggers).

Include runbook URL and quick debug commands in every alert annotation:

```yaml
annotations:
  runbook_url: "https://runbooks.example.com/alerts/{{ $labels.alertname }}"
  quick_debug: |
    1. curl -sf https://{{ $labels.instance }}/health
    2. kubectl logs {{ $labels.pod }} --tail=50 -n production
```

## Dashboard Design

Hierarchy: **Overview** (fleet health, SLO status) → **Service** (RED metrics per service) → **Component** (DB, cache, queue) → **Instance** (pod/node drill-down).

Panel guidelines: max 7±2 panels per screen; use time series for trends, heatmaps for latency distributions, stat panels for current SLO status; red/amber/green color coding aligned to SLO thresholds; default time window 4 h for incidents, 7 d for trend review. Add reference lines for SLO targets and historical baselines.

Role-based dashboards: **SRE** (error budgets, burn rates, saturation), **Developer** (service-level RED), **Executive** (business SLA, reliability KPIs, revenue-correlated uptime).

## Load Testing (k6)

```js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // ramp up
    { duration: '5m', target: 50 },  // sustained
    { duration: '1m', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/orders');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

Integrate performance regression tests into CI with Lighthouse CI (frontend Core Web Vitals) and Artillery/k6 (API). Define rollback triggers: if P95 latency or error rate exceeds threshold post-deploy, auto-revert or block promotion to next stage.

## Incident Response

### Severity Classification

| Severity | Definition | IC Response Time | Update Cadence |
|----------|------------|-----------------|----------------|
| SEV1 (P0) | Full outage, data loss, security breach | 5 min IC assignment | Every 15 min |
| SEV2 (P1) | >25% user impact, revenue-generating system degraded | 30 min | Every 30 min |
| SEV3 (P2) | Single feature, <25% users, workaround available | 2 h (business hours) | Key milestones |
| SEV4 (P3) | Cosmetic, dev/test, no user impact | Next business day | Standard tickets |

### Incident Commander Responsibilities

1. **Command** — own the response process, make resource allocation decisions, bias toward action
2. **Communicate** — regular stakeholder updates, shield responders from distractions, manage status page
3. **Coordinate** — drive toward resolution, manage handoffs, plan rollback if fix-forward is risky
4. **Post-incident** — ensure blameless postmortem within 48 h, drive action item completion

### Response Phases

**Phase 1 — Triage:** classify severity, check recent deployments, sweep observability (traces → metrics → logs). Activate initial mitigation: traffic throttling, feature flag disable, circuit breaker, or rollback.

**Phase 2 — Root Cause:** five-why analysis; check DB lock contention, memory leaks, cascading dependency failures, certificate expiry.

**Phase 3 — Resolution:** prefer rollback over risky fix under pressure; validate fix in staging if time permits; deploy with canary and monitor error budget for 10+ min.

**Phase 4 — Postmortem:** blameless focus (system failures, not individuals); document complete timeline, what went well, improvement actions with owners and due dates; share broadly.

**Runbook template structure:** alert context → impact assessment → ordered investigation steps with time estimates → resolution actions → escalation path → follow-up tasks.

### Key Communication Template (SEV1/2)

```
[SEV{level}] {Service} — {Brief Description}

Impact: {user-facing description}
Status: investigating | mitigating | resolved
Affected Services: {list}
IC: {name} | Tech Lead: {name}
Next update: {timestamp}
Status page: {link}
```

## Synthetic Monitoring

Complement reactive alerting with proactive synthetic checks: HTTP uptime probes for critical endpoints, browser-based synthetic transactions for key user journeys (login, checkout), and API contract tests on a schedule. Synthetic monitoring detects issues before real users do and validates recovery after incidents.

## Business-Level Observability

Track metrics beyond RED/USE: feature adoption rates, conversion funnel health, revenue-correlated SLIs (checkout success rate, payment processing latency), and A/B test impact on reliability. Create executive dashboards that correlate technical SLOs with business KPIs.

## Observability Cost Optimization

**Metrics:** set retention tiers (high-resolution for 15 d, downsampled for 90 d, aggregated for 1 y); manage cardinality by auditing high-label-count metrics (`__name__` cardinality > 10 k is a warning sign).

**Logs:** apply tail-based sampling — always keep ERROR/WARN, sample INFO at 10–20%, drop DEBUG in production; route high-volume logs to cold storage (S3/GCS) after 7 d.

**Traces:** head-based sampling 10–20% for baseline coverage; tail-based sampling to always capture error traces, high-latency traces (>P99), and 100% for critical user journeys. Monitor collector pipeline throughput to avoid drop.

## Constraints

**MUST DO:** Use structured logging (JSON). Include request/correlation IDs. Alert on SLO burn rate, not just thresholds. Monitor business metrics alongside technical. Implement health check endpoints. Version-control dashboards and alert rules (GitOps for observability config).

**MUST NOT DO:** Log sensitive data (passwords, tokens, PII). Alert on every error — alert fatigue degrades response quality. Use string interpolation in logs. Skip correlation IDs in distributed systems. Ignore observability cost as systems scale.

## Reference Guide

| Topic | Load When |
|-------|-----------|
| Structured logging | Pino, logrus, zerolog, log levels, sampling |
| Prometheus metrics | Counter/Gauge/Histogram patterns, recording rules, PromQL |
| OpenTelemetry | Auto-instrumentation, collector config, sampling strategies |
| Alert design patterns | Burn rate, hysteresis, inhibit rules, routing |
| Dashboard design | RED/USE, Grafana templating, role-based views |
| Load testing | k6 stages, Artillery scenarios, CI integration |
| Profiling | Flame graphs, heap analysis, continuous profiling |
| Incident response | Runbook templates, PIR format, communication cadence |
| Cost optimization | Cardinality management, log sampling, trace retention |

## Knowledge Base

Prometheus, Grafana, Loki, OpenTelemetry, Jaeger, Zipkin, DataDog, New Relic, Dynatrace, ELK Stack, Splunk, Fluentd, Fluent Bit, PagerDuty, Opsgenie, k6, Artillery, Gatling, AWS CloudWatch, GCP Cloud Monitoring, Azure Monitor, Istio telemetry, Chaos Monkey, Gremlin
