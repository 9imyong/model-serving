# app/adapters/kafka/event_bus.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional

from app.domain.events import DomainEvent
from app.ports.event_bus import EventBus

from app.adapters.kafka.serializer import serialize_event
from app.adapters.kafka.topics import topic_for


@dataclass(slots=True)
class KafkaEventBus(EventBus):
    """
    Kafka 기반 EventBus (Producer)

    - publish(event) 호출 시 topic으로 메시지 발행
    - key=job_id로 설정해 같은 job_id 이벤트의 파티션 순서 보장
    - producer는 lazy-start 또는 앱 startup에서 start() 호출 가능
    """

    bootstrap_servers: str
    client_id: str = "model-serving"
    acks: str = "all"
    linger_ms: int = 5

    _producer: Optional[object] = field(default=None, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def start(self) -> None:
        async with self._lock:
            if self._producer is not None:
                return

            try:
                from aiokafka import AIOKafkaProducer  # type: ignore
            except Exception as e:
                raise RuntimeError("aiokafka is required for KafkaEventBus") from e

            producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                acks=self.acks,
                linger_ms=self.linger_ms,
            )
            await producer.start()
            self._producer = producer

    async def close(self) -> None:
        async with self._lock:
            producer = self._producer
            self._producer = None

        if producer is not None:
            await producer.stop()

    async def publish(self, event: DomainEvent) -> None:
        if self._producer is None:
            await self.start()

        assert self._producer is not None
        topic = topic_for(event)
        value = serialize_event(event)

        # 파티셔닝 키: job_id가 있으면 그걸 사용
        job_id = getattr(event, "job_id", None)
        key = job_id.encode("utf-8") if isinstance(job_id, str) else None

        # send_and_wait: 전달 성공(브로커 acks)까지 대기
        await self._producer.send_and_wait(topic, value=value, key=key)  # type: ignore[attr-defined]
