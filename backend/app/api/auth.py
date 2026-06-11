from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.core.security import create_access_token
from backend.app.models import User
from backend.app.schemas import LoginRequest, TokenResponse, UserCreate, UserRead
from backend.app.services.users import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_nickname,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_create: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    if get_user_by_email(db, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",
        )

    if get_user_by_nickname(db, user_create.nickname):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 닉네임입니다.",
        )

    return create_user(db, user_create)


@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, login_request.email, login_request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user
