from pydantic import BaseModel, Field


class ChampionRotationResponse(BaseModel):
    free_champion_ids: list[int] = Field(alias="freeChampionIds")
    free_champion_ids_for_new_players: list[int] = Field(alias="freeChampionIdsForNewPlayers")
    max_new_player_level: int = Field(alias="maxNewPlayerLevel")

    model_config = {"populate_by_name": True}
