"""Create core schema tables.

Revision ID: 20260201190000
Revises:
Create Date: 2026-02-01 19:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260201190000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "theses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("asset_type", sa.Text(), nullable=False),
        sa.Column("asset_symbol", sa.Text()),
        sa.Column("trigger_event", sa.Text()),
        sa.Column("core_thesis", sa.Text(), nullable=False),
        sa.Column("bull_case", postgresql.ARRAY(sa.Text())),
        sa.Column("bear_case", postgresql.ARRAY(sa.Text())),
        sa.Column("historical_precedent", sa.Text()),
        sa.Column("entry_consideration", sa.Text()),
        sa.Column("target", sa.Text()),
        sa.Column("invalidation", sa.Text()),
        sa.Column("vehicle", sa.Text()),
        sa.Column("position_size", sa.Text()),
        sa.Column("entry_date", sa.TIMESTAMP(timezone=True)),
        sa.Column("entry_price", sa.Numeric()),
        sa.Column("status", sa.Text(), server_default=sa.text("'watching'")),
        sa.Column("price_at_creation", sa.Numeric()),
        sa.Column("current_price", sa.Numeric()),
        sa.Column("price_change_percent", sa.Numeric()),
        sa.Column("updates", postgresql.JSONB()),
    )

    op.create_table(
        "macro_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("full_text", sa.Text()),
        sa.Column("url", sa.Text()),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("event_type", sa.Text()),
        sa.Column("regions", postgresql.ARRAY(sa.Text())),
        sa.Column("entities", postgresql.ARRAY(sa.Text())),
        sa.Column("significance_score", sa.Integer()),
        sa.Column("score_components", postgresql.JSONB()),
        sa.Column("priority_flag", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("raw_facts", postgresql.ARRAY(sa.Text())),
        sa.Column("metal_impacts", postgresql.JSONB()),
        sa.Column("historical_precedent", sa.Text()),
        sa.Column("counter_case", sa.Text()),
        sa.Column("crypto_transmission", postgresql.JSONB()),
        sa.Column("status", sa.Text(), server_default=sa.text("'new'")),
        sa.Column("thesis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("theses.id")),
    )

    op.create_table(
        "metals_knowledge",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("metal", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "historical_cases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("event_name", sa.Text(), nullable=False),
        sa.Column("date_range", sa.Text()),
        sa.Column("event_type", sa.Text()),
        sa.Column("significance_score", sa.Integer()),
        sa.Column("structural_drivers", postgresql.ARRAY(sa.Text())),
        sa.Column("metal_impacts", postgresql.JSONB()),
        sa.Column("traditional_market_reaction", postgresql.ARRAY(sa.Text())),
        sa.Column("crypto_reaction", postgresql.ARRAY(sa.Text())),
        sa.Column("crypto_transmission", postgresql.JSONB()),
        sa.Column("time_delays", postgresql.ARRAY(sa.Text())),
        sa.Column("lessons", postgresql.ARRAY(sa.Text())),
        sa.Column("counter_examples", postgresql.ARRAY(sa.Text())),
    )
    op.execute("ALTER TABLE historical_cases ADD COLUMN embedding vector(1536)")

    op.create_table(
        "central_bank_comms",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("bank", sa.Text(), nullable=False),
        sa.Column("comm_type", sa.Text()),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("full_text", sa.Text()),
        sa.Column("key_phrases", postgresql.ARRAY(sa.Text())),
        sa.Column("sentiment", sa.Text()),
        sa.Column("sentiment_score", sa.Numeric()),
        sa.Column("change_vs_previous", sa.Text()),
        sa.Column("forward_guidance", sa.Text()),
    )

    op.create_table(
        "economic_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("event_name", sa.Text(), nullable=False),
        sa.Column("event_date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("region", sa.Text()),
        sa.Column("impact_level", sa.Text()),
        sa.Column("expected_value", sa.Text()),
        sa.Column("actual_value", sa.Text()),
        sa.Column("previous_value", sa.Text()),
        sa.Column("surprise_direction", sa.Text()),
        sa.Column("surprise_magnitude", sa.Numeric()),
        sa.Column("historical_metal_impact", postgresql.JSONB()),
    )

    op.create_table(
        "daily_digests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("digest_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("priority_events", postgresql.JSONB()),
        sa.Column("metals_snapshot", postgresql.JSONB()),
        sa.Column("economic_calendar", postgresql.JSONB()),
        sa.Column("active_theses", postgresql.JSONB()),
        sa.Column("full_digest", sa.Text()),
        sa.UniqueConstraint("digest_date", name="uq_daily_digests_digest_date"),
    )


def downgrade() -> None:
    op.drop_table("daily_digests")
    op.drop_table("economic_events")
    op.drop_table("central_bank_comms")
    op.drop_table("historical_cases")
    op.drop_table("metals_knowledge")
    op.drop_table("macro_events")
    op.drop_table("theses")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
