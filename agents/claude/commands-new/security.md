---
description: Security audit — threat modeling, dependency scanning, secret detection, OWASP review.
---

# /security — Security Audit

Read the **security-guardian** skill from `~/dev/skill-hub/agents/general_skills/security-guardian.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `scan` | Full scan | SAST + dependency audit + secret detection |
| `secrets` | Secret scan | Find hardcoded secrets, tokens, API keys |
| `deps` | Dependency audit | CVE scan with severity and fix recommendations |
| `threat <feature>` | Threat model | STRIDE analysis for a feature or system |
| `review <file>` | Code review | Security-focused review of specific file |
| *(no args)* | Quick scan | Secret detection + dependency audit |

## Output

```
SECURITY REPORT: [MODE]

Secrets:       [OK / X found]
Dependencies:  [X critical, Y high, Z medium]
SAST:          [X issues]
Compliance:    [checklist status]

[If issues: severity-sorted list with fix recommendations]
```
