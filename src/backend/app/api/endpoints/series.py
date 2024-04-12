from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models import models
from src.backend.app.schemas import series, matches

router = APIRouter()

series_crud = CRUDBase(models.Series)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[series.SeriesBaseSchema])
async def get_all_series(db: Session = Depends(get_db)):
    series = series_crud.get_all(db)
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Series found.."
        )
    return series


@router.get("/{series_id}", status_code=status.HTTP_200_OK, response_model=series.SeriesBaseSchema)
async def get_series(series_id: int, db: Session = Depends(get_db)):
    series = series_crud.get(db=db, id=series_id)
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Series with this id: `{series_id}` found"
        )
    return series


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=series.SeriesBaseSchema)
async def create_series(payload: series.SeriesCreateSchema, db: Session = Depends(get_db)):
    new_series = models.Series(**payload.model_dump())
    db.add(new_series)
    db.commit()
    db.refresh(new_series)
    return new_series


@router.put("/{series_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_series(
        series_id: int, payload: series.SeriesCreateSchema, db: Session = Depends(get_db)
):
    db_series = series_crud.get(db=db, id=series_id)
    if not db_series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Series with this id: {series_id} found .....",
        )
    updated_series = series_crud.update(db=db, db_obj=db_series, obj_in=payload)
    return updated_series


@router.delete("/{series_id}", status_code=status.HTTP_200_OK)
async def delete_series(series_id: int, db: Session = Depends(get_db)):
    db_series = series_crud.get(db=db, id=series_id)
    if not db_series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Series with this id: {series_id} found .....",
        )
    series_crud.remove(db=db, id=series_id)
    return {"status": "success", "message": "Item removed successfully"}


@router.get("/{series_id}/matches", status_code=status.HTTP_200_OK,
            response_model=List[matches.MatchBaseSchema])
async def get_all_matches_for_this_series(series_id: int, db: Session = Depends(get_db)):
    tournament = series_crud.get(db=db, id=series_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no series with this id: `{series_id}` found"
        )

    matches_ = db.query(models.Match).filter(models.Match.series_id == tournament.id).all()
    if not len(matches_):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no matches for this series id: {tournament.id} found"
        )

    return matches_
