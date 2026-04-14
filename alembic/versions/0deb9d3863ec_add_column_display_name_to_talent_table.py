"""add column 'display_name' to 'talent' table

Revision ID: 0deb9d3863ec
Revises: 43ad3c09e503
Create Date: 2026-04-14 15:56:26.191341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0deb9d3863ec'
down_revision: Union[str, None] = '43ad3c09e503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        ALTER TABLE talent 
        ADD COLUMN display_name text;
    """)



def downgrade() -> None:
    """Downgrade schema."""
    pass
