# app/api/errors/__init__.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.middleware.error_mapper import map_exception


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        http_exc = await map_exception(exc)
        return JSONResponse(
            status_code= http_exc.status_code,
            content=http_exc.detail,
        )
