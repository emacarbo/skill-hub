"""Data models for conversion intelligence."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    """Tracked funnel events."""
    SESSION_START = "session_start"
    FEATURE_USED = "feature_used"
    FEATURE_GATE_HIT = "feature_gate_hit"
    UPGRADE_CLICKED = "upgrade_clicked"
    PAYWALL_SHOWN = "paywall_shown"
    PAYWALL_DISMISSED = "paywall_dismissed"
    PAYWALL_CONVERTED = "paywall_converted"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"


class AgentSignal(str, Enum):
    """Confidence levels for agent signals."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient_data"


@dataclass(frozen=True)
class FunnelEvent:
    """A single tracked event."""
    event_type: EventType
    timestamp: datetime
    user_id: str
    session_id: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ConversionMetrics:
    """Computed conversion metrics for a time window."""
    window_days: int
    sessions: int
    paywall_shown: int
    paywall_dismissed: int
    paywall_converted: int
    gate_hits: int
    upgrade_clicks: int
    conversion_rate: float | None  # None if data artifact
    funnel_reach: float  # shown / sessions
    bounce_rate_under_3s: float | None
    avg_dismiss_seconds: float | None
    cr_data_artifact: bool  # converted > shown


@dataclass(frozen=True)
class Benchmark:
    """Industry benchmark for a category."""
    category: str
    metric: str
    median: float
    top_quartile: float
    gap_pp: float  # gap vs median in percentage points


@dataclass(frozen=True)
class TimingSignal:
    """Output from the Timing Agent."""
    signal: str
    confidence: AgentSignal
    explanation: str
    recommendation: str
    estimated_impact_pp: float | None


@dataclass(frozen=True)
class CohortSignal:
    """Output from the Cohort Agent."""
    key_differentiator: str
    pattern: str
    recommendation: str
    confidence: AgentSignal


@dataclass(frozen=True)
class ChurnSignal:
    """Output from the Churn Agent."""
    signal: str
    confidence: AgentSignal
    mrr_cents: int
    active_subs: int
    churn_rate_30d: float
    mrr_growth_rate: float
    explanation: str
    recommendation: str


@dataclass(frozen=True)
class AppliedFix:
    """Record of a fix that was applied."""
    description: str
    applied_at: datetime
    file_path: str
    cr_before: float | None
    cr_after: float | None
    delta_pp: float | None


@dataclass
class AppConfig:
    """Application configuration."""
    name: str
    category: str  # e.g. "productivity", "media", "education", "saas"
    platform: str  # e.g. "web", "mobile", "desktop"
    payment_provider: str | None = None  # "stripe", "paddle", "lemonsqueezy", None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
