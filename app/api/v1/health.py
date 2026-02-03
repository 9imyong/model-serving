from fastapi import APIRouter
from app.domain.errors import JobNotFound

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}
