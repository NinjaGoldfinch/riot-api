from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.rate_limit import InMemoryRateLimiter, RateLimitMiddleware, RateLimitPolicy


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def policy(bucket_type: str, max_requests: int = 1) -> RateLimitPolicy:
    return RateLimitPolicy(
        bucket_type=bucket_type,
        max_requests=max_requests,
        window_seconds=60,
    )


def test_rate_limiter_blocks_after_limit() -> None:
    clock = FakeClock()
    limiter = InMemoryRateLimiter(clock=clock)
    app_policy = policy("application", max_requests=2)

    first = limiter.check("client", app_policy)
    second = limiter.check("client", app_policy)
    third = limiter.check("client", app_policy)

    assert first.allowed is True
    assert first.remaining == 1
    assert second.allowed is True
    assert second.remaining == 0
    assert third.allowed is False
    assert third.remaining == 0


def test_rate_limiter_resets_after_window() -> None:
    clock = FakeClock()
    limiter = InMemoryRateLimiter(clock=clock)
    app_policy = policy("application")

    assert limiter.check("client", app_policy).allowed is True
    assert limiter.check("client", app_policy).allowed is False

    clock.advance(60)

    assert limiter.check("client", app_policy).allowed is True


def create_test_app(
    *,
    enabled: bool = True,
    application_limit: int = 10,
    service_limit: int = 10,
    method_limit: int = 1,
) -> FastAPI:
    app = FastAPI()
    limiter = InMemoryRateLimiter(clock=FakeClock())
    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        enabled=enabled,
        application_policy=policy("application", application_limit),
        service_policy=policy("service", service_limit),
        method_policy=policy("method", method_limit),
        excluded_paths={"/health"},
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/account/{name}")
    async def account(name: str) -> dict[str, str]:
        return {"name": name}

    @app.get("/api/v1/account/{name}/summary")
    async def account_summary(name: str) -> dict[str, str]:
        return {"name": name}

    @app.get("/api/v1/matches/{puuid}")
    async def matches(puuid: str) -> dict[str, str]:
        return {"puuid": puuid}

    return app


async def test_rate_limit_middleware_returns_all_bucket_headers() -> None:
    app = create_test_app(application_limit=10, service_limit=5, method_limit=2)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/account/Ninja")

    assert response.status_code == 200
    assert response.headers["X-RateLimit-Application-Limit"] == "10"
    assert response.headers["X-RateLimit-Application-Remaining"] == "9"
    assert response.headers["X-RateLimit-Service-Limit"] == "5"
    assert response.headers["X-RateLimit-Service-Remaining"] == "4"
    assert response.headers["X-RateLimit-Method-Limit"] == "2"
    assert response.headers["X-RateLimit-Method-Remaining"] == "1"
    assert response.headers["X-RateLimit-Remaining"] == "1"


async def test_rate_limit_middleware_blocks_method_bucket_with_headers() -> None:
    app = create_test_app(application_limit=10, service_limit=10, method_limit=1)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/api/v1/account/Ninja")
        second = await client.get("/api/v1/account/Ninja")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["X-RateLimit-Type"] == "method"
    assert second.headers["Retry-After"] == "60"
    assert second.headers["X-RateLimit-Method-Remaining"] == "0"
    assert second.json()["detail"]["code"] == "RATE_LIMITED"


async def test_rate_limit_middleware_blocks_service_bucket_across_methods() -> None:
    app = create_test_app(application_limit=10, service_limit=1, method_limit=10)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/api/v1/account/Ninja")
        second = await client.get("/api/v1/account/Ninja/summary")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["X-RateLimit-Type"] == "service"
    assert second.headers["X-RateLimit-Service-Remaining"] == "0"


async def test_rate_limit_middleware_blocks_application_bucket_across_services() -> None:
    app = create_test_app(application_limit=1, service_limit=10, method_limit=10)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/api/v1/account/Ninja")
        second = await client.get("/api/v1/matches/fake-puuid")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["X-RateLimit-Type"] == "application"
    assert second.headers["X-RateLimit-Application-Remaining"] == "0"


async def test_rate_limit_middleware_skips_excluded_paths() -> None:
    app = create_test_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/health")
        second = await client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200
    assert "X-RateLimit-Limit" not in first.headers


async def test_rate_limit_middleware_can_be_disabled() -> None:
    app = create_test_app(enabled=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/api/v1/account/Ninja")
        second = await client.get("/api/v1/account/Ninja")

    assert first.status_code == 200
    assert second.status_code == 200
    assert "X-RateLimit-Limit" not in first.headers
