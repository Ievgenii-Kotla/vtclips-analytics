from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import PlainTextResponse, JSONResponse

import src.api.services as svc
from src.api.db import get_connection

router = APIRouter()

@router.get("/")
def root():
    return "Nothing here yet..."

@router.get("/summary")
def summary():
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
def summary(conn=Depends(get_connection)):
    return svc.summary(conn)

@router.get("/status")
def status():
    return svc.status()

@router.get("/health", response_class=PlainTextResponse)
def test():
    return "OK"

@router.get("/jinja")
def jinja(request: Request):
    html = svc.jinja(request)
    return html

@router.get("/daisy")
def daisy(request: Request):
    return svc.daisy(request)

@router.get("/charts")
def charts(request: Request):
    return svc.charts(request)

@router.get("/header-info")
def header_info():
    return "399 999 clips in the database"

@router.get("/sample_chart", response_class=JSONResponse)
def sample_chart():
    return [svc.sample_chart(), ]