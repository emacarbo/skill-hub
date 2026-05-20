---
name: debugging-master
description: "Expert debugger applying four-phase root-cause methodology, hypothesis-driven analysis, multi-language debugger commands, observability-driven production diagnosis, distributed system tracing, CPU/memory profiling, and browser/serverless debugging. Use when investigating errors, analyzing stack traces, finding root causes of unexpected behavior, troubleshooting production incidents, tracing distributed failures across microservices, profiling performance bottlenecks, or performing log analysis and root cause analysis."
metadata:
  domain: quality
  triggers: debug, error, bug, exception, traceback, stack trace, troubleshoot, not working, crash, fix issue, root cause, production incident, performance bottleneck, memory leak, distributed tracing, flaky, intermittent failure
  role: specialist
  scope: analysis
---

# Debugging Master

Expert debugger applying systematic root-cause methodology to isolate and resolve issues in any codebase — from local unit test failures to distributed production incidents.

## When to Use

- Investigating errors, exceptions, or unexpected behavior
- Analyzing stack traces and log entries
- Troubleshooting crashes, timeouts, or data corruption
- Diagnosing production incidents across microservices
- Profiling CPU, memory, or I/O bottlenecks
- Debugging browser-rendered or serverless functions
- Setting up distributed tracing infrastructure for a team

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Symptom fixes are failure. Random changes waste time and create new bugs. If you haven't completed Phase 1, you cannot propose fixes.

**Stop and return to Phase 1 if you're thinking:**
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that" (without evidence)
- "One more fix attempt" (when already tried 2+)

**3+ fixes failed?** Question the architecture — each fix revealing a new problem in a different place signals a structural issue, not a symptom to patch.

## Core Workflow (Four Phases)

### Phase 1: Root Cause Investigation

Complete this phase before attempting ANY fix.

1. **Read error messages carefully** — don't skim. Stack traces contain line numbers, file paths, and error codes that often point directly to the source.

2. **Reproduce consistently** — establish exact steps that trigger the issue every time. If not reproducible, gather more data. Never guess.

3. **Check recent changes** — git diff, recent commits, new dependencies, config or environment changes.

4. **Gather evidence in multi-component systems** — add diagnostic instrumentation at each layer boundary BEFORE proposing fixes:
```bash
# Layer 1: entry point
echo "=== Input received: ${INPUT:+SET}${INPUT:-UNSET}"

# Layer 2: processing
echo "=== State after transform: $TRANSFORMED_VALUE"

# Layer 3: external call
curl -v "$API_URL" 2>&1 | head -30

# Layer 4: output
echo "=== Final result: $RESULT"
```
Run once to observe WHERE it breaks, then investigate that specific component.

5. **Trace data flow** — where does the bad value originate? What called this function with the bad value? Trace backward up the call stack to the source. Fix at source, not at symptom.

### Phase 2: Pattern Analysis

1. Find working examples — locate similar code in the same codebase that behaves correctly
2. Compare against references — read reference implementations completely; partial understanding causes new bugs
3. Identify every difference — list all differences between working and broken, however small
4. Understand dependencies — what config, environment, or state does this code assume?

### Phase 3: Hypothesis and Testing

1. **Form ONE specific hypothesis** — "I think X is the root cause because Y." Write it down.
2. **Make the smallest possible change** to test it — one variable at a time
3. **Verify before continuing** — did it work? Yes → Phase 4. No → form new hypothesis. Do NOT layer more fixes.
4. **When uncertain** — say "I don't understand X" and ask or research rather than guessing.

### Phase 4: Fix and Prevent

1. Create a failing test case that reproduces the bug (simplest possible reproduction)
2. Implement ONE fix addressing the confirmed root cause
3. Verify: test passes, no other tests broken, issue resolved
4. Add regression tests and monitoring/alerts to prevent recurrence
5. Remove all debug code (console.log, breakpoints, debug endpoints) before committing

## Debugging Strategy Selection

Choose strategy based on issue characteristics:

| Scenario | Strategy |
|----------|----------|
| Reproducible locally | Interactive debugger (pdb, Node inspect, dlv) |
| Production incident | Observability-driven (Sentry, DataDog, traces) |
| Complex state / race condition | Time-travel debugging (rr, Redux DevTools) |
| Intermittent under load | Chaos engineering, statistical delta debugging |
| Regression hunting | `git bisect` |
| Performance bottleneck | Profiler + flamegraph before any code change |

## Language Debugger Commands

**Python (pdb):**
```bash
python -m pdb script.py          # launch debugger
# b 42          — set breakpoint at line 42
# n             — step over
# s             — step into
# p some_var    — print variable
# bt            — print full traceback
# c             — continue to next breakpoint
```

**JavaScript/Node.js:**
```bash
node --inspect-brk script.js     # pause at first line, attach Chrome DevTools
# chrome://inspect → click "inspect"
# Sources panel: add breakpoints, watch expressions, step through
```

**Go (Delve):**
```bash
dlv debug ./cmd/server
# (dlv) break main.go:55
# (dlv) continue
# (dlv) print myVar
# (dlv) goroutines    — list all goroutines
```

**Git bisect (regression hunting):**
```bash
git bisect start
git bisect bad                   # current commit is broken
git bisect good v1.2.0           # last known good tag/commit
# Test midpoint → git bisect good OR git bisect bad
git bisect reset
```

## Browser DevTools Debugging

**JavaScript (Chrome/Firefox):**
- Sources panel → breakpoints, conditional breakpoints, logpoints (no code change needed)
- Network panel → XHR/fetch requests, response bodies, timing, failed requests
- Performance panel → flamechart for CPU hotspots and long tasks
- Memory panel → heap snapshots, allocation timelines for leak detection
- Console → `console.trace()`, `console.time()`, `debugger` statement

**React/Vue DevTools:**
```javascript
// Pause on component re-render
// Install React DevTools → Components panel → gear icon → "Highlight updates"

// Manual breakpoint in React event handler
function handleSubmit(e) {
  debugger;  // Chrome DevTools pauses here
  // ...
}
```

## Serverless Debugging

**AWS Lambda:**
```bash
# Local testing with SAM
sam local invoke FunctionName --event event.json
sam local start-api  # local API Gateway simulation

# Remote debugging with structured logs
console.log(JSON.stringify({ level: 'DEBUG', requestId: context.awsRequestId, payload }));

# CloudWatch Logs Insights for production
fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20
```

**Common serverless pitfalls:**
- Cold start latency masking actual errors — check init duration separately
- Missing environment variables in execution environment vs local
- Timeout too short — check `context.getRemainingTimeInMillis()` before expensive ops
- Lambda concurrency limits causing throttling — check for 429 in CloudWatch

## Production-Safe Debugging Techniques

Use these to investigate production issues without risk:

- **OpenTelemetry spans** — add non-invasive attributes to existing traces
- **Feature-flagged debug logging** — conditional verbose logs for specific user IDs
- **Sampling-based profiling** — Pyroscope continuous profiling at <1% overhead
- **Read-only debug endpoints** — protected by auth, rate-limited state inspection
- **Gradual traffic shifting** — canary deploy debug version to 10% of traffic

**Observability data sources for production triage:**
```
Error tracking:  Sentry, Rollbar, Bugsnag
APM metrics:     DataDog, New Relic, Dynatrace
Distributed traces: Jaeger, Zipkin, Honeycomb
Log aggregation: ELK, Splunk, Loki/Grafana
Session replays: LogRocket, FullStory
```

**Query patterns:**
- Error frequency and trend over time
- Deployment timeline correlation (did it start after a deploy?)
- Affected user cohorts (all users? specific plan? specific region?)
- Related errors or warnings in the same time window

## Distributed System Tracing

For multi-service failures, trace across service boundaries:

```bash
# 1. Get the trace ID from the error report
TRACE_ID="abc123def456"

# 2. Pull all spans for this trace
# Jaeger UI → search by trace ID
# Or via API:
curl "http://jaeger:16686/api/traces/$TRACE_ID" | jq '.data[0].spans[] | {service: .processID, operation: .operationName, duration: .duration, error: .tags[]? | select(.key == "error")}'

# 3. Look for: high duration spans, error tags, missing child spans (dropped request)
# 4. Find the span where latency/error originated — that service owns the root cause
```

**Correlation ID propagation check:**
```bash
# Verify trace context propagates through your services
curl -H "traceparent: 00-$(python3 -c 'import secrets; print(secrets.token_hex(16))')-$(python3 -c 'import secrets; print(secrets.token_hex(8))')-01" \
  http://service-a/endpoint

# Then check downstream services received the same trace ID
```

## Performance Profiling

**Golden rule: measure before optimizing.** Profile first, then fix the confirmed bottleneck.

**Node.js CPU flamegraph:**
```bash
node --prof server.js          # run with profiling
node --prof-process isolate-*.log > profile.txt  # process
# Or use clinic.js:
npx clinic flame -- node server.js
```

**Python (py-spy):**
```bash
py-spy record -o flamegraph.svg --pid $(pgrep python)
py-spy top --pid $(pgrep python)  # live top-like view
```

**Go (pprof):**
```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
# In pprof: top10, web (opens flamegraph in browser)
```

**Memory leak detection:**
```bash
# Node.js heap snapshot
node --inspect server.js
# DevTools → Memory → Take Heap Snapshot → compare two snapshots

# Python memory_profiler
python -m memory_profiler script.py
```

**Before/after measurement template:**
```
| Metric       | Before  | After  | Delta  |
|--------------|---------|--------|--------|
| P50 latency  | 480ms   | 48ms   | -90%   |
| P99 latency  | 3,100ms | 280ms  | -91%   |
| RPS @ 50 VUs | 42      | 380    | +804%  |
| DB queries   | 23 (N+1)| 1      | -96%   |
```

**Common quick-wins to profile first:**
```
Database: missing indexes, N+1 queries, SELECT *, no connection pooling
Node.js: sync I/O in hot path, JSON.parse of large objects in loop, no compression
Bundle: Moment.js, full Lodash, unoptimized images, missing code splitting
API: no pagination, serial awaits that could be parallel, no caching headers
```

## Hypothesis Categories

When generating hypotheses, consider these root cause categories:

- **Logic errors** — race conditions, null pointer, off-by-one, incorrect conditionals
- **State management** — stale cache, incorrect state transitions, shared mutable state
- **Integration failures** — API contract changes, timeouts, auth expiry, missing retries
- **Resource exhaustion** — memory leaks, connection pool starvation, file descriptor limits
- **Configuration drift** — missing env vars, changed feature flags, deployment differences
- **Data corruption** — schema mismatches, encoding issues, truncation

## Constraints

**MUST DO**
- Reproduce the issue consistently before proposing any fix
- Gather complete error messages, stack traces, and evidence
- Test one hypothesis at a time with the smallest possible change
- Document root cause and fix for future reference
- Add regression tests after fixing
- Remove all debug code before committing

**MUST NOT**
- Guess without testing
- Make multiple changes at once
- Skip reproduction steps
- Assume you know the cause before tracing evidence
- Debug in production without safeguards (feature flags, canary, rollback plan)
- Leave console.log, debugger statements, or debug endpoints in committed code
- Attempt a 4th fix if 3 already failed without questioning the architecture

## Output Template

When debugging, provide:
1. **Root Cause** — what specifically caused the issue, with evidence
2. **Evidence** — stack trace, logs, or failing test that proves it
3. **Fix** — code change that resolves the root cause (not the symptom)
4. **Prevention** — regression test or monitoring safeguard to prevent recurrence
