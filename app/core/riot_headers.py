from collections.abc import Mapping
from contextvars import ContextVar

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

RIOT_RATE_LIMIT_HEADERS = {
    "x-app-rate-limit": "X-Riot-App-Rate-Limit",
    "x-app-rate-limit-count": "X-Riot-App-Rate-Limit-Count",
    "x-method-rate-limit": "X-Riot-Method-Rate-Limit",
    "x-method-rate-limit-count": "X-Riot-Method-Rate-Limit-Count",
    "x-service-rate-limit": "X-Riot-Service-Rate-Limit",
    "x-service-rate-limit-count": "X-Riot-Service-Rate-Limit-Count",
    "x-rate-limit-type": "X-Riot-Rate-Limit-Type",
    "retry-after": "X-Riot-Retry-After",
}

_riot_rate_limit_headers: ContextVar[dict[str, str] | None] = ContextVar(
    "riot_rate_limit_headers",
    default=None,
)


def clear_riot_rate_limit_headers() -> None:
    _riot_rate_limit_headers.set({})


def capture_riot_rate_limit_headers(headers: Mapping[str, str] | None) -> None:
    if headers is None:
        return

    captured = dict(_riot_rate_limit_headers.get() or {})
    for source_header, forwarded_header in RIOT_RATE_LIMIT_HEADERS.items():
        value = headers.get(source_header)
        if value is not None:
            captured[forwarded_header] = value

    _riot_rate_limit_headers.set(captured)


def get_riot_rate_limit_headers() -> dict[str, str]:
    return dict(_riot_rate_limit_headers.get() or {})


class RiotRateLimitHeaderMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        clear_riot_rate_limit_headers()

        async def send_with_riot_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for header, value in get_riot_rate_limit_headers().items():
                    headers[header] = value

            await send(message)

        await self.app(scope, receive, send_with_riot_headers)
