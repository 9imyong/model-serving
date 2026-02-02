"""Jobs API v1."""
from fastapi import APIRouter

from app.api.v1.models import CreateJobRequest, CreateJobResponse
from app.application.usecases.create_job import CreateJobUseCase
from app.application.dtos import CreateJobDTO
from app.adapters.inmemory.job_repository import InMemoryJobRepository

router = APIRouter()

# 임시 wiring (다음 단계에서 DI / container로 이동)
_repo = InMemoryJobRepository()
_create_job_uc = CreateJobUseCase(repo=_repo)


@router.post("/jobs", response_model=CreateJobResponse, status_code=201)
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