from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Team
from src.backend.app.schemas.teams import TeamBaseSchema, TeamCreateSchema

router = APIRouter()

team_crud = CRUDBase(Team)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TeamBaseSchema])
async def get_all_teams(db: Session = Depends(get_db)):
    teams = team_crud.get_all(db)
    if not teams:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Team found.."
        )
    return teams


@router.get("/{team_id}", status_code=status.HTTP_200_OK, response_model=TeamBaseSchema)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    team = team_crud.get(db=db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Team with this id: `{team_id}` found"
        )
    return team


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TeamBaseSchema)
async def create_team(payload: TeamCreateSchema, db: Session = Depends(get_db)):
    new_team = Team(**payload.model_dump())
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


@router.put("/{team_id}", status_code=status.HTTP_202_ACCEPTED, response_model=TeamBaseSchema)
async def update_team(
        team_id: int, payload: TeamCreateSchema, db: Session = Depends(get_db)
):
    db_team = team_crud.get(db=db, id=team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Team with this id: {team_id} found .....",
        )
    updated_team = team_crud.update(db=db, db_obj=db_team, obj_in=payload)
    return updated_team


@router.delete("/{team_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    db_team = team_crud.get(db=db, id=team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Team with this id: {team_id} found .....",
        )
    team_crud.remove(db=db, id=team_id)
    return {"status": "success", "message": "Item removed successfully"}
