"""add neutral_color column to talent

Revision ID: 43ad3c09e503
Revises: 0d1b77dcec70
Create Date: 2026-03-11 17:48:47.704460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43ad3c09e503'
down_revision: Union[str, None] = '0d1b77dcec70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        ALTER TABLE talent
        ADD COLUMN neutral_color text;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
