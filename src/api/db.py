from psycopg2 import pool
import os

conn_pool: pool.ThreadedConnectionPool = None

def init_db_pool():
    global conn_pool
    conn_pool = pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=os.environ['DATABASE_URL']
    )

def get_connection():
    conn = conn_pool.getconn()
    try:
        yield conn
    finally:
        conn_pool.putconn(conn)