"""add table chart_videos_per_talent_montly

Revision ID: 16a9649a8e86
Revises: 4e7989b983dc
Create Date: 2025-12-10 19:47:58.210143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16a9649a8e86'
down_revision: Union[str, None] = '4e7989b983dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
               CREATE TABLE chart_videos_per_talent_monthly
               (
                   published_at_month date,
                   videos_num integer,
                   talent_name text,
                   color text,
                   order_id integer
               );
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
