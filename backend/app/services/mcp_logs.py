from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models import McpToolLog


def create_mcp_tool_log(
    db: Session,
    *,
    user_id: int | None,
    tool_name: str,
    status: str,
    message: str | None,
    request_payload: dict,
    response_summary: dict,
    duration_ms: int | None,
) -> McpToolLog | None:
    log = McpToolLog(
        user_id=user_id,
        tool_name=tool_name,
        status=status,
        message=message,
        request_payload=request_payload,
        response_summary=response_summary,
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
