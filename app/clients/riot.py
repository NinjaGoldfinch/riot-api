import asyncio
import logging
import os
import ssl
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
import certifi
from pulsefire.clients import RiotAPIClient
from pulsefire.middlewares import (
    http_error_middleware,
    json_response_middleware,
    rate_limiter_middleware,
)
from pulsefire.ratelimiters import RiotAPIRateLimiter

from app.core.config import settings
from app.core.errors import (
    ConfigurationError,
    RiotAPIError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotUnavailableError,
)
from app.core.regions import AccountRoutingRegion, PlatformRegion, RoutingRegion
from app.core.riot_headers import capture_riot_rate_limit_headers

LOGGER = logging.getLogger(__name__)

type RiotOperation[T] = Callable[[], Awaitable[T]]
type MiddlewareCallable = Callable[[Any], Awaitable[Any]]


def configure_ssl_certificates() -> None:
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())


def create_ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


def create_client_session() -> aiohttp.ClientSession:
    connector = aiohttp.TCPConnector(ssl=create_ssl_context())
    return aiohttp.ClientSession(connector=connector)


def riot_header_capture_middleware():
    def constructor(next_call: MiddlewareCallable) -> MiddlewareCallable:
        async def middleware(invocation: Any) -> Any:
            response = await next_call(invocation)
            capture_riot_rate_limit_headers(response.headers)
            return response

        return middleware

    return constructor


def create_riot_api_client(api_key: str) -> RiotAPIClient:
    return RiotAPIClient(
        default_headers={"X-Riot-Token": api_key},
        middlewares=[
            json_response_middleware(),
            riot_header_capture_middleware(),
            http_error_middleware(),
            rate_limiter_middleware(RiotAPIRateLimiter()),
        ],
    )


class RiotClient:
    def __init__(self, api_key: str, pulsefire_client: Any | None = None) -> None:
        if not api_key:
            raise ConfigurationError("RIOT_API_KEY is required.")
        configure_ssl_certificates()
        self._owns_client = pulsefire_client is None
        self._opened = not self._owns_client
        self._open_lock = asyncio.Lock()
        self._client = pulsefire_client or create_riot_api_client(api_key)

    async def open(self) -> None:
        if self._opened or not self._owns_client:
            return
        async with self._open_lock:
            if self._opened:
                return
            self._client.session = create_client_session()
            self._opened = True

    async def close(self) -> None:
        if not self._opened or not self._owns_client:
            return
        async with self._open_lock:
            if not self._opened:
                return
            await self._client.session.close()
            self._client.session = None
            self._opened = False

    async def _request(self, operation_name: str, operation: RiotOperation[Any]) -> Any:
        await self.open()
        try:
            return await operation()
        except aiohttp.ClientResponseError as exc:
            capture_riot_rate_limit_headers(exc.headers)
            raise translate_riot_error(exc, operation_name) from exc
        except (aiohttp.ClientConnectionError, TimeoutError) as exc:
            LOGGER.warning(
                "Riot API %s failed due to a connection issue: %s: %s",
                operation_name,
                type(exc).__name__,
                exc,
            )
            raise RiotUnavailableError("Riot API is unavailable. Try again later.") from exc
        except RuntimeError as exc:
            if "session is None" not in str(exc):
                raise
            LOGGER.warning(
                "Riot API %s failed because the Pulsefire session was closed",
                operation_name,
            )
            raise RiotUnavailableError("Riot API client session is unavailable.") from exc

    async def get_account_by_riot_id(
        self,
        region: AccountRoutingRegion,
        game_name: str,
        tag_line: str,
    ) -> dict[str, Any]:
        return await self._request(
            "get_account_by_riot_id",
            lambda: self._client.get_account_v1_by_riot_id(
                region=region,
                game_name=game_name,
                tag_line=tag_line,
            ),
        )

    async def get_summoner_by_puuid(self, platform: PlatformRegion, puuid: str) -> dict[str, Any]:
        return await self._request(
            "get_summoner_by_puuid",
            lambda: self._client.get_lol_summoner_v4_by_puuid(region=platform, puuid=puuid),
        )

    async def get_champion_rotation(self, platform: PlatformRegion) -> dict[str, Any]:
        return await self._request(
            "get_champion_rotation",
            lambda: self._client.get_lol_champion_v3_rotation(region=platform),
        )

    async def get_lol_status(self, platform: PlatformRegion) -> dict[str, Any]:
        return await self._request(
            "get_lol_status",
            lambda: self._client.get_lol_status_v4_platform_data(region=platform),
        )

    async def get_ranked_entries_by_summoner_id(
        self,
        platform: PlatformRegion,
        summoner_id: str,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "get_ranked_entries_by_summoner_id",
            lambda: self._client.get_lol_league_v4_entries_by_summoner(
                region=platform,
                summoner_id=summoner_id,
            ),
        )

    async def get_ranked_entries_by_puuid(
        self,
        platform: PlatformRegion,
        puuid: str,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "get_ranked_entries_by_puuid",
            lambda: self._client.get_lol_league_v4_entries_by_puuid(
                region=platform,
                puuid=puuid,
            ),
        )

    async def get_match_ids(
        self,
        region: RoutingRegion,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        return await self._request(
            "get_match_ids",
            lambda: self._client.get_lol_match_v5_match_ids_by_puuid(
                region=region,
                puuid=puuid,
                queries={"start": start, "count": count},
            ),
        )

    async def get_match(self, region: RoutingRegion, match_id: str) -> dict[str, Any]:
        return await self._request(
            "get_match",
            lambda: self._client.get_lol_match_v5_match(region=region, id=match_id),
        )

    async def get_active_game_by_puuid(
        self,
        platform: PlatformRegion,
        puuid: str,
    ) -> dict[str, Any]:
        return await self._request(
            "get_active_game_by_puuid",
            lambda: self._client.get_lol_spectator_v5_active_game_by_summoner(
                region=platform,
                puuid=puuid,
            ),
        )

    async def get_featured_games(self, platform: PlatformRegion) -> dict[str, Any]:
        return await self._request(
            "get_featured_games",
            lambda: self._client.get_lol_spectator_v5_featured_games(region=platform),
        )


def translate_riot_error(exc: aiohttp.ClientResponseError, operation_name: str) -> RiotAPIError:
    status_code = exc.status
    LOGGER.warning("Riot API %s failed with HTTP %s", operation_name, status_code)

    if status_code == 404:
        return RiotNotFoundError("The requested Riot resource was not found.")
    if status_code in {401, 403}:
        return RiotForbiddenError("Riot API rejected the request. Check your API key and access.")
    if status_code == 429:
        return RiotRateLimitError("Riot API rate limit exceeded. Try again later.")
    if status_code >= 500:
        return RiotUnavailableError("Riot API is unavailable. Try again later.")
    return RiotAPIError(f"Riot API request failed with status {status_code}.")


_riot_client: RiotClient | None = None


async def get_riot_client() -> RiotClient:
    global _riot_client
    if _riot_client is None:
        _riot_client = RiotClient(settings.riot_api_key)
    await _riot_client.open()
    return _riot_client


async def close_riot_client() -> None:
    global _riot_client
    if _riot_client is not None:
        await _riot_client.close()
        _riot_client = None
