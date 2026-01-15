"""add table chart_cum_clips_per_talent_daily

Revision ID: c7a951fbe4a4
Revises: 7de579e0b3ea
Create Date: 2026-01-15 16:17:55.200153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7a951fbe4a4'
down_revision: Union[str, None] = '7de579e0b3ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_cum_count_clips_per_talent_daily (
            cum_sum integer,
            talent_name text,
            pub_date date
        );
    """)

def downgrade() -> None:
    """
    Downgrade schema."""
    pass
