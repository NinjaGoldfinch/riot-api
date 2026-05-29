"""Initial operational tables.

Revision ID: 0001_initial_operational_tables
Revises:
Create Date: 2026-05-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_operational_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "riot_cache_entries",
        sa.Column("cache_key", sa.String(length=512), primary_key=True),
        sa.Column("resource_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "riot_rate_limit_observations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("region", sa.String(length=32), nullable=False, index=True),
        sa.Column("service", sa.String(length=64), nullable=False, index=True),
        sa.Column("method", sa.String(length=128), nullable=False, index=True),
        sa.Column("limit_type", sa.String(length=32), nullable=False, index=True),
        sa.Column("limit_header", sa.String(length=255), nullable=True),
        sa.Column("count_header", sa.String(length=255), nullable=True),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("riot_rate_limit_observations")
    op.drop_table("riot_cache_entries")
