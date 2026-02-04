from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import NotFoundError
from app.domain.events import InferenceCompleted
from app.ports.event_bus import EventBus
from app.ports.repositories import JobRepository


@dataclass(slots=True)
class JobCreatedHandler:
    """
    job.created.v1 메시지를 처리하는 워커 핸들러

    멱등 기준(추천):
    - job_id로 Job을 조회해서 status가 이미 COMPLETED/FAILED면 스킵
    - 또는 별도의 'processed_events' 저장소(추후 DB/Redis)로 exactly-once 흉내
    """
    repo: JobRepository
    event_bus: EventBus

    async def __call__(self, payload: dict) -> None:
        event_type = payload.get("event_type")
        data = payload.get("data") or {}

        if event_type != "JobCreated":
            return  # 관심 없는 이벤트면 무시

        job_id = data.get("job_id")
        if not job_id:
            return

        # 1) 멱등 처리 (job 상태 기반)
        try:
            job = await self.repo.get(job_id)
        except NotFoundError:
            # 아직 저장 전 이벤트가 왔거나(레이스), 데이터 유실 등
            # 정책: 재시도 유도하려면 예외를 던져야 함.
            raise

        # 예: status가 문자열/enum 어떤 형태든 처리되게 단순화
        status_str = getattr(job.status, "value", str(job.status))

        if status_str in ("COMPLETED", "FAILED"):
            return  # 이미 처리 완료 → 스킵

        # 2) 실제 처리(스켈레톤)
        # TODO: status RUNNING 업데이트 등
        # TODO: OCR/Inference 수행
        result_payload = {"ok": True}  # placeholder

        # TODO: status COMPLETED 업데이트 등

        # 3) 완료 이벤트 발행(선택)
        await self.event_bus.publish(
            InferenceCompleted(job_id=job_id, result_payload=result_payload)
        )
