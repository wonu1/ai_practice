from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagRead(TagCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TagListResponse(BaseModel):
    items: list[TagRead]
