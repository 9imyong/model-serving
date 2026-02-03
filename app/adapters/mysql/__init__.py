# app/adapters/mysql/session.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings  # DB_DSN 여기서 가져온다고 가정 mysql+aiomysql://app:app@mysql:3306/app


engine: AsyncEngine = create_async_engine(
    settings.DB_DSN,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
