# app/application/queries/get_job_status.py
from __future__ import annotations

from dataclasses import dataclass

from app.application.dto import JobStatusResponse
from app.ports.repositories import JobRepository


@dataclass(slots=True)
class GetJobStatusUseCase:
    repo: JobRepository

    def execute(self, job_id: str) -> JobStatusResponse:
        job = self.repo.get(job_id)
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            input_uri=job.input_uri,
            created_at=job.created_at,
        )
