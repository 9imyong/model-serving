# app/application/commands/process_job.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.application.dto import JobMessage
from app.application.policies import ProcessingMode, should_skip_processing
from app.domain.events import InferenceCompleted
from app.domain.job import JobStatus
from app.ports.event_bus import EventBus
from app.ports.model_runner import ModelRunner
from app.ports.repositories import JobRepository


@dataclass(slots=True)
class ProcessJobUseCase:
    repo: JobRepository
    model_runner: ModelRunner
    event_bus: EventBus
    processing_mode: ProcessingMode = ProcessingMode.STANDARD

    def execute(self, message: JobMessage) -> None:
        job = self.repo.get(message.job_id)
        if should_skip_processing(job):
            return

        job.mark_running()
        self.repo.save(job)

        try:
            result = self.model_runner.infer(
                job.input_uri or "",
                options=message.payload or {},
            )
        except Exception:
            job.mark_failed()
            self.repo.save(job)
            raise

        if self.processing_mode is ProcessingMode.STANDARD:
            self.repo.save_result(job.id, result)
            job.mark_succeeded()
            self.repo.save(job)
        elif self.processing_mode is ProcessingMode.WRITER_SPLIT:
            self.event_bus.publish(
                InferenceCompleted(job_id=job.id, result_payload=_to_payload(result)),
            )
            job.mark_inferred()
            self.repo.save(job)
        else:
            self.repo.save_result(job.id, result)
            job.mark_succeeded()
            self.repo.save(job)


def _to_payload(result: Any) -> dict:
    if isinstance(result, dict):
        return result
    return {"result": result}
