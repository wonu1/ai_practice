from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Tag
from backend.app.schemas import TagListResponse, TagRead


def list_tags(db: Session) -> TagListResponse:
    tags = db.scalars(select(Tag).order_by(Tag.name.asc())).all()
    return TagListResponse(
        items=[TagRead.model_validate(tag) for tag in tags]
    )
