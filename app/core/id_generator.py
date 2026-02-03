"""ID generator."""
from __future__ import annotations

import uuid


def generate_job_id() -> str:
    return uuid.uuid4().hex
