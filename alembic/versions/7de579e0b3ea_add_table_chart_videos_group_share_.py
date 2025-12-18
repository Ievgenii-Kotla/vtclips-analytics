"""add table chart_videos_group_share_monthly

Revision ID: 7de579e0b3ea
Revises: 16a9649a8e86
Create Date: 2025-12-15 21:11:01.438172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7de579e0b3ea'
down_revision: Union[str, None] = '16a9649a8e86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_videos_group_share_monthly (
            published_at_month date,
            videos_num integer,
            group_name text,
            order_id integer,
            pct integer
       ); 
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
