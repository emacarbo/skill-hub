#!/usr/bin/env python3
"""Generate a structural wiki from token-savior's index.

Usage:
    token-savior-wiki.py <project_root> [--full]

Produces .context/wiki/ with:
    index.md      — catalog of all articles
    overview.md   — architecture, high-impact files, dependency flow
    <topic>.md    — per-topic articles (api, database, models, etc.)
    .wiki-meta.json — metadata for staleness detection
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Token-savior imports (pure Python, no MCP)
from token_savior.project_indexer import ProjectIndexer
from token_savior.query_api import create_project_query_functions

# --- Topic mapping -----------------------------------------------------------

TOPIC_MAP = {
    "api": ["api", "routes", "endpoints", "routers", "handlers"],
    "data-model": ["schemas", "entities", "domain"],
    "auth": ["auth", "security", "permissions", "middleware"],
    "testing": ["tests", "test", "__tests__", "spec", "fixtures"],
    "config": ["config", "settings"],
    "services": ["services", "usecases", "use_cases"],
    "frontend": ["ui", "components", "pages", "layouts", "hooks"],
    "database": ["db", "migrations", "alembic", "prisma"],
    "jobs": ["jobs", "workers", "queues", "celery", "dags"],
    "dbt-layers": ["staging", "intermediate", "marts", "contracts", "snapshots", "macros"],
    "models": ["models"],
}

# Directories to exclude from wiki (non-source, tooling, generated)
EXCLUDE_DIRS = {
    ".claude", ".github", ".planning", ".git", "node_modules",
    "__pycache__", ".venv", "dist", "build", "target",
    "dbt_packages", "dbt_internal_packages",
}

MIN_FILES_FOR_TOPIC = 3


def git_head(project_root: str) -> str:
    """Get current git HEAD SHA."""
    try:
        return subprocess.check_output(
            ["git", "-C", project_root, "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def git_short(rev: str) -> str:
    return rev[:8] if rev != "unknown" else rev


def is_excluded(filepath: str) -> bool:
    """Check if a file is in an excluded directory."""
    parts = Path(filepath).parts
    return any(p in EXCLUDE_DIRS for p in parts)


def is_source_file(filepath: str) -> bool:
    """Check if a file is a source file (not a standalone config/doc at root)."""
    p = Path(filepath)
    # Root-level non-source files
    if len(p.parts) == 1:
        return p.suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".go", ".rs"}
    return True


def classify_files(files: list[str]) -> dict[str, list[str]]:
    """Group files into topic buckets by directory patterns."""
    topics: dict[str, list[str]] = defaultdict(list)
    uncategorized: list[str] = []

    # Filter to source files in non-excluded directories
    source_files = [f for f in files if not is_excluded(f) and is_source_file(f)]

    for f in source_files:
        parts = Path(f).parts
        matched = False
        # Check all path components against topic patterns
        for topic, dirs in TOPIC_MAP.items():
            if any(d in parts for d in dirs):
                topics[topic].append(f)
                matched = True
                break
        if not matched:
            uncategorized.append(f)

    # If "models" and "dbt-layers" both matched, merge dbt-layers into models
    # (dbt projects have models/staging, models/marts — both match)
    if "models" in topics and "dbt-layers" in topics:
        topics["dbt-layers"].extend(topics.pop("models"))
    elif "models" in topics:
        # Rename to something more descriptive if dbt dirs are inside models/
        model_files = topics["models"]
        has_dbt_subdirs = any(
            d in Path(f).parts for f in model_files
            for d in ("staging", "intermediate", "marts", "contracts")
        )
        if has_dbt_subdirs:
            topics["dbt-layers"] = topics.pop("models")

    # Filter out topics with too few files
    result = {t: fs for t, fs in topics.items() if len(fs) >= MIN_FILES_FOR_TOPIC}

    # Merge uncategorized into "other" if substantial
    if len(uncategorized) >= MIN_FILES_FOR_TOPIC:
        result["other"] = uncategorized

    return result


def get_top_files_by_dependents(
    files: list[str],
    fns: dict,
    limit: int = 10,
) -> list[tuple[str, int]]:
    """Rank files by number of dependents (most depended-on first)."""
    ranked = []
    for f in files:
        try:
            deps = fns["get_file_dependents"](file_path=f)
            ranked.append((f, len(deps)))
        except Exception:
            ranked.append((f, 0))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:limit]


def build_overview(
    project_root: str,
    summary: str,
    files: list[str],
    topics: dict[str, list[str]],
    fns: dict,
    git_rev: str,
) -> str:
    """Build overview.md content."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short = git_short(git_rev)

    # Structure table — only real directories, exclude noise
    dir_counts: dict[str, int] = defaultdict(int)
    for f in files:
        p = Path(f)
        if len(p.parts) < 2:
            continue  # Skip root-level files
        top = p.parts[0]
        if top in EXCLUDE_DIRS:
            continue
        dir_counts[top] += 1
    top_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    structure_rows = "\n".join(
        f"| {d}/ | {c} |" for d, c in top_dirs if c > 0
    )

    # High-impact files — only source files, not tooling/config
    source_only = [f for f in files if not is_excluded(f) and is_source_file(f)]
    high_impact = get_top_files_by_dependents(source_only, fns, limit=10)
    impact_rows = "\n".join(
        f"| {f} | {n} |" for f, n in high_impact if n > 0
    )

    # Extract key stats from summary
    stats_line = ""
    for line in summary.split("\n"):
        if line.startswith("Files:"):
            stats_line = line
            break

    lines = [
        f"<!-- generated: {today} | rev: {short} -->",
        "",
        "# Project Overview",
        "",
        f"**Root:** `{project_root}`",
        f"**Stats:** {stats_line}" if stats_line else "",
        "",
        "## Structure",
        "",
        "| Directory | Files |",
        "|-----------|-------|",
        structure_rows,
        "",
        "## High-Impact Files",
        "",
        "| File | Dependents |",
        "|------|-----------|",
        impact_rows if impact_rows else "| (no dependency data) | — |",
        "",
        "## Topics",
        "",
        "| Topic | Files | Article |",
        "|-------|-------|---------|",
    ]

    for topic, topic_files in sorted(topics.items()):
        lines.append(f"| {topic} | {len(topic_files)} | [{topic}.md]({topic}.md) |")

    return "\n".join(lines) + "\n"


def build_topic_article(
    topic: str,
    topic_files: list[str],
    fns: dict,
    git_rev: str,
) -> str:
    """Build a topic article."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short = git_short(git_rev)

    # Key files with dependents
    ranked = get_top_files_by_dependents(topic_files, fns, limit=10)

    lines = [
        f"<!-- generated: {today} | rev: {short} -->",
        "",
        f"# {topic.replace('-', ' ').title()}",
        "",
        f"**Files:** {len(topic_files)}",
        "",
        "## Key Files",
        "",
        "| File | Dependents |",
        "|------|-----------|",
    ]

    for f, n in ranked:
        lines.append(f"| {f} | {n} |")

    # Functions and classes in top files
    top_files = [f for f, _ in ranked[:5]]

    all_funcs = []
    all_classes = []
    for f in top_files:
        try:
            all_funcs.extend(fns["get_functions"](file_path=f, max_results=20))
        except Exception:
            pass
        try:
            all_classes.extend(fns["get_classes"](file_path=f, max_results=20))
        except Exception:
            pass

    if all_classes:
        lines.extend([
            "",
            "## Classes",
            "",
            "| Class | File | Methods |",
            "|-------|------|---------|",
        ])
        for c in all_classes[:15]:
            methods = ", ".join(c.get("methods", [])[:5])
            if len(c.get("methods", [])) > 5:
                methods += f" (+{len(c['methods']) - 5})"
            lines.append(f"| {c['name']} | {c.get('file', '')} | {methods} |")

    if all_funcs:
        lines.extend([
            "",
            "## Functions",
            "",
            "| Function | File | Params |",
            "|----------|------|--------|",
        ])
        for fn in all_funcs[:20]:
            params = ", ".join(fn.get("params", []))
            lines.append(f"| {fn['name']} | {fn.get('file', '')} | ({params}) |")

    # Imports / dependencies for top files
    deps_lines = []
    for f in top_files[:3]:
        try:
            file_deps = fns["get_file_dependencies"](file_path=f, max_results=10)
            if file_deps:
                deps_lines.append(f"- **{f}** → {', '.join(file_deps[:5])}")
        except Exception:
            pass

    if deps_lines:
        lines.extend([
            "",
            "## Dependencies",
            "",
        ] + deps_lines)

    return "\n".join(lines) + "\n"


def build_index(
    topics: dict[str, list[str]],
    git_rev: str,
    project_name: str,
) -> str:
    """Build index.md catalog."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short = git_short(git_rev)

    lines = [
        f"<!-- generated: {today} | rev: {short} -->",
        "",
        f"# Wiki Index — {project_name}",
        "",
        "| Article | Covers | Files |",
        "|---------|--------|-------|",
        "| [overview](overview.md) | Architecture, high-impact files, structure | — |",
    ]

    for topic, topic_files in sorted(topics.items()):
        lines.append(f"| [{topic}]({topic}.md) | {topic.replace('-', ' ').title()} | {len(topic_files)} |")

    lines.extend([
        "",
        f"Last built: {today} | Git: {short}",
        "Stale? Run `/token-savior-wiki` to regenerate.",
    ])

    return "\n".join(lines) + "\n"


def write_meta(
    wiki_dir: Path,
    git_rev: str,
    project_name: str,
    topics: dict[str, list[str]],
    articles: list[str],
) -> None:
    """Write .wiki-meta.json for staleness detection."""
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_rev": git_rev,
        "project": project_name,
        "articles": articles,
        "topics": {
            topic: {"files": files, "status": "generated"}
            for topic, files in topics.items()
        },
    }
    (wiki_dir / ".wiki-meta.json").write_text(json.dumps(meta, indent=2) + "\n")


def ensure_gitignore(project_root: Path) -> None:
    """Add .context/wiki/ to .gitignore if not present."""
    gitignore = project_root / ".gitignore"
    marker = ".context/wiki/"
    if gitignore.exists():
        content = gitignore.read_text()
        if marker in content:
            return
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n# Generated codebase wiki\n{marker}\n"
        gitignore.write_text(content)
    else:
        gitignore.write_text(f"# Generated codebase wiki\n{marker}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project_root> [--full]")
        sys.exit(1)

    project_root = sys.argv[1]
    force_full = "--full" in sys.argv

    root_path = Path(project_root).resolve()
    if not root_path.is_dir():
        print(f"Error: {project_root} is not a directory")
        sys.exit(1)

    project_name = root_path.name
    wiki_dir = root_path / ".context" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)

    git_rev = git_head(project_root)
    meta_file = wiki_dir / ".wiki-meta.json"

    # Incremental check
    skip_topics: set[str] = set()
    if not force_full and meta_file.exists():
        old_meta = json.loads(meta_file.read_text())
        old_rev = old_meta.get("git_rev", "")
        if old_rev == git_rev:
            print(f"Wiki is up to date (rev {git_short(git_rev)}). Use --full to force.")
            return
        # Find changed files since last build
        try:
            changed_output = subprocess.check_output(
                ["git", "-C", project_root, "diff", "--name-only", old_rev, "HEAD"],
                text=True, stderr=subprocess.DEVNULL,
            )
            changed_files = set(changed_output.strip().split("\n")) if changed_output.strip() else set()
        except subprocess.CalledProcessError:
            changed_files = None  # Can't diff — do full rebuild

        if changed_files is not None:
            old_topics = old_meta.get("topics", {})
            for topic, info in old_topics.items():
                topic_files = set(info.get("files", []))
                if not topic_files & changed_files:
                    skip_topics.add(topic)

    # Index the project
    print(f"Indexing {project_name}...")
    indexer = ProjectIndexer(project_root)
    index = indexer.index()
    fns = create_project_query_functions(index)

    # Gather data
    summary = fns["get_project_summary"]()
    all_files = fns["list_files"]()

    # Filter to source files only
    source_files = [f for f in all_files if not is_excluded(f)]

    # Classify into topics
    topics = classify_files(source_files)
    articles = ["index.md", "overview.md"]

    # Write overview (always regenerated)
    print("Writing overview.md...")
    overview = build_overview(project_root, summary, source_files, topics, fns, git_rev)
    (wiki_dir / "overview.md").write_text(overview)

    # Write topic articles
    for topic, topic_files in sorted(topics.items()):
        if topic in skip_topics:
            print(f"Skipping {topic}.md (no changes)")
            articles.append(f"{topic}.md")
            continue
        print(f"Writing {topic}.md ({len(topic_files)} files)...")
        article = build_topic_article(topic, topic_files, fns, git_rev)
        (wiki_dir / f"{topic}.md").write_text(article)
        articles.append(f"{topic}.md")

    # Write index
    print("Writing index.md...")
    index_content = build_index(topics, git_rev, project_name)
    (wiki_dir / "index.md").write_text(index_content)

    # Write metadata
    write_meta(wiki_dir, git_rev, project_name, topics, articles)

    # Remove stale flag
    stale = wiki_dir / ".stale"
    if stale.exists():
        stale.unlink()

    # Ensure .gitignore
    ensure_gitignore(root_path)

    # Report
    skipped = len(skip_topics)
    generated = len(articles) - 2 - skipped  # minus index + overview
    print(f"\nWiki generated for {project_name}")
    print(f"  Articles: {len(articles)} ({generated} generated, {skipped} skipped, 2 always rebuilt)")
    print(f"  Git rev: {git_short(git_rev)}")
    print(f"  Path: .context/wiki/")


if __name__ == "__main__":
    main()
