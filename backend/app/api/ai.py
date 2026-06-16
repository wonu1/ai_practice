from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models import User
from backend.app.schemas import (
    AgentAssistWritingRequest,
    AgentAssistWritingResponse,
    GitHubIssueItem,
    GitHubIssueSearchRequest,
    GitHubIssueSearchResponse,
    SimilarPostItem,
    SimilarPostsRequest,
    SimilarPostsResponse,
)
from backend.app.services.agent import run_agent_graph
from backend.app.services.embeddings import search_similar_posts
from backend.app.services.mcp_client import search_github_issues_via_mcp
from backend.app.services.mcp_logs import create_mcp_tool_log
from backend.app.services.rag import summarize_similar_posts


router = APIRouter(prefix="/ai", tags=["ai"])


def _to_similar_post_items(items: list[dict]) -> list[SimilarPostItem]:
    return [
        SimilarPostItem(
            post_id=item.get("post_id", 0),
            title=item.get("title", ""),
            content_preview=item.get("content_preview", ""),
            tag_names=item.get("tag_names", []),
            similarity=item.get("similarity", 0.0),
        )
        for item in items
    ]


def _to_github_issue_items(items: list[dict]) -> list[GitHubIssueItem]:
    return [
        GitHubIssueItem(
            title=item.get("title", ""),
            url=item.get("url", ""),
            repository=item.get("repository", ""),
            state=item.get("state", ""),
            summary=item.get("summary", ""),
        )
        for item in items
    ]


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
    db: Session = Depends(get_db),
) -> GitHubIssueSearchResponse:
    result = await search_github_issues_via_mcp(
        query=request.query,
        repository=request.repository,
        limit=request.limit,
    )
    items = result.get("items", [])

    create_mcp_tool_log(
        db,
        user_id=current_user.id,
        tool_name="github_search_issues",
        status=result.get("status", "mcp_error"),
        message=result.get("message"),
        request_payload=request.model_dump(),
        response_summary={"item_count": len(items)},
        duration_ms=result.get("duration_ms"),
    )

    return GitHubIssueSearchResponse(
        status=result.get("status", "mcp_error"),
        message=result.get("message"),
        items=_to_github_issue_items(items),
    )


@router.post("/agent/assist-writing", response_model=AgentAssistWritingResponse)
async def assist_writing_with_agent(
    request: AgentAssistWritingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentAssistWritingResponse:
    state = await run_agent_graph(
        db,
        title=request.title,
        content=request.content,
        tags=request.tags,
    )
    final_answer = state.get("final_answer", {})
    rag_results = state.get("rag_results", {})
    mcp_results = state.get("mcp_results", {})
    control = state.get("control", {})
    errors = control.get("errors", [])

    return AgentAssistWritingResponse(
        status="partial" if errors else "ok",
        message="; ".join(errors) if errors else None,
        feedback=final_answer.get("feedback", []),
        draft=final_answer.get("draft", ""),
        similar_posts=_to_similar_post_items(rag_results.get("similar_posts", [])),
        external_refs=_to_github_issue_items(mcp_results.get("github_issues", [])),
        used_sources=final_answer.get("used_sources", []),
        control=control,
    )
