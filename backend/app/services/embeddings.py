import os
from dataclasses import dataclass

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models import Post, PostEmbedding


@dataclass(frozen=True)
class SimilarPostResult:
    post_id: int
    title: str
    content: str
    tag_names: list[str]
    similarity: float
    source_text: str


@dataclass(frozen=True)
class SimilarPostSearchResult:
    items: list[SimilarPostResult]
    status: str
    message: str | None = None


def build_post_embedding_source(title: str, content: str, tags: list[str]) -> str:
    normalized_tags = ", ".join(tag.strip().lower() for tag in tags if tag.strip())
    return f"제목: {title}\n태그: {normalized_tags}\n본문:\n{content}"


def _configure_langsmith() -> None:
    settings = get_settings()

    if settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        if settings.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key


def _get_embedding_client() -> OpenAIEmbeddings | None:
    settings = get_settings()

    if settings.ai_provider != "openai" or not settings.openai_api_key:
        return None

    _configure_langsmith()
    return OpenAIEmbeddings(
        model=settings.ai_embedding_model,
        api_key=settings.openai_api_key,
    )


def create_embedding_vector(text: str) -> list[float] | None:
    client = _get_embedding_client()

    if client is None:
        return None

    return client.embed_query(text)


def upsert_post_embedding(db: Session, post: Post, tag_names: list[str]) -> None:
    settings = get_settings()
    source_text = build_post_embedding_source(post.title, post.content, tag_names)

    try:
        vector = create_embedding_vector(source_text)
    except Exception:
        return

    if vector is None:
        return

    statement = insert(PostEmbedding).values(
        post_id=post.id,
        embedding_model=settings.ai_embedding_model,
        source_text=source_text,
        embedding=vector,
    )
    statement = statement.on_conflict_do_update(
        constraint="uq_post_embeddings_post_id",
        set_={
            "embedding_model": statement.excluded.embedding_model,
            "source_text": statement.excluded.source_text,
            "embedding": statement.excluded.embedding,
        },
    )
    db.execute(statement)


def search_similar_posts(
    db: Session,
    *,
    title: str,
    content: str,
    tags: list[str],
    limit: int = 5,
    exclude_post_id: int | None = None,
) -> SimilarPostSearchResult:
    source_text = build_post_embedding_source(title, content, tags)

    try:
        query_vector = create_embedding_vector(source_text)
    except Exception:
        return SimilarPostSearchResult(
            items=[],
            status="search_failed",
            message="입력한 글을 임베딩하는 중 문제가 발생했습니다.",
        )

    if query_vector is None:
        return SimilarPostSearchResult(
            items=[],
            status="missing_api_key",
            message="OpenAI API 키가 없어 유사 게시글을 찾을 수 없습니다.",
        )

    distance = PostEmbedding.embedding.cosine_distance(query_vector)
    statement = (
        select(
            Post,
            PostEmbedding.source_text,
            (1 - distance).label("similarity"),
        )
        .join(PostEmbedding, PostEmbedding.post_id == Post.id)
        .order_by(distance)
        .limit(limit)
    )

    if exclude_post_id is not None:
        statement = statement.where(Post.id != exclude_post_id)

    try:
        rows = db.execute(statement).all()
    except Exception:
        return SimilarPostSearchResult(
            items=[],
            status="search_failed",
            message="유사 게시글을 검색하는 중 문제가 발생했습니다.",
        )

    items = [
        SimilarPostResult(
            post_id=post.id,
            title=post.title,
            content=post.content,
            tag_names=[tag.name for tag in post.tags],
            similarity=float(similarity),
            source_text=row_source_text,
        )
        for post, row_source_text, similarity in rows
    ]

    if not items:
        return SimilarPostSearchResult(
            items=[],
            status="no_results",
            message="아직 비슷한 게시글을 찾지 못했습니다.",
        )

    return SimilarPostSearchResult(items=items, status="ok")
