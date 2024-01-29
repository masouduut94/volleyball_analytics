from typing import List

import sqlalchemy.orm
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.schemas import (TeamBaseSchema, NationBaseSchema, PlayerData, VideoData, MatchData, ServiceData, RallyData,
                         SeriesData,
                         CameraData, ListTeamSchema)

from api.database import Session, Base, engine, get_db
from api.models import Team, Nation, Player, Series, Camera, Video, Match, Rally
from fastapi.middleware.cors import CORSMiddleware

# ######################################### Defining APIs #######################
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
app = FastAPI(debug=False)


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


# ############ TEAM

# TODO: Add /api/ to all paths
@app.get('/team/{team_id}', status_code=status.HTTP_200_OK)
async def get_team_by_id(team_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team not found")
    return TeamBaseSchema.model_validate(team).model_dump()


@app.get('/team/', status_code=status.HTTP_200_OK)
async def get_all_teams(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    teams = db.query(Team).all()
    # return ListTeamSchema.model_validate(teams).model_dump()
    return [TeamBaseSchema.model_validate(team).model_dump() for team in teams]


@app.post('/team/', status_code=status.HTTP_201_CREATED)
async def create_team(team_data: TeamBaseSchema, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_team = Team(**team_data.model_dump(exclude={"id"}))
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return TeamBaseSchema.model_validate(new_team).model_dump()


@app.delete('/team/{team_id}', status_code=status.HTTP_200_OK)
async def delete_team_by_id(team_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team not found")
    db.delete(team)
    db.commit()
    return {"ok": True}


# @app.put("/team/{team_id}")
# async def update_team(team_id: int, team_data: TeamData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
#     team = db.get(Team, team_id)
#     if not team:
#         raise HTTPException(status_code=404, detail="team not found")
#
#     stored_item_model = TeamData(**stored_item_data)
#     update_data = item.dict(exclude_unset=True)
#     updated_item = stored_item_model.copy(update=update_data)
#     items[item_id] = jsonable_encoder(updated_item)
#     update_item_encoded = jsonable_encoder(team)
#     items[item_id] = update_item_encoded
#     return update_item_encoded



# ############ NATION


@app.get('/nation/{nation_id}')
async def get_nation_by_id(nation_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    nation = db.get(Nation, nation_id)
    if not nation:
        raise HTTPException(status_code=404, detail="Nation not found")
    return NationBaseSchema.model_validate(nation).model_dump()


@app.get('/nation/')
async def get_all_nations(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    nations = db.query(Nation).all()
    return [NationBaseSchema.model_validate(nation).model_dump() for nation in nations]


@app.post('/nation/', status_code=status.HTTP_201_CREATED)
async def create_nation(nation_data: NationBaseSchema, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_nation = Nation(**nation_data.model_dump(exclude={"id"}))
    db.add(new_nation)
    db.commit()
    db.refresh(new_nation)
    return NationBaseSchema.model_validate(new_nation).model_dump()


@app.delete('/nation/{nation_id}')
async def delete_nation_by_id(nation_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    nation = db.get(Nation, nation_id)
    if not nation:
        raise HTTPException(status_code=404, detail="Nation not found")
    db.delete(nation)
    db.commit()
    return {"ok": True}


# ############### PLAYER


@app.get('/player/{player_id}')
async def get_player_by_id(player_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerData.model_validate(player).model_dump()


@app.get('/player/')
async def get_all_players(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    players = db.query(Player).all()
    return [PlayerData.model_validate(player).model_dump() for player in players]


@app.post('/player/', status_code=status.HTTP_201_CREATED)
async def create_player(player_data: PlayerData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_player = Player(**player_data.model_dump(exclude={"id"}))
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return PlayerData.model_validate(new_player).model_dump()


@app.delete('/player/{player_id}')
async def delete_player_by_id(player_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    player = db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    db.commit()
    return {"ok": True}


# ################# SERIES


@app.get('/series/{series_id}')
async def get_series_by_id(series_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    series = db.get(Series, series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    return SeriesData.model_validate(series).model_dump()


@app.get('/series/')
async def get_all_series(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    series = db.query(Series).all()
    return [SeriesData.model_validate(s).model_dump() for s in series]


@app.post('/series/', status_code=status.HTTP_201_CREATED)
async def create_series(series_data: SeriesData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_serie = Series(**series_data.model_dump(exclude={"id"}))
    db.add(new_serie)
    db.commit()
    db.refresh(new_serie)
    return SeriesData.model_validate(new_serie).model_dump()


@app.delete('/series/{series_id}')
async def delete_series_by_id(series_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    series = db.get(Series, series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    db.delete(series)
    db.commit()
    return {"ok": True}

# ################# CAMERA


@app.get('/camera/{camera_id}')
async def get_camera_by_id(camera_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    camera = db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return CameraData.model_validate(camera).model_dump()


@app.get('/camera/')
async def get_all_camera(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    camera = db.query(Camera).all()
    return [CameraData.model_validate(c).model_dump() for c in camera]


@app.post('/camera/', status_code=status.HTTP_201_CREATED)
async def create_camera(camera_data: CameraData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_camera = Camera(**camera_data.model_dump(exclude={"id"}))
    print(new_camera)
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return CameraData.model_validate(new_camera).model_dump()


@app.delete('/camera/{camera_id}')
async def delete_camera_by_id(camera_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    camera = db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(camera)
    db.commit()
    return {"ok": True}


# ################# VIDEO


@app.get('/video/{video_id}')
async def get_video_by_id(video_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoData.model_validate(video).model_dump()


@app.get('/video/')
async def get_all_video(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    video = db.query(Video).all()
    return [VideoData.model_validate(c).model_dump() for c in video]


@app.post('/video/', status_code=status.HTTP_201_CREATED)
async def create_video(video_data: VideoData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_video = Video(**video_data.model_dump(exclude={"id"}))
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return VideoData.model_validate(new_video).model_dump()


@app.delete('/video/{video_id}')
async def delete_video_by_id(video_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(video)
    db.commit()
    return {"ok": True}


# ################# MATCH


@app.get('/match/{match_id}')
async def get_match_by_id(match_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="match not found")
    return MatchData.model_validate(match).model_dump()


@app.get('/match/')
async def get_all_match(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    match = db.query(Match).all()
    return [MatchData.model_validate(c).model_dump() for c in match]


@app.post('/match/', status_code=status.HTTP_201_CREATED)
async def create_match(match_data: MatchData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_match = Match(**match_data.model_dump(exclude={"id"}))
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return MatchData.model_validate(new_match).model_dump()


@app.delete('/match/{match_id}')
async def delete_match_by_id(match_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="match not found")
    db.delete(match)
    db.commit()
    return {"ok": True}


# ################# RALLY


@app.get('/rally/{rally_id}')
async def get_rally_by_id(rally_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    rally = db.get(Rally, rally_id)
    if not rally:
        raise HTTPException(status_code=404, detail="rally not found")
    return RallyData.model_validate(rally).model_dump()


@app.get('/rally/')
async def get_all_rally(db: sqlalchemy.orm.Session = Depends(get_db)) -> List[dict]:
    rally = db.query(Rally).all()
    return [RallyData.model_validate(c).model_dump() for c in rally]


@app.post('/rally/', status_code=status.HTTP_201_CREATED)
async def create_rally(rally_data: RallyData, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    new_rally = Rally(**rally_data.model_dump(exclude={"id"}))
    db.add(new_rally)
    db.commit()
    db.refresh(new_rally)
    return RallyData.model_validate(new_rally).model_dump()


@app.delete('/rally/{rally_id}')
async def delete_rally_by_id(rally_id: int, db: sqlalchemy.orm.Session = Depends(get_db)) -> dict:
    rally = db.get(Rally, rally_id)
    if not rally:
        raise HTTPException(status_code=404, detail="Rally not found")
    db.delete(rally)
    db.commit()
    return {"ok": True}


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


