from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models import User
from backend.app.schemas import PostCreate, PostListResponse, PostRead
from backend.app.services.posts import create_post, get_post_detail, list_posts


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostListResponse)
def read_posts(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
) -> PostListResponse:
    return list_posts(db=db, page=page, size=size, keyword=keyword, tag=tag)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post_api(
    post_create: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostRead:
    return create_post(db=db, post_create=post_create, author=current_user)


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Session = Depends(get_db)) -> PostRead:
    post = get_post_detail(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return post
