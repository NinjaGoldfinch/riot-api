from fastapi import APIRouter, Depends

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import PlatformRegion, parse_platform_region
from app.schemas.summoner import SummonerResponse
from app.services.summoner_service import SummonerService

router = APIRouter(prefix="/summoner", tags=["Summoner"])


@router.get("/{platform}/{puuid}", response_model=SummonerResponse)
async def get_summoner_by_puuid(
    platform: str,
    puuid: str,
    riot_client: RiotClient = Depends(get_riot_client),
) -> SummonerResponse:
    platform_region: PlatformRegion = parse_platform_region(platform)
    service = SummonerService(riot_client)
    return await service.get_by_puuid(platform_region, puuid)
