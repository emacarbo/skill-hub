"""Conversion Intel MCP Server.

Self-hosted SaaS conversion intelligence. Tracks funnel events, runs
behavioral agents (Timing, Cohort, Churn), benchmarks against category
medians, and logs applied fixes for impact measurement.

Inspired by Voltaire — same patterns, fully open, no vendor lock-in.
"""
from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .agents import ChurnAgent, CohortAgent, TimingAgent
from .models import AppConfig, AppliedFix, ConversionMetrics, EventType, FunnelEvent
from .store import EventStore

DATA_DIR = Path(os.environ.get(
    "CONVERSION_INTEL_DATA",
    Path.home() / ".conversion-intel",
))

store = EventStore(DATA_DIR)
timing_agent = TimingAgent()
cohort_agent = CohortAgent()
churn_agent = ChurnAgent()

mcp = FastMCP(
    "conversion-intel",
    instructions="SaaS conversion intelligence — track funnels, analyze behavior, optimize conversion",
)

# ── Category benchmarks (expandable) ────────────────────────────────────────

BENCHMARKS = {
    "saas": {"cr_median": 3.2, "cr_top_quartile": 6.5, "churn_median": 5.0},
    "productivity": {"cr_median": 2.8, "cr_top_quartile": 5.5, "churn_median": 4.5},
    "media": {"cr_median": 1.5, "cr_top_quartile": 3.8, "churn_median": 7.0},
    "education": {"cr_median": 2.5, "cr_top_quartile": 5.0, "churn_median": 6.0},
    "gaming": {"cr_median": 2.0, "cr_top_quartile": 4.5, "churn_median": 8.0},
    "ecommerce": {"cr_median": 3.5, "cr_top_quartile": 7.0, "churn_median": 6.5},
}


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def create_app(name: str, category: str, platform: str = "web") -> dict:
    """Register a new app for conversion tracking.

    Categories: saas, productivity, media, education, gaming, ecommerce.
    Returns the app config.
    """
    config = AppConfig(name=name, category=category, platform=platform)
    store.create_app(config)
    return {
        "status": "created",
        "app": asdict(config),
        "next_step": "Start recording events with record_event or connect_payment_provider",
    }


@mcp.tool()
def get_stats(app_name: str) -> dict:
    """Get current state of an app — config, event counts, data health.

    Voltaire pattern: first tool to call, determines first-run vs recurring mode.
    """
    config = store.get_config(app_name)
    if config is None:
        return {"error": f"App '{app_name}' not found. Use create_app first."}

    events = store.get_events(app_name)
    now = datetime.now(timezone.utc)
    seven_days = now - timedelta(days=7)
    thirty_days = now - timedelta(days=30)

    event_counts = {}
    for e in events:
        t = e["event_type"]
        event_counts[t] = event_counts.get(t, 0) + 1

    recent_events = [e for e in events if e["timestamp"] >= seven_days.isoformat()]

    fixes = store.get_fixes(app_name)

    has_payment = config.payment_provider is not None
    has_sdk_events = event_counts.get(EventType.PAYWALL_SHOWN.value, 0) > 0

    return {
        "app": asdict(config),
        "mode": "recurring" if has_sdk_events else "first_run",
        "total_events": len(events),
        "events_7d": len(recent_events),
        "event_breakdown": event_counts,
        "payment_connected": has_payment,
        "sdk_installed": has_sdk_events,
        "fixes_applied": len(fixes),
        "last_fix": fixes[-1] if fixes else None,
        "data_health": "good" if len(events) > 100 else "thin" if len(events) > 10 else "empty",
    }


@mcp.tool()
def record_event(
    app_name: str,
    event_type: str,
    user_id: str,
    session_id: str,
    metadata: dict | None = None,
) -> dict:
    """Record a single funnel event.

    Event types: session_start, feature_used, feature_gate_hit,
    upgrade_clicked, paywall_shown, paywall_dismissed, paywall_converted,
    subscription_cancelled.
    """
    try:
        et = EventType(event_type)
    except ValueError:
        return {"error": f"Unknown event type: {event_type}. Valid: {[e.value for e in EventType]}"}

    event = FunnelEvent(
        event_type=et,
        timestamp=datetime.now(timezone.utc),
        user_id=user_id,
        session_id=session_id,
        metadata=metadata or {},
    )
    store.record_event(app_name, event)
    return {"status": "recorded", "event_type": event_type, "total": store.event_count(app_name)}


@mcp.tool()
def analyze_funnel(app_name: str, window_days: int = 30) -> dict:
    """Full conversion analysis — metrics, benchmarks, agent signals.

    Voltaire pattern: returns raw data. The calling agent reasons about it,
    synthesizes agent signals, and presents a diagnosis.
    """
    config = store.get_config(app_name)
    if config is None:
        return {"error": f"App '{app_name}' not found"}

    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    events = store.get_events(app_name, since=since)

    # Compute metrics
    sessions = len({e["session_id"] for e in events})
    shown = len([e for e in events if e["event_type"] == EventType.PAYWALL_SHOWN.value])
    dismissed = len([e for e in events if e["event_type"] == EventType.PAYWALL_DISMISSED.value])
    converted = len([e for e in events if e["event_type"] == EventType.PAYWALL_CONVERTED.value])
    gate_hits = len([e for e in events if e["event_type"] == EventType.FEATURE_GATE_HIT.value])
    upgrade_clicks = len([e for e in events if e["event_type"] == EventType.UPGRADE_CLICKED.value])

    cr_data_artifact = converted > shown
    cr = (converted / shown * 100) if shown > 0 and not cr_data_artifact else None
    funnel_reach = shown / sessions if sessions > 0 else 0.0

    metrics = ConversionMetrics(
        window_days=window_days,
        sessions=sessions,
        paywall_shown=shown,
        paywall_dismissed=dismissed,
        paywall_converted=converted,
        gate_hits=gate_hits,
        upgrade_clicks=upgrade_clicks,
        conversion_rate=round(cr, 2) if cr is not None else None,
        funnel_reach=round(funnel_reach, 3),
        bounce_rate_under_3s=None,  # needs timestamp analysis
        avg_dismiss_seconds=None,  # needs timestamp analysis
        cr_data_artifact=cr_data_artifact,
    )

    # Benchmarks
    category = config.category
    bench = BENCHMARKS.get(category, BENCHMARKS["saas"])
    benchmark = {
        "category": category,
        "cr_median": bench["cr_median"],
        "cr_top_quartile": bench["cr_top_quartile"],
        "gap_pp": round(cr - bench["cr_median"], 2) if cr is not None else None,
        "churn_median": bench["churn_median"],
    }

    # Run agents
    all_events = store.get_events(app_name)  # agents may need full history
    timing = timing_agent.analyze(all_events)
    cohort = cohort_agent.analyze(all_events)
    churn = churn_agent.analyze(all_events)

    # Trend (daily CR for the window)
    from collections import defaultdict
    daily: dict[str, dict[str, int]] = defaultdict(lambda: {"shown": 0, "converted": 0})
    for e in events:
        day = e["timestamp"][:10]
        if e["event_type"] == EventType.PAYWALL_SHOWN.value:
            daily[day]["shown"] += 1
        elif e["event_type"] == EventType.PAYWALL_CONVERTED.value:
            daily[day]["converted"] += 1

    trend = []
    for day in sorted(daily.keys()):
        d = daily[day]
        day_cr = (d["converted"] / d["shown"] * 100) if d["shown"] > 0 else 0
        trend.append({"date": day, "cr_pct": round(day_cr, 2), "paywall_views": d["shown"]})

    # Applied fixes
    fixes = store.get_fixes(app_name, limit=3)

    return {
        "app": {"name": config.name, "category": config.category, "platform": config.platform},
        "metrics": asdict(metrics),
        "benchmark": benchmark,
        "agents": {
            "timing": asdict(timing) if timing else None,
            "cohort": asdict(cohort) if cohort else None,
            "churn": asdict(churn) if churn else None,
        },
        "trend_daily": trend[-14:],  # last 14 days
        "applied_fixes": fixes,
    }


@mcp.tool()
def mark_applied(app_name: str, description: str, file_path: str) -> dict:
    """Log that a fix was applied. Enables before/after impact tracking.

    Voltaire pattern: every change is recorded so future runs have
    full historical context.
    """
    # Get current CR as the "before" baseline
    config = store.get_config(app_name)
    if config is None:
        return {"error": f"App '{app_name}' not found"}

    since = datetime.now(timezone.utc) - timedelta(days=7)
    events = store.get_events(app_name, since=since)
    shown = len([e for e in events if e["event_type"] == EventType.PAYWALL_SHOWN.value])
    converted = len([e for e in events if e["event_type"] == EventType.PAYWALL_CONVERTED.value])
    cr_before = (converted / shown * 100) if shown > 0 else None

    fix = AppliedFix(
        description=description,
        applied_at=datetime.now(timezone.utc),
        file_path=file_path,
        cr_before=round(cr_before, 2) if cr_before is not None else None,
        cr_after=None,  # filled on next analysis
        delta_pp=None,
    )
    store.record_fix(app_name, fix)

    return {
        "status": "logged",
        "fix": description,
        "cr_at_time_of_fix": cr_before,
        "note": "Run analyze_funnel after collecting more data to measure impact",
    }


@mcp.tool()
def list_apps() -> dict:
    """List all registered apps."""
    apps = store.list_apps()
    results = []
    for name in apps:
        config = store.get_config(name)
        if config:
            results.append({
                "name": config.name,
                "category": config.category,
                "platform": config.platform,
                "events": store.event_count(name),
            })
    return {"apps": results, "count": len(results)}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
