from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from src.api.routes import router
from src.api.db import init_db_pool, conn_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_pool()
    try:
        yield
    finally:
        conn_pool.closeall()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

app.include_router(router)
