from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models import User
from backend.app.services.comments import delete_comment, get_comment


router = APIRouter(prefix="/comments", tags=["comments"])


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_api(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    comment = get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다.",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글을 삭제할 권한이 없습니다.",
        )

    delete_comment(db=db, comment=comment)
