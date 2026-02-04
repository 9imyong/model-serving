"""CreateJobUseCase 테스트."""
from __future__ import annotations

import pytest

from app.application.commands.create_job import CreateJobUseCase
from app.application.dto import CreateJobDTO
from app.application.errors import ConflictError
from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.adapters.inmemory.idem_gate import InMemoryIdemGate
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.domain.events import JobCreated
from app.domain.job import JobStatus


@pytest.fixture
def repo():
    return InMemoryJobRepository()


@pytest.fixture
def event_bus():
    return InMemoryEventBus()


@pytest.fixture
def idem_gate():
    return InMemoryIdemGate()


@pytest.fixture
def create_job_uc(repo, event_bus, idem_gate):
    return CreateJobUseCase(repo=repo, event_bus=event_bus, idem_gate=idem_gate)


@pytest.mark.asyncio
async def test_create_job_without_input_uri(create_job_uc, repo, event_bus):
    dto = CreateJobDTO(model_name="default", input_uri="")
    out = await create_job_uc.execute(dto)
    assert out.job_id
    assert out.status == JobStatus.PENDING
    assert out.created_at is not None
    job = await repo.get(out.job_id)
    assert job.id == out.job_id
    assert job.input_uri == ""
    events = event_bus.events
    assert len(events) == 1
    assert isinstance(events[0], JobCreated)
    assert events[0].job_id == out.job_id


@pytest.mark.asyncio
async def test_create_job_with_input_uri(create_job_uc, repo, event_bus):
    dto = CreateJobDTO(model_name="ocr", input_uri="s3://b/k")
    out = await create_job_uc.execute(dto)
    assert out.job_id
    job = await repo.get(out.job_id)
    assert job.input_uri == "s3://b/k"
    assert job.model_name == "ocr"
    events = event_bus.events
    assert len(events) == 1
    assert events[0].payload.get("input_uri") == "s3://b/k"


@pytest.mark.asyncio
async def test_create_job_duplicate_input_uri_raises_conflict(create_job_uc):
    dto = CreateJobDTO(model_name="m", input_uri="same-uri")
    await create_job_uc.execute(dto)
    with pytest.raises(ConflictError):
        await create_job_uc.execute(dto)
