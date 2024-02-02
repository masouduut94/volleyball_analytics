from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing_extensions import List

from src.backend.app.api.deps import SessionDep
from src.backend.app.crud.base import CRUDBase
from src.backend.app.models.models import Camera
from src.backend.app.schemas.cameras import CameraBaseSchema

router = APIRouter()

camera_crud = CRUDBase(Camera)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[CameraBaseSchema])
def get_all_cameras(db: Session = SessionDep):
    cameras = camera_crud.get_all(db)
    if not cameras:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera found.."
        )
    return cameras


@router.get("/{camera_id}", status_code=status.HTTP_200_OK, response_model=CameraBaseSchema)
def get_camera(camera_id: int, db: Session = SessionDep):
    camera = camera_crud.get(db=db, id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera with this id: `{camera_id}` found"
        )
    return camera


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CameraBaseSchema)
def create_camera(payload: CameraBaseSchema, db: Session = SessionDep):
    new_camera = Camera(**payload.model_dump())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera


@router.patch("/{camera_id}", status_code=status.HTTP_202_ACCEPTED)
def update_camera(
        camera_id: int, payload: CameraBaseSchema, db: Session = CameraBaseSchema
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
def delete_camera(camera_id: int, db: Session = SessionDep):
    db_camera = camera_crud.get(db=db, id=camera_id)
    if not db_camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Camera with this id: {camera_id} found .....",
        )
    camera_crud.remove(db=db, id=camera_id)
    return {"status": "success", "message": "Item removed successfully"}

