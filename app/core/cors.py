from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    allowed_origins = settings.cors_origins
    if not allowed_origins:
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials="*" not in allowed_origins,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-RateLimit-Type",
            "X-Riot-App-Rate-Limit",
            "X-Riot-App-Rate-Limit-Count",
            "X-Riot-Method-Rate-Limit",
            "X-Riot-Method-Rate-Limit-Count",
            "X-Riot-Service-Rate-Limit",
            "X-Riot-Service-Rate-Limit-Count",
            "X-Riot-Rate-Limit-Type",
            "X-Riot-Retry-After",
        ],
    )
