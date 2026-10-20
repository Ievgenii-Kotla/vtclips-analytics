"""add table for svideo categorized

Revision ID: 2556cada30e1
Revises: 41cde6b3a66d
Create Date: 2026-10-16 20:26:07.733859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2556cada30e1'
down_revision: Union[str, None] = '41cde6b3a66d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_svideos_categorized (
            youtube_video_id text,
            published_at date, 
            title text, 
            talent_name text, 
            talent_id integer,
            category text
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass


