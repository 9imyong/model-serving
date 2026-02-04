"""Logging setup."""
from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    """
    환경별 로깅 레벨 설정.
    - 개발(ENV != production): aiokafka/kafka 등 서드파티는 기본 레벨 유지 (Topic not found 등 로그 노출).
    - 프로덕션(ENV=production): aiokafka 등은 ERROR만 노출해 노이즈 감소.
    """
    env = os.getenv("ENV", "").strip().lower()
    is_production = env in ("production", "prod")

    if is_production:
        for name in ("aiokafka", "aiokafka.producer", "aiokafka.consumer", "kafka"):
            logging.getLogger(name).setLevel(logging.ERROR)
