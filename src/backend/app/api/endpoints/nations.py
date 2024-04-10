from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Nation
from src.backend.app.schemas.nations import NationBaseSchema, NationCreateSchema

router = APIRouter()

nation_crud = CRUDBase(Nation)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[NationBaseSchema])
async def get_all_nations(db: Session = Depends(get_db)):
    nations = nation_crud.get_all(db)
    if not nations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Nation found.."
        )
    return nations


@router.get("/{nation_id}", status_code=status.HTTP_200_OK, response_model=NationBaseSchema)
async def get_nation(nation_id: int, db: Session = Depends(get_db)):
    nation = nation_crud.get(db=db, id=nation_id)
    if not nation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Nation with this id: `{nation_id}` found"
        )
    return nation


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NationBaseSchema)
async def create_nation(payload: NationCreateSchema, db: Session = Depends(get_db)):
    new_nation = Nation(**payload.model_dump())
    db.add(new_nation)
    db.commit()
    db.refresh(new_nation)
    return new_nation


@router.put("/{nation_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_nation(
        nation_id: int, payload: NationCreateSchema, db: Session = Depends(get_db)
):
    db_nation = nation_crud.get(db=db, id=nation_id)
    if not db_nation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Nation with this id: {nation_id} found .....",
        )
    updated_nation = nation_crud.update(db=db, db_obj=db_nation, obj_in=payload)
    return updated_nation


@router.delete("/{nation_id}", status_code=status.HTTP_200_OK)
async def delete_nation(nation_id: int, db: Session = Depends(get_db)):
    db_nation = nation_crud.get(db=db, id=nation_id)
    if not db_nation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Nation with this id: {nation_id} found .....",
        )
    nation_crud.remove(db=db, id=nation_id)
    return {"status": "success", "message": "Item removed successfully"}
