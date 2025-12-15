"""change patient_age to date_of_birth

Revision ID: 8b226e1e7c95
Revises: 74124f429c6e
Create Date: 2025-12-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b226e1e7c95'
down_revision = '74124f429c6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, clear existing values (they were age strings, not dates)
    op.execute("""
        UPDATE drug_transactions 
        SET patient_age = NULL 
        WHERE patient_age IS NOT NULL
    """)
    
    # Rename column from patient_age to date_of_birth
    op.alter_column('drug_transactions', 'patient_age',
                    new_column_name='date_of_birth',
                    existing_type=sa.String(20),
                    existing_nullable=True)
    
    # Change column type from String to Date
    # Use USING clause to handle conversion (since we cleared data, this will set NULL values)
    op.execute("""
        ALTER TABLE drug_transactions 
        ALTER COLUMN date_of_birth TYPE DATE 
        USING NULL
    """)
    
    # Add comment
    op.execute("""
        COMMENT ON COLUMN drug_transactions.date_of_birth IS 'Patient date of birth'
    """)


def downgrade() -> None:
    # Change column type back to String
    op.alter_column('drug_transactions', 'date_of_birth',
                    type_=sa.String(20),
                    existing_type=sa.Date(),
                    existing_nullable=True)
    
    # Rename column back to patient_age
    op.alter_column('drug_transactions', 'date_of_birth',
                    new_column_name='patient_age',
                    existing_type=sa.String(20),
                    existing_nullable=True)

