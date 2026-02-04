"""Worker entrypoint."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트의 .env 로드 (uv run 시 cwd 기준)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.core.logging import configure_logging
configure_logging()

from app.adapters.kafka.consumer import KafkaConsumerRunner
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.adapters.mysql.repository import MySQLJobRepository
from app.adapters.kafka.event_bus import KafkaEventBus
from app.worker.handler import JobCreatedHandler

def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _repo_backend() -> str:
    if _env("BACKEND", "").lower() == "infra":
        return "mysql"
    return _env("REPO_BACKEND", "inmemory")


def _event_bus_backend() -> str:
    if _env("BACKEND", "").lower() == "infra":
        return "kafka"
    return _env("EVENT_BUS", "inmemory")


def _get_repo():
    if _repo_backend() == "mysql":
        return MySQLJobRepository.from_env()
    return InMemoryJobRepository()


def _get_event_bus():
    if _event_bus_backend() == "kafka":
        return KafkaEventBus(bootstrap_servers=_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    return InMemoryEventBus()


BOOTSTRAP_SERVERS = _env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
GROUP_ID = _env("KAFKA_CONSUMER_GROUP", "model-serving-worker")
TOPICS = [_env("KAFKA_TOPIC_OCR", "job.created.v1")]

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    repo = _get_repo()
    event_bus = _get_event_bus()
    handler = JobCreatedHandler(repo=repo, event_bus=event_bus)

    runner = KafkaConsumerRunner(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        topics=TOPICS,
        handler=handler,
        max_retries=3,
        retry_backoff_sec=0.5,
    )

    await runner.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
