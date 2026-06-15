from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models import User
from backend.app.schemas import (
    GitHubIssueItem,
    GitHubIssueSearchRequest,
    GitHubIssueSearchResponse,
    SimilarPostItem,
    SimilarPostsRequest,
    SimilarPostsResponse,
)
from backend.app.services.embeddings import search_similar_posts
from backend.app.services.mcp_client import search_github_issues_via_mcp
from backend.app.services.rag import summarize_similar_posts


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/posts/similar", response_model=SimilarPostsResponse)
def find_similar_posts(
    request: SimilarPostsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SimilarPostsResponse:
    search_result = search_similar_posts(
        db,
        title=request.title,
        content=request.content,
        tags=request.tags,
        limit=request.limit,
        exclude_post_id=request.exclude_post_id,
    )
    results = search_result.items
    summary = summarize_similar_posts(
        title=request.title,
        content=request.content,
        tags=request.tags,
        similar_posts=results,
    )
    status = search_result.status
    message = search_result.message

    if results and summary is None:
        status = "summary_failed"
        message = "유사 게시글은 찾았지만 요약을 생성하지 못했습니다."

    return SimilarPostsResponse(
        status=status,
        message=message,
        summary=summary,
        items=[
            SimilarPostItem(
                post_id=result.post_id,
                title=result.title,
                content_preview=result.content[:200],
                tag_names=result.tag_names,
                similarity=result.similarity,
            )
            for result in results
        ]
    )


@router.post("/github/issues", response_model=GitHubIssueSearchResponse)
async def search_github_issues(
    request: GitHubIssueSearchRequest,
    current_user: User = Depends(get_current_user),
) -> GitHubIssueSearchResponse:
    result = await search_github_issues_via_mcp(
        query=request.query,
        repository=request.repository,
        limit=request.limit,
    )

    return GitHubIssueSearchResponse(
        status=result.get("status", "mcp_error"),
        message=result.get("message"),
        items=[
            GitHubIssueItem(
                title=item.get("title", ""),
                url=item.get("url", ""),
                repository=item.get("repository", ""),
                state=item.get("state", ""),
                summary=item.get("summary", ""),
            )
            for item in result.get("items", [])
        ],
    )
