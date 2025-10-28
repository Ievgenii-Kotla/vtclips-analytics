"""fix PK in youtube_video_keyword

Revision ID: 95e0e19f8c5f
Revises: initial
Create Date: 2025-10-08 16:19:49.925364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95e0e19f8c5f'
down_revision: Union[str, None] = 'initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop old PK column and create new one."""

    op.execute("""
        ALTER TABLE youtube_video_keyword
        DROP youtube_video_keyword_id,
        ADD CONSTRAINT pk_youtube_video_keyword PRIMARY KEY (youtube_video_id, keyword_id);
   """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
