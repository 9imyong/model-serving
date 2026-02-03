# app/adapters/mysql/repository.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.mysql.errors import map_integrity_error
from app.adapters.mysql.models import JobModel
from app.application.errors import NotFoundError
from app.domain.job import Job
from app.ports.repositories import JobRepository


class MySQLJobRepository(JobRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, job: Job) -> None:
        row = JobModel(
            job_id=job.id,
            input_uri=job.input_uri,
            model_name=job.model_name,
            status=str(job.status),
            # created_at은 DB default 사용
        )
        self.session.add(row)

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise_if_duplicate_input_uri(e)  # ✅ 여기서 409로 변환
            raise  # duplicate가 아니면 원래 에러 그대로 던짐


    async def get_by_id(self, job_id: str) -> Job:
        stmt = select(JobModel).where(JobModel.job_id == job_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            raise NotFoundError(f"job not found: {job_id}")

        return Job.restore(
            job_id=row.job_id,
            input_uri=row.input_uri,
            model_name=row.model_name,
            status=row.status,
            created_at=row.created_at,
        )

    async def get_by_input_uri(self, input_uri: str) -> Job:
        stmt = select(JobModel).where(JobModel.input_uri == input_uri)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            raise NotFoundError(f"job not found for input_uri={input_uri}")

        return Job.restore(
            job_id=row.job_id,
            input_uri=row.input_uri,
            model_name=row.model_name,
            status=row.status,
            created_at=row.created_at,
        )
