from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

logger = logging.getLogger(__name__)

MessageHandler = Callable[[dict], Awaitable[None]]


@dataclass(slots=True)
class KafkaConsumerRunner:
    """
    Kafka Consumer 실행기 (aiokafka 기반)
    - topic 구독
    - 메시지 처리 성공 시 commit
    - 실패 시 재시도(간단 backoff) 후에도 실패하면 로깅 (DLQ 훅은 TODO)
    """

    bootstrap_servers: str
    group_id: str
    topics: list[str]
    handler: MessageHandler

    client_id: str = "model-serving-worker"
    enable_auto_commit: bool = False  # 우리가 처리 성공 시점에 commit
    max_retries: int = 3
    retry_backoff_sec: float = 0.5

    _consumer: Optional[object] = field(default=None, init=False)
    _stopping: asyncio.Event = field(default_factory=asyncio.Event, init=False)

    async def start(self) -> None:
        try:
            from aiokafka import AIOKafkaConsumer  # type: ignore
        except Exception as e:
            raise RuntimeError("aiokafka is required for KafkaConsumerRunner") from e

        consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            client_id=self.client_id,
            enable_auto_commit=self.enable_auto_commit,
            auto_offset_reset="earliest",  # 개발 단계: earliest, 운영은 보통 latest 또는 토픽 정책에 맞춤
        )
        await consumer.start()
        self._consumer = consumer
        logger.info("kafka_consumer_started", extra={"topics": self.topics, "group_id": self.group_id})

    async def stop(self) -> None:
        self._stopping.set()
        consumer = self._consumer
        self._consumer = None
        if consumer is not None:
            await consumer.stop()
        logger.info("kafka_consumer_stopped")

    async def run_forever(self) -> None:
        if self._consumer is None:
            await self.start()

        assert self._consumer is not None
        consumer = self._consumer

        try:
            while not self._stopping.is_set():
                msg = await consumer.getone()  # 단건씩 처리(초기 스켈레톤)
                await self._process_message_with_retry(consumer, msg)
        finally:
            await self.stop()

    async def _process_message_with_retry(self, consumer: object, msg: object) -> None:
        # aiokafka ConsumerRecord는 msg.value가 bytes
        value_bytes = getattr(msg, "value", None)
        topic = getattr(msg, "topic", None)
        partition = getattr(m
