from __future__ import annotations

from typing import Protocol


class JobRepository(Protocol):
    def exists_by_input_uri(self, input_uri: str) -> bool: ...
    def create(self, input_uri: str) -> str: ...
