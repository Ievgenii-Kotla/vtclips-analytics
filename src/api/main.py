import os
from fastapi import FastAPI
import psycopg2
from starlette.responses import PlainTextResponse

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

@app.get("/health", response_class=PlainTextResponse)
async def test():
    return "OK"

@app.get("/status")
async def status():
    with open('/app/collector_info/state/api_quota_state.json', 'r') as f:
         quota_status = f.read()
    with open('/app/collector_info/logs/error.log', 'r') as f:
        error_log = f.read()
    with open('/app/collector_info/logs/warning.log', 'r') as f:
        warning_log = f.read()
    with open('/app/collector_info/logs/info.log', 'r') as f:
        info_log = f.read()

    return PlainTextResponse(
        f"""QUOTA_STATUS:\n {quota_status}\n\n
ERRORS:\n {error_log}\n\n
WARNINGS:\n {warning_log}\n\n
INFO:\n {info_log}
"""
    )