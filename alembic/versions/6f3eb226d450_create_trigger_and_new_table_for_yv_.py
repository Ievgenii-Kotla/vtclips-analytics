"""create trigger and new table for yv count status

Revision ID: 6f3eb226d450
Revises: fc22442cdfa5
Create Date: 2025-10-24 17:03:10.767930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f3eb226d450'
down_revision: Union[str, None] = 'fc22442cdfa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create a table for keywords-count status and a trigger for auto-updating the table with new videos."""

    op.execute("""
    CREATE TABLE keywords_count_status (
        youtube_video_id text PRIMARY KEY,
        keywords_counted_at timestamptz,
        FOREIGN KEY (youtube_video_id) REFERENCES youtube_video(youtube_video_id) ON DELETE CASCADE
    );
    
    CREATE FUNCTION create_kcs_row() RETURNS trigger AS $$
    BEGIN
        INSERT INTO keywords_count_status(youtube_video_id, keywords_updated_at) VALUES (NEW.youtube_video_id, NULL);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    CREATE TRIGGER yv_insert_kcs
    AFTER INSERT ON youtube_video
    FOR EACH ROW
    EXECUTE FUNCTION create_kcs_row();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
