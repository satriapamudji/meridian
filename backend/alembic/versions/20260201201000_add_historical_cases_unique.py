"""Add unique constraint for historical cases.

Revision ID: 20260201201000
Revises: 20260201194000
Create Date: 2026-02-01 20:10:00.000000
"""
from __future__ import annotations

from alembic import op

revision = "20260201201000"
down_revision = "20260201194000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_historical_cases_event_date",
        "historical_cases",
        ["event_name", "date_range"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_historical_cases_event_date",
        "historical_cases",
        type_="unique",
    )
