from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models import User
from backend.app.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentRead,
    PostCreate,
    PostListResponse,
    PostRead,
    PostUpdate,
)
from backend.app.services.comments import create_comment, list_comments_by_post
from backend.app.services.posts import (
    create_post,
    delete_post,
    get_post,
    get_post_detail,
    list_posts,
    update_post,
)


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


@router.get("/{post_id}/comments", response_model=CommentListResponse)
def read_post_comments(post_id: int, db: Session = Depends(get_db)) -> CommentListResponse:
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return list_comments_by_post(db=db, post_id=post_id)


@router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_post_comment(
    post_id: int,
    comment_create: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommentRead:
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return create_comment(
        db=db,
        post_id=post_id,
        comment_create=comment_create,
        author=current_user,
    )


@router.patch("/{post_id}", response_model=PostRead)
def update_post_api(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostRead:
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글을 수정할 권한이 없습니다.",
        )

    return update_post(db=db, post=post, post_update=post_update)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_api(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글을 삭제할 권한이 없습니다.",
        )

    delete_post(db=db, post=post)
