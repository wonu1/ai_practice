import os

from langchain_openai import ChatOpenAI

from backend.app.core.config import get_settings
from backend.app.services.embeddings import SimilarPostResult


def _configure_langsmith() -> None:
    settings = get_settings()

    if settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        if settings.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key


def _get_chat_client() -> ChatOpenAI | None:
    settings = get_settings()

    if settings.ai_provider != "openai" or not settings.openai_api_key:
        return None

    _configure_langsmith()
    return ChatOpenAI(
        model=settings.ai_chat_model,
        api_key=settings.openai_api_key,
    )


def summarize_similar_posts(
    *,
    title: str,
    content: str,
    tags: list[str],
    similar_posts: list[SimilarPostResult],
) -> str | None:
    if not similar_posts:
        return None

    client = _get_chat_client()
    if client is None:
        return None

    context = "\n\n".join(
        [
            "\n".join(
                [
                    f"[{index}] 제목: {post.title}",
                    f"태그: {', '.join(post.tag_names)}",
                    f"유사도: {post.similarity:.3f}",
                    f"본문 일부: {post.content[:500]}",
                ]
            )
            for index, post in enumerate(similar_posts, start=1)
        ]
    )

    prompt = f"""
새 게시글:
제목: {title}
태그: {", ".join(tags)}
본문:
{content}

유사 게시글 후보:
{context}

위 정보를 바탕으로 한국어로만 답하세요.
1. 새 게시글과 기존 게시글들이 어떤 점에서 비슷한지 2문장 이내로 요약하세요.
2. 사용자가 먼저 읽으면 좋을 기존 게시글을 1~2개만 제목 기준으로 추천하세요.
3. 근거 없는 내용은 만들지 마세요.
""".strip()

    try:
        response = client.invoke(prompt)
    except Exception:
        return None

    if isinstance(response.content, str):
        return response.content.strip()

    return str(response.content).strip()
