from typing import Any

from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import RoutingRegion
from app.schemas.matches import (
    MatchDetailResponse,
    MatchHistoryResponse,
    MatchParticipantResponse,
)


class MatchService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_match_ids(
        self,
        region: RoutingRegion,
        puuid: str,
        start: int,
        count: int,
    ) -> MatchHistoryResponse:
        cache_key = f"match-history:{region}:{puuid}:{start}:{count}"

        async def fetch_match_ids() -> MatchHistoryResponse:
            match_ids = await self._riot_client.get_match_ids(region, puuid, start, count)
            return MatchHistoryResponse(match_ids=match_ids)

        return await cache.get_or_set(
            cache_key,
            settings.match_history_cache_ttl_seconds,
            fetch_match_ids,
        )

    async def get_match_detail(self, region: RoutingRegion, match_id: str) -> MatchDetailResponse:
        cache_key = f"match-detail:{region}:{match_id}"

        async def fetch_match_detail() -> MatchDetailResponse:
            match = await self._riot_client.get_match(region, match_id)
            return self._normalize_match_detail(match, match_id)

        return await cache.get_or_set(
            cache_key,
            settings.match_detail_cache_ttl_seconds,
            fetch_match_detail,
        )

    def _normalize_match_detail(self, match: dict[str, Any], match_id: str) -> MatchDetailResponse:
        metadata = match.get("metadata", {})
        info = match.get("info", {})
        participants = [
            self._normalize_participant(participant) for participant in info.get("participants", [])
        ]
        return MatchDetailResponse(
            match_id=metadata.get("matchId", match_id),
            game_creation=info.get("gameCreation"),
            game_duration=info.get("gameDuration"),
            game_mode=info.get("gameMode"),
            queue_id=info.get("queueId"),
            map_id=info.get("mapId"),
            game_version=info.get("gameVersion"),
            winning_team_id=self._winning_team_id(info.get("teams", [])),
            participants=participants,
        )

    @staticmethod
    def _normalize_participant(participant: dict[str, Any]) -> MatchParticipantResponse:
        kills = participant.get("kills", 0)
        deaths = participant.get("deaths", 0)
        assists = participant.get("assists", 0)
        return MatchParticipantResponse(
            puuid=participant.get("puuid", ""),
            riot_id_game_name=participant.get("riotIdGameName"),
            riot_id_tagline=participant.get("riotIdTagline"),
            summoner_name=participant.get("summonerName") or participant.get("riotIdGameName"),
            champion_name=participant.get("championName"),
            champion_id=participant.get("championId"),
            team_id=participant.get("teamId"),
            team_position=participant.get("teamPosition"),
            kills=kills,
            deaths=deaths,
            assists=assists,
            kda=MatchService._calculate_kda(kills, deaths, assists),
            win=participant.get("win", False),
            gold_earned=participant.get("goldEarned"),
            total_damage_dealt_to_champions=participant.get("totalDamageDealtToChampions"),
            vision_score=participant.get("visionScore"),
            items=[
                participant.get(f"item{slot}", 0)
                for slot in range(7)
                if participant.get(f"item{slot}", 0) != 0
            ],
        )

    @staticmethod
    def _calculate_kda(kills: int, deaths: int, assists: int) -> float:
        if deaths == 0:
            return float(kills + assists)
        return round((kills + assists) / deaths, 2)

    @staticmethod
    def _winning_team_id(teams: list[dict[str, Any]]) -> int | None:
        for team in teams:
            if team.get("win"):
                return team.get("teamId")
        return None
