"""add info_fully_updated_at to the youtube_video table

Revision ID: 48bd05e8def0
Revises: 0deb9d3863ec
Create Date: 2026-04-29 17:53:10.771687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48bd05e8def0'
down_revision: Union[str, None] = '0deb9d3863ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
    ALTER TABLE youtube_video
    ADD COLUMN info_fully_updated_at timestamptz;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
