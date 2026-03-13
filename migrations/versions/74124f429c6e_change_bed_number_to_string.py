"""change bed_number to string

Revision ID: 74124f429c6e
Revises: b589ede1cdad
Create Date: 2025-12-15 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74124f429c6e'
down_revision: Union[str, None] = 'b589ede1cdad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change bed_number from Integer to String(10) to support A/B values
    op.alter_column('drug_transactions', 'bed_number',
                    type_=sa.String(10),
                    existing_type=sa.Integer(),
                    existing_nullable=True,
                    comment='Bed identifier (A, B, or number)')


def downgrade() -> None:
    # Revert bed_number back to Integer
    op.alter_column('drug_transactions', 'bed_number',
                    type_=sa.Integer(),
                    existing_type=sa.String(10),
                    existing_nullable=True)

