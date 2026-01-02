"""Add unique constraint for macro events.

Revision ID: 20260201205000
Revises: 20260201201000
Create Date: 2026-02-01 20:50:00.000000
"""
from __future__ import annotations

from alembic import op

revision = "20260201205000"
down_revision = "20260201201000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_macro_events_source_headline_published",
        "macro_events",
        ["source", "headline", "published_at"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_macro_events_source_headline_published",
        "macro_events",
        type_="unique",
    )
