"""Inventory stock movements (STORE file)."""

from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .base import Base


class InventoryStock(Base):
    """Inventory stock movements (STORE file). One row = one movement; stock level = sum(quantity) per drug."""

    __tablename__ = 'inventory_stock'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    doc_id = Column(Integer, nullable=False)
    line_number = Column(Integer, nullable=True)
    cat = Column(Integer, nullable=True)
    cr = Column(Integer, nullable=True, comment='Consuming department / warehouse')
    transaction_date = Column(Date, nullable=False, index=True)
    movement_number = Column(Integer, nullable=False)
    movement_description = Column(String(255), nullable=True)
    drug_code = Column(String(50), nullable=False, index=True)
    drug_name = Column(String(255), nullable=False)
    m_field = Column(String(50), nullable=True)
    cs = Column(Integer, nullable=True, comment='Supplying department')
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    total_price = Column(Numeric(14, 2), nullable=False)
    voucher = Column(String(50), nullable=True)
    source_file = Column(String(255), nullable=True)
    ingestion_date = Column(DateTime, nullable=False, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index('idx_inventory_stock_drug_date', 'drug_code', 'transaction_date'),
        Index('idx_inventory_stock_transaction_date', 'transaction_date'),
    )
