from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import Comment, Post, Tag
from backend.app.schemas import PostListItem, PostListResponse, PostRead, UserSummary


def _apply_post_filters(statement: Select[tuple[Post]], keyword: str | None, tag: str | None):
    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(
            or_(
                Post.title.ilike(like_keyword),
                Post.content.ilike(like_keyword),
            )
        )

    if tag:
        statement = statement.join(Post.tags).where(Tag.name == tag)

    return statement


def list_posts(
    db: Session,
    page: int = 1,
    size: int = 10,
    keyword: str | None = None,
    tag: str | None = None,
) -> PostListResponse:
    base_statement = _apply_post_filters(select(Post), keyword, tag)
    total = db.scalar(select(func.count()).select_from(base_statement.subquery())) or 0

    posts = db.scalars(
        base_statement.options(
            selectinload(Post.author),
            selectinload(Post.tags),
        )
        .order_by(Post.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    comment_counts = dict(
        db.execute(
            select(Comment.post_id, func.count(Comment.id))
            .where(Comment.post_id.in_([post.id for post in posts]))
            .group_by(Comment.post_id)
        ).all()
    )

    items = [
        PostListItem(
            id=post.id,
            title=post.title,
            author=UserSummary.model_validate(post.author),
            tags=[tag.name for tag in post.tags],
            comment_count=comment_counts.get(post.id, 0),
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        for post in posts
    ]

    return PostListResponse(items=items, page=page, size=size, total=total)


def get_post_detail(db: Session, post_id: int) -> PostRead | None:
    post = db.scalar(
        select(Post)
        .where(Post.id == post_id)
        .options(
            selectinload(Post.author),
            selectinload(Post.tags),
        )
    )
    if post is None:
        return None

    return PostRead(
        id=post.id,
        title=post.title,
        content=post.content,
        author=UserSummary.model_validate(post.author),
        tags=[tag.name for tag in post.tags],
        created_at=post.created_at,
        updated_at=post.updated_at,
    )
