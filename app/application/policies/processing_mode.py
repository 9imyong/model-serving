# app/application/commands/create_job.py
from __future__ import annotations

from dataclasses import dataclass

from app.application.dto import CreateJobDTO, CreateJobResponse
from app.application.errors import ConflictError
from app.core.id_generator import generate_job_id
from app.domain.events import JobCreated
from app.domain.job import Job
from app.ports.event_bus import EventBus
from app.ports.repositories import JobRepository


@dataclass(slots=True)
class CreateJobUseCase:
    repo: JobRepository
    event_bus: EventBus

    def execute(self, dto: CreateJobDTO) -> CreateJobResponse:
        job_id = generate_job_id()
        job = Job.create(job_id, input_uri=dto.input_uri, model_name=dto.model_name)

        # ✅ exists 체크 대신 "저장"에서 멱등성 보장 (DB UNIQUE + DuplicateKeyError 권장)
        try:
            self.repo.save(job)
        except Exception as e:
            # repo에서 DuplicateKeyError 같은 명확한 예외로 올리게 만드는 게 베스트
            raise ConflictError("job already exists for this input_uri", source="repo_exists") from e

        self.event_bus.publish(
            JobCreated(
                job_id=job_id,
                payload={"input_uri": dto.input_uri, "model_name": dto.model_name},
            )
        )

        return CreateJobResponse(
            job_id=job_id,
            status=job.status,
            created_at=job.created_at,
        )
