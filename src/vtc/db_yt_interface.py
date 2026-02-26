from __future__ import annotations
from typing import Tuple, List
import datetime
import os
import traceback
import json
import logging
from random import randint, choices
import time
from zoneinfo import ZoneInfo
import unicodedata
import html
from pathlib import Path
import pandas as pd

from googleapiclient.discovery import build, HttpError
from psycopg2 import errors, DatabaseError
from psycopg2.extras import execute_values

from vtc_exceptions import NoQuotaError, VerificationError

# create the logger
logger = logging.getLogger(__name__)

class Helper:
    @staticmethod
    def normalize(text):
        text = unicodedata.normalize('NFKC', text)
        text = html.unescape(text)
        return text

class PrepareAPI:
    QUOTA_FILEPATH = Path(__file__).resolve().parents[2] / "state/api_quota_state.json"
    # options for key's purpose
    UNDEFINED = "undefined"
    UNIVERSAL = 'universal'
    SEARCH = 'search'
    PLAYLIST_ITEMS = 'playlist_items'
    VIDEO_LIST = 'video_list'
    CHANNELS = 'channels'

    @staticmethod
    def current_time_utc():
        return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

    def __init__(self, quota_points=10000, filepath=QUOTA_FILEPATH, delay=False):

        self.quota_points_max = quota_points
        self.filepath = filepath
        self.active_key: str = None
        self.api_quotas: dict[str, dict[str, int]] = None
        self.last_reset_at: datetime.datetime = None
        self.last_update_at: datetime.datetime = None
        self.api_keys: dict[str, str] = self.load_api_keys()
        self.load_api_quotas_info()
        self.delay = delay
        if self.needs_reset():
            self.reset_and_reload_quotas()

    def needs_reset(self):
        """Check if it is time to reset."""

        pacific_tz = ZoneInfo("America/Los_Angeles")
        utc_tz = ZoneInfo("UTC")

        now = datetime.datetime.now(pacific_tz)
        midnight = datetime.datetime.combine(now.date(), datetime.time.min, tzinfo=pacific_tz)
        target_reset_time = midnight.astimezone(utc_tz)

        if self.last_reset_at < target_reset_time or len(self.api_keys) != len(self.api_quotas):
            return True
        else:
            return False

    def seconds_until_reset(self):
        """Return number of seconds left until reset."""

        pacific_tz = ZoneInfo("America/Los_Angeles")
        now = datetime.datetime.now(pacific_tz)
        midnight = datetime.datetime.combine(now.date(), datetime.time.min, tzinfo=pacific_tz)
        next_midnight = midnight + datetime.timedelta(days=1)
        seconds_until_midnight = int((next_midnight - now).total_seconds())
        return seconds_until_midnight


    @staticmethod
    def load_api_keys() -> dict[str, str]:
        """ Load API keys from environmental variables. """
        api_keys = os.getenv('API_KEYS').split(",")
        api_keys_dict = {f"API_key{i}": value for i, value in enumerate(api_keys)}
        return api_keys_dict

    def load_api_quotas_info(self) -> None:
        """
        Load information about API keys from a file.

        Per API key:
        - max quota points
        - available quota points
        - quota points that are reserved
        - purpose of the key
        - coefficient (limits percentage wise the quantity of quota points that can be used)
        General:
        - last reset time
        - last update time
         """

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as err:
            logger.error("File with info about quotas is not found. ", err)
            self.last_update_at = self.current_time_utc()
            # Using self._reset_quotas and inline loading instead of self.reset_and_reload_quotas
            #   to avoid infinite loop if the file couldn't be created for some reason
            self._reset_quotas()
            logger.error(f"New file created. {self.filepath}")
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        self.api_quotas = data["API_quotas"]
        self.last_reset_at = datetime.datetime.fromisoformat(data["last_reset_at"])
        self.last_update_at = datetime.datetime.fromisoformat(data["last_update_at"])

    def save_api_quotas_info(
            self,
            quotas: dict,
            last_reset_at: datetime.datetime,
            last_update_at: datetime.datetime
    ) -> None:
        """ Save new quota values for all API keys, last reset and last update(other than reset) times to a file. """
        data = {
            "API_quotas": quotas,
            "last_reset_at": last_reset_at.isoformat(),
            "last_update_at": last_update_at.isoformat()
        }
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_api_key(self, threshold=100, delay=None, random_key=True, purpose=None) -> str:
        """
        Get working API key to access YT.

        Parameters:
            threshold (int): quota price of the action (cuts off keys with not enough quota)
            delay (bool): delay on/off
            random_key (bool): give random key on/off. Off - give key with the least quota points
            purpose (str): selects keys that are dedicated for this purpose
        """

        while True:
            if self.needs_reset():
                self.reset_and_reload_quotas()

            # Using '// threshold' to ignore small quota leftovers that can't be used
            valid_quotas = {
                key_id: stats['available'] // threshold
                for key_id, stats in self.api_quotas.items()
                if stats['available'] >= threshold and stats.get('purpose', None) in [purpose, PrepareAPI.UNIVERSAL]
            }
            total_actions_available = sum(valid_quotas.values())
            if total_actions_available > 0:
                break
            else:
                message = f"No available quota for {purpose} key.\n"
                logger.info(message)
                raise NoQuotaError(message)

        if random_key:
            key_id = choices(list(valid_quotas.keys()),
                             weights=[value / total_actions_available for value in valid_quotas.values()],
                             k=1)[0]
        else:
            key_id = min(valid_quotas, key=valid_quotas.get)

        if delay is not None:
            self.delay = delay

        if self.delay:
            # make minimal delay directly proportional to the price of an action
            # (lower price - more possible actions - lower delay)
            base_time = threshold
            min_delay = 0
            max_delay = max((self.seconds_until_reset() * 2) // total_actions_available, base_time * 2)
            delay_sec = randint(min_delay, max_delay)
            logger.info(f'Delay: {delay_sec} seconds.')
            while delay_sec > 0:
                print(f'Time left: {delay_sec} seconds.')
                sleep_time = min(100, delay_sec)
                time.sleep(sleep_time)
                delay_sec -= sleep_time

        return self.api_keys[key_id]

    def get_api_key_id(self, api_key):
        """Return corresponding dictionary key (id) associated with the given API key."""
        return next(key for key, value in self.api_keys.items() if value == api_key)

    def change_quota(self, api_key: str, change: int):
        """ Change quota by the 'change' value for a specified API key in the file and for the current instance. """

        key = self.get_api_key_id(api_key)
        # Update
        self.api_quotas[key]['available'] = self.api_quotas[key]['available'] + change
        self.save_api_quotas_info(
            self.api_quotas,
            self.last_reset_at,
            self.current_time_utc()
        )
        self.load_api_quotas_info()

    def get_quota_left(self, api_key):
        key = next(key for key, value in self.api_keys.items() if value == api_key)
        quota_left = self.api_quotas[key]['available']
        return quota_left

    def _reset_quotas(self, lower_boundary=98, upper_boundary=98):
        """ Reset the file that stores quota counters, and times of last reset and last update. """
        self.api_keys = self.load_api_keys()
        quotas = {
            f"API_key{i}": {
                'max': self.quota_points_max,
                'available': int(available_points := randint(lower_boundary, upper_boundary) * 100
                                 * self.api_quotas.get(f'API_key{i}', {}).get('coefficient', 1)),
                'reserve': int(self.quota_points_max - available_points),
                'purpose': self.api_quotas.get(f'API_key{i}', {}).get('purpose', PrepareAPI.UNDEFINED),
                'coefficient': self.api_quotas.get(f'API_key{i}', {}).get('coefficient', 1),
            } for i, _ in enumerate(self.api_keys)}
        self.save_api_quotas_info(
            quotas,
            self.current_time_utc(),
            self.current_time_utc()
        )

    def reset_and_reload_quotas(self):
        """ Reset the file that stores info about quotas.
        Update instance attributes with the new content of the file. """
        self._reset_quotas()
        self.load_api_quotas_info()
        logger.info('Quotas updated and reloaded.')

    def temporary_disable_key(self, api_key_id):
        """ Disable key until the next reset. """

        if api_key_id in self.api_quotas:
            self.api_quotas[api_key_id]['available'] = 0
            logger.error(f'API key {api_key_id} disabled until the next reset. Check if the key is still valid.')
        else:
            logger.error(f"Couldn't disable API key {api_key_id}. API key not found.")

        self.save_api_quotas_info(
            self.api_quotas,
            self.last_reset_at,
            self.current_time_utc()
        )


class SearchYTByKeyword:
    def __init__(self,
                 connection,
                 talents_names: tuple[str] | None = None,
                 start_search_datetime: str = '1970-01-01 00:00:00+00:00',
                 end_search_datetime: str = '9000-01-01 00:00:00+00:00',
                 priority: tuple[int, ...] = (0, 1),
                 usage_enabled: bool = True,
                 purity: tuple[str] = ('pure', 'mixed', 'dirty'),
                 api_service: PrepareAPI = None,
                 search_layer: int = None,
                 cooldown_period: datetime.timedelta = datetime.timedelta(days=1),
                 newer_first: bool = False,
                 ):
        # Command line arguments that where provided
        self.connection = connection
        self.talents_names = talents_names
        self.start_search_datetime = start_search_datetime
        self.end_search_datetime = end_search_datetime
        self.priority = priority
        self.usage_enabled = usage_enabled
        self.purity = purity
        self.api_service = api_service or PrepareAPI()  # Use the first one that evaluates to True
        self.search_layer = search_layer
        if search_layer is None:
            self.set_max_search_layer()

        # Variables that are necessary to prepare and make a YT search request
        self.cursor = self.connection.cursor()
        self.quota_points = 10000  # set by YT
        self.quota_left = self.quota_points
        self.api_key = None

        self.talents_ids = (None,)
        self.all_talents = True
        if self.talents_names:
            self.set_talents_ids()
            self.all_talents = False

        self.search_map: List[Tuple[int, str, datetime.datetime, datetime.datetime], ] | None = None
        self.response = None
        self.subsearch_map: List[Tuple[int, datetime.datetime, datetime.datetime, str, str,
        int, int, datetime.datetime | None, datetime.datetime | None, int, bool]] | None = None
        self.cooldown_period = cooldown_period
        self.newer_first = newer_first

        # Default values for constant YT search parameters
        self.part = "snippet"
        self.max_results = 50
        self.order = None
        self.published_after = datetime.datetime.fromisoformat(start_search_datetime)
        self.published_before = datetime.datetime.fromisoformat(end_search_datetime)
        self.search_query = None
        self.region_code = "US"
        self.safe_Search = "none"
        self.type = "video"

        # Variables used to save to DB
        self.keyword_id: tuple[int] = (None,)
        self.new_yt_video_ids = None
        self.new_yt_channel_ids = None
        self.search_yt_id = None
        self.youtube_video_values = None
        self.youtube_channel_values = None
        self.datetime_now = None
        self.parent_search_id: int | None = None
        self.update_datetime_now()

        # Other
        self.session_videos_total: int = 0
        self.session_videos_new: int = 0
        self.session_channels_total: int = 0
        self.session_channels_new: int = 0
        self.session_searches: int = 0

    def set_max_search_layer(self):
        query = """
SELECT MAX(search_layer)
FROM search_yt
"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        max_search_layer = cursor.fetchone()[0]
        if max_search_layer is None:
            max_search_layer = 1
        self.search_layer = max_search_layer
        cursor.close()

    def update_datetime_now(self):
        self.datetime_now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)

    def set_search_map(self):
        """
        Create a map indicating when each relevant keyword has not yet been searched.

        Variables used:
        - self.usage_enabled
        - self.priority
        - self.purity
        - self.talents_ids
        - self.all_talents
        - self.start_search_datetime
        - self.end_search_datetime
        - self.connection

        Variables changed:
        self.search_map: Tuple[Tuple[keyword, start, end], ...]
        """

        # example with default values:
        # usage_enabled = TRUE,
        # priority IN (0, 1),
        # purity IN ('pure'),
        # talent_id in () OR  all_talents = TRUE

        # This particular query uses start and end that are specified in youtube search request
        # Instead of using the publishing time of the newest video in a search as end.
        query = """
-- line for query highlighting in IDE
SELECT 1;
SET TIME ZONE 'UTC';
-- Filter out unnecessary rows from "keyword" table (like rows with talents that would not be used for the search etc.)
WITH RECURSIVE keyword_processed AS (
    SELECT 
        k.keyword_word, 
        k.keyword_id, 
        k.date_since_relevant 
    FROM 
        keyword AS k
    INNER JOIN 
        keyword_talent AS kt 
    ON 
        k.keyword_id = kt.keyword_id
    WHERE 
        k.usage_enabled = %(usage_enabled)s
        AND k.priority IN %(priority)s
        AND k.purity IN %(purity)s
        AND (kt.talent_id IN %(talents_ids)s OR %(all_talents)s IS TRUE)
    GROUP BY k.keyword_word, k.keyword_id, k.date_since_relevant
),
-- Select search instances that lie within the time scope. 
search_processed AS (
    SELECT
        ks.keyword_id, 
        s.search_yt_id, 
        s.published_before, 
        s.published_after
    FROM
        keyword_search_yt AS ks 
    JOIN
        search_yt AS s 
    ON 
        s.search_yt_id = ks.search_yt_id
        AND s.published_before > %(start_dt)s
        AND s.published_after < %(end_dt)s
    WHERE s.search_layer = %(search_layer)s
),
-- Combine data and cast search periods into tstzrange for further computations
keyword_search AS (
    SELECT 
        kp.keyword_id, 
        kp.keyword_word, 
        kp.date_since_relevant,
        sp.search_yt_id,
        CASE
            WHEN sp.published_after IS NULL OR sp.published_before IS NULL
            THEN 'empty'::tstzrange
            ELSE tstzrange(sp.published_after, sp.published_before, '[]')
        END AS search_period
    FROM 
        keyword_processed AS kp
    LEFT JOIN
        search_processed AS sp
    ON 
        kp.keyword_id = sp.keyword_id
    GROUP BY 
        kp.keyword_id, 
        kp.keyword_word, 
        kp.date_since_relevant,
        sp.search_yt_id,
        search_period
),
-- Put 'search_period''s into multiranges
-- This automatically combines overlapping and adjacent searches
-- But does not combine periods, where the first one ends at (n) time and the next one starts at (n + 1 second) time
keyword_combined_search_raw AS (
    SELECT 
        ks.keyword_id,
        ks.keyword_word,
        ks.date_since_relevant,
        range_agg(ks.search_period) AS search_periods
    FROM 
        keyword_search AS ks 
    GROUP BY
        ks.keyword_id,
        ks.keyword_word,
        ks.date_since_relevant
),
-- Calculate periods that where not searched
non_searched_periods AS (
    SELECT
        kcsr.keyword_id,
        kcsr.keyword_word,
        tstzmultirange(
            tstzrange('-infinity', LEAST(%(datetimenow)s, %(end_dt)s), '[]') 
            - tstzrange('-infinity', GREATEST(kcsr.date_since_relevant, %(start_dt)s), '[]')
        ) - kcsr.search_periods AS non_searched
    FROM
        keyword_combined_search_raw AS kcsr
),
-- Unnest periods from tstzmultirange
non_searched_periods_unnested AS (
    SELECT
        nsp.keyword_id,
        nsp.keyword_word,
        unnest(nsp.non_searched) AS non_searched
    FROM 
        non_searched_periods AS nsp
)
-- Unpack start and end datetimes from tstzrange, 
-- Prepare data by cutting off non-inclusive borders
-- Exclude 1 second periods
SELECT 
    nspu.keyword_id,
    nspu.keyword_word,
    lower(nspu.non_searched) + interval '1 second' AS "start",
    CASE
        WHEN upper_inc(nspu.non_searched) IS TRUE
        THEN upper(nspu.non_searched)
        ELSE upper(nspu.non_searched) - interval '1 second'
    END AS "end"
FROM
    non_searched_periods_unnested AS nspu
WHERE lower(nspu.non_searched) + interval '1 second' <> upper(nspu.non_searched)
    AND lower(nspu.non_searched) < %(datetimenow)s - %(cooldown_period)s
;
"""

        values = {
            'usage_enabled': self.usage_enabled,
            'priority': self.priority,
            'purity': self.purity,
            'talents_ids': self.talents_ids,
            'all_talents': self.all_talents,
            'start_dt': self.start_search_datetime,
            'end_dt': self.end_search_datetime,
            'datetimenow': self.datetime_now,
            'search_layer': self.search_layer,
            'cooldown_period': self.cooldown_period
        }
        cursor = self.connection.cursor()
        logger.info("Creating the search map...")
        cursor.execute(query, values)
        logger.info("Search map created.")
        self.search_map = cursor.fetchall()
        cursor.close()

        if self.search_map:
            return True
        else:
            return False

    def prepare_query_and_period_alg1(self):
        """
        Set the query text and the period that'll be used in YT search request

        This algorithm provides:
        - the oldest period
        - a time span for the period is set to 1 day.
        - a query text that is a single keyword
        """

        #  Requires self.search_map to be updated before each new use
        pick = max if self.newer_first else min
        keyword_id, keyword_word, start, end = pick(self.search_map, key=lambda x: x[2])

        end = min(
            start + self.calculate_search_interval(keyword_word=keyword_word, published_after=start),
            self.datetime_now,
            end
        )
        self.keyword_id = (keyword_id,)
        self.search_query = f'"{keyword_word}"'
        self.published_after = start
        self.published_before = end

        if end - start < datetime.timedelta(hours=23, minutes=59, seconds=59):
            logger.info(f"Current search's length is {end - start} hh:mm:ss")

    def calculate_search_interval(self, keyword_word=None, published_after=None):
        """
        Calculate search interval.

        Parameters:
            keyword_word (str): Keyword itself, e.g. '@irys'
            published_after (datetime.datetime): Start of the current search
        return:
            datetime.timedelta: length of the new search interval
        """

        def days(total_days: int):
            return datetime.timedelta(days=total_days-1, hours=23, minutes=59, seconds=59)

        if keyword_word is None:
            # todo: fix: self. search_query is None on the fisrt run.
            #  Meaning it stores value of the previous run on non-first runs
            keyword_word = self.search_query.strip('"')
        if published_after is None:
            published_after = self.published_before
        default_search_interval = days(2)
        # collect information about the previous search with the keyword
        query = """
SELECT s.published_after, s.published_before, s.results_per_page, k.priority
FROM search_yt AS s
JOIN keyword_search_yt AS ks
    ON s.search_yt_id = ks.search_yt_id
JOIN keyword AS k
    ON ks.keyword_id = k.keyword_id
JOIN keyword_talent AS kt
    ON k.keyword_id = kt.keyword_id
WHERE q = %(keyword_word)s
    AND published_after < %(published_after)s
ORDER BY published_before DESC
LIMIT 1;
"""
        values = {
            'keyword_word': keyword_word,
            'published_after': published_after
        }
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        data = cursor.fetchone()
        cursor.close()

        if data:
            # Unpack information about the previous search
            start, end, matches, priority = data
            prev_search_period: datetime.timedelta = end - start
        else:
            # get priority value for the current keyword
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT priority FROM keyword WHERE keyword_word = %s;", (keyword_word,))
                priority = cursor.fetchone()[0]

        # special case for when the keyword is a video id (priority 99)
        if priority == 99:
            return self.datetime_now - published_after

        # No previous search
        if data is None:
            return default_search_interval

        # Previous search is not recent
        if published_after - end < datetime.timedelta(seconds=1):
            return default_search_interval

        if matches == 0:
            return days(7)

        if 1 <= matches <= 10:
            return max(days(4), prev_search_period)

        if 11 <= matches <= 40:
            return prev_search_period

        if 41 <= matches <= 50:
            return min(prev_search_period, default_search_interval)

        # Behavior for other situations
        logger.error('Unexpected calculation of the search interval')
        return default_search_interval

    # TBI
    def updated_quota(self):
        pass

    # TBI
    def set_group_names(self):
        pass

    def set_talents_ids(self):
        """ Convert a tuple of names into a tuple of IDs by matching names and IDs in the DB. """
        query = """
SELECT t.talent_id
FROM talent AS t 
WHERE LOWER(t.first_name_eng) = LOWER(%(name)s);
"""
        ids = []
        cursor = self.connection.cursor()
        for name in self.talents_names:
            cursor.execute(query, {'name': name})
            talent_id = cursor.fetchone()[0]
            if talent_id is not None:
                ids.append(int(talent_id))
            elif talent_id is None:
                logger.error(f"Warning: Talent's name '{name}' did not match any talents.")
            if cursor.fetchall():
                logger.error(f"Warning: Talent's name '{name}' matched more than one talent. Selected the first talent")
        cursor.close()
        self.talents_ids = tuple(ids)

    def filter_response(self):
        """ Filter out planned and active livestreams. """

        # Filter out planned and active livestreams
        original_qty = len(self.response["items"])
        self.response["items"] = [d for d in self.response["items"] if "videoId" in d["id"]]
        filter1_qty = len(self.response["items"])
        removed_non_video_qty = original_qty - filter1_qty
        if removed_non_video_qty:
            logger.warning(f"Discarded {removed_non_video_qty} non-video items from dataset (search)")

        # Validate videos relatability
        video_ids = ','.join(item["id"]["videoId"] for item in self.response["items"])
        api_key = self.api_service.get_api_key(threshold=1, delay=False, purpose=PrepareAPI.VIDEO_LIST)
        youtube = build('youtube', 'v3', developerKey=api_key)
        new_response_data = youtube.videos().list(
            part='snippet',
            id=video_ids
        ).execute()
        unrelated_videos_ids = []
        for video in new_response_data["items"]:
            all_text = (Helper.normalize(video["snippet"]["title"]) + '\n' +
                        Helper.normalize(video["snippet"]["description"]) + '\n' +
                        ' '.join(video["snippet"].get("tags", '')))
            if self.search_query.strip('"').lower() not in all_text.lower():
                unrelated_videos_ids.append(video["id"])
        self.response["items"] = [d for d in self.response["items"] if d["id"]["videoId"] not in unrelated_videos_ids]
        filter2_qty = len(self.response["items"])
        removed_unrelated_qty =  filter1_qty - filter2_qty
        if removed_unrelated_qty:
            logger.warning(f"Discarded {removed_unrelated_qty} unrelated videos from dataset (search)")
            logger.warning(f"Unrelated videos: {unrelated_videos_ids}")

        self.api_service.change_quota(api_key, -1)
        quota_left = self.api_service.get_quota_left(api_key)
        logger.info(f"Quota left for filtering: {quota_left}")

        # Check if there are 50 videos and if they all are published at the same time.
        #  (to avoid infinite sub-searches bug)
        if (len(self.response["items"]) == 50
            and len({item["snippet"]["publishedAt"] for item in self.response["items"]}) == 1):
            self.response["items"].pop()

    def search(self):
        """ Conduct prepared search. """

        if self.api_key is None:
            logger.error("API key not found.")
        youtube = build('youtube', 'v3', developerKey=self.api_key)

        # Search for videos related to a specific query
        self.response = youtube.search().list(
            part="snippet",
            maxResults=self.max_results,
            publishedAfter=self.published_after.isoformat(),
            publishedBefore=self.published_before.isoformat(),
            q=self.search_query,
            regionCode="US",
            safeSearch="none",
            type="video",
        ).execute()

        logger.info(f"max results: {self.max_results}\n"
                    f"publishedAfter: {self.published_after}\n"
                    f"publishedBefore: {self.published_before}\n"
                    f"q: {self.search_query}")
        self.api_service.change_quota(self.api_key, -100)
        self.quota_left = self.api_service.get_quota_left(self.api_key)

    def prepare_search(self):
        """ Prepare all the necessary data and variables for the search. """

        self.update_datetime_now()
        self.parent_search_id = None
        # Create the map of what keywords where searched already and at what time periods.
        self.set_search_map()
        # 'priority' *99 values are reserved for potentially _one big single search per keyword_ type of keywords
        priority_99 = {(x + 1) % 100 == 0 for x in self.priority}
        if priority_99 == {True}:
            searches_needed = len(self.search_map)
        elif priority_99 == {False}:
            searches_needed = sum(((dt[3] - dt[2]) // datetime.timedelta(days=2)) + 1 for dt in self.search_map)
        else:
            searches_needed = "UNKNOWN"
        logger.info(f"About {searches_needed} searches needed")
        # Current algorithm for providing the search details
        self.prepare_query_and_period_alg1()

    def subsearch_next_and_save(self):
        self.api_key = self.api_service.get_api_key(purpose=PrepareAPI.SEARCH)
        try:
            self.set_subsearch_map()
            if not self.subsearch_map:
                return False
            if not self.prepare_subsearch_query():
                return False
            self.search()
            self.filter_response()
            self.save()
        except HttpError as err:
            if err.resp.status == 403:
                api_key_id = self.api_service.get_api_key_id(api_key=self.api_key)
                quota_left = self.api_service.get_quota_left(api_key=self.api_key)
                logger.error(f'Quota exceeded (prematurely). '
                            f'API key: {api_key_id}. '
                            f'Quota left: {quota_left}'
                            f'Error 403 : {err}')
                self.api_service.temporary_disable_key(api_key_id)
            else:
                logger.error(err)
                time.sleep(60)
        return True

    def set_subsearch_map(self):
        """Create a map with all searches that need to be subsearched.
        (ones that have 50 videos per search and have not been sub-searched) """

        query = """
SELECT 1;
SET TIME ZONE UTC;
WITH subsearch AS (
    SELECT parent_id, COUNT(*) AS quantity
    FROM search_yt
    GROUP BY parent_id
)
SELECT
    s1.search_yt_id,
    s1.published_after,
    s1.published_before,
    s1.q,
    s1.region_code,
    s1.search_layer,
    COALESCE(sb.quantity, 0) AS subsearch_qty,
    s2.published_after,
    s2.published_before,
    (
        SELECT array_agg(ks.keyword_id)
        FROM keyword_search_yt as ks
        WHERE ks.search_yt_id = s1.search_yt_id
    ),
    s1.is_q_quoted
FROM search_yt AS s1 
LEFT JOIN subsearch AS sb
    ON s1.search_yt_id = sb.parent_id
LEFT JOIN search_yt AS s2
    ON s1.search_yt_id = s2.parent_id
WHERE s1.results_per_page = 50
    AND (sb.quantity = 1 OR sb.quantity is NULL)
    AND s1.subsearch_enabled IS TRUE
ORDER BY s1.searched_at;
"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.subsearch_map = cursor.fetchall()
        cursor.close()

        if self.subsearch_map:
            return True
        else:
            return False

    def prepare_subsearch_query(self):
        def get_default_middle_point():
            middle_point = parent_published_after + ((parent_published_before - parent_published_after) // 2)
            middle_point = middle_point.replace(microsecond=0) + datetime.timedelta(seconds=1)
            return middle_point

        self.update_datetime_now()
        logger.info(f'Searches in need for subsearching: {len(self.subsearch_map)}\n'
                    f'Total subsearches needed: {sum([2 - num[6] for num in self.subsearch_map])}')

        data = self.subsearch_map.pop(0)
        (
            parent_id,  # parent search id
            parent_published_after,
            parent_published_before,
            q,
            region_code,
            search_layer,
            subsearch_qty,
            child_published_after,
            child_published_before,
            keyword_ids,
            is_q_quoted
        ) = data
        
        query = """
        SELECT yv.published_at
        FROM search_yt_youtube_video syyv 
        JOIN youtube_video yv ON syyv.youtube_video_id = yv.youtube_video_id 
        WHERE syyv.search_yt_id = %s
        ORDER BY yv.published_at;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (parent_id,))
            rows = cursor.fetchall()
        if rows:
            middle_point = rows[(len(rows)//2)][0]
            if len(rows) == 1:
                middle_point = get_default_middle_point()
                logger.warning(f'A single video for search {parent_id} '
                               f'is not enough to determine optimized middle point')
                logger.warning(f'Default middle point for sub-search boundaries selected')
        else:
            middle_point = get_default_middle_point()
            logger.warning(f'No valid videos for search {parent_id} to determine optimized middle point')
            logger.warning(f'Default middle point for sub-search boundaries selected')

        if subsearch_qty == 0:
            self.published_after = parent_published_after
            self.published_before = middle_point - datetime.timedelta(seconds=1)
        elif subsearch_qty == 1:
            self.published_after = middle_point
            self.published_before = parent_published_before
        else:
            raise ValueError(f'subsearch_qty value {subsearch_qty} is unsupported')
        self.search_layer = search_layer
        self.search_query = q if (q.startswith('"') and q.endswith('"')) else f'"{q}"'
        self.parent_search_id = parent_id
        self.keyword_id = keyword_ids
        if (
                self.published_after >= self.published_before
                or middle_point <= parent_published_after
                or middle_point >= parent_published_before
        ):
            logger.error("Invalid time boundaries for a sub-search")
            time.sleep(60)
            return False
        return True

    def search_next_and_save(self):
        """ Coordinate the process of searching YT. """

        self.api_key = self.api_service.get_api_key(purpose=PrepareAPI.SEARCH)
        try:
            self.prepare_search()
            if not self.search_map:
                return False
            self.search()
            self.filter_response()
            self.validate_results_per_page_qty()
            self.save()
        except HttpError as err:
            if err.resp.status == 403:
                api_key_id = self.api_service.get_api_key_id(api_key=self.api_key)
                quota_left = self.api_service.get_quota_left(api_key=self.api_key)
                logger.error(f'Quota exceeded (prematurely). '
                            f'API key: {api_key_id}. '
                            f'Quota left: {quota_left}')
                self.api_service.temporary_disable_key(api_key_id)
            else:
                logger.error(err)
                time.sleep(60)
        return True

    def save_youtube_channel(self):
        """ Save new information to the 'youtube_channel' table. """

        youtube_channel_query = """
        INSERT INTO youtube_channel (
            youtube_channel_id,
            channel_info_last_updated,
            title,
            added_at,
            playlist_id
        )
        VALUES %s
        ON CONFLICT (youtube_channel_id) DO NOTHING
        RETURNING youtube_channel_id;
        """

        self.youtube_channel_values = [
            [
                item["snippet"]["channelId"],
                self.datetime_now,
                item["snippet"]["channelTitle"],
                self.datetime_now,
                "UU" + item["snippet"]["channelId"][2:] if item["snippet"]["channelId"][:2] == "UC" else None
            ]
            for item in self.response["items"]
        ]
        self.new_yt_channel_ids = execute_values(
            self.cursor,
            youtube_channel_query,
            self.youtube_channel_values,
            template="(%s, %s, %s, %s, %s)",
            fetch=True
        )

    def save_youtube_video(self):
        """ Save new information to the 'youtube_video' table. """
        youtube_video_query = """
    INSERT INTO youtube_video (
        youtube_video_id,
        youtube_channel_id,
        published_at,
        description_trimmed,
        live_broadcast_content,
        updated_at,
        added_at,
        title_normalized
    )
    VALUES %s
    ON CONFLICT (youtube_video_id) DO NOTHING
    RETURNING youtube_video_id;
    """
        self.youtube_video_values = [
            [
                item["id"]["videoId"],
                item["snippet"]["channelId"],
                datetime.datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
                item["snippet"]["description"],
                item["snippet"]["liveBroadcastContent"],
                self.datetime_now,
                self.datetime_now,
                Helper.normalize(item['snippet']['title'])
            ]
            for item in self.response["items"]
        ]
        self.new_yt_video_ids = execute_values(
            self.cursor,
            youtube_video_query,
            self.youtube_video_values,
            template=(
                "(%s, %s, %s, %s, %s, %s, %s, %s)"
            ),
            fetch=True
        )

    def save_search_yt(self):
        """ Save new information to the 'search_yt' table. """
        search_yt_query = """
    INSERT INTO search_yt (
        kind,
        searched_at,
        published_after,
        published_before,
        results_per_page_max,
        results_per_page,
        prev_page_token,
        next_page_token,
        total_results,
        region_code,
        q,
        search_layer,
        parent_id,
        is_q_quoted,
        subsearch_enabled
    )
    VALUES %s
    RETURNING search_yt_id;
    """
        subsearch_enabled = (False
                             if self.response["pageInfo"]["resultsPerPage"] == 50
                                and len(self.response["items"]) == 0
                             else True)
        if not subsearch_enabled:
            logger.warning("subsearch_enable flag set to False for this search")
        search_yt_values = [
            [
                self.response["kind"],
                self.datetime_now,
                self.published_after,
                self.published_before,
                self.max_results,
                self.response["pageInfo"]["resultsPerPage"],
                self.response.get("prevPageToken"),
                self.response.get("nextPageToken"),
                self.response["pageInfo"]["totalResults"],
                self.response["regionCode"],
                self.search_query.strip('"'),
                self.search_layer,
                self.parent_search_id,
                self.search_query.startswith('"') and self.search_query.endswith('"'),
                subsearch_enabled,
            ]
        ]
        search_yt_ids = execute_values(
            self.cursor,
            search_yt_query,
            search_yt_values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            fetch=True
        )
        self.search_yt_id = search_yt_ids[0][0]

    def save_keyword_search_yt(self):
        """ Save new info to the 'keyword_search_yt' junction table. """
        keyword_search_yt_query = """
        INSERT INTO keyword_search_yt (
            search_yt_id,
            keyword_id
        )
        VALUES %s
        RETURNING search_yt_id, keyword_id;
        """
        keyword_search_yt_values = [
            [
                self.search_yt_id,
                keyword_id
            ]
            for keyword_id in self.keyword_id
        ]
        execute_values(
            self.cursor,
            keyword_search_yt_query,
            keyword_search_yt_values,
            template="(%s, %s)",
            fetch=False
        )

    def save_search_yt_youtube_video(self):
        """ Save new info to the 'search_yt_youtube_video' junction table. """
        search_yt_youtube_video_query = """
        INSERT INTO search_yt_youtube_video (
            search_yt_id,
            youtube_video_id
        )
        VALUES %s
        RETURNING *;
        """
        search_yt_youtube_video_values = [
            [
                self.search_yt_id,
                item['id']['videoId']
            ]
            for item in self.response['items']
        ]
        execute_values(
            self.cursor,
            search_yt_youtube_video_query,
            search_yt_youtube_video_values,
            template="(%s, %s)",
            fetch=False
        )

    def save(self):
        """ Save the data that was received from YouTube to the DB. Save the information about the search itself."""
        try:
            self.save_youtube_channel()
            self.save_youtube_video()
            self.save_search_yt()
            self.save_keyword_search_yt()
            self.save_search_yt_youtube_video()
        except Exception as e:
            traceback.print_exc()
            self.connection.rollback()
            logger.error(f"An error occurred while saving: {e} \nTransaction rolled back. ")
            logger.error(self.response)
            raise
        else:
            self.connection.commit()
            logger.info("Changes committed.")

        # 'logging' a few stats
        logger.info(f'Videos in response - '
                    f'Total: {len(self.youtube_video_values)} '
                    f'New: {len(self.new_yt_video_ids)}')
        logger.info(f'Channels in response: - '
                    f'Total: {len(self.youtube_channel_values)} '
                    f'New: {len(self.new_yt_channel_ids)}')
        logger.info(f'Newest search id: {self.search_yt_id}')
        logger.info(f'Quota left for current key: {self.quota_left}\n')

        self.session_videos_total += len(self.youtube_video_values)
        self.session_videos_new += len(self.new_yt_video_ids)
        self.session_channels_total += len(self.youtube_channel_values)
        self.session_searches += 1

    def validate_results_per_page_qty(self):
        """ Check if 'resultsPerPage' returned in the response matches actual number of responses. """
        if self.response['pageInfo']['resultsPerPage'] != len(self.response['items']):
            logger.warning("resultsPerPage value does not match the actual number of results per page")

    def session_stats(self):
        logger.info("Session statistics: ")
        logger.info(f"Searches conducted: {self.session_searches}")
        logger.info(f'Videos found - '
                    f'Total: {self.session_videos_total} '
                    f'New: {self.session_videos_new}')
        logger.info(f'Channels found - '
                    f'Total: {self.session_channels_total} '
                    f'New: {self.session_channels_new}\n')


class PlaylistItems:
    def __init__(self,
                 connection,
                 api_service: PrepareAPI | None = None,
                 only_talents: bool = False,
                 cooldown_period: datetime.timedelta = datetime.timedelta(days=30)):
        # todo: don't forget to close the connection
        # todo: wrap all connections into context managers
        self.connection = connection
        self.api_service= api_service or PrepareAPI()
        self.prev_page_token: str | None = None
        self.next_page_token: str | None = None
        self.api_key: str | None = None
        self.response: dict | None = None
        self.datetime_now: datetime.datetime | None = None
        self.max_results = 50
        self.caught_up: bool | None = None
        # data for choosing a playlist_id
        self.playlist_id: str | None = None
        self.cooldown_period = cooldown_period
        self.only_talents = only_talents
        self.playlist_404_counter: int = 0
        # data for saving
        self.playlist_items_request_id: int | None = None
        self.playlist_qty: int | None = None

    def get_new_playlist_items(self, delay_sec: float = 0):
        """Get all items from the 'upload' playlist and save them to the DB"""
        self.playlist_id = None
        self.caught_up = False
        page = 1
        while True:
            time.sleep(delay_sec)
            if not self._do_request_and_save():
                is_success = False
                break
            self._update_next_page_token()
            if not self.next_page_token:
                is_success = True
                break
            if self.caught_up:
                is_success = True
                break
            logger.info(f'Page (current run): {page}\n')
            page += 1
        logger.info(f"Success: {is_success}\n")
        return is_success

    def _do_request_and_save(self):
        wait_seconds: int = 60
        try:
            if not self.playlist_id:
                if not self._set_playlist_id():
                    return False
            self._prepare_request()
            try:
                self._do_request()
            finally:
                self._update_quota_after_request()
            self._filter_response()
            self._save()
            self._do_stop_check()
        except HttpError as err:
            if err.resp.status == 403:
                api_key_id = self.api_service.get_api_key_id(api_key=self.api_key)
                quota_left = self.api_service.get_quota_left(api_key=self.api_key)
                logger.error(f'Quota exceeded (prematurely). '
                               f'API key: {api_key_id}. '
                               f'Quota left: {quota_left}')
                self.api_service.temporary_disable_key(api_key_id)
                return True
            elif err.resp.status == 500:
                logger.warning(f'YouTube server error (500). Retry in {wait_seconds} seconds.')
                time.sleep(wait_seconds)
                return True
            elif err.resp.status == 404:
                self.playlist_404_counter += 1
                if self.playlist_404_counter < 4:
                    logger.warning(f'Playlist unavailable (404). id: {self.playlist_id}. '
                                   f'Try: {self.playlist_404_counter} '
                                   f'Retry in {wait_seconds} seconds.')
                    time.sleep(wait_seconds)
                else:
                    self._update_playlist_unavailable()
                    logger.warning(f'Playlist unavailable (404). id: {self.playlist_id} '
                                   f'Try: {self.playlist_404_counter}')
                    logger.warning(f'Playlist availability changed to FALSE')
                    self.playlist_404_counter = 0
                return True
            elif err.resp.status == 503:
                logger.warning(f'YouTube server error (503). Retry in {wait_seconds} seconds.')
                time.sleep(wait_seconds)
                return True
            else:
                logger.error(err)
                time.sleep(wait_seconds)
                return True
        except DatabaseError as err:
            logger.error(f'Database error. \n {err}')
            logger.error(traceback.format_exc())
            raise DatabaseError(err)
        else:
            logger.info(f'Newest playlistItems request id: {self.playlist_items_request_id}')
            return True

    def _update_playlist_unavailable(self):
        query = """
        UPDATE youtube_channel
        SET playlist_available = FALSE
        WHERE playlist_id = %s;
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (self.playlist_id,))
        self.connection.commit()

    def _set_playlist_id(self):

        if self.only_talents:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT youtube_channel_id FROM youtube_channel_talent;")
                channels = [row[0] for row in cursor.fetchall()]
        else:
            channels = None

        query = """
        WITH last_requests AS (
            SELECT DISTINCT ON (yc.playlist_id) yc.playlist_id, pir.requested_at, pir.next_page_token, pir.caught_up
            FROM youtube_channel AS yc
            LEFT JOIN playlist_items_request AS pir
                ON yc.playlist_id = pir.playlist_id
            WHERE yc.playlist_available IS TRUE 
                AND yc.playlist_id IS NOT NULL
                AND (yc.is_other IS FALSE OR yc.is_other IS NULL)
                AND (%(channels)s IS NULL OR yc.youtube_channel_id = ANY(%(channels)s))
            ORDER BY yc.playlist_id, pir.requested_at DESC, pir.playlist_items_request_id DESC
         )
         SELECT playlist_id
         FROM last_requests
         WHERE requested_at IS NULL
            OR next_page_token IS NOT NULL AND caught_up IS NOT TRUE
            OR requested_at < CURRENT_TIMESTAMP - %(cooldown)s 
         ORDER BY next_page_token NULLS LAST, -- in the middle of paging through a playlist
            requested_at ASC NULLS FIRST, -- never requested first, then oldest
            playlist_id -- for ordering consistency
        """
        values = {'channels': channels, 'cooldown': self.cooldown_period}
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            self.playlist_qty = cursor.rowcount
            row = cursor.fetchone()
            if row:
                self.playlist_id = row[0]
            else:
                self.playlist_id = None

        if self.playlist_id:
            logger.info(f'Playlist selected. ID: {self.playlist_id} ')
            with self.connection.cursor() as cur:
                cur.execute(
                    "SELECT title FROM youtube_channel WHERE playlist_id = %s;",
                    (self.playlist_id,))
                logger.info(f'Title: {cur.fetchone()[0]}')
            return True
        else:
            logger.info("No valid playlists.")
            return False

    def _prepare_request(self):
        logger.info(f"At least {self.playlist_qty} playlist_items_requests needed")
        self.api_key = self.api_service.get_api_key(threshold=1, delay=False, purpose=PrepareAPI.PLAYLIST_ITEMS)
        self._update_next_page_token()

    def _do_request(self):
        youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.response = youtube.playlistItems().list(
            part='snippet,status,id,contentDetails',
            maxResults=self.max_results,
            playlistId=self.playlist_id,
            pageToken=self.next_page_token
        ).execute()

    def _update_quota_after_request(self):
        self.api_service.change_quota(self.api_key, -1)
        quota_left = self.api_service.get_quota_left(self.api_key)
        logger.info(f"Quota left: {quota_left}")

    def _update_datetime_now(self):
        self.datetime_now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)

    def _filter_response(self):
        def remove_nul_chars_in_nested_dict(dict_: dict) -> None:
            for key, value in dict_.items():
                if isinstance(value, dict):
                    remove_nul_chars_in_nested_dict(value)
                elif isinstance(value, list):
                    for l in value:
                        remove_nul_chars_in_nested_dict(l)
                elif isinstance(value, str):
                    if '\x00' in value:
                        dict_[key] = value.replace("\x00", "")
                        logger.warning('NUL (0x00) character detected in string')
                        logger.info(f"Removed NUL char (0x00) in {key}: {value}")

        all_qty = len(self.response["items"])
        self.response["items"] = [
            item for item in self.response["items"] if item["snippet"]["resourceId"]["kind"] == "youtube#video"
        ]
        only_video_qty = len(self.response["items"])
        removed_qty = all_qty - only_video_qty
        if removed_qty:
            logger.warning(f"Discarded {removed_qty} non-video items from dataset (playlist)")

        remove_nul_chars_in_nested_dict(self.response)

    def _update_next_page_token(self):
        query = """
        SELECT CASE WHEN caught_up THEN NULL ELSE next_page_token END
        FROM playlist_items_request
        WHERE playlist_id = %(playlist_id)s
        ORDER BY requested_at DESC
        LIMIT 1;
        """
        value = {'playlist_id': self.playlist_id}
        with self.connection.cursor() as cur:
            cur.execute(query, value)
            row = cur.fetchone()
        self.next_page_token = row[0] if row else None

    def _save(self):
        self._update_datetime_now()
        try:
            self._save_playlist_items_request()
            self._save_youtube_video()
            self._save_playlist_items_request_youtube_video()
            if self.only_talents:
                self._save_keyword()
                self._save_keyword_talent()
        except errors.ForeignKeyViolation as err:
            self.connection.rollback()
            logger.warning(f"Foreign key violation detected: {err} \nTransaction rolled back. ")
            if (err.diag.constraint_name == 'fk_youtube_video_youtube_channel_id'
                    and err.diag.table_name == 'youtube_video'):
                self._handle_fk_violation(err)
            else:
                logger.error("Unexpected foreign key violation")
                time.sleep(60)
        except DatabaseError as e:
            self.connection.rollback()
            logger.error(f"A DB error occurred while saving playlist items: {e} \nTransaction rolled back. ")
            logger.error(traceback.format_exc())
            time.sleep(60)
        except Exception as e:
            self.connection.rollback()
            logger.error(f"An error occurred while saving playlist items: {e} \nTransaction rolled back. ")
            logger.error(traceback.format_exc())
            raise
        else:
            self.connection.commit()
            logger.info("Changes committed. (PlaylistItems request)")

    def _handle_fk_violation(self, err):
        s = err.diag.message_detail

        pattern_before = "(youtube_channel_id)=("
        pattern_after = ")"

        s = s.partition(pattern_before)[2]
        channel_id = s.partition(pattern_after)[0]

        query = """
        INSERT INTO youtube_channel (
            youtube_channel_id,
            channel_info_last_updated,
            title,
            added_at,
            playlist_id
        )
        VALUES (%s, %s, %s, %s, %s);
        """

        title = [item['snippet']['videoOwnerChannelTitle'] for item in self.response["items"]
                 if item['snippet']['videoOwnerChannelId'] == channel_id][0]
        values = [
            channel_id,
            self.datetime_now,
            title,
            self.datetime_now,
            "UU" + channel_id[2:] if channel_id[:2] == "UC" else None
        ]
        with self.connection.cursor() as cur:
            cur.execute(query, values)
            self.connection.commit()
        logger.warning(f'New channel added to fix FK violation. \nId: {channel_id} Title: {title}')

    def _save_playlist_items_request(self):
        query = """
        INSERT INTO playlist_items_request (
            playlist_id,
            requested_at,
            max_results,
            total_results,
            results_per_page,
            prev_page_token,
            next_page_token,
            etag
        )
        VALUES %s
        RETURNING playlist_items_request_id;
        """
        values = [
            [
                self.playlist_id,
                self.datetime_now,
                self.max_results,
                self.response['pageInfo']['totalResults'],
                self.response['pageInfo']['resultsPerPage'],
                self.response.get('prevPageToken', None),
                self.response.get('nextPageToken', None),
                self.response['etag']
            ],
        ]

        with self.connection.cursor() as cur:
            rows = execute_values(cur, query, values, template="(%s, %s, %s, %s, %s, %s, %s, %s)", fetch=True)
            self.playlist_items_request_id = rows[0][0]  # cur.fetchone()[0]

    def _save_playlist_items_request_youtube_video(self):
        query = """
        INSERT INTO playlist_items_request_youtube_video (
            playlist_items_request_id,
            youtube_video_id
        )
        VALUES %s
        """
        values = [
            [
                self.playlist_items_request_id,
                item['snippet']['resourceId']['videoId']
            ]
            for item in self.response['items']
        ]
        with self.connection.cursor() as cur:
            execute_values(cur, query, values, template="(%s, %s)", fetch=False)

    def _save_youtube_video(self):
        query = """
        INSERT INTO youtube_video (
            youtube_video_id,
            youtube_channel_id,
            published_at,
            updated_at,
            added_at,
            title_normalized,
            description_normalized
        )
        VALUES %s
        ON CONFLICT (youtube_video_id) DO UPDATE
        SET
            youtube_video_id = EXCLUDED.youtube_video_id,
            youtube_channel_id = EXCLUDED.youtube_channel_id,
            published_at = EXCLUDED.published_at,
            updated_at = EXCLUDED.updated_at,
            added_at = COALESCE(youtube_video.added_at, EXCLUDED.added_at),
            title_normalized = EXCLUDED.title_normalized,
            description_normalized = EXCLUDED.description_normalized
        RETURNING youtube_video_id;
        """
        values = [
            [
                item['snippet']['resourceId']['videoId'],  # youtube_video_id
                item['snippet']['videoOwnerChannelId'],  # youtube_channel_id
                item['contentDetails']['videoPublishedAt'],  # published_at
                self.datetime_now,  # updated_at
                self.datetime_now,  # added_at
                Helper.normalize(item['snippet']['title']),  # title_normalized
                Helper.normalize(item['snippet']['description']),  # description_normalized
            ]
            for item in self.response['items']
        ]
        with self.connection.cursor() as cur:
            execute_values(
                cur,
                query,
                values,
                template="(%s, %s, %s, %s, %s, %s, %s)",
                fetch=False)
            result = cur.fetchall()

    def _save_keyword(self):
        """Save new video ids to the 'keyword' table. """

        query = """
        INSERT INTO keyword (
            keyword_word,
            date_since_relevant,
            priority
        )
        VALUES %s
        ON CONFLICT (keyword_word, priority) DO NOTHING
        RETURNING keyword_id;
        """
        values = [
            [
                item['snippet']['resourceId']['videoId'],
                item['contentDetails']['videoPublishedAt'],
                99
            ]
            for item in self.response['items']
        ]
        with self.connection.cursor() as cur:
            rows = execute_values(
                cur,
                query,
                values,
                fetch=True
            )
        logger.info(f'New keywords: {len(rows)}')

    def _save_keyword_talent(self):
        query = """
        INSERT INTO keyword_talent (
            keyword_id,
            talent_id
        )
        SELECT k.keyword_id, yct.talent_id
        FROM keyword k
        JOIN youtube_video yv ON yv.youtube_video_id = k.keyword_word
        JOIN youtube_channel_talent yct ON yct.youtube_channel_id = yv.youtube_channel_id
        WHERE keyword_word = ANY(%s)
        ON CONFLICT (keyword_id, talent_id) DO NOTHING
        RETURNING keyword_id, talent_id;
        """
        values = [item['snippet']['resourceId']['videoId'] for item in self.response['items']]
        with self.connection.cursor() as cur:
            cur.execute(query, (values,))
            rows = cur.fetchall()
            logger.info(f'New keyword_talent pairs: {len(rows)}')

    def _do_stop_check(self):
        """Check if the playlist items request should be stopped.
        Condition: current playlist_items_request has videos from another playlist_items_request."""

        query_reached_end = """
        SELECT BOOL_OR(next_page_token IS NULL)
        FROM playlist_items_request
        WHERE playlist_id = %(playlist_id)s
        """
        query_duplicates = """
        WITH all_requests_for_playlist AS (
            SELECT playlist_items_request_id
            FROM playlist_items_request
            WHERE playlist_id = %(playlist_id)s
        ),
        all_videos_for_playlist AS (
            SELECT playlist_items_request_id, youtube_video_id
            FROM playlist_items_request_youtube_video
            WHERE playlist_items_request_id IN (SELECT playlist_items_request_id FROM all_requests_for_playlist)
        )
        SELECT COUNT(*)
        FROM all_videos_for_playlist avfp1
        WHERE NOT (avfp1.playlist_items_request_id = %(request_id)s
                -- exclude the 'previous page' of the playlist in the current update run if there is one
                OR avfp1.playlist_items_request_id = (%(request_id)s - 1))
            AND EXISTS (
                SELECT youtube_video_id 
                FROM all_videos_for_playlist avfp2
                WHERE playlist_items_request_id = %(request_id)s
                    AND avfp1.youtube_video_id = avfp2.youtube_video_id
            );
        """
        values = {'playlist_id': self.playlist_id, 'request_id': self.playlist_items_request_id}
        with self.connection.cursor() as cur:
            cur.execute(query_duplicates, values)
            duplicates = cur.fetchone()[0] > 0
            cur.execute(query_reached_end, values)
            reached_end = cur.fetchone()[0]
            if duplicates and reached_end:
                logger.info(f"Request {self.playlist_items_request_id} caught up to fully parsed playlist.")
                cur.execute("UPDATE playlist_items_request SET caught_up = TRUE WHERE playlist_items_request_id = %s;",
                            (self.playlist_items_request_id,))
                self.connection.commit()
                self.caught_up = True
            else:
                self.caught_up = False


class Channels:
    """Working with YT Data API 'channels' endpoint."""
    def __init__(self,
                 connection,
                 api_service: PrepareAPI | None = None,
                 only_unupdated: bool = False,
                 cooldown_period: datetime.timedelta = datetime.timedelta(days=30)):

        self._connection = connection
        self._api_service= api_service or PrepareAPI()
        self._api_key: str | None = None
        self._response: dict | None = None
        self._datetime_now: datetime.datetime | None = None
        # data for choosing a channel
        self._channels: list[str] | None = None
        self._channel_id: str | None = None
        self._cooldown_period = cooldown_period
        self._only_unupdated = only_unupdated
        # data for saving

    def update_channels_info(self, channel_count:int=1, delay_sec:float=0) -> int:

        self._set_channels_to_update()
        logger.info(f"{len(self._channels)} are queued for an info update.")
        channel_count = min(channel_count, len(self._channels))
        wait_seconds = 60

        for i in range(channel_count):
            time.sleep(delay_sec)
            try:
                self._prepare_request()
                self._request()
                self._api_service.change_quota(self._api_key, -1)
                self._verify_response()
                self._save()
            except VerificationError:
                continue
            except NoQuotaError:
                logger.info(f"{i} channels received an info update.\n")
                raise
            except HttpError as err:
                if err.resp.status == 403:
                    api_key_id = self._api_service.get_api_key_id(api_key=self._api_key)
                    quota_left = self._api_service.get_quota_left(api_key=self._api_key)
                    logger.error(f'Quota exceeded (prematurely). '
                                 f'API key: {api_key_id}. '
                                 f'Quota left: {quota_left}')
                    self._api_service.temporary_disable_key(api_key_id)
                    return True
                elif err.resp.status == 500:
                    logger.warning(f'YouTube server error (500). Retry in {wait_seconds} seconds.')
                    time.sleep(wait_seconds)
                    return True
                elif err.resp.status == 503:
                    logger.warning(f'YouTube server error (503). Retry in {wait_seconds} seconds.')
                    time.sleep(wait_seconds)
                    return True
                else:
                    logger.error(err)
                    time.sleep(wait_seconds)
                    return True
            except Exception as e:
                logger.error(f"Unexpected error during channels info update. Only {i} were updated.\n{e}")
                raise


        logger.info(f"{channel_count} channels received an info update.")
        quota_left = self._api_service.get_quota_left(self._api_key)
        logger.info(f"Quota left: {quota_left}")
        return channel_count

    def _set_channels_to_update(self):
        """Set a list of channels that have to have their info to be fully updated."""
        cooldown_clause = "" if self._only_unupdated else "OR info_fully_updated_at < CURRENT_TIMESTAMP - %(cooldown)s"

        query = f"""
        SELECT youtube_channel_id
        FROM youtube_channel 
        WHERE 
            info_accessible = TRUE 
            AND (
                info_fully_updated_at IS NULL
                {cooldown_clause}
            )
        ORDER BY 
            info_fully_updated_at ASC NULLS FIRST,
            channel_info_last_updated ASC,
            youtube_channel_id;
        """
        values = {}
        if not self._only_unupdated:
            values['cooldown'] = self._cooldown_period

        with self._connection.cursor() as cur:
            cur.execute(query, values)
            rows = cur.fetchall()

        self._channels = [row[0] for row in rows]

    def _prepare_request(self):
        self._api_key = self._api_service.get_api_key(threshold=1, delay=False, purpose=PrepareAPI.CHANNELS)
        self._channel_id = self._channels.pop(0)

    def _request(self):
        youtube = build('youtube', 'v3', developerKey=self._api_key)
        self._response = youtube.channels().list(
            part='snippet,statistics',
            id=self._channel_id,
        ).execute()

    def _verify_response(self):
        # verify there is a channel
        if "items" not in self._response:
            logging.warning(f"Channel request for {self._channel_id} got no matches")
            self._self_set_channel_info_unaccessible()
            raise VerificationError

        # verify channels id
        if self._response["items"][0]["id"] != self._channel_id:
            logging.error("Received info for the wrong channel in the response")
            raise Exception(f'Channel id mismatch: asking for {self._channel_id}, got:\n{self._response}')

        # verify there is more than 1 channel
        if len(self._response["items"]) > 1:
            logging.warning(f"Channel request for {self._channel_id} got multiple items.\n"
                            f"The first one will be used, others ignored. Data: \n{self._response}")

    def _self_set_channel_info_unaccessible(self):
        query = """
        UPDATE youtube_channel
        SET info_accessible = FALSE
        WHERE youtube_channel_id = %(channel_id)s;
        """
        values = {"channel_id": self._channel_id}
        with self._connection.cursor() as cur:
            cur.execute(query, values)
            self._connection.commit()
        logging.warning(f"Set info_accessible = FALSE for {self._channel_id}.")


    def _save(self):
        self._update_datetime_now()
        try:
            self._save_youtube_channel()
            self._save_youtube_channel_stats()
        except DatabaseError as e:
            self._connection.rollback()
            logger.error(f"A DB error occurred while saving channel info: {e} \nTransaction rolled back. ")
            logger.error(traceback.format_exc())
            time.sleep(60)
        except Exception as e:
            self._connection.rollback()
            logger.error(f"An error occurred while saving channel info: {e} \nTransaction rolled back. ")
            logger.error(traceback.format_exc())
            raise
        else:
            self._connection.commit()
            logger.info("Changes committed. (Channels request)")


    def _save_youtube_channel(self):
        """Save fuller channel info to the 'youtube_channel' table. """

        query = """
        UPDATE youtube_channel
        SET 
            title = %(title)s,
            description = %(description)s,
            custom_url = %(custom_url)s,
            published_at = %(published_at)s,
            thumbnail_default = %(thumbnail_default)s,
            info_fully_updated_at = %(info_fully_updated_at)s
        WHERE youtube_channel_id = %(youtube_channel_id)s;
        """

        values = {
            'title': Helper.normalize(self._response["items"][0]["snippet"]["title"]),
            'description': Helper.normalize(self._response["items"][0]["snippet"]["description"]),
            'custom_url': self._response["items"][0]["snippet"]["customUrl"],
            'published_at': self._response["items"][0]["snippet"]["publishedAt"],
            'thumbnail_default': self._response["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
            'info_fully_updated_at': self._datetime_now,
            'youtube_channel_id': self._response["items"][0]["id"],
        }

        with self._connection.cursor() as cur:
            cur.execute(query, values)

    def _save_youtube_channel_stats(self):
        """Save channel stats to the 'youtube_channel_stats' table. """

        query = """
        INSERT INTO youtube_channel_stats ( 
            youtube_channel_id,
            view_count,
            subscriber_count,
            video_count,
            gathered_at
        )
        VALUES (
            %(youtube_channel_id)s,
            %(view_count)s,
            %(subscriber_count)s,
            %(video_count)s,
            %(gathered_at)s
        );
        """

        values = {
            'youtube_channel_id': self._response["items"][0]["id"],
            'view_count': self._response["items"][0]["statistics"]["viewCount"],
            'subscriber_count': self._response["items"][0]["statistics"]["subscriberCount"],
            'video_count': self._response["items"][0]["statistics"]["videoCount"],
            'gathered_at': self._datetime_now,
        }

        with self._connection.cursor() as cur:
            cur.execute(query, values)

    def _update_datetime_now(self):
        self._datetime_now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)
