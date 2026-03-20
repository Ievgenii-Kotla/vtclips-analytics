"""tune autovacuum for youtube_video and youtube_video_statuses

Revision ID: 0d1b77dcec70
Revises: 7c6e9d1fcc00
Create Date: 2026-03-06 11:22:54.079868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d1b77dcec70'
down_revision: Union[str, None] = '7c6e9d1fcc00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE youtube_video SET (
        autovacuum_vacuum_scale_factor = 0.01,
        autovacuum_vacuum_threshold = 1000
    );
    ALTER TABLE youtube_video_statuses SET (
        autovacuum_vacuum_scale_factor = 0.01,
        autovacuum_vacuum_threshold = 1000
    );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
