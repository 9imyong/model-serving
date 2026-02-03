from __future__ import annotations

from typing import Any

from app.domain.errors import JobNotFound
from app.domain.job import Job, JobStatus
from app.ports.repositories import JobRepository


def _job_to_store(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "status": job.status,
        "input_uri": job.input_uri,
        "model_name": job.model_name,
        "created_at": job.created_at,
    }


def _store_to_job(data: dict[str, Any]) -> Job:
    return Job(
        id=data["id"],
        status=JobStatus(data["status"]) if isinstance(data["status"], str) else data["status"],
        input_uri=data.get("input_uri", ""),
        model_name=data.get("model_name", "default"),
        created_at=data.get("created_at"),
    )


class InMemoryJobRepository(JobRepository):
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._results: dict[str, Any] = {}
        self._input_uris: set[str] = set()

    def save(self, job: Job) -> None:
        is_new = job.id not in self._jobs
        self._jobs[job.id] = _job_to_store(job)
        if is_new and job.input_uri:
            self._input_uris.add(job.input_uri)

    def get(self, job_id: str) -> Job:
        data = self._jobs.get(job_id)
        if data is None:
            raise JobNotFound()
        return _store_to_job(data)

    def exists_by_input_uri(self, input_uri: str) -> bool:
        return input_uri in self._input_uris

    def save_result(self, job_id: str, result: Any) -> None:
        self._results[job_id] = result
