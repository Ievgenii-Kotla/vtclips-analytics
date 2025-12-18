"""add chart_all_clips_day table

Revision ID: 481f39b1c0ae
Revises: cdf544176592
Create Date: 2025-12-02 17:55:36.229110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '481f39b1c0ae'
down_revision: Union[str, None] = 'cdf544176592'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_all_clips_day (
            published_at_date date,
            clips_num integer
        );
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
