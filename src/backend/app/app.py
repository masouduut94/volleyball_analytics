from src.backend.app.api.endpoints import cameras, nations, rallies, series, teams, videos, matches, players
from src.backend.app.db.engine import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/api/check")
def root():
    return {"message": "API is ok."}


app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(nations.router, prefix="/api/nations", tags=["nations"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(rallies.router, prefix="/api/rallies", tags=["rallies"])
app.include_router(series.router, prefix="/api/series", tags=["series"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
