import scripts.just_check.schemas as schemas
import scripts.just_check.models as models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from scripts.just_check import get_db

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def get_users(
        db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ""
):
    skip = (page - 1) * limit

    users = (
        db.query(models.User)
        .filter(models.User.first_name.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return {"Status": "Success", "Results": len(users), "Users": users}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserBaseSchema, db: Session = Depends(get_db)):
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Status": "Success", "User": new_user}


@router.patch("/{userId}", status_code=status.HTTP_202_ACCEPTED)
def update_user(
        userId: str, payload: schemas.UserBaseSchema, db: Session = Depends(get_db)
):
    user_query = db.query(models.User).filter(models.User.id == userId)
    db_user = user_query.first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No User with this id: {userId} found",
        )
    update_data = payload.dict(exclude_unset=True)
    user_query.filter(models.User.id == userId).update(
        update_data, synchronize_session=False
    )
    db.commit()
    db.refresh(db_user)
    return {"Status": "Success", "User": db_user}


@router.get("/{userId}", status_code=status.HTTP_200_OK)
def get_user(userId: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == userId).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No User with this id: `{userId}` found",
        )
    return {"Status": "Success", "User": user}


@router.delete("/{userId}", status_code=status.HTTP_200_OK)
def delete_user(userId: str, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == userId)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with this id: {userId} found",
        )
    user_query.delete(synchronize_session=False)
    db.commit()
    return {"Status": "Success", "Message": "User deleted successfully"}