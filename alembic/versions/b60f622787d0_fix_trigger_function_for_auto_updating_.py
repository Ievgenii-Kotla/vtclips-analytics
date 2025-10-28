"""fix: trigger function for auto-updating keywords_cound_status video id rows

Revision ID: b60f622787d0
Revises: d0992557cef8
Create Date: 2025-10-28 12:32:32.878951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b60f622787d0'
down_revision: Union[str, None] = 'd0992557cef8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix the trigger for auto-updating keywords_count_status with new videos."""

    op.execute("""
        DROP TRIGGER yv_insert_kcs ON youtube_video;
        DROP FUNCTION create_kcs_row();
    
        CREATE FUNCTION create_kcs_row() RETURNS trigger AS
        $$
        BEGIN
           INSERT INTO keywords_count_status(youtube_video_id, keywords_counted_at)
           VALUES (NEW.youtube_video_id, NULL);
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
