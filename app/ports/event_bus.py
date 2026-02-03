# app/ports/event_bus.py
from __future__ import annotations

from typing import Protocol
from app.domain.events import DomainEvent


class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
