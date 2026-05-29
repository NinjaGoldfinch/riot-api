from typing import Any

from pydantic import BaseModel


class MatchHistoryResponse(BaseModel):
    match_ids: list[str]


class MatchParticipantResponse(BaseModel):
    puuid: str
    summoner_name: str | None = None
    champion_name: str
    kills: int
    deaths: int
    assists: int
    win: bool


class MatchDetailResponse(BaseModel):
    match_id: str
    game_creation: int | None = None
    game_duration: int | None = None
    game_mode: str | None = None
    queue_id: int | None = None
    participants: list[MatchParticipantResponse]
    raw: dict[str, Any] | None = None
