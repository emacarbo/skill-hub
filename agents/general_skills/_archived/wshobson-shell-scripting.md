---
name: wshobson-shell-scripting
description: Defensive Bash scripting, Bats testing, and ShellCheck static analysis patterns
---

# Shell Scripting

Covers defensive Bash programming (strict mode, error trapping, safe file handling), Bats testing framework, and ShellCheck configuration for production-grade shell scripts.

## Key Patterns

- **Always strict mode** -- `set -Eeuo pipefail` at the top of every script
- **Quote all variables** -- `"$var"` prevents word splitting and globbing
- **Trap for cleanup** -- `trap 'rm -rf "$TMPDIR"' EXIT` ensures cleanup on any exit
- **Use `[[ ]]` over `[ ]`** -- safer, supports `&&`/`||` inside, regex matching
- **Validate inputs early** -- `[[ -f "$file" ]]` or `: "${REQUIRED_VAR:?not set}"`
- **Use `mktemp -d` for temp files** -- always clean up via EXIT trap
- **Design for idempotency** -- rerunning should be safe (check-then-create)
- **Support dry-run mode** -- wrap commands in a `run_cmd()` that prints instead of executing
- **Structured logging** -- `log_info`, `log_warn`, `log_error` with timestamps to stderr
- **Test with Bats** -- `@test` blocks, `setup`/`teardown`, mock external commands via PATH stubs

## Quick Reference

### Script template

```bash
#!/bin/bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
trap 'echo "Error on line $LINENO" >&2' ERR
trap 'rm -rf -- "$TMPDIR"' EXIT
TMPDIR=$(mktemp -d)

log_info()  { echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $*" >&2; }
log_error() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose) VERBOSE=true; shift ;;
        -o|--output)  OUTPUT="$2"; shift 2 ;;
        -h|--help)    echo "Usage: $0 [-v] -o FILE"; exit 0 ;;
        *)            log_error "Unknown option: $1"; exit 1 ;;
    esac
done

: "${OUTPUT:?-o/--output is required}"

log_info "Starting"
# ... script body ...
```

### Bats test template

```bash
#!/usr/bin/env bats

setup() {
    export TMPDIR=$(mktemp -d)
    source "${BATS_TEST_DIRNAME}/../bin/script.sh"
}

teardown() { rm -rf "$TMPDIR"; }

@test "succeeds with valid input" {
    run my_function "valid"
    [ "$status" -eq 0 ]
}

@test "fails with missing argument" {
    run my_function
    [ "$status" -ne 0 ]
    [[ "$output" == *"ERROR"* ]]
}
```

### ShellCheck .shellcheckrc

```
shell=bash
enable=avoid-nullary-conditions,require-variable-braces
disable=SC1091
```

### Top ShellCheck fixes

| Code   | Issue                        | Fix                                  |
|--------|------------------------------|--------------------------------------|
| SC2086 | Unquoted variable            | `"$var"` instead of `$var`           |
| SC2181 | Indirect exit code check     | `if cmd; then` instead of `if [ $? ]`|
| SC2015 | `&&`/`||` instead of if-else | Use explicit `if/then/else/fi`       |
| SC2009 | `grep` on `ps` output        | Use `pgrep -f pattern`               |

## When to Use

- Writing production automation or deployment scripts
- Building CI/CD pipeline shell steps
- Setting up Bats test suites for shell utilities
- Configuring ShellCheck linting in pre-commit hooks or CI
- Creating portable, error-resilient system administration tools
