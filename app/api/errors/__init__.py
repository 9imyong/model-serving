# app/api/errors/__init__.py
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.middleware.error_mapper import map_exception

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        http_exc = await map_exception(exc)
        # 500이면 서버 로그에 한 번 더 기록 (map_exception 내부에서도 로그하지만, 요청 경로 등 확인용)
        if http_exc.status_code >= 500:
            logger.error(
                "Request %s %s -> %s: %s",
                request.method,
                request.url.path,
                http_exc.status_code,
                http_exc.detail,
            )
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail,
        )
