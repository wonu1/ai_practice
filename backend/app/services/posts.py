from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import Comment, Post, Tag, User
from backend.app.schemas import (
    PostCreate,
    PostListItem,
    PostListResponse,
    PostRead,
    PostUpdate,
    UserSummary,
)
from backend.app.services.embeddings import upsert_post_embedding


def _normalize_tag_names(tag_names: list[str]) -> list[str]:
    normalized_names = []
    seen_names = set()

    for tag_name in tag_names:
        normalized_name = tag_name.strip().lower()
        if not normalized_name or normalized_name in seen_names:
            continue
        normalized_names.append(normalized_name)
        seen_names.add(normalized_name)

    return normalized_names


def _get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    normalized_names = _normalize_tag_names(tag_names)
    if not normalized_names:
        return []

    existing_tags = db.scalars(select(Tag).where(Tag.name.in_(normalized_names))).all()
    existing_tag_map = {tag.name: tag for tag in existing_tags}

    tags = []
    for tag_name in normalized_names:
        tag = existing_tag_map.get(tag_name)
        if tag is None:
            tag = Tag(name=tag_name)
            db.add(tag)
        tags.append(tag)

    return tags


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


def create_post(db: Session, post_create: PostCreate, author: User) -> PostRead:
    tag_names = _normalize_tag_names(post_create.tags)
    post = Post(
        user_id=author.id,
        title=post_create.title,
        content=post_create.content,
        tags=_get_or_create_tags(db, tag_names),
    )
    db.add(post)
    db.flush()
    upsert_post_embedding(db, post, tag_names)
    db.commit()
    db.refresh(post)
    post_read = get_post_detail(db, post.id)
    if post_read is None:
        raise RuntimeError("생성된 게시글을 다시 조회할 수 없습니다.")
    return post_read


def update_post(db: Session, post: Post, post_update: PostUpdate) -> PostRead:
    update_data = post_update.model_dump(exclude_unset=True)

    if "title" in update_data:
        post.title = update_data["title"]
    if "content" in update_data:
        post.content = update_data["content"]
    if "tags" in update_data and update_data["tags"] is not None:
        post.tags = _get_or_create_tags(db, update_data["tags"])

    db.add(post)
    db.commit()
    db.refresh(post)

    post_read = get_post_detail(db, post.id)
    if post_read is None:
        raise RuntimeError("수정된 게시글을 다시 조회할 수 없습니다.")
    return post_read


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


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
