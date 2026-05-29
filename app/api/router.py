from fastapi import APIRouter

from app.api.routes import account, matches, ranked, summoner

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(account.router)
api_router.include_router(summoner.router)
api_router.include_router(ranked.router)
api_router.include_router(matches.router)
