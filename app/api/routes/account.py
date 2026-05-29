from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.config import settings
from app.core.regions import AccountRoutingRegion, normalize_account_routing_region
from app.schemas.account import AccountResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/{game_name}/{tag_line}", response_model=AccountResponse)
async def get_account_by_riot_id_with_default_region(
    game_name: str,
    tag_line: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> AccountResponse:
    routing_region: AccountRoutingRegion = normalize_account_routing_region(
        settings.default_routing_region
    )
    service = AccountService(riot_client)
    return await service.get_by_riot_id(routing_region, game_name, tag_line)


@router.get("/{region}/{game_name}/{tag_line}", response_model=AccountResponse)
async def get_account_by_riot_id(
    region: str,
    game_name: str,
    tag_line: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> AccountResponse:
    routing_region: AccountRoutingRegion = normalize_account_routing_region(region)
    service = AccountService(riot_client)
    return await service.get_by_riot_id(routing_region, game_name, tag_line)
