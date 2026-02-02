"""Error mapping middleware."""
# app/api/errors/error_mapper.py
from __future__ import annotations

from fastapi import HTTPException

# domain / application 예외
from app.domain.errors import (
    DomainError,
    InvalidStateError,
    NotFoundError,
)
from app.application.errors import (
    UseCaseError,
    ConflictError,
)

from app.api.errors.http_exceptions import ApiError


def map_exception(exc: Exception) -> HTTPException:
    """
    내부 예외를 HTTPException으로 변환한다.
    """

    # ---- Domain ----
    if isinstance(exc, InvalidStateError):
        return ApiError(
            status_code=409,
            code="INVALID_STATE",
            message="Invalid resource state",
        )

    if isinstance(exc, NotFoundError):
        return ApiError(
            status_code=404,
            code="NOT_FOUND",
            message="Resource not found",
        )

    if isinstance(exc, DomainError):
        return ApiError(
            status_code=400,
            code="DOMAIN_ERROR",
            message=str(exc),
        )

    # ---- Application ----
    if isinstance(exc, ConflictError):
        return ApiError(
            status_code=409,
            code="CONFLICT",
            message=str(exc),
        )

    if isinstance(exc, UseCaseError):
        return ApiError(
            status_code=400,
            code="USECASE_ERROR",
            message=str(exc),
        )

    # ---- Fallback ----
    return ApiError(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Unexpected server error",
    )
