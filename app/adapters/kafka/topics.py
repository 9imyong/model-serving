# app/adapters/kafka/topics.py
from __future__ import annotations

from app.domain.events import JobCreated, InferenceCompleted, DomainEvent


def topic_for(event: DomainEvent) -> str:
    # 운영에서는 settings로 뽑아도 됨
    if isinstance(event, JobCreated):
        return "job.created.v1"
    if isinstance(event, InferenceCompleted):
        return "inference.completed.v1"
    return "domain.event.v1"
