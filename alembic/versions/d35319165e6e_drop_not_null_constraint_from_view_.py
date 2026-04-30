"""drop NOT NULL constraint from view_count column of youtube_video_stats table

Revision ID: d35319165e6e
Revises: 4a8ed47bfd71
Create Date: 2026-04-30 05:06:33.717243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd35319165e6e'
down_revision: Union[str, None] = '4a8ed47bfd71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_video_stats
        ALTER COLUMN view_count DROP NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
