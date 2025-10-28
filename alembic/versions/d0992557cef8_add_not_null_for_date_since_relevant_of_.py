"""add not null for date_since_relevant of keyword table

Revision ID: d0992557cef8
Revises: ba0b78fe5372
Create Date: 2025-10-27 10:35:34.471888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0992557cef8'
down_revision: Union[str, None] = 'ba0b78fe5372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE keyword ALTER COLUMN date_since_relevant SET NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
