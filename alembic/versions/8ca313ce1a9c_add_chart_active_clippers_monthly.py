"""add chart_active_clippers_monthly

Revision ID: 8ca313ce1a9c
Revises: 481f39b1c0ae
Create Date: 2025-12-05 15:49:39.080248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ca313ce1a9c'
down_revision: Union[str, None] = '481f39b1c0ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE chart_active_clippers_monthly (
            published_at_month date,
            clippers_num integer
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
