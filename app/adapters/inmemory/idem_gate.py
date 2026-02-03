# app/adapters/inmemory/idem_gate.py
from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass


def _idem_key(input_uri: str) -> str:
    return hashlib.sha256(input_uri.encode("utf-8")).hexdigest()

@dataclass(slots=True)
class InMemoryIdemGate:
    _lock: asyncio.Lock = asyncio.Lock()
    _store: dict[str, str] = None  # type: ignore[assignment]
    def __post_init__(self) -> None:
        if self._store is None:
            self._store = {}
    async def reserve(self, input_uri: str, job_id: str) -> bool:
        k = _idem_key(input_uri)
        async with self._lock:
            if k in self._store:
                return False
            self._store[k] = job_id
            return True

    async def get(self, input_uri: str) -> str | None:
        return self._store.get(_idem_key(input_uri))
