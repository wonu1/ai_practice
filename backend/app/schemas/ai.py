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
    items: list[SimilarPostItem]
