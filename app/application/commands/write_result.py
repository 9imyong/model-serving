# app/application/commands/write_result.py
from __future__ import annotations

from dataclasses import dataclass

from app.application.dto import InferenceResultMessage
from app.application.policies import should_skip_write_result
from app.ports.repositories import JobRepository


@dataclass(slots=True)
class WriteResultUseCase:
    repo: JobRepository

    def execute(self, message: InferenceResultMessage) -> None:
        job = self.repo.get(message.job_id)
        if should_skip_write_result(job):
            return

        self.repo.save_result(job.id, message.result_payload or {})
        job.mark_succeeded()
        self.repo.save(job)
