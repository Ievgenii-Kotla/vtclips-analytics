"""Add ids of the videos into the 'keyword' table as keywords"""

from vtc import db_yt_interface, connect_to_db

insert_query = """
INSERT INTO keyword (
    keyword_word, 
    date_since_relevant, 
    priority
) 
SELECT 
    youtube_video_id,
    published_at - INTERVAL '1 month',
    100
FROM youtube_video yv
LEFT JOIN keyword k ON yv.youtube_video_id = k.keyword_word
WHERE k.keyword_word IS NULL;
"""

pre_check_query = """
SELECT COUNT(*)
FROM youtube_video yv
LEFT JOIN keyword k ON yv.youtube_video_id = k.keyword_word
WHERE k.keyword_word IS NULL;
"""

with connect_to_db.connect_to_staging_test_db() as conn:
    with conn.cursor() as cur:
        cur.execute(pre_check_query)
        user_input = input(f'{cur.fetchone()[0]} keywords will be added. Continue? y/n: ')
        if user_input == 'y':
            cur.execute(insert_query)
            print(f'{cur.rowcount} rows created')
        else:
            print('Operation aborted')
