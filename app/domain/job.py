"""Job domain."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.domain.errors import InvalidJobState


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass(slots=True)
class Job:
    """
    Light DDD:
    - 상태 전이 + 불변조건만 가진다.
    - 외부(HTTP/DB/Kafka) 개념 금지.
    """

    id: str
    status: JobStatus = JobStatus.PENDING

    def start(self) -> None:
        if self.status is not JobStatus.PENDING:
            raise InvalidJobState(f"cannot start job from status={self.status}")
        self.status = JobStatus.RUNNING

    def complete(self) -> None:
        if self.status is not JobStatus.RUNNING:
            raise InvalidJobState(f"cannot complete job from status={self.status}")
        self.status = JobStatus.SUCCEEDED

    def fail(self) -> None:
        if self.status not in (JobStatus.PENDING, JobStatus.RUNNING):
            raise InvalidJobState(f"cannot fail job from status={self.status}")
        self.status = JobStatus.FAILED

