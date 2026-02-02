from __future__ import annotations

import uuid
from app.ports.job_repository import JobRepository


class InMemoryJobRepository(JobRepository):
    def __init__(self):
        self._jobs: dict[str, str] = {}

    def exists_by_input_uri(self, input_uri: str) -> bool:
        return input_uri in self._jobs.values()

    def create(self, input_uri: str) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = input_uri
        return job_id
