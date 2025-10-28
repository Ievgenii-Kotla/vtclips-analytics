"""add defaults and constraints for counting keywords

Revision ID: d9748d3ee3c2
Revises: 2f6dac3e3ed5
Create Date: 2025-10-18 14:36:25.075010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9748d3ee3c2'
down_revision: Union[str, None] = '2f6dac3e3ed5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
    ALTER TABLE keyword ALTER COLUMN added_at SET DEFAULT (now() AT TIME ZONE 'UTC');
    ALTER TABLE keyword ALTER COLUMN added_at SET NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
