from typing_extensions import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models import models
from src.backend.app.schemas import matches, rallies

router = APIRouter()

match_crud = CRUDBase(models.Match)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[matches.MatchBaseSchema])
async def get_all_matches(db: Session = Depends(get_db)):
    matches = match_crud.get_all(db)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no match found.."
        )
    return matches


@router.get("/{match_id}", status_code=status.HTTP_200_OK, response_model=matches.MatchBaseSchema)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    match = match_crud.get(db=db, id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match with this id: `{match_id}` found"
        )
    return match


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=matches.MatchBaseSchema)
async def create_match(payload: matches.MatchCreateSchema, db: Session = Depends(get_db)):
    new_match = models.Match(**payload.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


@router.put("/{match_id}", status_code=status.HTTP_202_ACCEPTED, response_model=matches.MatchBaseSchema)
async def update_match(
        match_id: int, payload: matches.MatchCreateSchema, db: Session = Depends(get_db)
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


@router.get("/{match_id}/rallies", status_code=status.HTTP_200_OK,
            response_model=List[rallies.RallyBaseSchema])
async def get_all_rallies_for_this_match(match_id: int, db: Session = Depends(get_db)):
    match = match_crud.get(db=db, id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no match with this id: `{match_id}` found"
        )

    rallies = db.query(models.Rally).filter(models.Rally.match_id == match.id).all()
    if not len(rallies):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no rallies for this match id: {match.id} found"
        )
    rallies = sorted(rallies, key=lambda x: x.order)
    return rallies


@router.get("/{match_id}/rallies/{rally_order}", status_code=status.HTTP_200_OK,
            response_model=rallies.RallyBaseSchema)
async def get_this_rally_in_this_match(match_id: int, rally_order: int, db: Session = Depends(get_db)):
    match = match_crud.get(db=db, id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"match with this id: `{match_id}` not found"
        )

    rallies = db.query(models.Rally).filter(models.Rally.match_id == match.id).all()
    if not len(rallies) or rally_order > len(rallies):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the requested rally order_number for match: {match.id} not found"
        )
    rallies = sorted(rallies, key=lambda x: x.order)
    return rallies[rally_order]
