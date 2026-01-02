"""Add unique constraint for metals knowledge.

Revision ID: 20260201194000
Revises: 20260201190000
Create Date: 2026-02-01 19:40:00.000000
"""
from __future__ import annotations

from alembic import op

revision = "20260201194000"
down_revision = "20260201190000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_metals_knowledge_metal_category",
        "metals_knowledge",
        ["metal", "category"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_metals_knowledge_metal_category",
        "metals_knowledge",
        type_="unique",
    )
