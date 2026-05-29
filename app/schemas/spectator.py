from typing import Any

from pydantic import BaseModel, Field


class CurrentGameResponse(BaseModel):
    game_id: int = Field(alias="gameId")
    game_type: str = Field(alias="gameType")
    game_start_time: int = Field(alias="gameStartTime")
    map_id: int = Field(alias="mapId")
    game_length: int = Field(alias="gameLength")
    platform_id: str = Field(alias="platformId")
    game_mode: str = Field(alias="gameMode")
    banned_champions: list[dict[str, Any]] = Field(alias="bannedChampions")
    game_queue_config_id: int | None = Field(default=None, alias="gameQueueConfigId")
    participants: list[dict[str, Any]]
    observers: dict[str, Any]

    model_config = {"populate_by_name": True}


class FeaturedGamesResponse(BaseModel):
    game_list: list[dict[str, Any]] = Field(alias="gameList")
    client_refresh_interval: int = Field(alias="clientRefreshInterval")

    model_config = {"populate_by_name": True}
