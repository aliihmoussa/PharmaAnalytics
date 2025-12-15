"""Initial migration - create drug_transactions, data_ingestion_log, data_ingestion_errors tables

Revision ID: b589ede1cdad
Revises: 
Create Date: 2025-12-13 23:39:28.002762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b589ede1cdad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create drug_transactions table
    op.create_table(
        'drug_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('cat', sa.Integer(), nullable=True),
        sa.Column('cr', sa.Integer(), nullable=True, comment='Consuming department'),
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
        sa.Column('ad_date', sa.Date(), nullable=True, comment='Admission date'),
        sa.Column('room_number', sa.Integer(), nullable=True),
        sa.Column('bed_number', sa.Integer(), nullable=True),
        sa.Column('patient_age', sa.String(length=20), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('ingestion_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('quantity != 0', name='chk_quantity_not_zero'),
    )
    
    # Create indexes for drug_transactions
    op.create_index('ix_drug_transactions_transaction_date', 'drug_transactions', ['transaction_date'])
    op.create_index('ix_drug_transactions_drug_code', 'drug_transactions', ['drug_code'])
    op.create_index('idx_transactions_date_dept', 'drug_transactions', ['transaction_date', 'cr'])
    op.create_index('idx_transactions_drug_date', 'drug_transactions', ['drug_code', 'transaction_date'])
    op.create_index('idx_transactions_cat', 'drug_transactions', ['cat'])
    op.create_index('idx_transactions_cr', 'drug_transactions', ['cr'])
    op.create_index('idx_transactions_cs', 'drug_transactions', ['cs'])
    op.create_index('idx_transactions_qty_negative', 'drug_transactions', ['quantity'], postgresql_where=sa.text('quantity < 0'))
    
    # Create data_ingestion_log table
    op.create_table(
        'data_ingestion_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_year', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True, comment='SHA256 hash of original file'),
        sa.Column('total_records', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_records', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_records', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ingestion_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("ingestion_status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')", name='chk_ingestion_status'),
    )
    
    # Create indexes for data_ingestion_log
    op.create_index('ix_data_ingestion_log_ingestion_status', 'data_ingestion_log', ['ingestion_status'])
    op.create_index('ix_data_ingestion_log_file_name', 'data_ingestion_log', ['file_name'])
    
    # Create data_ingestion_errors table
    op.create_table(
        'data_ingestion_errors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ingestion_log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=True, comment='Original row number in file'),
        sa.Column('raw_data', sa.Text(), nullable=True, comment='JSON of raw row data'),
        sa.Column('error_type', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create index for data_ingestion_errors
    op.create_index('ix_data_ingestion_errors_ingestion_log_id', 'data_ingestion_errors', ['ingestion_log_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_data_ingestion_errors_ingestion_log_id', table_name='data_ingestion_errors')
    op.drop_index('ix_data_ingestion_log_file_name', table_name='data_ingestion_log')
    op.drop_index('ix_data_ingestion_log_ingestion_status', table_name='data_ingestion_log')
    op.drop_index('idx_transactions_qty_negative', table_name='drug_transactions')
    op.drop_index('idx_transactions_cs', table_name='drug_transactions')
    op.drop_index('idx_transactions_cr', table_name='drug_transactions')
    op.drop_index('idx_transactions_cat', table_name='drug_transactions')
    op.drop_index('idx_transactions_drug_date', table_name='drug_transactions')
    op.drop_index('idx_transactions_date_dept', table_name='drug_transactions')
    op.drop_index('ix_drug_transactions_drug_code', table_name='drug_transactions')
    op.drop_index('ix_drug_transactions_transaction_date', table_name='drug_transactions')
    
    # Drop tables
    op.drop_table('data_ingestion_errors')
    op.drop_table('data_ingestion_log')
    op.drop_table('drug_transactions')
