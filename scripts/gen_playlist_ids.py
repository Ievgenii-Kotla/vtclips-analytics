"""
Generate playlist ids for existing channels that don't yet have it

Alters the production DB. Be careful.
"""

from vtc import connect_to_db
from psycopg2.extras import execute_values


query_read = """
SELECT youtube_channel_id
FROM youtube_channel
WHERE playlist_id IS NULL;
"""
with connect_to_db.connect_to_db() as conn:
    with conn.cursor() as cur:
        cur.execute(query_read)
        channel_ids = [row[0] for row in cur.fetchall()]

    values = [
        [
            channel_id,
            'UU' + channel_id[2:] if channel_id[:2] == 'UC' else None
        ]
        for channel_id in channel_ids
    ]

    query_write = """
    UPDATE youtube_channel
    SET playlist_id = data.playlist_id 
    FROM (VALUES %s) AS data(youtube_channel_id, playlist_id)
    WHERE youtube_channel.youtube_channel_id = data.youtube_channel_id
    RETURNING youtube_channel.youtube_channel_id;
    """

    with conn.cursor() as cur:
        rows = execute_values(
            cur,
            query_write,
            values,
            template='(%s, %s)',
            fetch=True
        )
    print(f'Updated {len(rows)} playlist ids')
