from pydantic import BaseModel

from app.schemas.account import AccountResponse
from app.schemas.matches import MatchHistoryResponse
from app.schemas.ranked import RankedResponse
from app.schemas.summoner import SummonerResponse


class PlayerSummaryResponse(BaseModel):
    account: AccountResponse
    summoner: SummonerResponse
    ranked: RankedResponse
    recent_matches: MatchHistoryResponse
