from fastapi import APIRouter
from app.domain.errors import JobNotFound, InvalidJobState

router = APIRouter()

@router.get("/debug/boom-notfound")
async def boom_notfound():
    raise JobNotFound()

@router.get("/debug/boom-conflict")
async def boom_conflict():
    raise InvalidJobState("cannot transition from DONE to RUNNING")