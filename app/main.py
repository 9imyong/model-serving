# app/main.py
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.logging import AccessLogMiddleware

app = FastAPI()

# middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AccessLogMiddleware)

# error mapper
register_exception_handlers(app)