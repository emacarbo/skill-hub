---
name: python-core
description: "Comprehensive Python 3.11+ specialist covering type-safe code, async patterns, testing, packaging, performance, and project scaffolding. Use when building Python applications, designing async systems, writing pytest suites, optimizing bottlenecks, choosing a web or CLI framework, or designing Pydantic multi-model contracts."
license: MIT
metadata:
  domain: language
  triggers: Python, type hints, mypy, pytest, async, asyncio, Pydantic, packaging, performance, FastAPI, Django, Flask, Click, Typer, structlog, cProfile, dataclasses, Poetry
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fastapi-expert, devops-engineer
---

# Python Core

Modern Python 3.11+ specialist. Type-safe, async-first, production-ready.

## When to Use

- Writing type-annotated Python with full mypy strict coverage
- Implementing async/await for I/O-bound operations
- Setting up pytest suites with fixtures, mocking, and parametrize
- Creating or distributing packages (Poetry / uv / pyproject.toml)
- Profiling and optimizing CPU or memory bottlenecks
- Choosing between FastAPI, Django, Flask, Click, or Typer
- Designing Pydantic multi-model patterns for API contracts
- Configuring structured logging with structlog

## Core Workflow

1. **Analyze** — Review project structure, type coverage, test suite, dependencies
2. **Design interfaces** — Protocols, Pydantic models, dataclasses, type aliases
3. **Implement** — Pythonic code: full type hints, error handling, no bare excepts
4. **Test** — pytest suite >90% coverage; async tests via pytest-asyncio
5. **Validate** — `mypy --strict`, `ruff check --fix`, `black`; all must be green

## Framework Selection

```
What are you building?
├── API-first / Microservices  → FastAPI (async, Pydantic, uvicorn)
├── Full-stack / CMS / Admin   → Django (batteries-included, ORM)
├── Simple script / Learning   → Flask (minimal) or plain script
├── CLI tool                   → Typer (Click-based, type hints native)
└── Background workers         → Celery / ARQ + any framework
```

Ask before defaulting: Is this API-only or full-stack? Does the team know async?
Need admin UI? Existing infrastructure constraints?

## Async vs Sync Decision

```
async def  — I/O-bound: database, HTTP, file, real-time, microservices
def (sync) — CPU-bound, simple scripts, blocking-only libraries

Golden rule: I/O-bound → async | CPU-bound → sync + multiprocessing
Never mix sync blocking calls inside async coroutines.
```

| Need | Async Library |
|------|---------------|
| HTTP client | `httpx` |
| PostgreSQL | `asyncpg` |
| Redis | `redis-py` (async mode) |
| File I/O | `aiofiles` |
| ORM | SQLAlchemy 2.0 async, Tortoise |

## Type System

MUST annotate: function parameters, return types, class attributes, public APIs.
Can skip: local variables (let inference work), one-off scripts.

```python
# Python 3.10+ union syntax
def find_user(id: int) -> User | None: ...

# Generic collections (no import needed 3.9+)
def get_items() -> list[Item]: ...
def get_mapping() -> dict[str, int]: ...

# Protocol for structural subtyping
from typing import Protocol
class Closeable(Protocol):
    def close(self) -> None: ...
```

**mypy strict config (pyproject.toml):**
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
disallow_untyped_defs = true
```
Any `mypy --strict` error must be resolved before the implementation is complete.

## Pydantic Multi-Model Pattern

One resource → five models, each with a distinct contract:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    """POST body — required fields only."""
    workspace_id: str = Field(..., alias="workspaceId")
    class Config:
        populate_by_name = True

class ProjectUpdate(BaseModel):
    """PATCH body — all fields optional."""
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    """API response with computed fields."""
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    class Config:
        populate_by_name = True

class ProjectInDB(ProjectResponse):
    """DB document — adds doc_type for Cosmos/Mongo queries."""
    doc_type: str = "project"
```

## Async Deep-Dive

### Concurrency primitives
```python
import asyncio

# gather — fan-out, all must succeed (or use return_exceptions=True)
results = await asyncio.gather(*[fetch(url) for url in urls])

# TaskGroup (Python 3.11+) — structured concurrency, auto-cancels on error
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(url1))
    t2 = tg.create_task(fetch(url2))

# Semaphore — rate-limit concurrency
sem = asyncio.Semaphore(10)
async with sem:
    await api_call(url)

# Queue — producer/consumer backpressure
queue: asyncio.Queue[str] = asyncio.Queue(maxsize=50)
```

### Cancellation (always re-raise)
```python
async def cancelable():
    try:
        await long_running_io()
    except asyncio.CancelledError:
        await cleanup()
        raise  # must propagate
```

### Blocking code in async context
```python
import asyncio, concurrent.futures

async def run_blocking(fn, *args):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, fn, *args)
```

### Pitfalls
- Forgot `await` → returns coroutine object, nothing executes
- `time.sleep()` in async → blocks the event loop; use `asyncio.sleep()`
- CPU work in async → offload to `ProcessPoolExecutor`

## Testing Patterns

### Fixtures and parametrize
```python
import pytest
from pathlib import Path

@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.ini"
    cfg.write_text("host=localhost\nport=8080\n")
    return cfg

@pytest.mark.parametrize("port,valid", [(8080, True), (0, False), (99999, False)])
def test_port_validation(port: int, valid: bool) -> None:
    if valid:
        AppConfig(host="localhost", port=port)
    else:
        with pytest.raises(ValueError):
            AppConfig(host="localhost", port=port)
```

### Async tests
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint(app) -> None:
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/users")
    assert r.status_code == 200
```

### Mocking
```python
from unittest.mock import patch, Mock

def test_service_calls_api() -> None:
    mock_resp = Mock()
    mock_resp.json.return_value = {"id": 1}
    mock_resp.raise_for_status.return_value = None
    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = fetch_user(1)
    assert result["id"] == 1
    mock_get.assert_called_once()
```

### Property-based (Hypothesis)
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_reverse_twice_is_identity(s: str) -> None:
    assert s[::-1][::-1] == s
```

### Coverage
```bash
pytest --cov=myapp --cov-report=term-missing --cov-fail-under=80
```

### pytest.ini (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--strict-markers", "--tb=short"]
markers = ["slow", "integration", "unit", "e2e"]
```

## Performance Optimization

**Profile first — never optimize blindly.**

```bash
python -m cProfile -o out.prof script.py   # CPU profile
py-spy record -o profile.svg -- python script.py  # flamegraph, prod-safe
python -m memory_profiler script.py        # line-level memory
```

Key patterns:
- List comprehensions / generators over explicit loops
- `dict` / `set` for O(1) membership vs O(n) list search
- `"".join(parts)` over `+=` string concatenation
- `functools.lru_cache` / `functools.cache` for pure functions
- `__slots__` when creating millions of instances
- `multiprocessing.Pool` for CPU-bound parallelism
- `asyncio` / `httpx` async for I/O-bound concurrency
- `tracemalloc` + `gc` to detect memory leaks

## CLI Frameworks

| Need | Tool |
|------|------|
| Type-hint-native, modern | **Typer** (wraps Click, auto-generates help) |
| Maximum flexibility / plugins | **Click** |
| Simple single-command script | `argparse` (stdlib) |

```python
# Typer example
import typer

app = typer.Typer()

@app.command()
def ingest(path: str, verbose: bool = False) -> None:
    """Ingest data from PATH."""
    if verbose:
        typer.echo(f"Ingesting {path}")

if __name__ == "__main__":
    app()
```

## Logging / Observability

Prefer **structlog** over stdlib `logging` for machine-readable JSON logs in production.

```python
import structlog

log = structlog.get_logger()

def process_order(order_id: str) -> None:
    log.info("order.processing", order_id=order_id)
    try:
        result = do_work(order_id)
        log.info("order.done", order_id=order_id, result=result)
    except Exception as exc:
        log.error("order.failed", order_id=order_id, error=str(exc))
        raise
```

**structlog configuration (structlog + stdlib bridge):**
```python
import logging, structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

## Project Structure

```
# Medium API (FastAPI)
app/
├── main.py           # app factory, lifespan
├── api/              # route handlers (thin)
├── services/         # business logic
├── models/           # SQLAlchemy / Pydantic models
├── schemas/          # request/response schemas
├── dependencies/     # shared FastAPI Depends()
└── core/             # config, logging, exceptions
tests/
├── conftest.py
├── unit/
└── integration/
pyproject.toml
```

## Packaging (Poetry / uv)

```toml
# pyproject.toml
[tool.poetry]
name = "myapp"
version = "0.1.0"
python = "^3.11"

[tool.poetry.dependencies]
pydantic = "^2.0"
structlog = "^24.0"

[tool.poetry.dev-dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
mypy = "^1.8"
ruff = "^0.4"
black = "^24.0"
hypothesis = "^6.0"
```

```bash
# uv (faster alternative)
uv init myapp && cd myapp
uv add pydantic structlog
uv add --dev pytest mypy ruff
```

## Constraints

### MUST DO
- Type hints on all function signatures and class attributes
- `X | None` instead of `Optional[X]` (Python 3.10+)
- Dataclasses over manual `__init__` for plain data containers
- Context managers (`with` / `async with`) for all resources
- Google-style docstrings on public functions
- Comprehensive error handling — no bare `except:`
- Async/await for all I/O-bound work

### MUST NOT DO
- Skip type annotations on public APIs
- Use mutable default arguments (`def f(items=[])`)
- Mix sync blocking calls inside `async def`
- Ignore `mypy --strict` errors
- Use deprecated modules (`os.path` → `pathlib`)
- Hardcode secrets or configuration values
- Print-based logging in production code (use structlog)

## Output Checklist

When delivering Python implementations provide:
1. Module file with complete type hints (mypy strict-clean)
2. Test file with pytest fixtures and >90% coverage
3. Confirmation `mypy --strict` passes
4. Brief note on Pythonic patterns applied
