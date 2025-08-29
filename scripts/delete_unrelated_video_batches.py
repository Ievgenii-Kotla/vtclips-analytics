"""
DELETE from the DB all videos from all channels that
do not have a single video with any keyword in its title or description.
"""

import unicodedata
import html
import os
import psycopg2
from psycopg2 import sql




def delete_unrelated(conn):
    query_prepare_data = """
    SELECT 1;
    -- It is done this way for speed
    CREATE TEMP TABLE tmp_related_video AS
    SELECT DISTINCT ON (yv.youtube_video_id) yv.youtube_channel_id, yv.youtube_video_id, TRUE AS related
    FROM keyword AS k
    LEFT JOIN youtube_video yv ON yv.description_normalized ~* k.keyword_word OR yv.title_normalized ~* k.keyword_word
    WHERE k.priority IN (0, 1, 99);
    
    CREATE TEMP TABLE tmp_video_all AS
    SELECT yv.youtube_channel_id, yv.youtube_video_id, (CASE WHEN trv.related IS NULL THEN FALSE ELSE TRUE END) AS related
    FROM tmp_related_video trv
    RIGHT JOIN youtube_video yv ON trv.youtube_video_id = yv.youtube_video_id
    WHERE yv.description_normalized IS NOT NULL;
    """

    query_stats = """
    SELECT
        COUNT(*) FILTER (WHERE related = FALSE) AS unrelated_videos_qty,
        COUNT(*) FILTER (WHERE related = TRUE) AS related_videos_qty
    FROM tmp_video_all;
    """

    query_channels_for_cleanup = """
    CREATE TEMP TABLE tmp_channel_for_purge AS
    WITH channel_with_finished_playlist AS (
        SELECT DISTINCT ON (yc.youtube_channel_id) yc.youtube_channel_id
        FROM playlist_items_request pir
        JOIN youtube_channel yc USING (playlist_id)
        WHERE next_page_token IS NULL
        GROUP BY yc.youtube_channel_id
    ),
    channel_unrelated_to_vt AS (
        SELECT 
            youtube_channel_id,
            COUNT(*) FILTER (WHERE related = FALSE) AS unrelated_videos_qty,
            COUNT(*) FILTER (WHERE related = TRUE) AS related_videos_qty
        FROM tmp_video_all
        GROUP BY youtube_channel_id
            HAVING COUNT(*) FILTER (WHERE related = TRUE)  = 0
    )
        
    SELECT cwfp.youtube_channel_id
    FROM channel_with_finished_playlist cwfp
    JOIN channel_unrelated_to_vt cutv ON cutv.youtube_channel_id = cwfp.youtube_channel_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM youtube_channel_talent yct
        WHERE yct.youtube_channel_id = cwfp.youtube_channel_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM youtube_channel yc
        WHERE yc.youtube_channel_id = cwfp.youtube_channel_id AND yc.is_other IS TRUE
    );
    """

    query_videos_to_delete_qty = """
    SELECT COUNT(*)
    FROM tmp_channel_for_purge tcfp
    JOIN youtube_video yv ON tcfp.youtube_channel_id = yv.youtube_channel_id;
    """


    with conn.cursor() as cur:
        print("Preparing a list of unrelated videos. This may take a while.")
        cur.execute(query_prepare_data)

        cur.execute("SELECT COUNT(*) FROM youtube_video;")
        row = cur.fetchone()
        print(f"Videos total: {row[0]}")

        cur.execute(query_stats)
        row = cur.fetchone()
        print(f"Total keyword related videos: {row[1]}")
        print(f"Total keyword unrelated videos: {row[0]}")

        cur.execute(query_channels_for_cleanup)
        cur.execute("SELECT youtube_channel_id FROM tmp_channel_for_purge;")
        rows = cur.fetchall()
        print(f"Qty of channels that will be cleaned: {cur.rowcount}")

        cur.execute(query_videos_to_delete_qty)
        print(f"Total videos to be deleted: {cur.fetchone()[0]}")

    show = input("Show channel URLs? y/n: ")
    if show == 'y':
        channel_urls = ['https://www.youtube.com/channel/' + row[0] for row in rows]
        print(f"Channels that will be cleaned: \n{channel_urls}")

    do_delete = input("Delete permanently? y/n: ")
    if do_delete == 'y':
        print("Deleting. This may take a while.")
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM youtube_video yv 
                USING tmp_channel_for_purge tcfp 
                WHERE yv.youtube_channel_id = tcfp.youtube_channel_id; 
                """
            )
            print(f"Deleted {cur.rowcount} videos")

            print("Updating 'is_other' column for channels.")
            cur.execute(
                """
                UPDATE youtube_channel 
                SET is_other = TRUE 
                WHERE youtube_channel_id IN (SELECT youtube_channel_id FROM tmp_channel_for_purge);""")
            print(f"Set is_other = TRUE for {cur.rowcount} channels")
            print("Done.")
    else:
        print("Operation canceled")

if __name__ == '__main__':
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        delete_unrelated(conn)

