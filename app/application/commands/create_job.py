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
from app.ports.idempotency import IdempotencyGate


@dataclass(slots=True)
class CreateJobUseCase:
    repo: JobRepository
    event_bus: EventBus
    idem_gate: IdempotencyGate
    async def execute(self, dto: CreateJobDTO) -> CreateJobResponse:
        job_id = generate_job_id()
        # input_uri 없으면 멱등성 스킵(정책)
        if not dto.input_uri:
            job = Job.create(job_id, input_uri=None, model_name=dto.model_name)
            await self.repo.save(job)
            await self.event_bus.publish(JobCreated(job_id=job_id, payload={"model_name": dto.model_name}))
            return CreateJobResponse(job_id=job_id, status=job.status, created_at=job.created_at)
        # 1) 보조 멱등성 게이트 (InMemory/Redis 공통)
        reserved = await self.idem_gate.reserve(dto.input_uri, job_id)
        if not reserved:
            raise ConflictError("job already exists for this input_uri", source="idem_gate")
        # 2) 저장
        job = Job.create(job_id, input_uri=dto.input_uri, model_name=dto.model_name)
        await self.repo.save(job)
        # 3) 이벤트 발행
        await self.event_bus.publish(
            JobCreated(job_id=job_id, payload={"input_uri": dto.input_uri, "model_name": dto.model_name}),
        )
        return CreateJobResponse(job_id=job_id, status=job.status, created_at=job.created_at)
