"""add partial index on NULLs for infu_fully_updated_at col youtube_video table

Revision ID: 6acdc93a816c
Revises: c3aa80e6b415
Create Date: 2026-04-30 00:00:39.266806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6acdc93a816c'
down_revision: Union[str, None] = 'c3aa80e6b415'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE INDEX idx_info_fully_updated_at_youtube_video_null 
    ON youtube_video (info_fully_updated_at) WHERE info_fully_updated_at IS NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
