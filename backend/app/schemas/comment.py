from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.user import UserSummary


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentRead(CommentCreate):
    id: int
    author: UserSummary
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    items: list[CommentRead]
