"""fix missing color column and debut_datetime column in cum_count_clips_per_talent

Revision ID: 79fe651075c9
Revises: c7a951fbe4a4
Create Date: 2026-01-16 21:59:39.174282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79fe651075c9'
down_revision: Union[str, None] = 'c7a951fbe4a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    ALTER TABLE chart_cum_count_clips_per_talent_daily
    ADD COLUMN color text,
    ADD COLUMN debut_datetime timestamptz
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
