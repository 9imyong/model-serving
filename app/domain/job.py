"""Job domain."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.domain.errors import InvalidJobState


class JobStatus(str, Enum):
    PENDING = "PENDING"      # created
    RUNNING = "RUNNING"      # worker started
    INFERRED = "INFERRED"    # Case3: GPU inference 완료 (writer가 저장 후 SUCCEEDED)
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
    input_uri: str = ""
    model_name: str = "default"
    created_at: datetime | None = None

    @staticmethod
    def create(job_id: str, *, input_uri: str = "", model_name: str = "default") -> Job:
        return Job(
            id=job_id,
            status=JobStatus.PENDING,
            input_uri=input_uri,
            model_name=model_name,
            created_at=datetime.now(timezone.utc),
        )

    def mark_running(self) -> None:
        if self.status is not JobStatus.PENDING:
            raise InvalidJobState(f"cannot start job from status={self.status}")
        self.status = JobStatus.RUNNING

    def mark_succeeded(self) -> None:
        if self.status not in (JobStatus.RUNNING, JobStatus.INFERRED):
            raise InvalidJobState(f"cannot complete job from status={self.status}")
        self.status = JobStatus.SUCCEEDED

    def mark_inferred(self) -> None:
        if self.status is not JobStatus.RUNNING:
            raise InvalidJobState(f"cannot mark inferred from status={self.status}")
        self.status = JobStatus.INFERRED

    def mark_failed(self) -> None:
        if self.status not in (JobStatus.PENDING, JobStatus.RUNNING):
            raise InvalidJobState(f"cannot fail job from status={self.status}")
        self.status = JobStatus.FAILED

    # 별칭 (기존/테스트 호환)
    def start(self) -> None:
        self.mark_running()

    def complete(self) -> None:
        self.mark_succeeded()

    def fail(self) -> None:
        self.mark_failed()
