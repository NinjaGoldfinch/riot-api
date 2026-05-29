from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.clients.riot import close_riot_client
from app.core.config import settings
from app.core.errors import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_riot_client()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
