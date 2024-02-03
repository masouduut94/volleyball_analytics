from fastapi.middleware.cors import CORSMiddleware

from src.backend.app.api.endpoints import cameras, nations, rallies, series, teams  # , videos, players, matches
from src.backend.app.db.engine import engine, Base
# from src.backend.app.models import models
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/api/healthchecker")
def root():
    return {"message": "The API is LIVE!!"}


app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
# api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
app.include_router(nations.router, prefix="/api/nations", tags=["nations"])
# app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(rallies.router, prefix="/api/rallies", tags=["rallies"])
app.include_router(series.router, prefix="/api/series", tags=["series"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
# api_router.include_router(videos.router, prefix="/videos", tags=["videos"])


origins = [
    "http://localhost:8000",
]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )