# app/adapters/mysql/__init__.py (session wiring)
from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DB_DSN = os.getenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/model_serving").strip()

engine: AsyncEngine = create_async_engine(
    DB_DSN,
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
