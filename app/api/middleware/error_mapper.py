# app/api/middleware/error_mapper.py
from __future__ import annotations

import logging
import os

from fastapi import HTTPException

from app.api.errors.http_exceptions import ApiError
from app.application.errors import ConflictError, UseCaseError
from app.domain.errors import DomainError, InvalidStateError, NotFoundError

logger = logging.getLogger(__name__)


def _unwrap_exception_group(exc: Exception) -> Exception:
    """
    Python 3.11+ may raise ExceptionGroup in async contexts (TaskGroup/anyio).
    We map the most relevant inner exception.
    """
    if isinstance(exc, ExceptionGroup):  # type: ignore[name-defined]
        # pick the first exception as primary cause (simple & predictable)
        if exc.exceptions:
            inner = exc.exceptions[0]
            if isinstance(inner, Exception):
                return inner
    return exc


async def map_exception(exc: Exception) -> HTTPException:
    # Unwrap grouped exceptions (Python 3.11+)
    exc = _unwrap_exception_group(exc)

    # FastAPI/Starlette HTTP exceptions should pass through
    if isinstance(exc, HTTPException):
        return exc

    # ---- Domain ----
    if isinstance(exc, InvalidStateError):
        return ApiError(
            status_code=409,
            code=getattr(exc, "code", "INVALID_STATE"),
            message=str(exc),
        )

    if isinstance(exc, NotFoundError):
        return ApiError(
            status_code=404,
            code=getattr(exc, "code", "NOT_FOUND"),
            message=str(exc),
        )

    if isinstance(exc, DomainError):
        return ApiError(
            status_code=400,
            code=getattr(exc, "code", "DOMAIN_ERROR"),
            message=str(exc),
        )

    # ---- Application ----
    if isinstance(exc, ConflictError):
        return ApiError(
            status_code=409,
            code=getattr(exc, "code", "CONFLICT"),
            message=str(exc),
        )

    if isinstance(exc, UseCaseError):
        return ApiError(
            status_code=400,
            code=getattr(exc, "code", "USECASE_ERROR"),
            message=str(exc),
        )

    # ---- Fallback (500) ----
    # 로그에 전체 traceback 남김
    logger.exception("Unhandled exception: %s", exc)
    # 응답 메시지: 개발 시 원인 확인용 (EXPOSE_SERVER_ERROR=1 또는 미설정 시 실제 메시지)
    expose = os.getenv("EXPOSE_SERVER_ERROR", "1").strip().lower() in ("1", "true", "yes")
    message = str(exc) if expose else "Unexpected server error"
    return ApiError(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message=message,
    )
