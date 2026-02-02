# API v1
#/app/api/v1/__init__.py
from fastapi import APIRouter

from .health import router as health_router
from .jobs import router as jobs_router
from .debug import router as debug_router
# from .metrics import router as metrics_router


router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(jobs_router, tags=["jobs"])
router.include_router(debug_router, tags=["debug"])
# router.include_router(metrics_router, tags=["metrics"])