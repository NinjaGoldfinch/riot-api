from pydantic import BaseModel, Field


class SummonerResponse(BaseModel):
    id: str | None = None
    account_id: str | None = Field(default=None, alias="accountId")
    puuid: str
    profile_icon_id: int = Field(alias="profileIconId")
    revision_date: int = Field(alias="revisionDate")
    summoner_level: int = Field(alias="summonerLevel")

    model_config = {"populate_by_name": True}
