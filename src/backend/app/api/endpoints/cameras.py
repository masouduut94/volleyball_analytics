from sqlalchemy.orm import Session
from typing_extensions import List
from fastapi import Depends, HTTPException, status, APIRouter

from src.backend.app.db.engine import get_db
from src.backend.app.crud.base import CRUDBase
from src.backend.app.models.models import Camera
from src.backend.app.schemas.cameras import CameraBaseSchema

# from fastapi.encoders import jsonable_encoder
router = APIRouter()

camera_crud = CRUDBase(Camera)


@router.get(path="/", status_code=status.HTTP_200_OK, response_model=List[CameraBaseSchema])
async def get_all_cameras(db: Session = Depends(get_db)):
    cameras = camera_crud.get_all(db)
    if not cameras:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no cameras found.."
        )
    return cameras


@router.get("/{camera_id}", status_code=status.HTTP_200_OK)
async def get_camera(camera_id: str, db: Session = Depends(get_db)):
    camera = camera_crud.get(db=db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera with this id: `{camera_id}` found"
        )
    return camera


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_camera(payload: CameraBaseSchema, db: Session = Depends(get_db)):
    new_camera = Camera(**payload.model_dump())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera


@router.put("/{camera_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_camera(
        camera_id: str, payload: CameraBaseSchema, db: Session = Depends(get_db)
):
    db_camera = camera_crud.get(db=db, id=camera_id)
    if not db_camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera with this id: {camera_id} found .....",
        )
    updated_camera = camera_crud.update(db=db, db_obj=db_camera, obj_in=payload)
    return updated_camera


@router.delete("/{camera_id}", status_code=status.HTTP_200_OK)
async def delete_camera(camera_id: str, db: Session = Depends(get_db)):
    db_camera = camera_crud.get(db=db, id=camera_id)
    if not db_camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera with this id: {camera_id} found .....",
        )
    camera_crud.remove(db=db, id=int(camera_id))
    return {"status": "success", "message": "Item removed successfully"}
