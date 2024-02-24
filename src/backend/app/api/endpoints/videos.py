from typing_extensions import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from src.backend.app.crud.base import CRUDBase
from src.backend.app.db.engine import get_db
from src.backend.app.models.models import Video, Camera
from src.backend.app.schemas.videos import VideoCreateSchema, VideoBaseSchema

router = APIRouter()

video_crud = CRUDBase(Video)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[VideoBaseSchema])
async def get_all_videos(db: Session = Depends(get_db)):
    videos = video_crud.get_all(db)
    if not videos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no video found.."
        )
    return videos


@router.get("/{video_id}", status_code=status.HTTP_200_OK, response_model=VideoBaseSchema)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    video = video_crud.get(db=db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no video with this id: `{video_id}` found"
        )
    return video


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VideoBaseSchema)
async def create_video(payload: VideoCreateSchema, db: Session = Depends(get_db)):
    camera = db.get(entity=Camera, ident=payload.camera_type_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"No camera with this id: {payload.camera_type_id} found. .....",
        )
    new_video = Video(**payload.model_dump())
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video


@router.put("/{video_id}", status_code=status.HTTP_202_ACCEPTED, response_model=VideoBaseSchema)
async def update_video(
        video_id: int, payload: VideoCreateSchema, db: Session = Depends(get_db)
):
    db_video = video_crud.get(db=db, id=video_id)
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no video with this id: {video_id} found .....",
        )
    updated_video = video_crud.update(db=db, db_obj=db_video, obj_in=payload)
    return updated_video


@router.delete("/{video_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_video(video_id: int, db: Session = Depends(get_db)):
    db_video = video_crud.get(db=db, id=video_id)
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no video with this id: {video_id} found .....",
        )
    video_crud.remove(db=db, id=video_id)
    return {"status": "success", "message": "Item removed successfully"}
