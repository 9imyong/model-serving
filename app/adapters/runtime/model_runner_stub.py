"""Stub model runner (no GPU)."""
from __future__ import annotations

from typing import Any

from app.ports.model_runner import ModelRunner


class StubModelRunner(ModelRunner):
    def infer(self, input_uri: str, options: dict[str, Any] | None = None) -> Any:
        return {"stub": True, "input_uri": input_uri, "options": options or {}}
