# app/ports/idempotency.py
from __future__ import annotations
from typing import Protocol

class IdempotencyGate(Protocol):
    async def reserve(self, input_uri: str, job_id: str) -> bool: ...
    async def get(self, input_uri: str) -> str | None: ...
