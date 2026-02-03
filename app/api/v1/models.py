"""Models API v1."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    model_name: str = "default"
    input_uri: str = ""
    options: dict | None = None


class CreateJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime | None = None


class GetJobResponse(BaseModel):
    job_id: str
    status: str
    input_uri: str = ""
    created_at: datetime | None = None
