"""fix: remove trigger and trigger function

Revision ID: 636f77e56761
Revises: b60f622787d0
Create Date: 2025-10-30 17:33:10.464380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '636f77e56761'
down_revision: Union[str, None] = 'b60f622787d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove trigger and trigger function again."""

    op.execute("""
        DROP TRIGGER yv_insert_kcs ON youtube_video;
        DROP FUNCTION create_kcs_row();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
