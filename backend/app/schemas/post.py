from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.user import UserSummary


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None


class PostRead(PostBase):
    id: int
    author: UserSummary
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListItem(BaseModel):
    id: int
    title: str
    author: UserSummary
    tags: list[str] = Field(default_factory=list)
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    items: list[PostListItem]
    page: int
    size: int
    total: int
