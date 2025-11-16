"""update 'keyword' table descr

Revision ID: 1a55a93db071
Revises: 44db0a95fed1
Create Date: 2025-11-11 10:23:27.032925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a55a93db071'
down_revision: Union[str, None] = '44db0a95fed1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        COMMENT ON TABLE keyword IS 
        'Keywords that can be used to find or identify videos related to a talent.
            Guidelines:
            0 - channel''s handle
            1 - channel''s ID (str of seemingly random characters)
            2 - first name middle name last name (no space) 
            3 - last name middle name first name (no space)
            4 - first name middle name last name (with space inbetween)
            5 - last name middle name first name (with space inbetween)
            6 - first name
            7 - last name
            8 - middle name
            9 - nicknames popular
            10 - nicknames somewhat common
            11 - nicknames rare
            12 - channel handle without ''@''
            13 - group name
            14 - branch name (holoen, hololiveEN, etc.)
            99 - video_id of a video made by a talent
            Note: do not add/use keywords that are too short and may appear inside other words 
            like ame in america
            or wawa in kiwawa, fuwawa';
        """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
