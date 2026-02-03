# app/adapters/mysql/models.py
from __future__ import annotations

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(String(32), primary_key=True)
    input_uri = Column(String(1024), nullable=False)
    model_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(6), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("input_uri", name="uq_jobs_input_uri"),
    )
