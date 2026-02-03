# app/api/middleware/error_mapper.py
from __future__ import annotations

from fastapi import HTTPException

from app.domain.errors import DomainError, InvalidStateError, NotFoundError
from app.application.errors import UseCaseError, ConflictError
from app.api.errors.http_exceptions import ApiError


def map_exception(exc: Exception) -> HTTPException:
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

    # ---- Fallback ----
    return ApiError(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Unexpected server error",
    )
