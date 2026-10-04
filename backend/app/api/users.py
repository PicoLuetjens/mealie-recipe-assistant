from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import admin_user, hash_password
from app.models.user import User
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead])
def list_users(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "E-Mail ist bereits vergeben")
    user = User(email=body.email.lower(), display_name=body.display_name, password_hash=hash_password(body.password), is_admin=body.is_admin)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: UserUpdate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None: raise HTTPException(status.HTTP_404_NOT_FOUND, "Benutzer nicht gefunden")
    for field, value in body.model_dump(exclude_none=True).items(): setattr(user, field, value)
    db.commit(); db.refresh(user)
    return user

