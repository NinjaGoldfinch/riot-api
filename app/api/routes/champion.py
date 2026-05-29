from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import PlatformRegion, parse_platform_region
from app.schemas.champion import ChampionRotationResponse
from app.services.champion_service import ChampionService

router = APIRouter(prefix="/champion", tags=["Champion"])


@router.get("/{platform}/rotation", response_model=ChampionRotationResponse)
async def get_champion_rotation(
    platform: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> ChampionRotationResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = ChampionService(riot_client)
    return await service.get_rotation(platform_region)
