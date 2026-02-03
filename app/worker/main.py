"""Worker entrypoint."""
from __future__ import annotations

import asyncio
import logging

from app.adapters.kafka.consumer import KafkaConsumerRunner
from app.adapters.inmemory.job_repository import InMemoryJobRepository
from app.adapters.inmemory.event_bus import InMemoryEventBus
from app.worker.handlers import JobCreatedHandler

# 나중에 settings로 교체 권장
BOOTSTRAP_SERVERS = "localhost:9092"
GROUP_ID = "model-serving-worker"
TOPICS = ["job.created.v1"]

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    # 임시 wiring: 나중에 DI/Container로 이동
    repo = InMemoryJobRepository()
    event_bus = InMemoryEventBus()

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
