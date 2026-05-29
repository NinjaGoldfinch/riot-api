from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.riot_headers import (
    RiotRateLimitHeaderMiddleware,
    capture_riot_rate_limit_headers,
)


async def test_riot_rate_limit_headers_are_forwarded() -> None:
    app = FastAPI()
    app.add_middleware(RiotRateLimitHeaderMiddleware)

    @app.get("/riot-backed")
    async def riot_backed() -> dict[str, str]:
        capture_riot_rate_limit_headers(
            {
                "x-app-rate-limit": "20:1,100:120",
                "x-app-rate-limit-count": "1:1,1:120",
                "x-method-rate-limit": "20:1",
                "x-method-rate-limit-count": "1:1",
                "x-rate-limit-type": "method",
                "retry-after": "4",
            }
        )
        return {"status": "ok"}

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/riot-backed")

    assert response.status_code == 200
    assert response.headers["X-Riot-App-Rate-Limit"] == "20:1,100:120"
    assert response.headers["X-Riot-App-Rate-Limit-Count"] == "1:1,1:120"
    assert response.headers["X-Riot-Method-Rate-Limit"] == "20:1"
    assert response.headers["X-Riot-Method-Rate-Limit-Count"] == "1:1"
    assert response.headers["X-Riot-Rate-Limit-Type"] == "method"
    assert response.headers["X-Riot-Retry-After"] == "4"


async def test_riot_rate_limit_headers_are_cleared_per_request() -> None:
    app = FastAPI()
    app.add_middleware(RiotRateLimitHeaderMiddleware)

    @app.get("/with-headers")
    async def with_headers() -> dict[str, str]:
        capture_riot_rate_limit_headers({"x-app-rate-limit": "20:1"})
        return {"status": "ok"}

    @app.get("/without-headers")
    async def without_headers() -> dict[str, str]:
        return {"status": "ok"}

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/with-headers")
        second = await client.get("/without-headers")

    assert first.headers["X-Riot-App-Rate-Limit"] == "20:1"
    assert "X-Riot-App-Rate-Limit" not in second.headers
