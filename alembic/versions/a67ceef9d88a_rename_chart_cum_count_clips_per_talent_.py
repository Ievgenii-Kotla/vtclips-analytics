"""rename chart_cum_count_clips_per_talent_daily table

Revision ID: a67ceef9d88a
Revises: 79fe651075c9
Create Date: 2026-02-04 10:45:49.605491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a67ceef9d88a'
down_revision: Union[str, None] = '79fe651075c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    DROP TABLE chart_cum_count_clips_per_talent_daily;
    CREATE TABLE chart_cum_count_svideos_per_talent_daily (
            cum_sum integer,
            talent_name text,
            pub_date date,
            color text,
            debut_datetime timestamptz
    );
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
