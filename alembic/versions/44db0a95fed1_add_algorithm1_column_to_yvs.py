"""add 'algorithm1 column to yvs

Revision ID: 44db0a95fed1
Revises: a0432348bfce
Create Date: 2025-10-30 18:42:46.113276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44db0a95fed1'
down_revision: Union[str, None] = 'a0432348bfce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add a column that represents the time a video was categorized by algorithm1."""

    op.execute("""
        ALTER TABLE youtube_video_statuses ADD COLUMN algorithm1_classified_at timestamptz;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
