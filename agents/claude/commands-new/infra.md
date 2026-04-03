---
description: Infrastructure — CI/CD pipelines, Docker, Terraform, Kubernetes, deployment.
---

# /infra — Infrastructure & DevOps

Read the **devops-infrastructure** skill from `~/dev/skill-hub/agents/general_skills/devops-infrastructure.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `ci` | CI/CD | Create or update GitHub Actions workflow |
| `docker` | Docker | Dockerfile, docker-compose, multi-stage builds |
| `terraform <resource>` | IaC | Terraform module for resource |
| `k8s <workload>` | Kubernetes | Manifests, RBAC, networking |
| `deploy` | Deploy | Deployment strategy, validation, rollback plan |
| *(no args)* | Scan | Detect existing infra files, suggest improvements |

## Context

Auto-detect from project:
- `.github/workflows/` → GitHub Actions CI/CD
- `Dockerfile` → Container context
- `*.tf` → Terraform context
- `k8s/` or `manifests/` → Kubernetes context
- `docker-compose.yml` → Local dev environment
