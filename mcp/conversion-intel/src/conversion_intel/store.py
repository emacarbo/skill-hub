"""Event store — local JSON-based storage for self-hosted operation.

Stores events, config, and applied fixes in a single JSON file per app.
Production-ready alternative: swap this for PostgreSQL or SQLite.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import AppConfig, AppliedFix, EventType, FunnelEvent


class EventStore:
    """File-based event store for conversion tracking."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _app_file(self, app_name: str) -> Path:
        safe_name = app_name.lower().replace(" ", "-")
        return self._data_dir / f"{safe_name}.json"

    def _load(self, app_name: str) -> dict:
        path = self._app_file(app_name)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {"config": None, "events": [], "fixes": []}

    def _save(self, app_name: str, data: dict) -> None:
        path = self._app_file(app_name)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create_app(self, config: AppConfig) -> None:
        data = self._load(config.name)
        data["config"] = asdict(config)
        self._save(config.name, data)

    def get_config(self, app_name: str) -> AppConfig | None:
        data = self._load(app_name)
        cfg = data.get("config")
        if cfg is None:
            return None
        return AppConfig(**{k: v for k, v in cfg.items() if k != "created_at"}, created_at=datetime.fromisoformat(cfg["created_at"]))

    def list_apps(self) -> list[str]:
        return [p.stem for p in self._data_dir.glob("*.json")]

    def record_event(self, app_name: str, event: FunnelEvent) -> None:
        data = self._load(app_name)
        data["events"].append(asdict(event))
        self._save(app_name, data)

    def record_events_batch(self, app_name: str, events: list[FunnelEvent]) -> int:
        data = self._load(app_name)
        for e in events:
            data["events"].append(asdict(e))
        self._save(app_name, data)
        return len(events)

    def get_events(
        self,
        app_name: str,
        since: datetime | None = None,
        event_type: EventType | None = None,
    ) -> list[dict]:
        data = self._load(app_name)
        events = data.get("events", [])

        if since:
            since_str = since.isoformat()
            events = [e for e in events if e["timestamp"] >= since_str]

        if event_type:
            events = [e for e in events if e["event_type"] == event_type.value]

        return events

    def record_fix(self, app_name: str, fix: AppliedFix) -> None:
        data = self._load(app_name)
        data["fixes"].append(asdict(fix))
        self._save(app_name, data)

    def get_fixes(self, app_name: str, limit: int = 5) -> list[dict]:
        data = self._load(app_name)
        fixes = data.get("fixes", [])
        return fixes[-limit:]

    def event_count(self, app_name: str) -> int:
        data = self._load(app_name)
        return len(data.get("events", []))
