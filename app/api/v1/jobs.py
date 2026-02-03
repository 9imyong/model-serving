"""Jobs API v1."""
# app/api/v1/jobs.py
from fastapi import APIRouter

from app.api.v1.models import CreateJobRequest, CreateJobResponse, GetJobResponse
from app.application.dto import CreateJobDTO
from app.application.commands.create_job import CreateJobUseCase
from app.application.queries.get_job_status import GetJobStatusUseCase
from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.adapters.inmemory.idem_gate import InMemoryIdemGate
router = APIRouter()

# 임시 wiring (다음 단계에서 DI / container로 이동)
_repo = InMemoryJobRepository()
_event_bus = InMemoryEventBus()
_idem_gate = InMemoryIdemGate()
_create_job_uc = CreateJobUseCase(repo=_repo, event_bus=_event_bus, idem_gate=_idem_gate)
_get_job_status_uc = GetJobStatusUseCase(repo=_repo)

@router.post("/jobs", status_code=201, response_model=CreateJobResponse)
async def create_job(req: CreateJobRequest):
    dto = CreateJobDTO(
        model_name=req.model_name,
        input_uri=req.input_uri,
        options=req.options,
    )

    # ✅ usecase가 async이면 await
    out = await _create_job_uc.execute(dto)

    # ✅ response model은 await 하지 않음
    return CreateJobResponse(
        job_id=out.job_id,
        status=out.status.value if hasattr(out.status, "value") else str(out.status),
        created_at=out.created_at,
    )


@router.get("/jobs/{job_id}", response_model=GetJobResponse)
async def get_job(job_id: str):
    out = await _get_job_status_uc.execute(job_id)

    return GetJobResponse(
        job_id=out.job_id,
        status=out.status.value if hasattr(out.status, "value") else str(out.status),
        input_uri=out.input_uri,
        created_at=out.created_at,
    )
