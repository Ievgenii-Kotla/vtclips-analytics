"""chart_group_talent_mention_monthly

Revision ID: 7c6e9d1fcc00
Revises: ba246823585d
Create Date: 2026-03-03 19:35:51.647117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c6e9d1fcc00'
down_revision: Union[str, None] = 'ba246823585d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_group_talent_mentions_monthly (
            talent_id integer,
            talent_name text,
            talent_color text,
            d_channel_id text,
            d_channel_title text,
            d_channel_icon_url text,
            year_month date,
            talent_mentions_monthly integer,
            total_videos_monthly integer
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
