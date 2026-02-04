"""GetJobStatusUseCase 테스트."""
from __future__ import annotations

import pytest

from app.application.queries.get_job_status import GetJobStatusUseCase
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.domain.job import Job, JobStatus
from app.domain.errors import JobNotFound


@pytest.fixture
def repo():
    return InMemoryJobRepository()


@pytest.fixture
def get_job_status_uc(repo):
    return GetJobStatusUseCase(repo=repo)


@pytest.mark.asyncio
async def test_get_job_status(get_job_status_uc, repo):
    job = Job.create("job-1", input_uri="s3://b/k", model_name="m1")
    await repo.save(job)
    out = await get_job_status_uc.execute("job-1")
    assert out.job_id == "job-1"
    assert out.status == JobStatus.PENDING
    assert out.input_uri == "s3://b/k"
    assert out.created_at is not None


@pytest.mark.asyncio
async def test_get_job_status_not_found(get_job_status_uc):
    with pytest.raises(JobNotFound):
        await get_job_status_uc.execute("nonexistent")
