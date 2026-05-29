from app.clients.riot import RiotClient
from app.core.cache import cache
from app.core.config import settings
from app.core.regions import AccountRoutingRegion
from app.schemas.account import AccountResponse


class AccountService:
    def __init__(self, riot_client: RiotClient) -> None:
        self._riot_client = riot_client

    async def get_by_riot_id(
        self,
        region: AccountRoutingRegion,
        game_name: str,
        tag_line: str,
    ) -> AccountResponse:
        cache_key = f"account:{region}:{game_name.lower()}:{tag_line.lower()}"

        async def fetch_account() -> AccountResponse:
            account = await self._riot_client.get_account_by_riot_id(region, game_name, tag_line)
            return AccountResponse.model_validate(account)

        return await cache.get_or_set(
            cache_key,
            settings.account_cache_ttl_seconds,
            fetch_account,
        )
