# app/application/usecases/create_job.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.application.dtos import CreateJobDTO
from app.application.errors import ConflictError
from app.ports.job_repository import JobRepository

# ---- Ports (minimal, temporary placement)

@dataclass(slots=True)
class CreateJobUseCase:
    """
    Usecase = 시스템의 행동 단위
    - HTTP 모름
    - ORM 모름
    - 외부 의존성은 Port로 주입
    """
    repo: JobRepository

    def execute(self, dto: CreateJobDTO) -> str:
        """
        최소 구현:
        - 동일 input_uri 중복 생성 방지 예시
        - job_id 반환 (지금 단계에서는 도메인 Job을 아직 만들기 전이라 id만 반환)
        """
        if self.repo.exists_by_input_uri(dto.input_uri):
            raise ConflictError("job already exists for this input_uri")

        job_id = self.repo.create(dto.input_uri)
        return job_id
