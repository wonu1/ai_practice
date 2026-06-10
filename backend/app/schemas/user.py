from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    nickname: str = Field(..., min_length=2, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    id: int
    nickname: str

    model_config = ConfigDict(from_attributes=True)
