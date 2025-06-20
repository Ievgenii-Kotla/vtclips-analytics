import os
from fastapi import FastAPI
import psycopg2

app = FastAPI()


@app.get("/")
async def root():
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM youtube_channel;")
            rows = cur.fetchall()
            text = f"youtube_channels: {rows[0][0]})"
    return {"message": text}



@app.get("/summary")
async def summary():
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT 'playlists_parsed', COUNT(*)
            FROM (
                SELECT playlist_id
                FROM playlist_items_request
                GROUP BY playlist_id
            ) as pirpi
            UNION ALL
            SELECT 'channels_exist', COUNT(*)
            FROM youtube_channel
            UNION ALL
            SELECT 'videos_exist', COUNT(*) 
            FROM youtube_video
            UNION ALL
            SELECT 'keywords_parsed', COUNT(*)
            FROM (
                SELECT q
                FROM search_yt
                GROUP BY q
            ) as syq;
            """)
            rows = cur.fetchall()
            text = f"youtube_channels: {rows[0][0]})"
    return {"message": rows}

@app.get("/test")
async def test():
    return {"message": "test"}