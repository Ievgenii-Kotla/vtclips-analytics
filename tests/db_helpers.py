"""
Helper functions to insert, update, and delete test data in the database.
Each function takes a psycopg2 connection and performs one specific operation.
"""

from psycopg2 import sql
import datetime

DEFAULT_TIME = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

def create_row(conn, table_name, data):
    validate_columns(conn, table_name, data)
    query = get_query(table_name, data)
    with conn.cursor() as cur:
        cur.execute(query, data)
    conn.commit()

def get_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE';
        """)
        return {row[0] for row in cur.fetchall()}

def get_table_columns(conn, table_name:str):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
              AND table_schema = 'public';
        """, (table_name,))
        return {row[0] for row in cur.fetchall()}

def validate_columns(conn, table_name:str, data:dict):
    valid_cols = get_table_columns(conn, table_name)
    nonvalid_cols = set(data) - valid_cols
    if nonvalid_cols:
        raise ValueError(f"Column(s) {nonvalid_cols} for table '{table_name}' do not exist.")

def get_query(table_name:str, data:dict):
    cols = list(data.keys())
    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({places})").format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(", ").join(map(sql.Identifier, cols)),
        places=sql.SQL(", ").join(map(sql.Placeholder, cols))
    )
    return query

def insert(conn, table_name, **kwargs):
    valid_tables = get_tables(conn)
    if table_name not in valid_tables:
        raise ValueError(f"Table {table_name!r} does not exist")

    valid_cols = get_table_columns(conn, table_name)
    nonvalid_cols = set(kwargs) - valid_cols
    if nonvalid_cols:
        raise ValueError(f"Column(s) {nonvalid_cols} for table {table_name!r} do not exist.")

    cols = list(kwargs.keys())
    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({places})").format(
        table  = sql.Identifier(table_name),
        fields = sql.SQL(", ").join(map(sql.Identifier, cols)),
        places = sql.SQL(", ").join(map(sql.Placeholder, cols))
    )
    with conn.cursor() as cur:
        cur.execute(query, kwargs)
    conn.commit()

def insert_youtube_video(
        conn,
        youtube_video_id='video_id',
        youtube_channel_id='channel_id',
        published_at=DEFAULT_TIME,
        title='video_title',
        updated_at=DEFAULT_TIME,
        kind='youtube#video',
        thumbnail_default_url='default_url',
        thumbnail_medium_url='medium_url',
        thumbnail_high_url='high_url',
        added_at=DEFAULT_TIME,
        **kwargs
):
    table_name = 'youtube_video'
    data = {
        "youtube_video_id": youtube_video_id,
        "youtube_channel_id": youtube_channel_id,
        "published_at": published_at,
        "title": title,
        "updated_at": updated_at,
        "kind": kind,
        "thumbnail_default_url": thumbnail_default_url,
        "thumbnail_medium_url": thumbnail_medium_url,
        "thumbnail_high_url": thumbnail_high_url,
        "added_at": added_at,
    }
    data.update(kwargs)
    create_row(conn, table_name, data)


def insert_youtube_channel(conn,
                           channel_info_last_updated=DEFAULT_TIME,
                           title='channel_title',
                           added_at=DEFAULT_TIME,
                           youtube_channel_id='channel_id',
                           **kwargs
                           ):
    table_name = 'youtube_channel'
    data = {
        "channel_info_last_updated": channel_info_last_updated,
        "title": title,
        "added_at": added_at,
        "youtube_channel_id": youtube_channel_id
    }
    data.update(kwargs)
    create_row(conn, table_name, data)

def insert_search_yt(conn,
                     searched_at=DEFAULT_TIME,
                     published_after=DEFAULT_TIME,
                     published_before=DEFAULT_TIME,
                     results_per_page_max=50,
                     total_results=1,
                     results_per_page=1,
                     **kwargs
                     ):
    table_name = 'search_yt'
    data = {
        "searched_at": searched_at,
        "published_after": published_after,
        "published_before": published_before,
        "results_per_page_max": results_per_page_max,
        "total_results": total_results,
        "results_per_page": results_per_page
    }
    data.update(kwargs)
    create_row(conn, table_name, data)

def insert_search_yt_youtube_video(conn,
                                   search_yt_id=1,
                                   youtube_video_id=1,
                                   **kwargs
                                   ):
    table_name = 'search_yt_youtube_video'
    data = {
        "search_yt_id": search_yt_id,
        "youtube_video_id": youtube_video_id
    }
    data.update(kwargs)
    create_row(conn, table_name, data)

def truncate_all(conn):
    tables = get_tables(conn)
    tables = sql.SQL(", ").join(map(sql.Identifier, tables))
    with conn.cursor() as cur:
        cur.execute(sql.SQL("TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE").format(tables=tables))
    conn.commit()