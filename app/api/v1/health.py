from fastapi import APIRouter
from app.domain.errors import JobNotFound

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}
