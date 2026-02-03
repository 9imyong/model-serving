"""ExceptionGroup unwrap middleware (Python 3.11+ / Starlette TaskGroup)."""
from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.middleware.error_mapper import map_exception


class ExceptionGroupUnwrapMiddleware:
    """
    Starlette BaseHTTPMiddleware가 async 경로 예외를 ExceptionGroup으로 래핑할 때,
    첫 번째 내부 예외를 꺼내 map_exception으로 404/409 응답으로 변환해 전송.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except BaseExceptionGroup as eg:
            if not eg.exceptions:
                raise
            inner = eg.exceptions[0]
            if not isinstance(inner, Exception):
                raise
            http_exc = await map_exception(inner)
            response = JSONResponse(
                status_code=http_exc.status_code,
                content=http_exc.detail,
            )
            await response(scope, receive, send)
