from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import Comment, User
from backend.app.schemas import CommentCreate, CommentListResponse, CommentRead, UserSummary


def _to_comment_read(comment: Comment) -> CommentRead:
    return CommentRead(
        id=comment.id,
        content=comment.content,
        author=UserSummary.model_validate(comment.author),
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


def list_comments_by_post(db: Session, post_id: int) -> CommentListResponse:
    comments = db.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    ).all()

    return CommentListResponse(
        items=[_to_comment_read(comment) for comment in comments]
    )


def create_comment(
    db: Session,
    post_id: int,
    comment_create: CommentCreate,
    author: User,
) -> CommentRead:
    comment = Comment(
        post_id=post_id,
        user_id=author.id,
        content=comment_create.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _to_comment_read(comment)
