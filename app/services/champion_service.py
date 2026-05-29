from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import PlatformRegion
from app.schemas.champion import ChampionRotationResponse


class ChampionService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_rotation(self, platform: PlatformRegion) -> ChampionRotationResponse:
        cache_key = f"champion-rotation:{platform}"

        async def fetch_rotation() -> ChampionRotationResponse:
            rotation = await self._riot_client.get_champion_rotation(platform)
            return ChampionRotationResponse.model_validate(rotation)

        return await cache.get_or_set(
            cache_key,
            settings.champion_rotation_cache_ttl_seconds,
            fetch_rotation,
        )
