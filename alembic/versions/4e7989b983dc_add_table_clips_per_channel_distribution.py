"""add table clips_per_channel_distribution

Revision ID: 4e7989b983dc
Revises: 8ca313ce1a9c
Create Date: 2025-12-05 18:21:59.992003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e7989b983dc'
down_revision: Union[str, None] = '8ca313ce1a9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_clips_per_channel_distribution (
            clip_count integer,
            channel_count integer
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
