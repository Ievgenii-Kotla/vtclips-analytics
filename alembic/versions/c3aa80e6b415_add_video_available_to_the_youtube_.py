"""add video_available to the youtube_video table

Revision ID: c3aa80e6b415
Revises: 48bd05e8def0
Create Date: 2026-04-29 20:06:37.218335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3aa80e6b415'
down_revision: Union[str, None] = '48bd05e8def0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
    ALTER TABLE youtube_video
    ADD COLUMN video_available boolean;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
