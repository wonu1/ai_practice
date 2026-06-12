from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas import TagListResponse
from backend.app.services.tags import list_tags


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def read_tags(db: Session = Depends(get_db)) -> TagListResponse:
    return list_tags(db)
