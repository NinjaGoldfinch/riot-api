from fastapi import APIRouter, Depends, Query

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import RoutingRegion, parse_routing_region
from app.schemas.matches import MatchDetailResponse, MatchHistoryResponse
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/{region}/{puuid}", response_model=MatchHistoryResponse)
async def get_match_history(
    region: str,
    puuid: str,
    start: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=1, le=100),
    riot_client: RiotClient = Depends(get_riot_client),
) -> MatchHistoryResponse:
    routing_region: RoutingRegion = parse_routing_region(region)
    service = MatchService(riot_client)
    return await service.get_match_ids(routing_region, puuid, start=start, count=count)


@router.get("/{region}/detail/{match_id}", response_model=MatchDetailResponse)
async def get_match_detail(
    region: str,
    match_id: str,
    riot_client: RiotClient = Depends(get_riot_client),
) -> MatchDetailResponse:
    routing_region: RoutingRegion = parse_routing_region(region)
    service = MatchService(riot_client)
    return await service.get_match_detail(routing_region, match_id)
