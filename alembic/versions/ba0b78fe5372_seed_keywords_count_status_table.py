"""seed keywords_count_status table

Revision ID: ba0b78fe5372
Revises: 6f3eb226d450
Create Date: 2025-10-24 18:26:28.603957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba0b78fe5372'
down_revision: Union[str, None] = '6f3eb226d450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        INSERT INTO keywords_count_status(youtube_video_id, keywords_counted_at)
        SELECT youtube_video_id, NULL FROM youtube_video yv;
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
