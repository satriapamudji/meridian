"""Add market context table for daily macro dashboard.

Revision ID: 20260201220000
Revises: 20260201213000
Create Date: 2026-02-01 22:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260201220000"
down_revision = "20260201213000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_context",
        # Primary key and date
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("context_date", sa.Date(), nullable=False, unique=True),
        # Regime classifications (derived from raw data)
        sa.Column(
            "volatility_regime",
            sa.Text(),
            nullable=True,
            comment="calm, normal, elevated, fear, crisis",
        ),
        sa.Column(
            "dollar_regime",
            sa.Text(),
            nullable=True,
            comment="weak, neutral, strong",
        ),
        sa.Column(
            "curve_regime",
            sa.Text(),
            nullable=True,
            comment="inverted, flat, normal, steep",
        ),
        sa.Column(
            "credit_regime",
            sa.Text(),
            nullable=True,
            comment="tight, normal, wide, stressed, crisis",
        ),
        # Tier 1: Vital Signs
        sa.Column("vix_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("vix_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("dxy_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("dxy_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("us10y_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("us10y_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("gold_level", sa.Numeric(12, 4), nullable=True),
        sa.Column("gold_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("oil_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("oil_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("spx_level", sa.Numeric(12, 4), nullable=True),
        sa.Column("spx_change_1d", sa.Numeric(10, 4), nullable=True),
        sa.Column("btc_level", sa.Numeric(12, 2), nullable=True),
        sa.Column("btc_change_1d", sa.Numeric(10, 4), nullable=True),
        # Tier 2: Volatility
        sa.Column("vvix_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("move_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("vix_term_structure", sa.Numeric(10, 4), nullable=True, comment="VIX/VX ratio"),
        # Tier 3: Rates & Curve
        sa.Column("us2y_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("us30y_level", sa.Numeric(10, 4), nullable=True),
        sa.Column("curve_2s10s", sa.Numeric(10, 4), nullable=True, comment="10Y-2Y spread"),
        sa.Column("breakeven_5y", sa.Numeric(10, 4), nullable=True),
        sa.Column("hy_spread", sa.Numeric(10, 4), nullable=True, comment="HY OAS in bps"),
        # Tier 6: Key Ratios (pre-calculated)
        sa.Column("gold_silver_ratio", sa.Numeric(10, 4), nullable=True),
        sa.Column("copper_gold_ratio", sa.Numeric(10, 6), nullable=True),
        sa.Column("vix_vix3m_ratio", sa.Numeric(10, 4), nullable=True),
        sa.Column("spy_rsp_ratio", sa.Numeric(10, 4), nullable=True),
        sa.Column("hyg_lqd_ratio", sa.Numeric(10, 4), nullable=True),
        # Position sizing
        sa.Column(
            "suggested_size_multiplier",
            sa.Numeric(5, 2),
            nullable=True,
            comment="0.25-1.0 based on regime",
        ),
        # Raw data storage (for flexibility and debugging)
        sa.Column(
            "raw_prices",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="All fetched prices keyed by symbol",
        ),
        sa.Column(
            "raw_fred",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="All fetched FRED series keyed by series ID",
        ),
        # Metadata
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    # Index for fast lookups by date
    op.create_index(
        "idx_market_context_date",
        "market_context",
        ["context_date"],
        unique=False,
        postgresql_using="btree",
    )


def downgrade() -> None:
    op.drop_index("idx_market_context_date", table_name="market_context")
    op.drop_table("market_context")
