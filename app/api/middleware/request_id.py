# """Request ID middleware."""
# app/api/middleware/request_id.py
from __future__ import annotations

import contextvars
import logging
import uuid
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# request_id를 어디서든 꺼내 쓸 수 있게 ContextVar로 보관
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

DEFAULT_HEADER = "X-Request-ID"

logger = logging.getLogger("app.api")


def get_request_id() -> str:
    """
    현재 요청 컨텍스트의 request_id를 반환한다.
    (미들웨어 밖에서 로그 필드로 포함시키는 용도)
    """
    return request_id_ctx.get() or ""


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    - 요청 헤더의 X-Request-ID가 있으면 그 값을 사용
    - 없으면 UUID4로 생성
    - 응답 헤더에 동일한 X-Request-ID를 포함
    - contextvars에 저장하여 로깅/트레이싱에 활용
    """

    def __init__(
        self,
        app,
        header_name: str = DEFAULT_HEADER,
        allow_external: bool = True,
        generator: Optional[Callable[[], str]] = None,
    ) -> None:
        super().__init__(app)
        self.header_name = header_name
        self.allow_external = allow_external
        self.generator = generator or (lambda: uuid.uuid4().hex)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = ""
        if self.allow_external:
            rid = request
