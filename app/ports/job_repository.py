# app/ports/job_repository.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class JobRecord:
    """
    Persistence/Adapter 레벨의 최소 레코드.
    - 지금 단계에서는 Domain 엔티티(Job) 없이 스모크 조회를 위한 형태만 제공
    """

    job_id: str
    input_uri: str


class JobRepository(Protocol):
    def exists_by_input_uri(self, input_uri: str) -> bool: ...
    def create(self, input_uri: str) -> str: ...
    def get(self, job_id: str) -> JobRecord: ...
