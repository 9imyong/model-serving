"""Pytest configuration and shared fixtures."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.adapters.inmemory.idem_gate import InMemoryIdemGate
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.application.commands.create_job import CreateJobUseCase
from app.application.queries.get_job_status import GetJobStatusUseCase
from app.main import app


@pytest.fixture
def inmemory_repo():
    return InMemoryJobRepository()


@pytest.fixture
def inmemory_event_bus():
    return InMemoryEventBus()


@pytest.fixture
def inmemory_idem_gate():
    return InMemoryIdemGate()


@pytest.fixture
def create_job_uc(inmemory_repo, inmemory_event_bus, inmemory_idem_gate):
    return CreateJobUseCase(
        repo=inmemory_repo,
        event_bus=inmemory_event_bus,
        idem_gate=inmemory_idem_gate,
    )


@pytest.fixture
def get_job_status_uc(inmemory_repo):
    return GetJobStatusUseCase(repo=inmemory_repo)


@pytest.fixture
def client(create_job_uc, get_job_status_uc):
    """API 테스트용 클라이언트. 인메모리 UseCase로 의존성 오버라이드."""
    from app.api.deps import get_create_job_uc, get_get_job_status_uc

    app.dependency_overrides[get_create_job_uc] = lambda: create_job_uc
    app.dependency_overrides[get_get_job_status_uc] = lambda: get_job_status_uc
    # BaseHTTPMiddleware가 예외를 ExceptionGroup으로 감싸서, 404/409가 예외로 튀어나오지 않도록
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
