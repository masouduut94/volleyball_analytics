from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Rally
from src.backend.app.schemas.rallies import RallyBaseSchema

router = APIRouter()
rally_crud = CRUDBase(Rally)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[RallyBaseSchema])
async def get_all_rallies(db: Session = Depends(get_db)):
    rallies: List[Rally] = rally_crud.get_all(db)
    if not rallies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Rally found.."
        )
    rallies = sorted(rallies, key=lambda x: x.order)
    return rallies


@router.get("/{rally_id}", status_code=status.HTTP_200_OK, response_model=RallyBaseSchema)
async def get_rally(rally_id: int, db: Session = Depends(get_db)):
    rally = rally_crud.get(db=db, id=rally_id)
    if not rally:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Rally with this id: `{rally_id}` found"
        )
    return rally


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RallyBaseSchema)
async def create_rally(payload: RallyBaseSchema, db: Session = Depends(get_db)):
    new_rally = Rally(**payload.model_dump())
    if new_rally.end_frame < new_rally.start_frame:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="rally start frame should be less than end frame...")
    db.add(new_rally)
    db.commit()
    db.refresh(new_rally)
    return new_rally


@router.put("/{rally_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_rally(
        rally_id: int, payload: RallyBaseSchema, db: Session = Depends(get_db)
):
    db_rally = rally_crud.get(db=db, id=rally_id)
    if not db_rally:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Rally with this id: {rally_id} found .....",
        )
    if payload.end_frame < payload.start_frame:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="rally start frame should be less than end frame...")
    updated_rally = rally_crud.update(db=db, db_obj=db_rally, obj_in=payload)
    return updated_rally


@router.delete("/{rally_id}", status_code=status.HTTP_200_OK)
async def delete_rally(rally_id: int, db: Session = Depends(get_db)):
    db_rally = rally_crud.get(db=db, id=rally_id)
    if not db_rally:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Rally with this id: {rally_id} found .....",
        )
    rally_crud.remove(db=db, id=rally_id)
    return {"status": "success", "message": "Item removed successfully"}
