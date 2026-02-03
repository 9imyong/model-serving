# app/adapters/inmemory/event_bus.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from app.domain.events import DomainEvent
from app.ports.event_bus import EventBus

EventHandler = Callable[[DomainEvent], Awaitable[None]]

@dataclass(slots=True)
class InMemoryEventBus(EventBus):
    """
    개발/테스트용 EventBus

    - publish된 이벤트를 메모리에 저장(events)
    - 핸들러 구독/실행(subscribe)
    - 핸들러 예외는 격리 (publish 자체는 성공 처리)
    """

    events: list[DomainEvent] = field(default_factory=list)
    _handlers: list[EventHandler] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def publish(self, event: DomainEvent) -> None:
        # 이벤트 저장/핸들러 스냅샷을 원자적으로
        async with self._lock:
            self.events.append(event)
            handlers = list(self._handlers)

        # 핸들러는 락 밖에서 실행 (핸들러가 느려도 publish lock을 잡지 않게)
        for h in handlers:
            try:
                await h(event)
            except Exception:
                # TODO: logger.exception(...) 으로 교체 가능
                # 핸들러 하나 실패가 전체 publish 실패가 되지 않도록 격리
                pass

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        self._handlers = [h for h in self._handlers if h is not handler]

    async def wait_for(self, predicate: Callable[[DomainEvent], bool], timeout: float = 2.0) -> DomainEvent:
        """
        테스트 편의: 특정 이벤트가 publish될 때까지 기다림.
        """
        end = asyncio.get_event_loop().time() + timeout
        idx = 0
        while True:
            # 새로 추가된 이벤트만 스캔
            while idx < len(self.events):
                ev = self.events[idx]
                idx += 1
                if predicate(ev):
                    return ev

            if asyncio.get_event_loop().time() >= end:
                raise TimeoutError("event not published in time")

            await asyncio.sleep(0.01)
