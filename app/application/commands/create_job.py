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

    async def execute(self, dto: CreateJobDTO) -> CreateJobResponse:
        if dto.input_uri and await self.repo.exists_by_input_uri(dto.input_uri):
            raise ConflictError("job already exists for this input_uri")

        job_id = generate_job_id()
        job = Job.create(job_id, input_uri=dto.input_uri, model_name=dto.model_name)

        await self.repo.save(job)
        await self.event_bus.publish(
            JobCreated(job_id=job_id, payload={"input_uri": dto.input_uri, "model_name": dto.model_name}),
        )

        return CreateJobResponse(
            job_id=job_id,
            status=job.status,
            created_at=job.created_at,
        )
