from typing import Any

from pulsefire.clients import RiotAPIClient

from app.core.config import settings
from app.core.errors import ConfigurationError
from app.core.regions import PlatformRegion, RoutingRegion


class RiotClient:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ConfigurationError("RIOT_API_KEY is required.")
        self._client = RiotAPIClient(default_headers={"X-Riot-Token": api_key})

    async def close(self) -> None:
        close = getattr(self._client, "close", None)
        if close is not None:
            result = close()
            if result is not None:
                await result

    async def get_account_by_riot_id(
        self,
        region: RoutingRegion,
        game_name: str,
        tag_line: str,
    ) -> dict[str, Any]:
        return await self._client.get_account_v1_by_riot_id(
            region=region,
            game_name=game_name,
            tag_line=tag_line,
        )

    async def get_summoner_by_puuid(self, platform: PlatformRegion, puuid: str) -> dict[str, Any]:
        return await self._client.get_lol_summoner_v4_by_puuid(region=platform, puuid=puuid)

    async def get_ranked_entries_by_summoner_id(
        self,
        platform: PlatformRegion,
        summoner_id: str,
    ) -> list[dict[str, Any]]:
        return await self._client.get_lol_league_v4_entries_by_summoner(
            region=platform,
            summoner_id=summoner_id,
        )

    async def get_match_ids(
        self,
        region: RoutingRegion,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        return await self._client.get_lol_match_v5_match_ids_by_puuid(
            region=region,
            puuid=puuid,
            queries={"start": start, "count": count},
        )

    async def get_match(self, region: RoutingRegion, match_id: str) -> dict[str, Any]:
        return await self._client.get_lol_match_v5_match(region=region, id=match_id)


_riot_client: RiotClient | None = None


async def get_riot_client() -> RiotClient:
    global _riot_client
    if _riot_client is None:
        _riot_client = RiotClient(settings.riot_api_key)
    return _riot_client


async def close_riot_client() -> None:
    global _riot_client
    if _riot_client is not None:
        await _riot_client.close()
        _riot_client = None
