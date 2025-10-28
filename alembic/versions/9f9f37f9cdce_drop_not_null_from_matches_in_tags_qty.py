"""drop NOT NULL from matches_in_tags_qty

Revision ID: 9f9f37f9cdce
Revises: d9748d3ee3c2
Create Date: 2025-10-21 18:10:41.970284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f9f37f9cdce'
down_revision: Union[str, None] = 'd9748d3ee3c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE youtube_video_keyword ALTER COLUMN matches_in_tags_qty DROP NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
