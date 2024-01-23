from fastapi import FastAPI
from .models import Match
from .schemas import MatchData

app = FastAPI()


@app.get('/match/{match_id}')
async def get_item(match_id: int):
    new = Match.get(match_id)
    res = MatchData.model_validate(new).model_dump()
    return res


# @app.get('/matches')
# async def create(match: MatchData):
#     new = Match(match.model_dump())
