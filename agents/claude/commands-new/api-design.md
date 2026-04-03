---
description: API design — REST endpoints, OpenAPI specs, versioning, auth patterns. Core for FastAPI work.
---

# /api-design — API Design

Read the **api-design-pro** skill from `~/dev/skill-hub/agents/general_skills/api-design-pro.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `design <resource>` | Design | REST endpoints, status codes, request/response schemas |
| `spec` | OpenAPI | Generate or update OpenAPI 3.1 spec from code |
| `review` | Review | Audit existing API for consistency, naming, versioning |
| `doc` | Documentation | Generate API docs from spec or code |
| *(no args)* | Interactive | Ask what API task to perform |

## Context

Auto-detect from project:
- `main.py` + FastAPI imports → FastAPI context (use python-web-frameworks skill)
- `openapi.yaml` / `openapi.json` → Existing spec to update
- `urls.py` → Django REST Framework context

## Standards

- RESTful resource naming (plural nouns, no verbs)
- RFC 7807 error responses
- Cursor-based pagination for lists
- Consistent envelope: `{ data, error, meta }`
