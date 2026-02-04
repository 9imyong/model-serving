"""ExceptionGroup unwrap + 앱 예외를 HTTP 응답으로 변환 (404/409 등, 트레이스백 방지)."""
from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.middleware.error_mapper import map_exception


class ExceptionGroupUnwrapMiddleware:
    """
    - Starlette BaseHTTPMiddleware가 래핑한 ExceptionGroup → 첫 번째 내부 예외로 변환 후 응답 전송.
    - 그 외 앱 예외(ConflictError, JobNotFound 등)도 map_exception으로 404/409 응답 전송.
    - 이미 응답을 보낸 뒤 발생한 예외는 재발생시켜 트레이스백만 방지하지 않음.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_wrapper(message: dict) -> None:
            nonlocal response_started
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        exc_to_handle: Exception | None = None
        try:
            await self.app(scope, receive, send_wrapper)
        except BaseExceptionGroup as eg:
            if not eg.exceptions:
                raise
            inner = eg.exceptions[0]
            if not isinstance(inner, Exception):
                raise
            exc_to_handle = inner
        except Exception as exc:
            exc_to_handle = exc
        else:
            return

        if response_started:
            raise exc_to_handle

        http_exc = await map_exception(exc_to_handle)
        response = JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail,
        )
        await response(scope, receive, send)
