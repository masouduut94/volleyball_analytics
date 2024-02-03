from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Series
from src.backend.app.schemas.series import SeriesBaseSchema

router = APIRouter()

series_crud = CRUDBase(Series)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[SeriesBaseSchema])
async def get_all_series(db: Session = Depends(get_db)):
    series = series_crud.get_all(db)
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Series found.."
        )
    return series


@router.get("/{series_id}", status_code=status.HTTP_200_OK, response_model=SeriesBaseSchema)
async def get_series(series_id: int, db: Session = Depends(get_db)):
    series = series_crud.get(db=db, id=series_id)
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Series with this id: `{series_id}` found"
        )
    return series


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SeriesBaseSchema)
async def create_series(payload: SeriesBaseSchema, db: Session = Depends(get_db)):
    new_series = Series(**payload.model_dump())
    db.add(new_series)
    db.commit()
    db.refresh(new_series)
    return new_series


@router.put("/{series_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_series(
        series_id: int, payload: SeriesBaseSchema, db: Session = Depends(get_db)
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
