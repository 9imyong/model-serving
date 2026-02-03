# app/api/deps.py
from __future__ import annotations

import os
from functools import lru_cache

from app.application.commands.create_job import CreateJobUseCase
from app.application.queries.get_job_status import GetJobStatusUseCase

from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.adapters.inmemory.idem_gate import InMemoryIdemGate

from app.adapters.mysql.repository import MySQLJobRepository
from app.adapters.idempotency.redis_gate import RedisIdempotencyGate
from app.adapters.kafka.event_bus import KafkaEventBus

def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()

@lru_cache
def get_repo():
    backend = _env("REPO_BACKEND", "inmemory")
    if backend == "mysql":
        # 너 mysql adapter에 맞춰 생성자/팩토리만 맞추면 됨
        # 예: MySQLJobRepository.from_env()
        return MySQLJobRepository.from_env()
    return InMemoryJobRepository()


@lru_cache
def get_event_bus():
    backend = _env("EVENT_BUS", "inmemory")
    if backend == "kafka":
        return KafkaEventBus(bootstrap_servers=_env("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"))
    return InMemoryEventBus()


@lru_cache
def get_idem_gate():
    backend = _env("IDEM_BACKEND", "inmemory")
    if backend == "redis":
        # 예: RedisIdempotencyGate.from_env() 형태로 맞추는 게 베스트
        return RedisIdempotencyGate.from_env()
    return InMemoryIdemGate()


def get_create_job_uc() -> CreateJobUseCase:
    return CreateJobUseCase(
        repo=get_repo(),
        event_bus=get_event_bus(),
        idem_gate=get_idem_gate(),
    )

def get_get_job_status_uc() -> GetJobStatusUseCase:
    return GetJobStatusUseCase(repo=get_repo())
