"""Widen inventory_stock unit_price and total_price to NUMERIC(14,2) to avoid overflow.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'inventory_stock',
        'unit_price',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.Numeric(precision=14, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        'inventory_stock',
        'total_price',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.Numeric(precision=14, scale=2),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'inventory_stock',
        'unit_price',
        existing_type=sa.Numeric(precision=14, scale=2),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        'inventory_stock',
        'total_price',
        existing_type=sa.Numeric(precision=14, scale=2),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )
