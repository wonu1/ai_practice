import re
from typing import Annotated, Any

import httpx
from pydantic import Field

from ai_board_mcp.config import get_settings


REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
GITHUB_TIMEOUT_SECONDS = 10.0


def _tool_response(
    status: str,
    message: str | None,
    items: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "items": items or [],
        "status": status,
        "message": message,
    }


def _normalize_limit(limit: int) -> int:
    return max(1, min(limit, 10))


def _build_search_query(query: str, repository: str | None) -> str:
    search_query = f"{query.strip()} type:issue"
    if repository:
        search_query = f"{search_query} repo:{repository.strip()}"
    return search_query


def _get_repository_name(item: dict[str, Any]) -> str:
    repository_url = str(item.get("repository_url") or "")
    if "/repos/" in repository_url:
        return repository_url.rsplit("/repos/", maxsplit=1)[-1]
    return ""


def _build_summary(body: str | None) -> str:
    normalized_body = " ".join((body or "").split())
    if not normalized_body:
        return "GitHub issue 본문 요약 정보가 없습니다."
    return normalized_body[:280]


def _build_headers() -> dict[str, str]:
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-board-mcp-server",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _map_github_item(item: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(item.get("title") or ""),
        "url": str(item.get("html_url") or ""),
        "repository": _get_repository_name(item),
        "state": str(item.get("state") or ""),
        "summary": _build_summary(item.get("body")),
    }


def github_search_issues(
    query: Annotated[
        str,
        Field(
            min_length=1,
            description="GitHub issue search query.",
        ),
    ],
    repository: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional repository filter in owner/name format.",
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            default=5,
            ge=1,
            le=10,
            description="Maximum number of issues to return.",
        ),
    ] = 5,
) -> dict[str, Any]:
    """Search GitHub issues related to a development question."""
    normalized_query = query.strip()
    normalized_repository = repository.strip() if repository else None
    normalized_limit = _normalize_limit(limit)

    if not normalized_query:
        return _tool_response("invalid_input", "검색어를 입력해야 합니다.")

    if normalized_repository and not REPOSITORY_PATTERN.fullmatch(normalized_repository):
        return _tool_response(
            "invalid_input",
            "repository는 owner/name 형식이어야 합니다.",
        )

    settings = get_settings()
    search_query = _build_search_query(normalized_query, normalized_repository)

    try:
        with httpx.Client(
            base_url=settings.github_api_base,
            headers=_build_headers(),
            timeout=GITHUB_TIMEOUT_SECONDS,
        ) as client:
            response = client.get(
                "/search/issues",
                params={
                    "q": search_query,
                    "per_page": normalized_limit,
                },
            )
    except httpx.TimeoutException:
        return _tool_response(
            "timeout",
            "GitHub API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.",
        )
    except httpx.HTTPError:
        return _tool_response(
            "github_error",
            "GitHub API 호출 중 문제가 발생했습니다.",
        )

    if response.status_code in {403, 429}:
        return _tool_response(
            "rate_limited",
            "GitHub API 호출 제한에 도달했습니다. 잠시 후 다시 시도해 주세요.",
        )

    if response.status_code == 422:
        return _tool_response(
            "invalid_input",
            "GitHub API가 검색어 또는 repository 조건을 처리하지 못했습니다.",
        )

    if response.status_code >= 400:
        return _tool_response(
            "github_error",
            "GitHub API가 검색 요청을 처리하지 못했습니다.",
        )

    try:
        data = response.json()
    except ValueError:
        return _tool_response(
            "github_error",
            "GitHub API 응답을 해석하지 못했습니다.",
        )

    items = [_map_github_item(item) for item in data.get("items", [])]

    if not items:
        return _tool_response("no_results", "관련 GitHub issue를 찾지 못했습니다.")

    return _tool_response("ok", None, items)
