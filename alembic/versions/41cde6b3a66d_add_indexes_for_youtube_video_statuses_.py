"""add indexes for youtube_video_statuses table

Revision ID: 41cde6b3a66d
Revises: 91e154b4d047
Create Date: 2026-05-06 17:13:22.494890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41cde6b3a66d'
down_revision: Union[str, None] = '91e154b4d047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE INDEX idx_youtube_video_statuses_keywords_counted_at_composite
    ON youtube_video_statuses(keywords_counted_at, youtube_video_id);
    
    CREATE INDEX idx_yvs_yv_id_algorithm1_classified_at_nulls 
    ON youtube_video_statuses (youtube_video_id)
    WHERE algorithm1_classified_at IS NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
