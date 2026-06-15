from typing import Annotated, Any

from pydantic import Field


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
    normalized_limit = max(1, min(limit, 10))

    if not normalized_query:
        return {
            "items": [],
            "status": "invalid_input",
            "message": "검색어를 입력해야 합니다.",
        }

    return {
        "items": [],
        "status": "not_implemented",
        "message": (
            "github_search_issues 도구는 등록되었지만 "
            "GitHub API 호출은 다음 단계에서 구현합니다."
        ),
        "debug": {
            "query": normalized_query,
            "repository": normalized_repository,
            "limit": normalized_limit,
        },
    }
