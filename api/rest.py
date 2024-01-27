from fastapi import FastAPI
from api.database import db_setup, Team, Nation, Player, Series, Camera, Match, Video, Rally
from .schemas import (TeamData, NationData, PlayerData, VideoData, MatchData, ServiceData, RallyData, SeriesData,
                      CameraData)

app = FastAPI()
mode = 'test'
session, engine = db_setup(mode=mode)


@app.get('/match/{match_id}')
async def get_item(match_id: int):
    new = Match.get(session, match_id)
    res = MatchData.model_validate(new).model_dump()
    return res

# @app.get('/matches')
# async def create(match: MatchData):
#     new = Match(match.model_dump())
