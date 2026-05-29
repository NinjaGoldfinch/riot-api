from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import PlatformRegion
from app.schemas.spectator import CurrentGameResponse, FeaturedGamesResponse


class SpectatorService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_active_game_by_puuid(
        self,
        platform: PlatformRegion,
        puuid: str,
    ) -> CurrentGameResponse:
        cache_key = f"spectator-active:{platform}:{puuid}"

        async def fetch_active_game() -> CurrentGameResponse:
            game = await self._riot_client.get_active_game_by_puuid(platform, puuid)
            return CurrentGameResponse.model_validate(game)

        return await cache.get_or_set(
            cache_key,
            settings.spectator_active_game_cache_ttl_seconds,
            fetch_active_game,
        )

    async def get_featured_games(self, platform: PlatformRegion) -> FeaturedGamesResponse:
        cache_key = f"spectator-featured:{platform}"

        async def fetch_featured_games() -> FeaturedGamesResponse:
            games = await self._riot_client.get_featured_games(platform)
            return FeaturedGamesResponse.model_validate(games)

        return await cache.get_or_set(
            cache_key,
            settings.spectator_featured_games_cache_ttl_seconds,
            fetch_featured_games,
        )
