"""Logging middleware."""
# app/api/middleware/logging.py
from __future__ import annotations

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.middleware.request_id import get_request_id

logger = logging.getLogger("app.api")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    - 요청 1건당 1줄 로그 (구조화 로그 전 단계)
    - request_id 포함
    - latency_ms 포함
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            logger.info(
                "http_request",
                extra={
                    "request_id": get_request_id(),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code if response else 500,
                    "latency_ms": round(elapsed_ms, 2),
                },
            )