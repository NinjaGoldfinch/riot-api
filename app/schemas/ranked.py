from pydantic import BaseModel


class RankedEntryResponse(BaseModel):
    queue_type: str
    tier: str | None = None
    rank: str | None = None
    league_points: int
    wins: int
    losses: int
    win_rate: float


class RankedResponse(BaseModel):
    queues: list[RankedEntryResponse]
