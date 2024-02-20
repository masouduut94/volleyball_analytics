from typing_extensions import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Player
from src.backend.app.schemas.players import PlayerCreateSchema, PlayerBaseSchema

router = APIRouter()

player_crud = CRUDBase(Player)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[PlayerBaseSchema])
async def get_all_players(db: Session = Depends(get_db)):
    players = player_crud.get_all(db)
    if not players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Player found.."
        )
    return players


@router.get("/{player_id}", status_code=status.HTTP_200_OK, response_model=PlayerBaseSchema)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    player = player_crud.get(db=db, id=player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Player with this id: `{player_id}` found"
        )
    return player


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PlayerBaseSchema)
async def create_player(payload: PlayerCreateSchema, db: Session = Depends(get_db)):
    new_player = Player(**payload.model_dump())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@router.put("/{player_id}", status_code=status.HTTP_202_ACCEPTED, response_model=PlayerBaseSchema)
async def update_player(
        player_id: int, payload: PlayerCreateSchema, db: Session = Depends(get_db)
):
    db_player = player_crud.get(db=db, id=player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Player with this id: {player_id} found .....",
        )
    updated_player = player_crud.update(db=db, db_obj=db_player, obj_in=payload)
    return updated_player


@router.delete("/{player_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_player(player_id: int, db: Session = Depends(get_db)):
    db_player = player_crud.get(db=db, id=player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Player with this id: {player_id} found .....",
        )
    player_crud.remove(db=db, id=player_id)
    return {"status": "success", "message": "item removed successfully"}
