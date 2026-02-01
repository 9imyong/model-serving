from fastapi import FastAPI

from app.api.v1 import health

app = FastAPI(title="Model Serving Platform")
app.include_router(health.router, prefix="/health", tags=["health"])
