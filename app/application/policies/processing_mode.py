"""Processing mode policy."""
from __future__ import annotations

from enum import Enum


class ProcessingMode(str, Enum):
    STANDARD = "STANDARD"           # Case1: inference 후 바로 repo.save_result + SUCCEEDED
    BATCHED = "BATCHED"            # Case2: GPU 배치 최적화
    WRITER_SPLIT = "WRITER_SPLIT"  # Case3: inference 완료 → result-topic → writer가 저장 후 SUCCEEDED
