from pydantic import BaseModel, Field


class SummonerResponse(BaseModel):
    id: str
    account_id: str = Field(alias="accountId")
    puuid: str
    profile_icon_id: int = Field(alias="profileIconId")
    revision_date: int = Field(alias="revisionDate")
    summoner_level: int = Field(alias="summonerLevel")

    model_config = {"populate_by_name": True}
