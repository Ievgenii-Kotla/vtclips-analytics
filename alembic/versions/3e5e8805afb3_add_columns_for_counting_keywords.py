"""add columns for counting keywords

Revision ID: 3e5e8805afb3
Revises: 95e0e19f8c5f
Create Date: 2025-10-18 13:16:32.130951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e5e8805afb3'
down_revision: Union[str, None] = '95e0e19f8c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        ALTER TABLE keyword
        ADD COLUMN added_at timestamptz;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
