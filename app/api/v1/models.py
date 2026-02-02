"""Models API v1."""
from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    input_uri: str


class CreateJobResponse(BaseModel):
    job_id: str


class GetJobResponse(BaseModel):
    job_id: str
    input_uri: str
