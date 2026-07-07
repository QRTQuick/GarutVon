from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import settings
from .routers.core import router as core_router
from .routers.auth_router import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="GarutVON API", version="0.0.1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.PUBLIC_BASE_URL, "http://localhost", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(core_router)
    app.include_router(auth_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("GarutVON API starting up. ENV={}", settings.ENV)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("GarutVON API shutting down.")

    return app


app = create_app()
