"""delete data that need to be recalculated (about keywords count)

Revision ID: 4249bf0c313b
Revises: 170e6aead73d
Create Date: 2025-11-15 11:54:42.457330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4249bf0c313b'
down_revision: Union[str, None] = '170e6aead73d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        UPDATE youtube_video_statuses
        SET keywords_counted_at = NULL
        WHERE keywords_counted_at IS NOT NULL;
        
        TRUNCATE TABLE youtube_video_keyword;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
