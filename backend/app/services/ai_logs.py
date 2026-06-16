from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models import AiLog


def create_ai_log(
    db: Session,
    *,
    user_id: int | None,
    feature_name: str,
    status: str,
    message: str | None,
    input_payload: dict,
    output_payload: dict,
    duration_ms: int | None,
) -> AiLog | None:
    log = AiLog(
        user_id=user_id,
        feature_name=feature_name,
        status=status,
        message=message,
        input_payload=input_payload,
        output_payload=output_payload,
        duration_ms=duration_ms,
    )
    db.add(log)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return None

    db.refresh(log)
    return log
