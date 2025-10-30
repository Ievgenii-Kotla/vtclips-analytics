"""fix: recreate trigger and trigger function

Revision ID: a0432348bfce
Revises: 812d851b0468
Create Date: 2025-10-30 17:38:45.243737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0432348bfce'
down_revision: Union[str, None] = '812d851b0468'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        CREATE FUNCTION create_kcs_row() RETURNS trigger AS
        $$
        BEGIN
           INSERT INTO youtube_video_statuses(youtube_video_id)
           VALUES (NEW.youtube_video_id);
           RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER yv_insert_kcs
           AFTER INSERT
           ON youtube_video
           FOR EACH ROW
        EXECUTE FUNCTION create_kcs_row();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
