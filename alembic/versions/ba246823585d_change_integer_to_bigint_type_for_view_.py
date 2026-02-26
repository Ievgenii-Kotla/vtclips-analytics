"""change integer to bigint type for view_count column in youtube_channel_stats

Revision ID: ba246823585d
Revises: e403eecf9632
Create Date: 2026-02-26 19:37:26.942471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba246823585d'
down_revision: Union[str, None] = 'e403eecf9632'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_channel_stats 
    ALTER COLUMN view_count TYPE bigint;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
