"""Event bus port."""
from __future__ import annotations

from typing import Any, Protocol


class EventBus(Protocol):
    def publish(self, event: Any) -> None: ...
