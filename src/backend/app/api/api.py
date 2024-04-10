from fastapi import APIRouter

from src.backend.app.api.endpoints import cameras, matches, nations, players, rallies, series, teams, videos

api_router = APIRouter()
api_router.include_router(cameras.router, prefix="/cameras", tags=["camera"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(nations.router, prefix="/nations", tags=["nations"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(rallies.router, prefix="/rallies", tags=["rallies"])
api_router.include_router(series.router, prefix="/series", tags=["series"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
