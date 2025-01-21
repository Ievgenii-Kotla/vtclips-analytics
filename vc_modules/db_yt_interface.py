from __future__ import annotations
from typing import Tuple, List
import datetime
import os
import traceback
import json

from googleapiclient.discovery import build
from psycopg2.extras import execute_values

from vc_modules import connect_to_db

# TODO: big things to add:
#  logging
#      move or duplicate every 'print()' to logging
#  write exceptions


class PrepareAPI:
    @staticmethod
    def current_time_utc():
        return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

    def __init__(self, quota_points=10000, filepath="api_quota_state.json"):
        def get_reset_target_time() -> datetime.datetime:
            time_now = self.current_time_utc()
            target_time = time_now.replace(hour=7, minute=0, second=0)
            if target_time > time_now:
                target_time -= datetime.timedelta(days=1)
            return target_time

        self.quota_points = quota_points
        self.filepath = filepath
        self.active_key: str = None
        self.api_quotas: dict[str, int] = None
        self.last_reset_at: datetime.datetime = None
        self.last_update_at: datetime.datetime = None
        self.api_keys: dict[str, str] = self.load_api_keys()
        self.load_api_quotas_info()

        if self.last_reset_at < get_reset_target_time() or len(self.api_keys) != len(self.api_quotas):
            self.reset_and_reload_quotas()

    @staticmethod
    def load_api_keys() -> dict[str, str]:
        """ Load API keys from environmental variables. """
        api_keys = os.getenv('API_keys').split(",")
        api_keys_dict = {f"API_key{i}": value for i, value in enumerate(api_keys)}
        return api_keys_dict

    def load_api_quotas_info(self) -> None:
        """ Load quota values for each API key, last reset and last update(other than reset) times from a file. """
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as err:
            print("File not found. ", err)
            self.last_update_at = self.current_time_utc()
            # Using self._reset_quotas and inline loading instead of self.reset_and_reload_quotas
            #   to avoid infinite loop if the file couldn't be created for some reason
            self._reset_quotas()
            print(f"New file created. {self.filepath}")
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

    def get_api_key(self, threshold=100) -> str:
        """ Get working API key to access YT. """
        quotas_over_threshold = {key: value for key, value in self.api_quotas.items() if value >= threshold}
        min_quota_key = min(quotas_over_threshold, key=quotas_over_threshold.get)
        return self.api_keys[min_quota_key]

    def change_quota(self, api_key: str, change: int):
        """ Change quota by the 'change' value for a specified API key in the file and for the current instance. """
        # Find corresponding dictionary key associated with the given API key
        key = next(key for key, value in self.api_keys.items() if value == api_key)

        # Update
        self.api_quotas[key] = self.api_quotas[key] + change
        self.save_api_quotas_info(
            self.api_quotas,
            self.last_reset_at,
            self.current_time_utc()
        )
        self.load_api_quotas_info()

    def get_quota_left(self, api_key):
        key = next(key for key, value in self.api_keys.items() if value == api_key)
        quota_left = self.api_keys[key]
        return quota_left

    def _reset_quotas(self):
        """ Reset the file that stores quota counters, and times of last reset and last update. """
        quotas = {f"API_key{i}": self.quota_points for i, _ in enumerate(self.api_keys)}
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


class SearchYTByKeyword:
    def __init__(self,
                 connection,
                 quota_in_reserve: int = 0,
                 talents_names: tuple[str] | None = None,
                 start_search_datetime: str = '1970-01-01 00:00:00+00:00',
                 end_search_datetime: str = '9000-01-01 00:00:00+00:00',
                 priority: tuple[int] = (0, 1),
                 usage_enabled: bool = True,
                 purity: tuple[str] = ('pure',),
                 api_service: PrepareAPI = None
                 ):
        # Command line arguments that where provided
        self.quota_in_reserve = quota_in_reserve
        self.talents_names = talents_names
        self.start_search_datetime = start_search_datetime
        self.end_search_datetime = end_search_datetime
        self.priority = priority
        self.usage_enabled = usage_enabled
        self.purity = purity

        # Variables that are necessary to prepare and make a YT search request
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.quota_points = 10000  # set by YT
        self.quota_left = self.quota_points
        self.api_service = api_service or PrepareAPI()  # Use the first one that evaluates to True

        self.talents_ids = (None,)
        self.all_talents = True
        if self.talents_names:
            self.set_talents_ids()
            self.all_talents = False

        self.search_map: List[Tuple[int, str, datetime.datetime, datetime.datetime], ] | None = None
        self.response = None

        # Default values for constant YT search parameters
        self.part = "snippet"
        self.max_results = 50
        self.order = None
        self.published_after = start_search_datetime
        self.published_before = end_search_datetime
        self.search_query = None
        self.region_code = "US"
        self.safe_Search = "none"
        self.type = "video"

        # Variables used to save to DB
        self.keyword_id = (None,)
        self.new_yt_channel_ids = None
        self.new_yt_video_ids = None
        self.search_yt_id = None
        self.youtube_video_values = None
        self.youtube_channel_values = None
        self.datetime_now = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)

        # Other
        self.session_videos_total: int = 0
        self.session_videos_new: int = 0
        self.session_channels_total: int = 0
        self.session_channels_new: int = 0
        self.session_searches: int = 0

    def close(self):
        if self.cursor:
            self.cursor.close()
            print("Cursor closed.")
        if self.connection:
            connect_to_db.connection_close(self.connection)

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
        AND (kt.talent_id IN %(talents_ids)s OR %(all_talents)s = TRUE)
    GROUP BY k.keyword_word, k.keyword_id, k.date_since_relevant
    -- Only include keywords that match a single talent
    HAVING COUNT(*) = 1    
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
            tstzrange('-infinity', %(datetimenow)s, '[]') 
            - tstzrange('-infinity', kcsr.date_since_relevant, '[]')
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
;
"""
        # Deprecated. Extremely slow query
        query0 = """
        -- line for query highlighting in IDE
        SELECT 1;
        SET TIME ZONE 'UTC';
        -- Filter out unnecessary rows from "keyword" table 
        --     (like rows with talents that would not be used for the search etc.)
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
                AND (kt.talent_id IN %(talents_ids)s OR %(all_talents)s = TRUE)
            GROUP BY k.keyword_word, k.keyword_id, k.date_since_relevant
            -- Only include keywords that match a single talent
            HAVING COUNT(*) = 1    
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
        -- Combine overlapping and adjacent searches
        keyword_combined_search_raw AS (
            SELECT 
                ks.keyword_id,
                ks.keyword_word,
                ks.date_since_relevant,
                ks.search_yt_id,
                ks.search_period,
                1 AS "level"
            FROM keyword_search AS ks
            UNION ALL
            SELECT
                kcsr.keyword_id,
                kcsr.keyword_word,
                kcsr.date_since_relevant,
                kcsr.search_yt_id,
                range_merge(kcsr.search_period, ks.search_period) AS search_period,
                kcsr.level + 1
            FROM 
                keyword_combined_search_raw AS kcsr
            JOIN 
                keyword_search AS ks
            ON 
                ks.keyword_id = kcsr.keyword_id
            WHERE 
                (
                    tstzrange(lower(kcsr.search_period), upper(kcsr.search_period) + interval '5 second', '[]') 
                    && tstzrange(lower(ks.search_period), upper(ks.search_period) + interval '5 second', '[]')
                ) 
                AND NOT (kcsr.search_period @> ks.search_period)
        ),
        -- Clean up from duplicates and non-final (incomplete) periods
        combined_search_periods AS (
            SELECT DISTINCT 
                kcsr.keyword_id, 
                kcsr.keyword_word, 
                kcsr.date_since_relevant,
                kcsr.search_period
            FROM 
                keyword_combined_search_raw AS kcsr
            WHERE 
                kcsr.level = (
                    SELECT 
                        MAX(kcsr2.level)
                    FROM 
                        keyword_combined_search_raw AS kcsr2
                    WHERE 
                        kcsr2.keyword_id = kcsr.keyword_id 
                        AND (kcsr2.search_yt_id = kcsr.search_yt_id OR kcsr2.search_yt_id IS NULL)
                )
        ),
        -- Calculate periods that where not searched
        non_searched_periods AS (
            SELECT DISTINCT
                csp1.keyword_id,
                csp1.keyword_word,
                tstzmultirange(
                    tstzrange('-infinity', %(datetimenow)s, '[]') 
                    - tstzrange('-infinity', csp1.date_since_relevant, '[]')
                ) - (
                    SELECT 
                        tstzmultirange(range_agg(csp2.search_period))
                    FROM
                        combined_search_periods AS csp2
                    WHERE
                        csp1.keyword_id = csp2.keyword_id
                ) AS non_searched
            FROM
                combined_search_periods AS csp1
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
            'datetimenow': self.datetime_now
        }
        cursor = self.connection.cursor()
        print("Creating the search map...")
        cursor.execute(query, values)
        print("Search map created.")
        self.search_map = cursor.fetchall()
        cursor.close()

    def prepare_query_and_period_alg1(self):
        """
        Set the query text and the period that'll be used in YT search request

        This algorithm provides:
        - the oldest period
        - a time span for the period is set to 1 day.
        - a query text that is a single keyword
        """

        #  Requires self.search_map to be updated before each new use
        keyword_id, keyword_word, start, end = None, None, None, None
        search_map = self.search_map
        for new_keyword_id, new_keyword_word, new_start, new_end in search_map:
            if start is None or new_start < start:
                keyword_id = new_keyword_id
                keyword_word = new_keyword_word
                start = new_start
                end = new_end

        end = min(
            start + datetime.timedelta(hours=23, minutes=59, seconds=59),
            self.datetime_now,
            end
        )
        self.keyword_id = (keyword_id,)
        self.search_query = keyword_word
        self.published_after = start.isoformat()
        self.published_before = end.isoformat()

        if end - start < datetime.timedelta(hours=23, minutes=59, seconds=59):
            print(f"Current search's length is {end - start} hh:mm:ss")

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
                print(f"Warning: Talent's name '{name}' did not match any talents.")
            # todo: fix: despite warning appears to use the first of all returned ids
            if cursor.fetchall():
                print(f"Warning: Talent's name '{name}' matched more than one talent.")
        cursor.close()
        self.talents_ids = tuple(ids)

    def filter_response(self):
        """ Filter out planned and active livestreams. """
        self.response["items"] = [d for d in self.response["items"] if d["snippet"]["liveBroadcastContent"] == "none"]

    def search(self):
        """ Conduct prepared search. """
        # Authenticate with the API using your API key
        api_key = self.api_service.get_api_key()
        if api_key is None:
            print("API key not found.")
        youtube = build('youtube', 'v3', developerKey=api_key)

        # todo: add an exception for not enough quota left
        # Search for videos related to a specific query
        self.response = youtube.search().list(
            part="snippet",
            maxResults=self.max_results,
            order="date",
            publishedAfter=self.published_after,
            publishedBefore=self.published_before,
            q=self.search_query,
            regionCode="US",
            safeSearch="none",
            type="video",
        ).execute()
        # todo: replace with a proper logging
        print(f"max results: {self.max_results}\n",
              f"publishedAfter: {self.published_after}\n",
              f"publishedBefore: {self.published_before}\n",
              f"q: {self.search_query}\n")
        self.api_service.change_quota(api_key, -100)
        self.quota_left = self.api_service.get_quota_left(api_key)

    def prepare_search(self):
        """ Prepare all the necessary data and variables for the search. """

        # Create the map of what keywords where searched already and at what time periods.
        self.set_search_map()
        # Current algorithm for providing the search details
        self.prepare_query_and_period_alg1()

    def search_next_and_save(self):
        """ Coordinate the process of searching YT. """
        self.prepare_search()
        self.search()
        self.filter_response()
        self.validate_results_per_page_qty()
        self.save()

    def save_youtube_channel(self):
        """ Save new information to the 'youtube_channel' table. """
        youtube_channel_query = """
        INSERT INTO youtube_channel (
            youtube_channel_id,
            channel_info_last_updated,
            title,
            added_at
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
                self.datetime_now
            ]
            for item in self.response["items"]
        ]
        self.new_yt_channel_ids = execute_values(
            self.cursor,
            youtube_channel_query,
            self.youtube_channel_values,
            template="(%s, %s, %s, %s)",
            fetch=True
        )

    def save_youtube_video(self):
        """ Save new information to the 'youtube_video' table. """
        youtube_video_query = """
    INSERT INTO youtube_video (
        youtube_video_id,
        youtube_channel_id,
        published_at,
        title,
        description_trimmed,
        live_broadcast_content,
        updated_at,
        kind,
        thumbnail_default_url,
        thumbnail_default_width,
        thumbnail_default_height,
        thumbnail_medium_url,
        thumbnail_medium_width,
        thumbnail_medium_height,
        thumbnail_high_url,
        thumbnail_high_width,
        thumbnail_high_height,
        added_at
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
                item["snippet"]["title"],
                item["snippet"]["description"],
                item["snippet"]["liveBroadcastContent"],
                self.datetime_now,
                item["id"]["kind"],
                item["snippet"]["thumbnails"]["default"]["url"],
                item["snippet"]["thumbnails"]["default"]["width"],
                item["snippet"]["thumbnails"]["default"]["height"],
                item["snippet"]["thumbnails"]["medium"]["url"],
                item["snippet"]["thumbnails"]["medium"]["width"],
                item["snippet"]["thumbnails"]["medium"]["height"],
                item["snippet"]["thumbnails"]["high"]["url"],
                item["snippet"]["thumbnails"]["high"]["width"],
                item["snippet"]["thumbnails"]["high"]["height"],
                self.datetime_now
            ]
            for item in self.response["items"]
        ]
        self.new_yt_video_ids = execute_values(
            self.cursor,
            youtube_video_query,
            self.youtube_video_values,
            template=(
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
        q
    )
    VALUES %s
    RETURNING search_yt_id;
    """
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
                self.search_query
            ]
        ]
        search_yt_ids = execute_values(
            self.cursor,
            search_yt_query,
            search_yt_values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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

        # todo: replace with more specific exceptions
        except Exception as e:
            traceback.print_exc()
            self.connection.rollback()
            print(f"An error occurred while saving: {e}")
            print("Transaction rolled back. ")
        else:
            self.connection.commit()
            print("Changes committed.")

        # todo: replace with a proper logging
        # 'logging' a few stats
        print('Videos in response.\n',
              'Total: ', len(self.youtube_video_values), '\n',
              'New  : ', len(self.new_yt_video_ids))
        print('Channels in response.\n',
              'Total: ', len(self.youtube_channel_values), '\n',
              'New  : ', len(self.new_yt_channel_ids))
        print('Newest search id: ', self.search_yt_id, '\n\n')
        print('Quota left for current key: ', self.quota_left)

        self.session_videos_total += len(self.youtube_video_values)
        self.session_videos_new += len(self.new_yt_video_ids)
        self.session_channels_total += len(self.youtube_channel_values)
        self.session_channels_new += len(self.new_yt_channel_ids)
        self.session_searches += 1

    def validate_results_per_page_qty(self):
        """ Check if 'resultsPerPage' returned in the response matches actual number of responses. """
        if self.response['pageInfo']['resultsPerPage'] != len(self.response['items']):
            print("resultsPerPage value does not match the actual number of results per page")

    def session_stats(self):
        print("Session statistics: ")
        print("Searches conducted: ", self.session_searches)
        print('Videos found:\n',
              'Total: ', self.session_videos_total, '\n',
              'New  : ', self.session_videos_new, '\n')
        print('Channels found:\n',
              'Total: ', self.session_channels_total, '\n',
              'New  : ', self.session_channels_new, '\n')


class SearchYTByChannel:
    # TBD
    pass


if __name__ == "__main__":
    connection = connect_to_db.connect_to_db()
    search_instance = SearchYTByKeyword(connection=connection)
    for i in range(2):
        search_instance.search_next_and_save()
    search_instance.session_stats()
    connect_to_db.connection_close(search_instance.connection)













