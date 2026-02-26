"""add column info_fully_updated_at to youtube_channel table

Revision ID: 6de196aadb67
Revises: 03f50cce4e50
Create Date: 2026-02-20 12:14:07.659892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6de196aadb67'
down_revision: Union[str, None] = '03f50cce4e50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_channel
    ADD COLUMN info_fully_updated_at timestamptz;
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
