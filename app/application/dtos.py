"""Application DTOs."""
# app/application/dtos.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CreateJobDTO:
    """
    내부(Application)에서 사용하는 DTO.
    - Pydantic 금지 (경계(api)에서만 사용)
    """
    input_uri: str
