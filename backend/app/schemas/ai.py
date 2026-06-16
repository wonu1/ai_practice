from pydantic import BaseModel, Field


class SimilarPostsRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    limit: int = Field(default=5, ge=1, le=10)
    exclude_post_id: int | None = None


class SimilarPostItem(BaseModel):
    post_id: int
    title: str
    content_preview: str
    tag_names: list[str]
    similarity: float


class SimilarPostsResponse(BaseModel):
    status: str = "ok"
    message: str | None = None
    summary: str | None = None
    items: list[SimilarPostItem]


class GitHubIssueSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    repository: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=5, ge=1, le=10)


class GitHubIssueItem(BaseModel):
    title: str
    url: str
    repository: str
    state: str
    summary: str


class GitHubIssueSearchResponse(BaseModel):
    status: str = "ok"
    message: str | None = None
    items: list[GitHubIssueItem]


class AgentAssistWritingRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class AgentAssistWritingResponse(BaseModel):
    status: str = "ok"
    message: str | None = None
    feedback: list[str]
    draft: str
    similar_posts: list[SimilarPostItem]
    external_refs: list[GitHubIssueItem]
    used_sources: list[dict]
    control: dict
