# app/adapters/kafka/serializer.py
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any

from app.domain.events import DomainEvent


def _event_type(event: DomainEvent) -> str:
    return event.__class__.__name__


def serialize_event(event: DomainEvent) -> bytes:
    """
    Kafka payload 표준 형태(권장):
    {
      "event_type": "...",
      "version": 1,
      "occurred_at": "...iso8601...",
      "data": { ...event fields... }
    }
    """
    data: dict[str, Any]
    if is_dataclass(event):
        data = asdict(event)
    else:
        # fallback
        data = dict(event.__dict__)

    payload = {
        "event_type": _event_type(event),
        "version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
