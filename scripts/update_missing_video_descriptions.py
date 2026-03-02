"""
Update all descriptions where description is NULL, (fixing older data integrity issue)

"""

import os
import json
import psycopg2
from psycopg2.extras import execute_values
from googleapiclient.discovery import build
from src.vtc import db_yt_interface

def main():
    ids = fetch_ids()
    print(f"The first 3 ids are: {ids[0]}, {ids[1]}, {ids[2]}")
    print(f"{len(ids)} videos are set for a description update.")
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        process(batch)

def fetch_ids():
    query = """
    SELECT youtube_video_id
    FROM youtube_video
    WHERE description_normalized IS NULL
    ORDER BY added_at;
    """
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            video_ids = [row[0] for row in cur.fetchall()]
    return video_ids

def process(batch):
    response, ids = request(batch)
    save(response, ids)

def request(ids):
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(threshold=1, delay=False, purpose=db_yt_interface.PrepareAPI.VIDEO_LIST)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.videos().list(
        part='snippet',
        id=','.join(ids)
    ).execute()
    api_service.change_quota(api_key, -1)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    return response, ids

def save(response, ids):
    query = """
    UPDATE youtube_video
    SET description_normalized = %(description_normalized)s
    WHERE youtube_video_id = %(youtube_video_id)s;
    """
    values = [
        {
            "youtube_video_id": video["id"],
            "description_normalized": db_yt_interface.Helper.normalize(video["snippet"]["description"])
        }
        for video in response["items"]
    ]

    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            for value_pair in values:
                cur.execute(query, value_pair)
            conn.commit()
            print(f"{len(values)} video descriptions updated.")


if __name__ == "__main__":
    main()