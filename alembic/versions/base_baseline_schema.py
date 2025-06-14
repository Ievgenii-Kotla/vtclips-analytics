"""baseline schema

Revision ID: base
Revises: 
Create Date: 2025-06-12 18:42:31.977762

"""
from typing import Sequence, Union
import os

from alembic import op, context
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'base'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    script_location = context.config.get_main_option('script_location')
    path = os.path.join(script_location, 'initial_vtc_schema.sql')
    with open(path) as f:
        op.execute(f.read())


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")