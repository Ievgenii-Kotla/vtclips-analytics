"""refactor: rename keywords_count_status

Revision ID: 812d851b0468
Revises: 636f77e56761
Create Date: 2025-10-30 17:35:06.053260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '812d851b0468'
down_revision: Union[str, None] = '636f77e56761'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        ALTER TABLE keywords_count_status RENAME TO youtube_video_statuses;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
