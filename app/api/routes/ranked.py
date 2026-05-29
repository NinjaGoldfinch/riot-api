from typing import Annotated

from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import PlatformRegion, parse_platform_region
from app.schemas.ranked import RankedResponse
from app.services.ranked_service import RankedService

router = APIRouter(prefix="/ranked", tags=["Ranked"])


@router.get("/{platform}/{puuid}", response_model=RankedResponse)
async def get_ranked_entries_by_puuid(
    platform: str,
    puuid: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> RankedResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = RankedService(riot_client)
    return await service.get_by_puuid(platform_region, puuid)


@router.get("/summoner-id/{platform}/{summoner_id}", response_model=RankedResponse)
async def get_ranked_entries_by_summoner_id(
    platform: str,
    summoner_id: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> RankedResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = RankedService(riot_client)
    return await service.get_by_summoner_id(platform_region, summoner_id)
