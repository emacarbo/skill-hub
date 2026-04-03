"""Skill Hub MCP Server.

Exposes skill lifecycle operations as MCP tools so agents can programmatically
evaluate, promote, sync, and discover skills.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP

SKILL_HUB_ROOT = Path(os.environ.get(
    "SKILL_HUB_ROOT",
    Path.home() / "dev" / "skill-hub",
))

mcp = FastMCP(
    "skill-hub",
    instructions="Skill lifecycle management — eval, promote, sync, discover, stats",
)


def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _save_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)


def _manifest() -> dict:
    return _load_yaml(SKILL_HUB_ROOT / "manifest.yaml")


def _stack_context() -> dict:
    return _load_yaml(SKILL_HUB_ROOT / "stack-context.yaml")


def _consolidation_map() -> dict:
    return _load_yaml(SKILL_HUB_ROOT / "agents" / "general_skills" / "consolidation-map.yaml")


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def get_stats() -> dict:
    """Get overall skill library health stats.

    Returns counts by status, total skills, last updated date,
    cluster count, and standalone count.
    """
    manifest = _manifest()
    skills = manifest.get("skills", [])

    status_counts: dict[str, int] = {}
    for s in skills:
        st = s.get("status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    cmap = _consolidation_map()
    clusters = cmap.get("clusters", [])
    standalones = cmap.get("standalones", [])

    general_skills_dir = SKILL_HUB_ROOT / "agents" / "general_skills"
    skill_files = list(general_skills_dir.glob("*.md"))
    lifecycle_files = [f for f in skill_files if f.name.startswith("skill-")]
    content_files = [f for f in skill_files if not f.name.startswith("skill-")]

    return {
        "total_manifest_entries": len(skills),
        "status_breakdown": status_counts,
        "cluster_count": len(clusters),
        "standalone_count": len(standalones),
        "general_skills_files": len(content_files),
        "lifecycle_skills": len(lifecycle_files),
        "manifest_updated": manifest.get("updated"),
        "skill_hub_root": str(SKILL_HUB_ROOT),
    }


@mcp.tool()
def eval_skill(skill_name: str) -> dict:
    """Evaluate a staged skill against the active tech stack.

    Checks if the skill's tags match any active_tags in stack-context.yaml.
    Returns relevance score, matching tags, and recommendation.
    """
    stack = _stack_context()
    active_tags = set(stack.get("active_tags", []))

    # Find skill in staging
    staging_dir = SKILL_HUB_ROOT / "skill-lifecycle" / "staging"
    skill_path = None
    for p in staging_dir.rglob("SKILL.md"):
        if skill_name in str(p):
            skill_path = p
            break

    if skill_path is None:
        return {"error": f"Skill '{skill_name}' not found in staging/"}

    content = skill_path.read_text()

    # Check manifest for existing entry
    manifest = _manifest()
    existing = next((s for s in manifest.get("skills", []) if s["name"] == skill_name), None)

    # Simple tag matching from content
    matched_tags = []
    for tag in active_tags:
        if tag.lower() in content.lower():
            matched_tags.append(tag)

    relevance = len(matched_tags) / max(len(active_tags), 1)

    if relevance >= 0.1:
        recommendation = "promote"
    else:
        recommendation = "reject"

    return {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "matched_tags": matched_tags,
        "relevance_score": round(relevance, 2),
        "recommendation": recommendation,
        "already_in_manifest": existing is not None,
        "active_tags_checked": sorted(active_tags),
    }


@mcp.tool()
def check_staleness(days_threshold: int = 30) -> dict:
    """Check for stale skills that haven't been updated recently.

    Returns skills whose date_updated is older than days_threshold.
    Also checks for skills in manifest that are missing from disk.
    """
    manifest = _manifest()
    now = datetime.now(timezone.utc)
    stale = []
    missing_on_disk = []

    general_dir = SKILL_HUB_ROOT / "agents" / "general_skills"

    for skill in manifest.get("skills", []):
        name = skill.get("name", "")
        status = skill.get("status", "")

        if status in ("rejected", "consolidated"):
            continue

        updated = skill.get("date_updated")
        if updated:
            try:
                updated_date = datetime.fromisoformat(updated).replace(tzinfo=timezone.utc)
                age_days = (now - updated_date).days
                if age_days > days_threshold:
                    stale.append({
                        "name": name,
                        "status": status,
                        "last_updated": updated,
                        "age_days": age_days,
                    })
            except (ValueError, TypeError):
                pass

        # Check if agent-ready skills exist on disk
        if status == "agent-ready":
            expected_path = general_dir / f"{name}.md"
            if not expected_path.exists():
                missing_on_disk.append(name)

    stale.sort(key=lambda x: x["age_days"], reverse=True)

    return {
        "threshold_days": days_threshold,
        "stale_skills": stale[:20],
        "stale_count": len(stale),
        "missing_on_disk": missing_on_disk,
        "missing_count": len(missing_on_disk),
    }


@mcp.tool()
def discover_gaps() -> dict:
    """Analyze the skill library for coverage gaps.

    Compares active stack tags against skills that cover each tag.
    Identifies tags with thin or no coverage.
    """
    stack = _stack_context()
    active_tags = stack.get("active_tags", [])
    manifest = _manifest()

    tag_coverage: dict[str, list[str]] = {tag: [] for tag in active_tags}

    for skill in manifest.get("skills", []):
        if skill.get("status") in ("rejected",):
            continue
        tags = skill.get("tech_stack_tags", [])
        name = skill.get("name", "")
        for tag in tags:
            if tag in tag_coverage:
                tag_coverage[tag].append(name)

    gaps = []
    thin = []
    well_covered = []

    for tag, skills in tag_coverage.items():
        if len(skills) == 0:
            gaps.append(tag)
        elif len(skills) <= 2:
            thin.append({"tag": tag, "skills": skills, "count": len(skills)})
        else:
            well_covered.append({"tag": tag, "count": len(skills)})

    return {
        "uncovered_tags": gaps,
        "thin_coverage": thin,
        "well_covered": well_covered,
        "total_active_tags": len(active_tags),
    }


@mcp.tool()
def get_consolidation_map() -> dict:
    """Get the full consolidation map — clusters, sources, blind spots.

    Returns the relationship contract between promoted skills and
    their consolidated targets.
    """
    cmap = _consolidation_map()
    clusters = cmap.get("clusters", [])
    standalones = cmap.get("standalones", [])

    summary = []
    for c in clusters:
        summary.append({
            "target": c["target_name"],
            "source_count": len(c.get("sources", [])),
            "blind_spots": c.get("blind_spots", []),
            "keep_separate": c.get("keep_separate", []),
        })

    return {
        "cluster_count": len(clusters),
        "standalone_count": len(standalones),
        "clusters": summary,
        "standalones": [s if isinstance(s, str) else s.get("name", str(s)) for s in standalones],
    }


@mcp.tool()
def search_skills(query: str) -> dict:
    """Search skills by name or description.

    Searches across manifest entries and general_skills files on disk.
    """
    manifest = _manifest()
    query_lower = query.lower()

    matches = []
    for skill in manifest.get("skills", []):
        name = skill.get("name", "")
        desc = skill.get("description", "")
        if query_lower in name.lower() or query_lower in desc.lower():
            matches.append({
                "name": name,
                "description": desc,
                "status": skill.get("status"),
                "consolidated_into": skill.get("consolidated_into"),
            })

    return {
        "query": query,
        "match_count": len(matches),
        "matches": matches[:20],
    }


@mcp.tool()
def mark_skill_used(skill_name: str, agent: str = "claude") -> dict:
    """Record that a skill was used today.

    Updates last_used in manifest.yaml for tracking activity.
    """
    manifest = _manifest()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for skill in manifest.get("skills", []):
        if skill.get("name") == skill_name:
            last_used = skill.get("last_used", {})
            last_used[agent] = today
            skill["last_used"] = last_used
            _save_yaml(SKILL_HUB_ROOT / "manifest.yaml", manifest)
            return {"skill": skill_name, "agent": agent, "marked": today}

    return {"error": f"Skill '{skill_name}' not found in manifest"}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
