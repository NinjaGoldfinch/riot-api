from typing import Any

from app.clients.riot import RiotClient
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
        match_ids = await self._riot_client.get_match_ids(region, puuid, start, count)
        return MatchHistoryResponse(match_ids=match_ids)

    async def get_match_detail(self, region: RoutingRegion, match_id: str) -> MatchDetailResponse:
        match = await self._riot_client.get_match(region, match_id)
        metadata = match.get("metadata", {})
        info = match.get("info", {})
        participants = [
            self._normalize_participant(participant)
            for participant in info.get("participants", [])
        ]
        return MatchDetailResponse(
            match_id=metadata.get("matchId", match_id),
            game_creation=info.get("gameCreation"),
            game_duration=info.get("gameDuration"),
            game_mode=info.get("gameMode"),
            queue_id=info.get("queueId"),
            participants=participants,
        )

    @staticmethod
    def _normalize_participant(participant: dict[str, Any]) -> MatchParticipantResponse:
        return MatchParticipantResponse(
            puuid=participant["puuid"],
            summoner_name=participant.get("summonerName") or participant.get("riotIdGameName"),
            champion_name=participant["championName"],
            kills=participant.get("kills", 0),
            deaths=participant.get("deaths", 0),
            assists=participant.get("assists", 0),
            win=participant.get("win", False),
        )
