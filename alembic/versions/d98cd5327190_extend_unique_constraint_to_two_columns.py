"""extend UNIQUE constraint to two columns
in 'keyword' table from 'keyword_word' only to also 'priority'

Revision ID: d98cd5327190
Revises: dbd01cb25645
Create Date: 2025-11-12 16:51:15.700850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd98cd5327190'
down_revision: Union[str, None] = 'dbd01cb25645'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE keyword
        DROP CONSTRAINT unique_keyword_word;
               
        ALTER TABLE keyword
        ADD CONSTRAINT unique_keyword_word_priority UNIQUE (keyword_word, priority);   
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
