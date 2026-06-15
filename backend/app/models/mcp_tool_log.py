from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base


class McpToolLog(Base):
    __tablename__ = "mcp_tool_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    response_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User | None"] = relationship()
