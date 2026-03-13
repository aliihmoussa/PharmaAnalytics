"""Drug transaction model."""

from sqlalchemy import (
    Column, Integer, String, Date, Numeric, DateTime, Index, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .base import Base


class DrugTransaction(Base):
    """Drug transaction model."""

    __tablename__ = 'drug_transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    doc_id = Column(Integer, nullable=False)
    line_number = Column(Integer, nullable=True)
    cat = Column(Integer, nullable=True)
    cr = Column(Integer, nullable=True, comment='Consuming department')
    transaction_date = Column(Date, nullable=False, index=True)
    movement_number = Column(Integer, nullable=False)
    movement_description = Column(String(255), nullable=True)
    drug_code = Column(String(50), nullable=False, index=True)
    drug_name = Column(String(255), nullable=False)
    m_field = Column(String(50), nullable=True)
    cs = Column(Integer, nullable=True, comment='Supplying department')
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    ad_date = Column(Date, nullable=True, comment='Admission date')
    room_number = Column(Integer, nullable=True)
    bed_number = Column(String(10), nullable=True, comment='Bed identifier (A, B, or number)')
    date_of_birth = Column(Date, nullable=True, comment='Patient date of birth')
    source_file = Column(String(255), nullable=True)
    ingestion_date = Column(DateTime, nullable=False, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint('quantity != 0', name='chk_quantity_not_zero'),
        Index('idx_transactions_date_dept', 'transaction_date', 'cr'),
        Index('idx_transactions_drug_date', 'drug_code', 'transaction_date'),
        Index('idx_transactions_cat', 'cat'),
        Index('idx_transactions_cr', 'cr'),
        Index('idx_transactions_cs', 'cs'),
        Index('idx_transactions_qty_negative', 'quantity', postgresql_where=quantity < 0),
    )
