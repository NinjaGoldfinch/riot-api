from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import (
    AccountRoutingRegion,
    PlatformRegion,
    RoutingRegion,
    normalize_account_routing_region,
    normalize_match_routing_region,
    parse_platform_region,
)
from app.schemas.player import PlayerSummaryResponse
from app.services.player_service import PlayerService

router = APIRouter(prefix="/player", tags=["Player"])


@router.get("/{platform}/{game_name}/{tag_line}/summary", response_model=PlayerSummaryResponse)
async def get_player_summary(
    platform: str,
    game_name: str,
    tag_line: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
    match_start: Annotated[int, Query(ge=0)] = 0,
    match_count: Annotated[int, Query(ge=1, le=20)] = 5,
) -> PlayerSummaryResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    account_region: AccountRoutingRegion = normalize_account_routing_region(platform_region)
    match_region: RoutingRegion = normalize_match_routing_region(platform_region)
    service = PlayerService(riot_client)
    return await service.get_summary(
        account_region=account_region,
        platform_region=platform_region,
        match_region=match_region,
        game_name=game_name,
        tag_line=tag_line,
        match_start=match_start,
        match_count=match_count,
    )
