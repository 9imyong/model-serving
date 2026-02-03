# app/main.py
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware.exception_group import ExceptionGroupUnwrapMiddleware
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.logging import AccessLogMiddleware

from app.api.v1 import router as v1_router
from app.api.v1.metrics import router as metrics_router


app = FastAPI()

# middleware (ExceptionGroup unwrap 먼저 → 기존 Exception 핸들러가 404/409 등 처리)
app.add_middleware(ExceptionGroupUnwrapMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AccessLogMiddleware)
# router v1
app.include_router(v1_router, prefix="/api/v1")
# metrics (root)
app.include_router(metrics_router)

# error mapper
register_exception_handlers(app)
