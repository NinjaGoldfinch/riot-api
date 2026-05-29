from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import PlatformRegion, parse_platform_region
from app.schemas.status import PlatformStatusResponse
from app.services.status_service import StatusService

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/{platform}", response_model=PlatformStatusResponse)
async def get_lol_status(
    platform: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> PlatformStatusResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = StatusService(riot_client)
    return await service.get_platform_data(platform_region)
