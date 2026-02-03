"""Application DTOs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.domain.job import JobStatus


# ---- Command input (API → Usecase) ----

@dataclass(frozen=True, slots=True)
class CreateJobDTO:
    model_name: str = "default"
    input_uri: str = ""
    options: dict[str, Any] | None = None


# ---- Command output (Usecase → API) ----

@dataclass(frozen=True, slots=True)
class CreateJobResponse:
    job_id: str
    status: JobStatus | str
    created_at: datetime | None = None


# ---- Kafka / Worker 메시지 ----

@dataclass(frozen=True, slots=True)
class JobMessage:
    """Kafka job-topic에서 받은 메시지."""
    job_id: str
    payload: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class InferenceResultMessage:
    """Result-topic 메시지 (Case3 writer consume)."""
    job_id: str
    result_payload: dict[str, Any] | None = None


# ---- Query output ----

@dataclass(frozen=True, slots=True)
class JobStatusResponse:
    job_id: str
    status: JobStatus | str
    input_uri: str = ""
    created_at: datetime | None = None
