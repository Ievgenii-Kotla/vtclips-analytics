"""add column info_accessible to youtube_channel table

Revision ID: e403eecf9632
Revises: 6de196aadb67
Create Date: 2026-02-20 12:59:02.921967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e403eecf9632'
down_revision: Union[str, None] = '6de196aadb67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_channel
    ADD COLUMN info_accessible boolean NOT NULL DEFAULT TRUE;
    COMMENT ON COLUMN youtube_channel.info_accessible IS 
        'Indicates whether the channel information could be retrieved via the YouTube Data API';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
