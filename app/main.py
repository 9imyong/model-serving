# app/main.py
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.logging import AccessLogMiddleware

from app.domain.errors import JobNotFound
from app.api.v1 import router as v1_router  # ✅ 여기 중요
from app.api.v1.metrics import router as metrics_router


app = FastAPI()

# middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AccessLogMiddleware)
# router v1
app.include_router(v1_router, prefix="/api/v1")
# metrics (root)
app.include_router(metrics_router)

# error mapper
register_exception_handlers(app)
