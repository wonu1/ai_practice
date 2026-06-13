import os

from langchain_openai import OpenAIEmbeddings
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models import Post, PostEmbedding


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
