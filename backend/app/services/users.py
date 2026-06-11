from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password, verify_password
from backend.app.models import User
from backend.app.schemas import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_nickname(db: Session, nickname: str) -> User | None:
    return db.scalar(select(User).where(User.nickname == nickname))


def create_user(db: Session, user_create: UserCreate) -> User:
    user = User(
        email=user_create.email,
        nickname=user_create.nickname,
        password_hash=hash_password(user_create.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
