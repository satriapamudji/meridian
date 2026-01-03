"""Add daily prices and ratios tables.

Revision ID: 20260201213000
Revises: 20260201205000
Create Date: 2026-02-01 21:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260201213000"
down_revision = "20260201205000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_prices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric()),
        sa.Column("high", sa.Numeric()),
        sa.Column("low", sa.Numeric()),
        sa.Column("close", sa.Numeric()),
        sa.Column("adj_close", sa.Numeric()),
        sa.Column("volume", sa.BigInteger()),
        sa.Column("source", sa.Text(), nullable=False, server_default=sa.text("'yahoo'")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("symbol", "price_date", name="uq_daily_prices_symbol_date"),
    )

    op.create_table(
        "price_ratios",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ratio_name", sa.Text(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(), nullable=False),
        sa.Column("base_symbol", sa.Text(), nullable=False),
        sa.Column("quote_symbol", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("ratio_name", "price_date", name="uq_price_ratios_name_date"),
    )


def downgrade() -> None:
    op.drop_table("price_ratios")
    op.drop_table("daily_prices")
