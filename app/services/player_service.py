from app.clients.riot import RiotClient
from app.core.regions import AccountRoutingRegion, PlatformRegion, RoutingRegion
from app.schemas.player import PlayerSummaryResponse
from app.services.account_service import AccountService
from app.services.match_service import MatchService
from app.services.ranked_service import RankedService
from app.services.summoner_service import SummonerService


class PlayerService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._account_service = AccountService(riot_client)
        self._summoner_service = SummonerService(riot_client)
        self._ranked_service = RankedService(riot_client)
        self._match_service = MatchService(riot_client)

    async def get_summary(
        self,
        *,
        account_region: AccountRoutingRegion,
        platform_region: PlatformRegion,
        match_region: RoutingRegion,
        game_name: str,
        tag_line: str,
        match_start: int,
        match_count: int,
    ) -> PlayerSummaryResponse:
        account = await self._account_service.get_by_riot_id(
            account_region,
            game_name,
            tag_line,
        )
        summoner = await self._summoner_service.get_by_puuid(platform_region, account.puuid)
        ranked = await self._ranked_service.get_by_puuid(platform_region, account.puuid)
        recent_matches = await self._match_service.get_match_ids(
            match_region,
            account.puuid,
            start=match_start,
            count=match_count,
        )

        return PlayerSummaryResponse(
            account=account,
            summoner=summoner,
            ranked=ranked,
            recent_matches=recent_matches,
        )
