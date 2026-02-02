# app/api/errors/http_exceptions.py
from __future__ import annotations

from fastapi import HTTPException
from typing import Optional


class ApiError(HTTPException):
    """
    API 레벨 공통 에러 베이스
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: Optional[dict] = None,
    ):
        payload = {
            "code": code,
            "message": message,
        }
        if detail:
            payload["detail"] = detail

        super().__init__(status_code=status_code, detail=payload)
