# app/adapters/mysql/repository.py
from __future__ import annotations

import os
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.mysql.errors import raise_if_duplicate_input_uri
from app.adapters.mysql.models import JobModel
from app.application.errors import NotFoundError
from app.domain.job import Job
from app.ports.repositories import JobRepository


def _default_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://user:pass@localhost:3306/model_serving",
    ).strip()


class MySQLJobRepository(JobRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @classmethod
    def from_env(cls) -> MySQLJobRepository:
        url = _default_database_url()
        engine = create_async_engine(url)
        session_factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        return cls(session_factory=session_factory)

    async def save(self, job: Job) -> None:
        async with self._session_factory() as session:
            row = JobModel(
                job_id=job.id,
                input_uri=job.input_uri,
                model_name=job.model_name,
                status=str(job.status),
            )
            session.add(row)
            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise_if_duplicate_input_uri(e)
                raise

    async def get(self, job_id: str) -> Job:
        async with self._session_factory() as session:
            return await self._get_by_id(session, job_id)

    async def get_by_id(self, job_id: str) -> Job:
        async with self._session_factory() as session:
            return await self._get_by_id(session, job_id)

    async def _get_by_id(self, session: AsyncSession, job_id: str) -> Job:
        stmt = select(JobModel).where(JobModel.job_id == job_id)
        result = await session.execute(stmt)
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
        async with self._session_factory() as session:
            stmt = select(JobModel).where(JobModel.input_uri == input_uri)
            result = await session.execute(stmt)
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

    async def exists_by_input_uri(self, input_uri: str) -> bool:
        async with self._session_factory() as session:
            stmt = select(1).where(JobModel.input_uri == input_uri).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def save_result(self, job_id: str, result: Any) -> None:
        # TODO: result 컬럼/테이블 추가 시 구현
        pass
