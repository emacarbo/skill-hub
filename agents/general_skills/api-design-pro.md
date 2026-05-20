---
name: api-design-pro
description: "Full-spectrum API architect covering REST, GraphQL, and AsyncAPI design; OpenAPI 3.1 spec generation and SDK delivery; style selection (REST vs GraphQL vs tRPC); versioning and deprecation; pagination; RFC 7807 error handling; documentation generation; breaking-change detection; and API gateway configuration. Use when designing new APIs or evolving existing ones, creating or auditing OpenAPI specs, choosing API paradigm for a project, implementing GraphQL schemas with Federation and DataLoader, documenting APIs for developers, or configuring gateways and rate limiting."
license: MIT
metadata:
  domain: api-architecture
  triggers: API design, REST API, GraphQL, OpenAPI, tRPC, API specification, API architecture, resource modeling, API versioning, API documentation, Apollo Federation, DataLoader, subscriptions, AsyncAPI, event-driven API, API gateway, Kong, AWS API Gateway, breaking change detection, SDK generation, rate limiting, pagination
  role: architect
  scope: design
---

# API Design Pro

Senior API architect covering the full API lifecycle: style selection, schema design, specification, documentation, review, async/event-driven patterns, and gateway configuration.

## When to Use

- Choosing between REST, GraphQL, tRPC, or AsyncAPI for a given context
- Designing REST resources, HTTP method semantics, pagination, and error responses
- Creating or validating OpenAPI 3.1 specifications and generating SDKs
- Designing GraphQL schemas with Apollo Federation, DataLoader, and subscriptions
- Generating developer-facing documentation, getting-started guides, and code examples
- Auditing an existing API for breaking changes, consistency, and best-practice violations
- Designing event-driven API contracts with AsyncAPI
- Configuring API gateways (Kong, AWS API Gateway) for routing, auth, and rate limiting

## Core Workflow

1. **Analyze domain** — Understand business requirements, data models, and consumer needs; confirm client types (web, mobile, third-party, internal)
2. **Choose style** — Select REST, GraphQL, tRPC, or AsyncAPI using the decision tree below
3. **Model resources** — Identify resources, relationships, and operations; sketch entity diagram before writing any spec
4. **Specify contract** — Create OpenAPI 3.1 spec (REST) or SDL (GraphQL); validate: `npx @redocly/cli lint openapi.yaml`
5. **Mock and verify** — Spin up mock server: `npx @stoplight/prism-cli mock openapi.yaml`; run breaking-change detection against previous version
6. **Document** — Generate developer guide, code examples (curl, JS, Python), and interactive docs (Swagger UI / Redoc)
7. **Govern evolution** — Design versioning, deprecation notices, and backward-compatibility strategy

## API Style Decision Tree

| Condition | Recommended Style |
|-----------|------------------|
| Multiple clients with different data needs (mobile vs web) | GraphQL |
| TypeScript monorepo, end-to-end type safety, no external consumers | tRPC |
| External/public API, third-party integrations, broad tooling support | REST + OpenAPI |
| Async/event-driven: webhooks, streaming, message queues | AsyncAPI |
| Simple CRUD, resource-oriented, cacheability is critical | REST |
| Real-time subscriptions with flexible queries | GraphQL |

Ask before deciding: Who are the API consumers? Do they control both client and server? Is discoverability or caching critical?

## REST Design Principles

Resource naming: use nouns in kebab-case (`/api/v1/user-profiles`), never verbs (`/getUsers`).

HTTP method semantics:
- **GET** — safe and idempotent; retrieve
- **POST** — create; not idempotent (use `Idempotency-Key` header for payments)
- **PUT** — replace entire resource; idempotent
- **PATCH** — partial update; not necessarily idempotent
- **DELETE** — remove; idempotent

URL structure: `/api/v1/{collection}`, `/api/v1/{collection}/{id}`, `/api/v1/{collection}/{id}/{sub-collection}`, `/api/v1/{collection}/{id}/{action}` (POST for actions like `/activate`).

## OpenAPI 3.1 Starter Template

```yaml
openapi: "3.1.0"
info:
  title: Example API
  version: "1.0.0"
paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      tags: [Users]
      parameters:
        - name: cursor
          in: query
          schema: { type: string }
        - name: limit
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                required: [data, pagination]
                properties:
                  data: { type: array, items: { $ref: "#/components/schemas/User" } }
                  pagination: { $ref: "#/components/schemas/CursorPage" }
        "400": { $ref: "#/components/responses/BadRequest" }
        "401": { $ref: "#/components/responses/Unauthorized" }
        "429": { $ref: "#/components/responses/TooManyRequests" }

components:
  schemas:
    User:
      type: object
      required: [id, email, created_at]
      properties:
        id:         { type: string, format: uuid, readOnly: true }
        email:      { type: string, format: email }
        name:       { type: string }
        created_at: { type: string, format: date-time, readOnly: true }
    CursorPage:
      type: object
      required: [next_cursor, has_more]
      properties:
        next_cursor: { type: string, nullable: true }
        has_more:    { type: boolean }
    Problem:                            # RFC 7807
      type: object
      required: [type, title, status]
      properties:
        type:     { type: string, format: uri }
        title:    { type: string }
        status:   { type: integer }
        detail:   { type: string }
        instance: { type: string, format: uri }
  responses:
    BadRequest:
      description: Invalid request parameters
      content: { application/problem+json: { schema: { $ref: "#/components/schemas/Problem" } } }
    Unauthorized:
      description: Missing or invalid authentication
      content: { application/problem+json: { schema: { $ref: "#/components/schemas/Problem" } } }
    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After: { schema: { type: integer } }
      content: { application/problem+json: { schema: { $ref: "#/components/schemas/Problem" } } }
  securitySchemes:
    BearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
security:
  - BearerAuth: []
```

## Error Handling — RFC 7807

Always use `Content-Type: application/problem+json`. The `type` field must be a stable, documented URI. Extend with `errors[]` for field-level validation failures:

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/users/req-abc123",
  "errors": [{ "field": "email", "message": "Must be a valid email address." }]
}
```

HTTP status codes: 400 (bad input), 401 (unauthenticated), 403 (forbidden), 404 (not found), 409 (conflict), 422 (semantic error), 429 (rate limited), 500 (server error).

## Pagination Patterns

Prefer cursor-based for large, frequently-updated datasets; offset for small, stable sets:

```json
// Cursor (preferred)
{ "data": [...], "pagination": { "next_cursor": "eyJpZCI6MTIzfQ==", "has_more": true } }

// Offset
{ "data": [...], "pagination": { "offset": 20, "limit": 10, "total": 150 } }
```

## Versioning Strategies

| Strategy | Example | Use When |
|----------|---------|----------|
| URL path (recommended) | `/api/v2/users` | Public APIs; explicit, easy to route |
| Header | `Accept: application/vnd.api+json;version=2` | Clean URLs, content negotiation |
| Media type | `Accept: application/vnd.myapi.v2+json` | Strict RESTful; complex to implement |
| Query param (avoid) | `/api/users?version=2` | Simple but not RESTful |

Breaking changes requiring a version bump: removing response fields, making optional fields required, changing field types, removing endpoints, modifying error formats.

Safe (non-breaking): adding optional request fields, adding response fields, adding endpoints, making required fields optional.

## GraphQL Architecture

### Schema-First Design with Federation

```graphql
# products subgraph
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Float!
}

# reviews subgraph — extends Product entity
type Product @key(fields: "id") {
  id: ID! @external
  reviews: [Review!]!
}

type Review {
  id: ID!
  rating: Int!
  body: String
  author: User! @shareable
}
```

### DataLoader — N+1 Prevention

```js
// One DataLoader per request in context
const context = ({ req }) => ({
  loaders: {
    user: new DataLoader(async (userIds) => {
      const users = await db.users.findMany({ where: { id: { in: userIds } } });
      return userIds.map((id) => users.find((u) => u.id === id) ?? null);
    }),
  },
});

// Resolver batches all lookups into a single query
const resolvers = {
  Review: { author: (review, _args, { loaders }) => loaders.user.load(review.authorId) },
};
```

### Query Complexity + Security

```js
import { createComplexityRule } from 'graphql-query-complexity';
const server = new ApolloServer({
  schema,
  validationRules: [createComplexityRule({ maximumComplexity: 1000 })],
});
```

Always apply: query depth limiting, field-level authorization, rate limiting per client.

## AsyncAPI for Event-Driven APIs

Use AsyncAPI 3.0 to document WebSocket, Kafka, AMQP, and SSE interfaces. Key elements mirror OpenAPI but describe channels and messages instead of paths:

```yaml
asyncapi: "3.0.0"
info:
  title: Order Events
  version: "1.0.0"
channels:
  order/created:
    messages:
      OrderCreated:
        payload:
          type: object
          properties:
            orderId: { type: string, format: uuid }
            customerId: { type: string }
            total: { type: number }
```

Publish AsyncAPI alongside OpenAPI when your service exposes both sync and async interfaces.

## API Gateway Configuration

### Kong (self-hosted / Konnect)

```yaml
# Rate limiting plugin
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
      policy: redis

# JWT validation plugin
  - name: jwt
    config:
      key_claim_name: kid
      claims_to_verify: [exp, nbf]
```

### AWS API Gateway

- Use Usage Plans + API Keys for per-consumer throttling (burst/rate limits).
- Attach Cognito User Pool or Lambda authorizer for JWT/OAuth validation.
- Enable WAF integration for OWASP rule set protection.
- Use VPC Link for private backend integration; avoid public Lambda URLs in production.
- Enable CloudWatch access logging with `$context.requestId` for traceability.

## Breaking-Change Detection

Run in CI to catch regressions before merge:

```yaml
- name: breaking-change-detection
  run: npx @opticdev/optic diff openapi-v1.yaml openapi-v2.yaml --check
```

Breaking changes: endpoint removal, response field removal, type change, required field addition, status code change.

## Documentation Generation

```bash
npx @redocly/cli build-docs openapi.yaml --output docs/index.html   # Redoc
npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./sdk
```

Developer guide: Introduction → Authentication → Quick Start → Endpoints → Data Models → Error Reference → Rate Limiting → Changelog → SDKs.

## API Design Review Scoring

Consistency (30%): naming, response envelope, error format uniformity.
Documentation (20%): all endpoints described, examples provided, error codes listed.
Security (20%): auth scheme documented, rate limiting configured, input validation enforced.
Usability (15%): pagination on lists, field selection supported, HATEOAS links where valuable.
Performance (15%): caching headers, ETag support, batch operations, async for heavy workloads.

## Constraints

### MUST DO
- Follow resource-oriented design (nouns, not verbs in URIs)
- Use consistent naming conventions — pick one (snake_case or camelCase) and apply everywhere
- Include comprehensive OpenAPI 3.1 spec validated with `@redocly/cli lint`
- Design error responses using RFC 7807 with stable `type` URIs
- Implement cursor-based pagination on all collection endpoints
- Version APIs with explicit deprecation policies before introducing breaking changes
- Document authentication flows and rate limiting headers
- Provide working code examples in at least curl and one SDK language

### MUST NOT DO
- Use verbs in resource URIs
- Return inconsistent response envelopes across endpoints
- Create breaking changes without a versioned migration path
- Skip error code documentation
- Ignore HTTP status code semantics
- Expose internal implementation details (database IDs, stack traces, internal service names)
- Create N+1 query problems in GraphQL resolvers (use DataLoader)
- Skip query depth/complexity limiting on GraphQL endpoints

## Output Checklist

When delivering an API design:
1. Resource model and relationships (diagram or table)
2. Style selection rationale (REST / GraphQL / tRPC / AsyncAPI)
3. OpenAPI 3.1 or AsyncAPI spec (validated, no lint errors)
4. Authentication and authorization flows documented
5. Error response catalog (all 4xx/5xx with RFC 7807 `type` URIs)
6. Pagination and filtering patterns
7. Versioning and deprecation strategy
8. Breaking-change assessment vs previous version (if evolving)
9. Developer quick-start guide with working code examples
10. Gateway configuration notes (auth, rate limits, routing)

