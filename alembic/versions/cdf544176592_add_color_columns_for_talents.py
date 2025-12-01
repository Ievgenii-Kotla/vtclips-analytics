"""add color columns for talents

Revision ID: cdf544176592
Revises: 003432ab4a90
Create Date: 2025-12-01 22:21:32.294745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdf544176592'
down_revision: Union[str, None] = '003432ab4a90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        ALTER TABLE talent
        ADD COLUMN dark_color text,
        ADD COLUMN light_color text;
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
