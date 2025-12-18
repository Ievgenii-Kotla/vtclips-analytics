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
def sample_chart(conn=Depends(get_connection)):
    return [svc.all_clips_day(conn),]
    # return [svc.sample_chart(), ]

@router.get("/overview", response_class=JSONResponse)
def overview(conn=Depends(get_connection)):
    return svc.overview(conn)

@router.get("/tab2", response_class=JSONResponse)
def tab_2(conn=Depends(get_connection)):
    return svc.tab_2(conn)

@router.get("/misc", response_class=JSONResponse)
def miscellaneous(conn=Depends(get_connection)):
    return svc.miscellaneous(conn)