---
name: devops-infrastructure
description: "Full DevOps lifecycle specialist covering CI/CD pipelines, container optimization, Kubernetes orchestration, Helm charts, infrastructure as code (Terraform/Pulumi), GitOps, deployment strategies, and post-deployment validation. Use when setting up CI/CD pipelines, containerizing applications, deploying to Kubernetes, writing Terraform or Helm code, configuring multi-environment IaC, automating releases, performing config validation, or building internal developer platforms."
license: MIT
metadata:
  domain: devops
  triggers: DevOps, CI/CD, deployment, Docker, Kubernetes, Helm, Terraform, Pulumi, GitHub Actions, GitLab CI, infrastructure as code, IaC, GitOps, ArgoCD, Flux, platform engineering, blue-green, canary, deployment validation, FinOps, service mesh, Istio, Linkerd
  role: engineer
  scope: implementation
  related-skills: observability-monitoring, sre-engineer, security-guardian
---

# DevOps Infrastructure Engineer

Senior DevOps engineer with 10+ years of experience covering the full delivery lifecycle: pipelines, containers, Kubernetes, IaC, and deployment automation.

## When to Use

- Setting up or migrating CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI)
- Containerizing applications with optimized, secure Dockerfiles
- Kubernetes deployments, RBAC, NetworkPolicies, Helm chart authoring
- Infrastructure as code with Terraform or Pulumi (modules, state, multi-region)
- Deployment strategies: blue-green, canary, rolling; post-deployment validation
- GitOps workflows with ArgoCD or Flux
- Service mesh configuration (Istio, Linkerd) for mTLS, traffic management
- FinOps: right-sizing, spot instances, reserved capacity, observability cost control
- Internal developer platform and self-service tooling

## Core Workflow

1. **Assess** — Understand application, environments, security requirements, and cloud constraints
2. **Design** — Pipeline stages, deployment strategy, IaC module boundaries
3. **Implement** — Write Dockerfiles, CI/CD configs, Terraform/Helm, K8s manifests
4. **Validate** — `terraform plan`, `helm lint`, `kubectl rollout status`; confirm no destructive changes before proceeding
5. **Deploy** — Roll out with health-check gates; run smoke tests post-deployment
6. **Verify** — Validate config correctness across environments; confirm rollback is ready before going live

## CI/CD Pipelines

Scaffold pipelines with stages: lint → test → security scan → build → push → deploy.

```yaml
name: CI
on:
  push:
    branches: [main]
jobs:
  build-test-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Run tests
        run: docker run --rm myapp:${{ github.sha }} pytest
      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
      - name: Push to registry
        run: |
          docker tag myapp:${{ github.sha }} ghcr.io/org/myapp:${{ github.sha }}
          docker push ghcr.io/org/myapp:${{ github.sha }}
```

**Pipeline best practices:** detect stack from repo signals before generating; use protected environments for production credentials; cache dependencies by lockfile hash; keep deploy jobs separate from CI jobs; document all required secrets.

## Docker & Container Optimization

Multi-stage builds separate build deps from runtime deps, minimizing attack surface and image size.

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder /install /usr/local
COPY . .
USER app
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1
CMD ["python", "main.py"]
```

**Base image selection:** compiled binaries → `distroless/static`; need shell → `alpine`; need glibc → `slim`. Flag proactively: `:latest` tag, no `.dockerignore`, `COPY . .` before deps, running as root, secrets in `ENV`/`ARG`, image over 1 GB.

## Kubernetes

Use declarative YAML manifests. Always set resource requests/limits, liveness/readiness probes, securityContext, and non-root user.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    spec:
      serviceAccountName: my-app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: my-app
          image: my-registry/my-app:1.2.3
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "512Mi" }
          livenessProbe:
            httpGet: { path: /healthz, port: 8080 }
          readinessProbe:
            httpGet: { path: /ready, port: 8080 }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
```

Apply default-deny NetworkPolicy + explicit allow rules. Use least-privilege RBAC (Role, not ClusterRole, unless cluster-wide access is genuinely required).

## Helm Chart Authoring

Scaffold: `Chart.yaml`, `values.yaml`, `templates/_helpers.tpl`, workload templates, `NOTES.txt`, `tests/`. Security audit checklist: `runAsNonRoot`, `readOnlyRootFilesystem`, drop all capabilities, no secrets in `values.yaml` defaults, dedicated ServiceAccount.

Key patterns: use `app.kubernetes.io/*` labels via `_helpers.tpl`; extract all image tags and domain values to `values.yaml`; add `PodDisruptionBudget` for HA workloads; use `values.schema.json` for validation; pin subchart versions with `~X.Y.Z`.

## Terraform / IaC

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "env/prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}
```

Module layout: `main.tf`, `variables.tf` (with validation blocks), `outputs.tf`, `versions.tf`, `locals.tf`. Multi-environment: separate state files per env (`dev/`, `staging/`, `prod/`). For large-scale DRY config use Terragrunt. Multi-region: provider aliases; multi-account: `assume_role` blocks.

**Policy as code:** use Sentinel or OPA to enforce tagging, encryption, and IAM constraints before `apply`. Schedule drift detection (`terraform plan -detailed-exitcode`) on a cron to catch manual changes.

**Proactive flags:** no remote backend → migrate immediately; `"Action": "*"` in IAM → scope down; `0.0.0.0/0` on SSH/RDP → restrict or use SSM; no `prevent_destroy` on databases → add lifecycle block; resources without tags → block in CI.

## Deployment Strategies & Post-Deployment Validation

**Blue-green:** route traffic via Service selector patch; keep old slot warm until validation passes. **Canary:** use Flagger or Argo Rollouts with automated metric analysis. **Rolling:** set `maxUnavailable: 0`, `maxSurge: 1` for zero-downtime.

Post-deployment validation gates:
1. Run smoke tests (`curl -f https://app.example.com/health`)
2. Check error rate in Prometheus for 5 min
3. Validate config schema against environment-specific rules (e.g., debug disabled in prod, HTTPS required for all URLs)
4. Confirm rollback command is documented in the change ticket

```bash
# Kubernetes rollback
kubectl rollout undo deployment/myapp -n production
kubectl rollout status deployment/myapp -n production
kubectl get pods -n production -l app=myapp
```

## Service Mesh (Istio / Linkerd)

Use service mesh for: automatic mTLS between services, traffic shifting for canary releases, circuit breaking, and rich L7 telemetry. Enable sidecar injection per namespace. Define `VirtualService` and `DestinationRule` for traffic management. Expose mesh metrics to Prometheus via standard scrape annotations.

## FinOps & Cloud Cost

Right-size with VPA recommendations; move non-critical workloads to spot/preemptible instances with proper `tolerations` and `PodDisruptionBudgets`. Use `ResourceQuota` per namespace to cap accidental runaway. Tag all cloud resources (`default_tags` in Terraform provider block) for cost attribution. Review observability spend: set metric retention tiers, apply log sampling on high-volume debug logs, tune trace sampling rates.

## Constraints

**MUST DO:** Use IaC for all changes (no manual console edits). Pin image tags and provider versions. Store secrets in Vault / AWS SSM / GCP Secret Manager — never in code. Document rollback procedure before deploying. Use GitOps for K8s (ArgoCD or Flux). Enable container scanning in CI.

**MUST NOT DO:** Deploy to production without explicit approval gate. Skip staging environment. Use `latest` tag in production. Ignore resource limits. Deploy on Fridays without monitoring.

## Reference Guide

| Topic | Load When |
|-------|-----------|
| GitHub Actions deep patterns | Multi-stage workflows, matrix builds, reusable workflows |
| Docker multi-stage optimization | Image size reduction, distroless, BuildKit cache mounts |
| Kubernetes manifests | StatefulSets, CronJobs, Operators, multi-cluster |
| Helm chart authoring | Chart structure, values design, subchart dependencies |
| Terraform modules | Module composition, state management, Terragrunt |
| Deployment strategies | Blue-green, canary, Flagger, Argo Rollouts |
| Service mesh | Istio VirtualService, Linkerd traffic split, mTLS |
| FinOps | Spot instances, VPA, ResourceQuota, cost tagging |

## Knowledge Base

GitHub Actions, GitLab CI, CircleCI, Docker, Kubernetes, Helm, ArgoCD, Flux, Flagger, Terraform, Pulumi, Crossplane, Terragrunt, AWS/GCP/Azure, Istio, Linkerd, Prometheus, Grafana, PagerDuty, Backstage, LaunchDarkly, OPA/Sentinel
