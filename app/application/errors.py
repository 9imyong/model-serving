# app/application/errors.py
from __future__ import annotations

class UseCaseError(Exception):
    """
    Application layer base error.

    - api/http를 모름
    - domain error와 구분되는 '흐름/정책' 오류
    """
    code: str = "USECASE_ERROR"
    message: str = "usecase error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)


class ConflictError(UseCaseError):
    code = "CONFLICT"
    message = "conflict occurred"