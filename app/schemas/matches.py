from typing import Any

from pydantic import BaseModel


class MatchHistoryResponse(BaseModel):
    match_ids: list[str]


class MatchParticipantResponse(BaseModel):
    puuid: str
    riot_id_game_name: str | None = None
    riot_id_tagline: str | None = None
    summoner_name: str | None = None
    champion_name: str | None = None
    champion_id: int | None = None
    team_id: int | None = None
    team_position: str | None = None
    kills: int
    deaths: int
    assists: int
    kda: float
    win: bool
    gold_earned: int | None = None
    total_damage_dealt_to_champions: int | None = None
    vision_score: int | None = None
    items: list[int]


class MatchDetailResponse(BaseModel):
    match_id: str
    game_creation: int | None = None
    game_duration: int | None = None
    game_mode: str | None = None
    queue_id: int | None = None
    map_id: int | None = None
    game_version: str | None = None
    winning_team_id: int | None = None
    participants: list[MatchParticipantResponse]
    raw: dict[str, Any] | None = None
