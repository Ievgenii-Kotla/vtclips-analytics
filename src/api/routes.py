from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import PlainTextResponse, JSONResponse
from fastapi.responses import Response
import json


import src.api.services as svc
from src.api.db import get_connection

router = APIRouter()

@router.get("/")
def root(request: Request):
    return svc.main(request)


@router.get("/status")
def status():
    return svc.status()

@router.get("/health", response_class=PlainTextResponse)
def test():
    return "OK"


@router.get("/api/header-info")
def header_info():
    return "399 999 clips in the database"

@router.get("/api/tab/overview", response_class=JSONResponse)
def overview(conn=Depends(get_connection)):
    return svc.overview(conn)

@router.get("/api/tab/2025", response_class=JSONResponse)
def tab_2(conn=Depends(get_connection)):
    return svc.tab_2025(conn)

@router.get("/api/tab/tab3")
def tab_3(conn=Depends(get_connection)):
    result = svc.tab_3(conn)
    return Response(
        content=json.dumps(result),
        media_type="application/json"
    )

@router.get("api/tab/who-clips-my-oshi", response_class=JSONResponse)
def who_clips_my_oshi(conn=Depends(get_connection)):
    return svc.who_clips_my_oshi(conn)

@router.get("api/tab/misc", response_class=JSONResponse)
def miscellaneous(conn=Depends(get_connection)):
    return svc.miscellaneous(conn)

@router.get("/{full_path:path}")
async def serve_page(request: Request, full_path: str):
    return svc.main(request)
