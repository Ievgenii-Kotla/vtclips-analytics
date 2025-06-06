"""Normalizes database text fields with NFKC if not yet processed"""

import unicodedata
from psycopg2 import sql

from vtc.connect_to_db import connect_to_db


def normalize_fields(conn, source_field:str, target_field:str):
    loops: int = 10000
    qty: int = 0
    read_query = sql.SQL("SELECT youtube_video_id, {source_field} "
                        "FROM youtube_video "
                        "WHERE {target_field} IS NULL AND {source_field} IS NOT NULL "
                        "LIMIT 1;").format(
        source_field=sql.Identifier(source_field),
        target_field=sql.Identifier(target_field)
    )
    write_query = sql.SQL("UPDATE youtube_video "
                          "SET {target_field} = %(text)s "
                          "WHERE youtube_video_id = %(id)s;").format(
        target_field=sql.Identifier(target_field)
    )

    with conn.cursor() as cur:
        for _ in range(loops):
            cur.execute(read_query)

            row = cur.fetchone()
            if row is None:
                print("No more descriptions to normalize")
                break

            video_id, text = row
            text = unicodedata.normalize('NFKC', text)
            cur.execute(write_query, {'id': video_id, 'text': text})
            qty += 1
        conn.commit()
    if qty == loops:
        return True, qty
    else:
        return False, qty


if __name__ == '__main__':
    with connect_to_staging_test_db() as conn:
        field_pairs = [['title', 'title_normalized'], ['description', 'description_normalized']]
        for fields in field_pairs:

            total_qty: int = 0
            while True:
                is_success, qty_updated = normalize_fields(conn, fields[0], fields[1])
                total_qty += qty_updated
                print(f"Total {fields[1]} fields updated: {total_qty}")
                if not is_success:
                    break

