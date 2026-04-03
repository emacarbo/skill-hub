"""Intelligence agents — Timing, Cohort, Churn.

Each agent analyzes a specific dimension of conversion behavior.
The server synthesizes their outputs into a unified diagnosis.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from .models import (
    AgentSignal,
    ChurnSignal,
    CohortSignal,
    ConversionMetrics,
    EventType,
    TimingSignal,
)


class TimingAgent:
    """Determines if the paywall fires before users experience core value.

    Needs ~10 paywall_shown events for a reliable signal.
    """

    MIN_EVENTS = 10

    def analyze(self, events: list[dict]) -> TimingSignal | None:
        paywall_events = [e for e in events if e["event_type"] == EventType.PAYWALL_SHOWN.value]

        if len(paywall_events) < self.MIN_EVENTS:
            return TimingSignal(
                signal="insufficient_data",
                confidence=AgentSignal.INSUFFICIENT,
                explanation=f"Need {self.MIN_EVENTS} paywall events, have {len(paywall_events)}",
                recommendation="Collect more data before analysis",
                estimated_impact_pp=None,
            )

        # Analyze: how many feature_used events happen before paywall_shown per session
        session_feature_counts: dict[str, int] = defaultdict(int)
        session_paywall_time: dict[str, str] = {}

        for e in events:
            sid = e["session_id"]
            if e["event_type"] == EventType.FEATURE_USED.value:
                if sid not in session_paywall_time:
                    session_feature_counts[sid] += 1
            elif e["event_type"] == EventType.PAYWALL_SHOWN.value:
                session_paywall_time[sid] = e["timestamp"]

        sessions_with_paywall = set(session_paywall_time.keys())
        features_before = [session_feature_counts.get(s, 0) for s in sessions_with_paywall]

        if not features_before:
            return None

        avg_features_before = sum(features_before) / len(features_before)
        zero_feature_sessions = sum(1 for f in features_before if f == 0)
        zero_pct = zero_feature_sessions / len(features_before)

        if zero_pct > 0.5:
            return TimingSignal(
                signal="too_early",
                confidence=AgentSignal.HIGH if zero_pct > 0.7 else AgentSignal.MEDIUM,
                explanation=f"{zero_pct:.0%} of sessions hit paywall with 0 feature interactions. "
                            f"Average features before paywall: {avg_features_before:.1f}",
                recommendation="Move paywall trigger to after first meaningful feature interaction",
                estimated_impact_pp=round(zero_pct * 2, 1),  # rough heuristic
            )

        if avg_features_before > 10:
            return TimingSignal(
                signal="possibly_late",
                confidence=AgentSignal.LOW,
                explanation=f"Users interact with {avg_features_before:.1f} features before seeing paywall. "
                            "They may already be getting full value without converting.",
                recommendation="Consider moving paywall earlier in the value curve",
                estimated_impact_pp=None,
            )

        return TimingSignal(
            signal="timing_ok",
            confidence=AgentSignal.MEDIUM,
            explanation=f"Users see {avg_features_before:.1f} features before paywall. Timing appears reasonable.",
            recommendation="Timing is not the bottleneck — investigate other factors",
            estimated_impact_pp=None,
        )


class CohortAgent:
    """Compares converter behavior against non-converters.

    Needs ~10 paywall sessions to produce a signal.
    """

    MIN_SESSIONS = 10

    def analyze(self, events: list[dict]) -> CohortSignal | None:
        # Group events by session
        sessions: dict[str, list[dict]] = defaultdict(list)
        for e in events:
            sessions[e["session_id"]].append(e)

        if len(sessions) < self.MIN_SESSIONS:
            return CohortSignal(
                key_differentiator="insufficient_data",
                pattern=f"Need {self.MIN_SESSIONS} sessions, have {len(sessions)}",
                recommendation="Collect more data",
                confidence=AgentSignal.INSUFFICIENT,
            )

        # Split into converters vs non-converters
        converters: list[str] = []
        non_converters: list[str] = []

        for sid, evts in sessions.items():
            types = {e["event_type"] for e in evts}
            if EventType.PAYWALL_CONVERTED.value in types:
                converters.append(sid)
            elif EventType.PAYWALL_SHOWN.value in types:
                non_converters.append(sid)

        if len(converters) < 3:
            return CohortSignal(
                key_differentiator="insufficient_conversions",
                pattern=f"Only {len(converters)} conversions — need at least 3 for comparison",
                recommendation="Collect more conversion data",
                confidence=AgentSignal.INSUFFICIENT,
            )

        # Compare feature usage patterns
        def feature_set(session_ids: list[str]) -> Counter:
            features: Counter = Counter()
            for sid in session_ids:
                for e in sessions[sid]:
                    if e["event_type"] == EventType.FEATURE_USED.value:
                        feat = e.get("metadata", {}).get("feature", "unknown")
                        features[feat] += 1
            return features

        converter_features = feature_set(converters)
        non_converter_features = feature_set(non_converters)

        # Find features disproportionately used by converters
        all_features = set(converter_features.keys()) | set(non_converter_features.keys())
        differentiators = []

        for feat in all_features:
            c_rate = converter_features.get(feat, 0) / max(len(converters), 1)
            nc_rate = non_converter_features.get(feat, 0) / max(len(non_converters), 1)
            if c_rate > nc_rate * 1.5 and converter_features.get(feat, 0) >= 2:
                differentiators.append((feat, c_rate, nc_rate))

        differentiators.sort(key=lambda x: x[1] - x[2], reverse=True)

        if differentiators:
            top = differentiators[0]
            return CohortSignal(
                key_differentiator=top[0],
                pattern=f"Converters use '{top[0]}' at {top[1]:.1f}x/session vs {top[2]:.1f}x for non-converters",
                recommendation=f"Guide users to '{top[0]}' before showing paywall — it correlates with conversion",
                confidence=AgentSignal.HIGH if len(converters) >= 10 else AgentSignal.MEDIUM,
            )

        return CohortSignal(
            key_differentiator="none_found",
            pattern="No clear feature differentiates converters from non-converters",
            recommendation="Investigate pricing, copy, or external factors instead of feature gating",
            confidence=AgentSignal.LOW,
        )


class ChurnAgent:
    """Tracks subscription health — MRR, churn rate, retention.

    Reads from tracked subscription events. Does not require external API
    by default; can be extended with Stripe integration.
    """

    def analyze(self, events: list[dict]) -> ChurnSignal | None:
        conversions = [e for e in events if e["event_type"] == EventType.PAYWALL_CONVERTED.value]
        cancellations = [e for e in events if e["event_type"] == EventType.SUBSCRIPTION_CANCELLED.value]

        if len(conversions) < 3:
            return ChurnSignal(
                signal="insufficient_data",
                confidence=AgentSignal.INSUFFICIENT,
                mrr_cents=0,
                active_subs=0,
                churn_rate_30d=0.0,
                mrr_growth_rate=0.0,
                explanation=f"Only {len(conversions)} conversions tracked — need subscription data",
                recommendation="Connect payment provider or track subscription events",
            )

        # Estimate active subs and churn
        active = len(conversions) - len(cancellations)
        active = max(active, 0)

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        thirty_days_ago_str = thirty_days_ago.isoformat()

        recent_cancellations = [c for c in cancellations if c["timestamp"] >= thirty_days_ago_str]
        recent_conversions = [c for c in conversions if c["timestamp"] >= thirty_days_ago_str]

        churn_rate = len(recent_cancellations) / max(active + len(recent_cancellations), 1)
        growth_rate = (len(recent_conversions) - len(recent_cancellations)) / max(active, 1)

        # Estimate MRR from metadata if available
        mrr_cents = 0
        for c in conversions:
            amount = c.get("metadata", {}).get("amount_cents", 0)
            mrr_cents += amount

        if churn_rate > 0.1:
            signal = "high_churn"
            confidence = AgentSignal.HIGH
            explanation = f"Churn rate {churn_rate:.1%}/month — {len(recent_cancellations)} cancellations in 30d"
            recommendation = "Investigate why users cancel — survey, session replay, or cohort analysis"
        elif churn_rate > 0.05:
            signal = "moderate_churn"
            confidence = AgentSignal.MEDIUM
            explanation = f"Churn rate {churn_rate:.1%}/month — within normal range but worth monitoring"
            recommendation = "Set up churn alerts and consider retention campaigns"
        else:
            signal = "healthy"
            confidence = AgentSignal.MEDIUM
            explanation = f"Churn rate {churn_rate:.1%}/month — healthy retention"
            recommendation = "Churn is not the bottleneck — focus on acquisition and conversion"

        return ChurnSignal(
            signal=signal,
            confidence=confidence,
            mrr_cents=mrr_cents,
            active_subs=active,
            churn_rate_30d=round(churn_rate, 4),
            mrr_growth_rate=round(growth_rate, 4),
            explanation=explanation,
            recommendation=recommendation,
        )
