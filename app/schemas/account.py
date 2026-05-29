from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    puuid: str
    game_name: str = Field(alias="gameName")
    tag_line: str = Field(alias="tagLine")

    model_config = {"populate_by_name": True}
