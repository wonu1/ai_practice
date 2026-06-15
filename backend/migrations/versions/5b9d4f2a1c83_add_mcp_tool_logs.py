"""add mcp tool logs

Revision ID: 5b9d4f2a1c83
Revises: 8d0f4a9b7c21
Create Date: 2026-06-15 14:44:09.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "5b9d4f2a1c83"
down_revision: str | None = "8d0f4a9b7c21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mcp_tool_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("response_summary", sa.JSON(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mcp_tool_logs_id"), "mcp_tool_logs", ["id"])
    op.create_index(op.f("ix_mcp_tool_logs_status"), "mcp_tool_logs", ["status"])
    op.create_index(op.f("ix_mcp_tool_logs_tool_name"), "mcp_tool_logs", ["tool_name"])
    op.create_index(op.f("ix_mcp_tool_logs_user_id"), "mcp_tool_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_mcp_tool_logs_user_id"), table_name="mcp_tool_logs")
    op.drop_index(op.f("ix_mcp_tool_logs_tool_name"), table_name="mcp_tool_logs")
    op.drop_index(op.f("ix_mcp_tool_logs_status"), table_name="mcp_tool_logs")
    op.drop_index(op.f("ix_mcp_tool_logs_id"), table_name="mcp_tool_logs")
    op.drop_table("mcp_tool_logs")
