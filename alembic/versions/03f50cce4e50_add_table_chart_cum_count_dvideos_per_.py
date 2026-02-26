"""add table chart_cum_count_dvideos_per_talent_daily

Revision ID: 03f50cce4e50
Revises: a67ceef9d88a
Create Date: 2026-02-04 22:10:20.425719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03f50cce4e50'
down_revision: Union[str, None] = 'a67ceef9d88a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE TABLE chart_cum_count_dvideos_per_talent_daily (
            cum_sum integer,
            talent_name text,
            pub_date date,
            color text,
            debut_datetime timestamptz
    );

    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
