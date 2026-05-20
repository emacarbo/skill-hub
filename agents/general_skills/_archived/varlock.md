---
name: varlock
description: Use when handling secrets, API keys, credentials, or .env files. Ensures secrets never appear in terminals, logs, or Claude's context. Trigger phrases include "environment variables", "secrets", ".env", "API key", "credentials".
version: 1.0.0
---

# Varlock Security Skill

Secure-by-default environment variable management for Claude Code sessions.

> **Repo**: https://github.com/dmno-dev/varlock | **Docs**: https://varlock.dev

## Security Rules for Claude

### Never Echo Secrets
```bash
# NEVER: echo $SECRET, cat .env, printenv | grep API
# ALWAYS: varlock load --quiet && echo "Secrets validated"
```

### Never Read .env Directly
```bash
# NEVER: cat .env, Read .env with tools
# ALWAYS: cat .env.schema (safe), varlock load (masked output)
```

### Never Include Secrets in Commands
```bash
# NEVER: curl -H "Authorization: Bearer sk_live_xxx" ...
# ALWAYS: curl -H "Authorization: Bearer $API_KEY" ...
# Or: varlock run -- curl ...
```

## Quick Start

```bash
curl -sSfL https://varlock.dev/install.sh | sh -s -- --force-no-brew
export PATH="$HOME/.varlock/bin:$PATH"
varlock init   # Create .env.schema from existing .env
```

## Schema: .env.schema

```bash
# @defaultSensitive=true @defaultRequired=infer

# @type=enum(development,staging,production) @sensitive=false
NODE_ENV=development

# @type=port @sensitive=false
PORT=3000

# @type=url @required
DATABASE_URL=

# @type=string(startsWith=sk_) @required @sensitive
STRIPE_SECRET_KEY=
```

### Annotations

| Annotation | Effect |
|------------|--------|
| `@sensitive` | Redacted in all output |
| `@sensitive=false` | Shown in logs |
| `@type=string(startsWith=X)` | Prefix validation |
| `@type=url`, `port`, `boolean`, `enum(a,b)` | Type validation |
| `@required` | Must be present |

## Safe Commands

```bash
varlock load              # Validate all (masks sensitive values)
varlock load --quiet      # Silent on success
varlock run -- npm start  # Inject validated env into command
cat .env.schema           # Schema is safe to read
```

## Common Patterns

```bash
# Validate before operations
varlock load --quiet || { echo "Env validation failed"; exit 1; }

# CI/CD (GitHub Actions)
- name: Validate environment
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: varlock load --quiet

# Docker
CMD ["varlock", "run", "--", "npm", "start"]
```

## When User Asks About Secrets

- **"Check if API key is set"**: `varlock load 2>&1 | grep "API_KEY"`
- **"Debug authentication"**: `varlock load` to validate types/presence
- **"Update a secret"**: Direct user to update .env manually or via secrets manager, then `varlock load`
- **"Show .env file"**: Refuse. Offer `varlock load` or `cat .env.schema`

## npm Scripts

```json
{
  "env:validate": "varlock load",
  "prestart": "varlock load --quiet",
  "start": "varlock run -- node server.js"
}
```

## Quick Reference

| Task | Command |
|------|---------|
| Validate all | `varlock load` |
| Quiet check | `varlock load --quiet` |
| Run with env | `varlock run -- <cmd>` |
| View schema | `cat .env.schema` |

| Never Do | Why |
|----------|-----|
| `cat .env` | Exposes all secrets |
| `echo $SECRET` | Exposes to Claude context |
| `printenv \| grep` | Exposes matching secrets |
| Hardcode in commands | In shell history |

## Security Checklist

- [ ] Install Varlock; create `.env.schema`
- [ ] Mark secrets with `@sensitive`; add `@defaultSensitive=true`
- [ ] Add `.env` to `.gitignore`; commit `.env.schema`
- [ ] Add `varlock load` to CI/CD
- [ ] Never use `cat .env` or `echo $SECRET` in Claude sessions
