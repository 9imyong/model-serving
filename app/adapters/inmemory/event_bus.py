"""In-memory event bus (no-op / stub for dev without Kafka)."""
from __future__ import annotations

from typing import Any


class InMemoryEventBus:
    def publish(self, event: Any) -> None:
        pass  # no-op; replace with Kafka adapter when wiring
