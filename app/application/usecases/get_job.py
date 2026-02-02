from __future__ import annotations

from dataclasses import dataclass

from app.ports.job_repository import JobRecord, JobRepository


@dataclass(slots=True)
class GetJobUseCase:
    """
    Query usecase (read model).
    - 지금 단계에서는 Domain 엔티티 없이 JobRecord만 반환
    """

    repo: JobRepository

    def execute(self, job_id: str) -> JobRecord:
        return self.repo.get(job_id)

