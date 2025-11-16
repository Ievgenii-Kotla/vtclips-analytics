"""add table talent_youtube_video

Revision ID: dbd01cb25645
Revises: 1a55a93db071
Create Date: 2025-11-12 12:04:07.197265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbd01cb25645'
down_revision: Union[str, None] = '1a55a93db071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE talent_youtube_video (
            talent_id integer NOT NULL,
            youtube_video_id text NOT NULL,
            algorithm integer NOT NULL,
            CONSTRAINT pk_talent_youtube_video PRIMARY KEY (talent_id, youtube_video_id, algorithm),
            CONSTRAINT fk_youtube_video_id FOREIGN KEY (youtube_video_id) REFERENCES youtube_video(youtube_video_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_talent_id FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
        );
        
        COMMENT ON TABLE talent_youtube_video IS 'Video-talent pairs. 
        Estimation of who is the video about and based on what algorithm';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
