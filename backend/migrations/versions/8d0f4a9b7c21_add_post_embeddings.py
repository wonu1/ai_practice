"""add post embeddings

Revision ID: 8d0f4a9b7c21
Revises: c604aa50c5d3
Create Date: 2026-06-14 01:48:12.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "8d0f4a9b7c21"
down_revision: str | None = "c604aa50c5d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "post_embeddings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", name="uq_post_embeddings_post_id"),
    )
    op.create_index(op.f("ix_post_embeddings_id"), "post_embeddings", ["id"])
    op.create_index(
        op.f("ix_post_embeddings_post_id"),
        "post_embeddings",
        ["post_id"],
    )
    op.create_index(
        "ix_post_embeddings_embedding_hnsw",
        "post_embeddings",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_post_embeddings_embedding_hnsw", table_name="post_embeddings")
    op.drop_index(op.f("ix_post_embeddings_post_id"), table_name="post_embeddings")
    op.drop_index(op.f("ix_post_embeddings_id"), table_name="post_embeddings")
    op.drop_table("post_embeddings")
