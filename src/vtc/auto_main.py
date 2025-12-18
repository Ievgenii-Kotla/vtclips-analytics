from __future__ import annotations
from collections.abc import Callable
import datetime
import logging
import os
import time

from psycopg2 import pool

import db_yt_interface, vtc_logging, data_prep
from vtc_exceptions import NoQuotaError

logger = logging.getLogger(__name__)

def search(connection,
           priority: tuple[int, ...],
           cooldown_factory: Callable[[], datetime.timedelta] = lambda: datetime.timedelta(days=2)):
    """Continuously fetch and save data available through the 'search' endpoint of YT API"""

    search_instance = db_yt_interface.SearchYTByKeyword(connection,
                                                        priority=priority,
                                                        cooldown_period=cooldown_factory())
    while True:
        search_instance.cooldown_period = cooldown_factory()
        # do subsearch if possible
        if search_instance.set_subsearch_map():
            search_instance.subsearch_next_and_save()
        # do normal search
        elif search_instance.set_search_map():
            search_instance.search_next_and_save()
        else:
            logger.info("No search map and no subsearch map.")
            break

    search_instance.session_stats()

def request_playlist_items(connection,
                           only_talents: bool,
                           cooldown_factory: Callable[[], datetime.timedelta] = lambda: datetime.timedelta(days=1)):
    """Continuously fetch and save data available through the 'playlist_items' endpoint of YT API"""

    playlist_items = db_yt_interface.PlaylistItems(connection,
                                                   only_talents=only_talents,
                                                   cooldown_period=cooldown_factory())
    while True:
        playlist_items.cooldown_period = cooldown_factory()
        if not playlist_items.get_new_playlist_items(delay_sec=0.5):
            break

def map_talents_videos(connection):
    """Continuously fetch and save data available through the 'playlist_items' endpoint of YT API"""

    instance = data_prep.MapTV(connection)
    instance.map_talents_to_video_all()


def period_since_quarter_start() -> datetime.timedelta:
    now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)
    quarter_start_month = (now.month - 1) // 3 * 3 + 1
    quarter_start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0)
    since_quarter_start = now - quarter_start
    return since_quarter_start

def period_since_month_start() -> datetime.timedelta:
    now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)
    since_month_start = now - now.replace(day=1, hour=0, minute=0, second=0)
    return since_month_start

def main():
    connection_pool = pool.SimpleConnectionPool(minconn=1, maxconn=1, dsn=os.environ['DATABASE_URL'])
    last_run_day = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).day - 1

    while True:
        current_day = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).day
        # up-to-date requests are guaranteed to have all data up to the start of the cooldown period
        tasks = [
            (search, {'priority': (0, 1), 'cooldown_factory': lambda: datetime.timedelta(days=2)}),
            (search, {'priority': (99,), 'cooldown_factory': period_since_quarter_start}),
            (request_playlist_items, {'only_talents': True, 'cooldown_factory': lambda: datetime.timedelta(days=1)}),
            (request_playlist_items, {'only_talents': False, 'cooldown_factory': period_since_month_start}),
        ]
        tasks_daily = [
            (data_prep.DBCalculations.map_keywords_all, {}),
            (map_talents_videos, {}),
            (data_prep.DBCharts.refresh_all_charts, {}),
        ]

        no_more_quotas = 0
        errors = 0
        task_complete = 0
        connection = None
        try:
            connection = connection_pool.getconn()
            for task in tasks:
                logger.info(f"Running task '{task[0].__name__}' with args: \n{task[1]}")
                try:
                    task[0](connection, **task[1])
                except NoQuotaError:
                    connection.rollback()
                    no_more_quotas += 1
                except Exception as e:
                    connection.rollback()
                    logger.exception(f"Unexpected error occurred while running task {task}: {e} ")
                    errors += 1
                else:
                    connection.commit()
                    task_complete += 1
            if current_day != last_run_day:
                for task in tasks_daily:
                    logger.info(f"Running daily task '{task[0].__name__}' with args: \n{task[1]}")
                    try:
                        task[0](connection, **task[1])
                    except Exception as e:
                        connection.rollback()
                        logger.exception(f"Unexpected error occurred while running daily task {task}: {e} ")
                    else:
                        connection.commit()
                        task_complete += 1
            last_run_day = current_day
        finally:
            if connection:
                connection_pool.putconn(connection)

        if errors:
            seconds = 900
            logger.error(f"Sleeping for {seconds} seconds before starting the next cycle due to error(s).")
            time.sleep(seconds)

        seconds = 3600
        logger.info(f"Finished tasks cycle. Out of {len(tasks)} tasks: "
                    f"No more quotas: {no_more_quotas}. Task complete: {task_complete}. Errors: {errors}.")
        logger.info(f"Sleeping for {seconds} seconds before starting the next cycle.\n")
        time.sleep(seconds)


if __name__ == '__main__':
    vtc_logging.setup_logger()
    main()

