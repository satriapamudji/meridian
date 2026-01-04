"""Add quantitative impacts and time horizon behavior to historical cases.

Revision ID: 20260201230000
Revises: 20260201220000
Create Date: 2026-02-01 23:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260201230000"
down_revision = "20260201220000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add quantitative_impacts column - structured quantitative data about the event's impact
    # Example: {"production_drop_pct": 5.0, "price_impact_pct": 15.0, "supply_disruption_mbpd": 1.5}
    op.add_column(
        "historical_cases",
        sa.Column("quantitative_impacts", postgresql.JSONB(), nullable=True),
    )

    # Add time_horizon_behavior column - how the event played out over different time frames
    # Example: {"short_term_1_5d": {...}, "medium_term_2_8w": {...}, "long_term_6m_plus": {...}}
    op.add_column(
        "historical_cases",
        sa.Column("time_horizon_behavior", postgresql.JSONB(), nullable=True),
    )

    # Add transmission_channels column - which transmission channels were activated
    # Example: ["oil_supply_disruption", "sanctions_trade_war"]
    op.add_column(
        "historical_cases",
        sa.Column("transmission_channels", postgresql.ARRAY(sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("historical_cases", "transmission_channels")
    op.drop_column("historical_cases", "time_horizon_behavior")
    op.drop_column("historical_cases", "quantitative_impacts")
