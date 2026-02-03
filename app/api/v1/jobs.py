"""Jobs API v1."""
from fastapi import APIRouter

from app.api.v1.models import CreateJobRequest, CreateJobResponse, GetJobResponse
from app.application.commands.create_job import CreateJobUseCase
from app.application.queries.get_job import GetJobUseCase
from app.application.dto import CreateJobDTO
from app.adapters.inmemory.job_repository import InMemoryJobRepository

router = APIRouter()

# 임시 wiring (다음 단계에서 DI / container로 이동)
_repo = InMemoryJobRepository()
_create_job_uc = CreateJobUseCase(repo=_repo)
_get_job_uc = GetJobUseCase(repo=_repo)


@router.post("/jobs", status_code=201, response_model=CreateJobResponse)
def create_job(req: CreateJobRequest):
    """
    API 책임:
    - 요청 검증 (Pydantic)
    - DTO 변환
    - Usecase 호출
    - 응답 변환
    """
    dto = CreateJobDTO(input_uri=req.input_uri)
    job_id = _create_job_uc.execute(dto)

    return CreateJobResponse(job_id=job_id)


@router.get("/jobs/{job_id}", response_model=GetJobResponse)
def get_job(job_id: str):
    record = _get_job_uc.execute(job_id)
    return GetJobResponse(job_id=record.job_id, input_uri=record.input_uri)