"""Metrics API v1."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
def metrics():