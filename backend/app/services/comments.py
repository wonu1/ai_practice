from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import Comment
from backend.app.schemas import CommentListResponse, CommentRead, UserSummary


def list_comments_by_post(db: Session, post_id: int) -> CommentListResponse:
    comments = db.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    ).all()

    return CommentListResponse(
        items=[
            CommentRead(
                id=comment.id,
                content=comment.content,
                author=UserSummary.model_validate(comment.author),
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment in comments
        ]
    )
