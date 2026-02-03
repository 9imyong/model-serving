"""Domain events."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class JobCreated:
    job_id: str
    payload: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class InferenceCompleted:
    job_id: str
    result_payload: dict[str, Any] | None = None
