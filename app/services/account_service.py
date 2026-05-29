from app.clients.riot import RiotClient
from app.core.regions import RoutingRegion
from app.schemas.account import AccountResponse


class AccountService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_by_riot_id(
        self,
        region: RoutingRegion,
        game_name: str,
        tag_line: str,
    ) -> AccountResponse:
        account = await self._riot_client.get_account_by_riot_id(region, game_name, tag_line)
        return AccountResponse.model_validate(account)
