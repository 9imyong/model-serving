from __future__ import annotations

import uuid
from app.domain.errors import JobNotFound
from app.ports.repositories import JobRecord, JobRepository


class InMemoryJobRepository(JobRepository):
    def __init__(self):
        self._jobs: dict[str, str] = {}

    def exists_by_input_uri(self, input_uri: str) -> bool:
        return input_uri in self._jobs.values()

    def create(self, input_uri: str) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = input_uri
        return job_id

    def get(self, job_id: str) -> JobRecord:
        input_uri = self._jobs.get(job_id)
        if input_uri is None:
            raise JobNotFound()
        return JobRecord(job_id=job_id, input_uri=input_uri)
