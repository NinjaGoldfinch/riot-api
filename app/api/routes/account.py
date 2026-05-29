from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import RoutingRegion, parse_routing_region
from app.schemas.account import AccountResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/{region}/{game_name}/{tag_line}", response_model=AccountResponse)
async def get_account_by_riot_id(
    region: str,
    game_name: str,
    tag_line: str,
    riot_client: RiotClient = Depends(get_riot_client),
) -> AccountResponse:
    routing_region: RoutingRegion = parse_routing_region(region)
    service = AccountService(riot_client)
    return await service.get_by_riot_id(routing_region, game_name, tag_line)
