from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.clients.riot import RiotClient, get_riot_client
from app.core.regions import (
    RoutingRegion,
    normalize_match_routing_region,
)
from app.schemas.matches import MatchDetailResponse, MatchHistoryResponse
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/{region}/detail/{match_id}", response_model=MatchDetailResponse)
async def get_match_detail(
    region: str,
    match_id: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
) -> MatchDetailResponse:
    routing_region: RoutingRegion = normalize_match_routing_region(region)
    service = MatchService(riot_client)
    return await service.get_match_detail(routing_region, match_id)


@router.get("/detail/{match_id}", include_in_schema=False)
async def get_match_detail_missing_region(match_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "INVALID_REGION",
                "message": (
                    "Match detail requests require a routing or platform region. "
                    f"Use /api/v1/matches/{{region}}/detail/{match_id}."
                ),
            }
        },
    )


@router.get("/{region}/{puuid}", response_model=MatchHistoryResponse)
async def get_match_history(
    region: str,
    puuid: str,
    riot_client: Annotated[RiotClient, Depends(get_riot_client)],
    start: Annotated[int, Query(ge=0)] = 0,
    count: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MatchHistoryResponse:
    routing_region: RoutingRegion = normalize_match_routing_region(region)
    service = MatchService(riot_client)
    return await service.get_match_ids(routing_region, puuid, start=start, count=count)
