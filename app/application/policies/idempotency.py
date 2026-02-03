"""Idempotency policy."""
from __future__ import annotations

from app.domain.job import Job, JobStatus


def should_skip_processing(job: Job) -> bool:
    """이미 처리된 상태면 skip (멱등성)."""
    return job.status in (JobStatus.SUCCEEDED, JobStatus.FAILED)


def should_skip_write_result(job: Job) -> bool:
    """이미 DONE(SUCCEEDED)이면 skip."""
    return job.status is JobStatus.SUCCEEDED
