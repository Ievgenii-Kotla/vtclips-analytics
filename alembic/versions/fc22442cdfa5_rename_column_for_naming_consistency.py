"""rename column for naming consistency

Revision ID: fc22442cdfa5
Revises: 9f9f37f9cdce
Create Date: 2025-10-24 16:50:47.565276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc22442cdfa5'
down_revision: Union[str, None] = '9f9f37f9cdce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
    ALTER TABLE youtube_video_keyword
    RENAME COLUMN updated_on TO updated_at;
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
