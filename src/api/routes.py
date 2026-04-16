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

@router.get("/api/about", response_class=HTMLResponse)
def header_info():
    return svc.about()

@router.get("/api/header-info", response_class=PlainTextResponse)
def header_info(conn=Depends(get_connection)):
    return svc.header_info(conn)

@router.get("/api/tab/overview", response_class=JSONResponse)
def overview(conn=Depends(get_connection)):
    return svc.overview(conn)

@router.get("/api/tab/talent", response_class=JSONResponse)
def tab_2(name: str | None = None, conn=Depends(get_connection)):
    return svc.talent_tab(conn, name)

@router.get("/api/talent_selector", response_class=JSONResponse)
def talent_selector(conn=Depends(get_connection)):
    return svc.talent_selector(conn)

@router.get("/api/talent_charts/{talent_name}", response_class=JSONResponse)
def talent_charts(talent_name: str, conn=Depends(get_connection)):
    return svc.talent_charts(conn, talent_name)

@router.get("/api/talent_charts_and_links/{talent_name}", response_class=JSONResponse)
def talent_charts(talent_name: str, conn=Depends(get_connection)):
    return svc.talent_charts_and_links(conn, talent_name)

@router.get("/api/tab/misc", response_class=JSONResponse)
def miscellaneous(conn=Depends(get_connection)):
    return svc.miscellaneous(conn)

@router.get("/{full_path:path}")
async def serve_page(request: Request, full_path: str):
    return svc.main(request)
