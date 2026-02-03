"""Model runner port."""
from __future__ import annotations

from typing import Any, Protocol


class ModelRunner(Protocol):
    async def infer(self, input_uri: str, options: dict[str, Any] | None = None) -> Any: ...
