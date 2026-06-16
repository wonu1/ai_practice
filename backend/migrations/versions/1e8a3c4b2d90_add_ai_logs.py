"""add ai logs

Revision ID: 1e8a3c4b2d90
Revises: 5b9d4f2a1c83
Create Date: 2026-06-16 15:48:03.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "1e8a3c4b2d90"
down_revision: str | None = "5b9d4f2a1c83"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("feature_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
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
    op.create_index(op.f("ix_ai_logs_id"), "ai_logs", ["id"])
    op.create_index(op.f("ix_ai_logs_feature_name"), "ai_logs", ["feature_name"])
    op.create_index(op.f("ix_ai_logs_status"), "ai_logs", ["status"])
    op.create_index(op.f("ix_ai_logs_user_id"), "ai_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_logs_user_id"), table_name="ai_logs")
    op.drop_index(op.f("ix_ai_logs_status"), table_name="ai_logs")
    op.drop_index(op.f("ix_ai_logs_feature_name"), table_name="ai_logs")
    op.drop_index(op.f("ix_ai_logs_id"), table_name="ai_logs")
    op.drop_table("ai_logs")
