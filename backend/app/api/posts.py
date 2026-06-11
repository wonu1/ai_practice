from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas import PostListResponse
from backend.app.services.posts import list_posts


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
