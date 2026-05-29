from fastapi import APIRouter

from app.api.routes import account, champion, matches, player, ranked, spectator, status, summoner

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(account.router)
v1_router.include_router(champion.router)
v1_router.include_router(summoner.router)
v1_router.include_router(ranked.router)
v1_router.include_router(matches.router)
v1_router.include_router(spectator.router)
v1_router.include_router(status.router)

v2_router = APIRouter(prefix="/api/v2")
v2_router.include_router(player.router)

api_router = APIRouter()
api_router.include_router(v1_router)
api_router.include_router(v2_router)
