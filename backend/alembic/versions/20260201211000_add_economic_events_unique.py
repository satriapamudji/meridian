"""Add unique constraint for economic events.

Revision ID: 20260201211000
Revises: 20260201205000
Create Date: 2026-02-01 21:10:00.000000
"""
from __future__ import annotations

from alembic import op

revision = "20260201211000"
down_revision = "20260201205000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_economic_events_name_date_region",
        "economic_events",
        ["event_name", "event_date", "region"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_economic_events_name_date_region",
        "economic_events",
        type_="unique",
    )
