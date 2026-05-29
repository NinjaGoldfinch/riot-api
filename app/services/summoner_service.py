from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import PlatformRegion
from app.schemas.summoner import SummonerResponse


class SummonerService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_by_puuid(self, platform: PlatformRegion, puuid: str) -> SummonerResponse:
        cache_key = f"summoner:{platform}:{puuid}"

        async def fetch_summoner() -> SummonerResponse:
            summoner = await self._riot_client.get_summoner_by_puuid(platform, puuid)
            return SummonerResponse.model_validate(summoner)

        return await cache.get_or_set(
            cache_key,
            settings.summoner_cache_ttl_seconds,
            fetch_summoner,
        )
