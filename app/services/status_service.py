from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import PlatformRegion
from app.schemas.status import PlatformStatusResponse


class StatusService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_platform_data(self, platform: PlatformRegion) -> PlatformStatusResponse:
        cache_key = f"lol-status:{platform}"

        async def fetch_status() -> PlatformStatusResponse:
            platform_data = await self._riot_client.get_lol_status(platform)
            return PlatformStatusResponse.model_validate(platform_data)

        return await cache.get_or_set(
            cache_key,
            settings.status_cache_ttl_seconds,
            fetch_status,
        )
