from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import PlatformRegion, parse_platform_region
from app.schemas.spectator import CurrentGameResponse, FeaturedGamesResponse
from app.services.spectator_service import SpectatorService

router = APIRouter(prefix="/spectator", tags=["Spectator"])


@router.get("/{platform}/featured", response_model=FeaturedGamesResponse)
async def get_featured_games(
    platform: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> FeaturedGamesResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = SpectatorService(riot_client)
    return await service.get_featured_games(platform_region)


@router.get("/{platform}/active/{puuid}", response_model=CurrentGameResponse)
async def get_active_game_by_puuid(
    platform: str,
    puuid: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> CurrentGameResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = SpectatorService(riot_client)
    return await service.get_active_game_by_puuid(platform_region, puuid)
