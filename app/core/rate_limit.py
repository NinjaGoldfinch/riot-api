from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse


@dataclass(frozen=True)
class RateLimitPolicy:
    bucket_type: str
    max_requests: int
    window_seconds: int


@dataclass
class RateLimitState:
    window_started_at: float
    request_count: int


@dataclass(frozen=True)
class RateLimitResult:
    bucket_type: str
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int


class InMemoryRateLimiter:
    def __init__(
        self,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._clock = clock
        self._buckets: dict[str, RateLimitState] = {}

    def check(self, bucket_id: str, policy: RateLimitPolicy) -> RateLimitResult:
        now = self._clock()
        state = self._buckets.get(bucket_id)

        if state is None or now - state.window_started_at >= policy.window_seconds:
            state = RateLimitState(window_started_at=now, request_count=0)
            self._buckets[bucket_id] = state

        state.request_count += 1
        reset_seconds = max(1, int(state.window_started_at + policy.window_seconds - now))
        remaining = max(0, policy.max_requests - state.request_count)

        return RateLimitResult(
            bucket_type=policy.bucket_type,
            allowed=state.request_count <= policy.max_requests,
            limit=policy.max_requests,
            remaining=remaining,
            reset_seconds=reset_seconds,
        )

    def clear(self) -> None:
        self._buckets.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        limiter: InMemoryRateLimiter,
        enabled: bool,
        application_policy: RateLimitPolicy,
        service_policy: RateLimitPolicy,
        method_policy: RateLimitPolicy,
        excluded_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter
        self._enabled = enabled
        self._application_policy = application_policy
        self._service_policy = service_policy
        self._method_policy = method_policy
        self._excluded_paths = excluded_paths or set()

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if not self._enabled or request.url.path in self._excluded_paths:
            return await call_next(request)

        results = self._check_limits(request)
        blocked_result = next((result for result in results if not result.allowed), None)

        if blocked_result is not None:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests. Try again later.",
                    }
                },
                headers=self._rate_limit_headers(results, blocked_result),
            )

        response = await call_next(request)
        self._apply_rate_limit_headers(response, results)
        return response

    def _check_limits(self, request: Request) -> list[RateLimitResult]:
        client_id = self._client_id(request)
        service_name = self._service_name(request)
        method_name = self._method_name(request)

        return [
            self._limiter.check(
                f"application:{client_id}",
                self._application_policy,
            ),
            self._limiter.check(
                f"service:{client_id}:{service_name}",
                self._service_policy,
            ),
            self._limiter.check(
                f"method:{client_id}:{method_name}",
                self._method_policy,
            ),
        ]

    def _rate_limit_headers(
        self,
        results: list[RateLimitResult],
        blocked_result: RateLimitResult,
    ) -> dict[str, str]:
        headers = {
            "Retry-After": str(blocked_result.reset_seconds),
            "X-RateLimit-Type": blocked_result.bucket_type,
        }
        headers.update(self._status_headers(results))
        return headers

    def _apply_rate_limit_headers(
        self,
        response: Response,
        results: list[RateLimitResult],
    ) -> None:
        for key, value in self._status_headers(results).items():
            response.headers[key] = value

    @staticmethod
    def _status_headers(results: list[RateLimitResult]) -> dict[str, str]:
        headers: dict[str, str] = {}
        for result in results:
            prefix = f"X-RateLimit-{result.bucket_type.title()}"
            headers[f"{prefix}-Limit"] = str(result.limit)
            headers[f"{prefix}-Remaining"] = str(result.remaining)
            headers[f"{prefix}-Reset"] = str(result.reset_seconds)

        most_constrained = min(results, key=lambda result: result.remaining)
        headers["X-RateLimit-Limit"] = str(most_constrained.limit)
        headers["X-RateLimit-Remaining"] = str(most_constrained.remaining)
        headers["X-RateLimit-Reset"] = str(most_constrained.reset_seconds)
        return headers

    @staticmethod
    def _client_id(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", maxsplit=1)[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    @staticmethod
    def _service_name(request: Request) -> str:
        path_parts = [part for part in request.url.path.split("/") if part]
        if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1].startswith("v"):
            return path_parts[2]
        return path_parts[0] if path_parts else "root"

    @staticmethod
    def _method_name(request: Request) -> str:
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        return f"{request.method}:{route_path}"
