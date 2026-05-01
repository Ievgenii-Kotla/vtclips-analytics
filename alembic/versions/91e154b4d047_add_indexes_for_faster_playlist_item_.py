"""add indexes for faster playlist_item_requesting

Revision ID: 91e154b4d047
Revises: d35319165e6e
Create Date: 2026-05-01 17:19:36.942196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91e154b4d047'
down_revision: Union[str, None] = 'd35319165e6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE INDEX idx_playlist_available_youtube_channel_true 
    ON youtube_channel (playlist_available) 
    WHERE playlist_available IS TRUE;
    
    CREATE INDEX idx_playlist_id_youtube_channel_not_null 
    ON youtube_channel (playlist_id) 
    WHERE playlist_id IS NOT NULL;
    
    CREATE INDEX idx_is_other_youtube_channel_not_true 
    ON youtube_channel (is_other) 
    WHERE is_other IS NOT TRUE;
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
