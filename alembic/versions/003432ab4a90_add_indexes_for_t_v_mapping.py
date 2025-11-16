"""add indexes for t-v mapping

Revision ID: 003432ab4a90
Revises: 4249bf0c313b
Create Date: 2025-11-16 11:17:48.998138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003432ab4a90'
down_revision: Union[str, None] = '4249bf0c313b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_talent_youtube_video_youtube_video_id ON talent_youtube_video(youtube_video_id);
        CREATE INDEX IF NOT EXISTS idx_youtube_video_youtube_channel_id ON youtube_video(youtube_channel_id);
        CREATE INDEX IF NOT EXISTS idx_youtube_video_keyword_youtube_video_id ON youtube_video_keyword(youtube_video_id);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
