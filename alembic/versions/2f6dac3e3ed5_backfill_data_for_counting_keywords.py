"""backfill data for counting keywords

Revision ID: 2f6dac3e3ed5
Revises: 3e5e8805afb3
Create Date: 2025-10-18 13:44:45.715943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f6dac3e3ed5'
down_revision: Union[str, None] = '3e5e8805afb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        UPDATE keyword
        SET added_at = CASE 
            WHEN priority IN(99) THEN (SELECT published_at FROM youtube_video WHERE youtube_video_id = keyword_word)
            ELSE '2024-01-01 00:00:00+00'
        END;
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
