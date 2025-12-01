import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import psycopg2
from starlette.responses import PlainTextResponse, JSONResponse

import src.api.services as svc

router = APIRouter()

@router.get("/")
def root():
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM youtube_channel;")
            rows = cur.fetchall()
            text = f"youtube_channels: {rows[0][0]})"
    return {"message": text}



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

@router.get("/test")
def test():
    return {"message": "test"}

@router.get("/health", response_class=PlainTextResponse)
def test():
    return "OK"

@router.get("/status")
def status():
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


@router.get("/jinja", response_class=HTMLResponse)
def jinja(request: Request):
    html = svc.jinja(request)
    return html

@router.get("/daisy", response_class=HTMLResponse)
def daisy(request: Request):
    return svc.daisy(request)

@router.get("/charts", response_class=HTMLResponse)
def charts(request: Request):
    return svc.charts(request)

@router.get("/header-info", response_class=PlainTextResponse)
def header_info():
    return "399 999 clips in the database"

@router.get("/sample_chart", response_class=JSONResponse)
def sample_chart():
    return [svc.sample_chart(), ]