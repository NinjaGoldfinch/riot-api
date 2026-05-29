from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import PlatformRegion
from app.schemas.ranked import RankedEntryResponse, RankedResponse


class RankedService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_by_summoner_id(
        self,
        platform: PlatformRegion,
        summoner_id: str,
    ) -> RankedResponse:
        cache_key = f"ranked:summoner-id:{platform}:{summoner_id}"

        async def fetch_ranked() -> RankedResponse:
            entries = await self._riot_client.get_ranked_entries_by_summoner_id(
                platform,
                summoner_id,
            )
            return RankedResponse(queues=[self._normalize_entry(entry) for entry in entries])

        return await cache.get_or_set(
            cache_key,
            settings.ranked_cache_ttl_seconds,
            fetch_ranked,
        )

    async def get_by_puuid(
        self,
        platform: PlatformRegion,
        puuid: str,
    ) -> RankedResponse:
        cache_key = f"ranked:puuid:{platform}:{puuid}"

        async def fetch_ranked() -> RankedResponse:
            entries = await self._riot_client.get_ranked_entries_by_puuid(platform, puuid)
            return RankedResponse(queues=[self._normalize_entry(entry) for entry in entries])

        return await cache.get_or_set(
            cache_key,
            settings.ranked_cache_ttl_seconds,
            fetch_ranked,
        )

    @staticmethod
    def _normalize_entry(entry: dict) -> RankedEntryResponse:
        wins = entry.get("wins", 0)
        losses = entry.get("losses", 0)
        total_games = wins + losses
        win_rate = round((wins / total_games) * 100, 2) if total_games else 0.0
        return RankedEntryResponse(
            queue_type=entry["queueType"],
            tier=entry.get("tier"),
            rank=entry.get("rank"),
            league_points=entry.get("leaguePoints", 0),
            wins=wins,
            losses=losses,
            win_rate=win_rate,
        )
