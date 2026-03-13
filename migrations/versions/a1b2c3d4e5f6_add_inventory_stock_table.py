"""Add inventory_stock table for STORE file ingestion.

Revision ID: a1b2c3d4e5f6
Revises: 8b226e1e7c95
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8b226e1e7c95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'inventory_stock',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('cat', sa.Integer(), nullable=True),
        sa.Column('cr', sa.Integer(), nullable=True, comment='Consuming department / warehouse'),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('movement_number', sa.Integer(), nullable=False),
        sa.Column('movement_description', sa.String(length=255), nullable=True),
        sa.Column('drug_code', sa.String(length=50), nullable=False),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('m_field', sa.String(length=50), nullable=True),
        sa.Column('cs', sa.Integer(), nullable=True, comment='Supplying department'),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('voucher', sa.String(length=50), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('ingestion_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_inventory_stock_drug_date', 'inventory_stock', ['drug_code', 'transaction_date'])
    op.create_index('idx_inventory_stock_transaction_date', 'inventory_stock', ['transaction_date'])
    op.create_index('ix_inventory_stock_drug_code', 'inventory_stock', ['drug_code'])
    op.create_index('ix_inventory_stock_transaction_date', 'inventory_stock', ['transaction_date'])


def downgrade() -> None:
    op.drop_index('ix_inventory_stock_transaction_date', table_name='inventory_stock')
    op.drop_index('ix_inventory_stock_drug_code', table_name='inventory_stock')
    op.drop_index('idx_inventory_stock_transaction_date', table_name='inventory_stock')
    op.drop_index('idx_inventory_stock_drug_date', table_name='inventory_stock')
    op.drop_table('inventory_stock')
