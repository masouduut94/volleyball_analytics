from typing_extensions import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Match
from src.backend.app.schemas.matches import MatchBaseSchema, MatchCreateSchema

router = APIRouter()

match_crud = CRUDBase(Match)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[MatchBaseSchema])
async def get_all_matches(db: Session = Depends(get_db)):
    matches = match_crud.get_all(db)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match found.."
        )
    return matches


@router.get("/{match_id}", status_code=status.HTTP_200_OK, response_model=MatchBaseSchema)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    match = match_crud.get(db=db, id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match with this id: `{match_id}` found"
        )
    return match


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MatchBaseSchema)
async def create_match(payload: MatchCreateSchema, db: Session = Depends(get_db)):
    new_match = Match(**payload.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


@router.put("/{match_id}", status_code=status.HTTP_202_ACCEPTED, response_model=MatchBaseSchema)
async def update_match(
        match_id: int, payload: MatchCreateSchema, db: Session = Depends(get_db)
):
    db_match = match_crud.get(db=db, id=match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match with this id: {match_id} found .....",
        )
    updated_match = match_crud.update(db=db, db_obj=db_match, obj_in=payload)
    return updated_match


@router.delete("/{match_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = match_crud.get(db=db, id=match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match with this id: {match_id} found .....",
        )
    match_crud.remove(db=db, id=match_id)
    return {"status": "success", "message": "Item removed successfully"}
