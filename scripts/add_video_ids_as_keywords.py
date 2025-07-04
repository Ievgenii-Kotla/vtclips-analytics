"""Add ids of the videos into the 'keyword' table as keywords"""

import os
import psycopg2


pre_check_keyword_query = """
SELECT COUNT(*)
FROM youtube_video
WHERE youtube_channel_id IN (
    SELECT youtube_channel_id
    FROM youtube_channel_talent
)
    AND youtube_video_id NOT IN (
        SELECT keyword_word
        FROM keyword
    );
"""
pre_check_keyword_talent_query = """
SELECT COUNT(*)
FROM youtube_video yv
JOIN youtube_channel_talent yct ON yct.youtube_channel_id = yv.youtube_channel_id;
"""

insert_to_keyword_query = """
INSERT INTO keyword (
    keyword_word, 
    date_since_relevant, 
    priority
) 
SELECT 
    youtube_video_id,
    published_at,
    100
FROM youtube_video
WHERE youtube_channel_id IN (
    SELECT youtube_channel_id
    FROM youtube_channel_talent
)
    AND youtube_video_id NOT IN (
        SELECT keyword_word
        FROM keyword
    );
"""
insert_to_keyword_talent_query = """
INSERT INTO keyword_talent (keyword_id, talent_id)
SELECT k.keyword_id, yct.talent_id
FROM keyword k
JOIN youtube_video yv ON k.keyword_word = yv.youtube_video_id
JOIN youtube_channel_talent yct ON yct.youtube_channel_id = yv.youtube_channel_id 
ON CONFLICT (keyword_id, talent_id) DO NOTHING;  
"""


with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
    with conn.cursor() as cur:
        cur.execute(pre_check_keyword_query)
        new_keywords_qty = cur.fetchone()[0]
        cur.execute(pre_check_keyword_talent_query)
        new_keywrod_talents_qty = cur.fetchone()[0]
        print(f'{new_keywords_qty} keywords and {new_keywrod_talents_qty} keyword-talent connections'
              f'will be added. (wrong calc)')
        user_input = input('Continue? y/n: ')
        if user_input == 'y':
            cur.execute(insert_to_keyword_query)
            print(f'{cur.rowcount} rows created (keyword)')
            cur.execute(insert_to_keyword_talent_query)
            print(f'{cur.rowcount} rows created (keyword_talent)')
        else:
            print('Operation canceled')
