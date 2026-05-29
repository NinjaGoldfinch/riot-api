from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.clients.riot import close_riot_client
from app.core.config import settings
from app.core.cors import configure_cors
from app.core.errors import register_exception_handlers
from app.core.metadata import APP_VERSION
from app.core.rate_limit import InMemoryRateLimiter, RateLimitMiddleware, RateLimitPolicy
from app.core.request_id import RequestIDMiddleware
from app.core.riot_headers import RiotRateLimitHeaderMiddleware
from app.db.lifecycle import shutdown_database, startup_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    await startup_database(settings)
    try:
        yield
    finally:
        await close_riot_client()
        await shutdown_database()


app = FastAPI(
    title=settings.app_name,
    version=APP_VERSION,
    lifespan=lifespan,
)
configure_cors(app, settings)
rate_limiter = InMemoryRateLimiter()
app.add_middleware(
    RateLimitMiddleware,
    limiter=rate_limiter,
    enabled=settings.rate_limit_enabled,
    application_policy=RateLimitPolicy(
        bucket_type="application",
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    ),
    service_policy=RateLimitPolicy(
        bucket_type="service",
        max_requests=settings.rate_limit_service_requests,
        window_seconds=settings.rate_limit_service_window_seconds,
    ),
    method_policy=RateLimitPolicy(
        bucket_type="method",
        max_requests=settings.rate_limit_method_requests,
        window_seconds=settings.rate_limit_method_window_seconds,
    ),
    excluded_paths={"/health"},
)
app.add_middleware(RiotRateLimitHeaderMiddleware)
app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/version", tags=["Health"])
async def version() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": APP_VERSION,
        "environment": settings.app_env,
    }
