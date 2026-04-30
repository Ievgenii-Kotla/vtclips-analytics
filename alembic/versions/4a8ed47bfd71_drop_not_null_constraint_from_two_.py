"""drop NOT NULL constraint from two columns in youtube_video_stats

Revision ID: 4a8ed47bfd71
Revises: 6acdc93a816c
Create Date: 2026-04-30 03:18:14.439606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a8ed47bfd71'
down_revision: Union[str, None] = '6acdc93a816c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_video_stats
        ALTER COLUMN like_count DROP NOT NULL,
        ALTER COLUMN comment_count DROP NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
