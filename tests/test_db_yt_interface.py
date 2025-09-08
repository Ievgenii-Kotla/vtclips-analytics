import unittest
import datetime
from unittest.mock import patch, ANY, MagicMock
import json
import os
from contextlib import ExitStack

from psycopg2 import DatabaseError
from dotenv import load_dotenv

from src.vtc import db_yt_interface
from src.vtc.db_yt_interface import PrepareAPI
from tests.fixtures import setup_test_db
import db_helpers

load_dotenv("../.env.test")

class ConsistentANY:
    def __init__(self):
        self.value = None

    def __eq__(self, other):
        if self.value is None:
            self.value = other
            return True
        else:
            return self.value == other


class TestSearchYTByKeywordSetMap(unittest.TestCase):
    @classmethod
    @patch('src.vtc.db_yt_interface.datetime.datetime', wraps=datetime.datetime)
    def setUpClass(cls, mock_datetime_datetime) -> None:
        mock_datetime_datetime.now.return_value = datetime.datetime(
            2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
        setup_test_db.reset_for_map()

        with db_helpers.connect_to_test_db() as connection:
            instance = db_yt_interface.SearchYTByKeyword(
                connection=connection,
                api_service=PrepareAPI(filepath='../state/test_api_quota_state.json', delay=False)
            )
            instance.set_search_map()


        cls.actual_dataset = [(
            item[1],
            item[2].astimezone(datetime.timezone.utc),
            item[3].astimezone(datetime.timezone.utc)
        ) for item in instance.search_map]

        cls.expected_dataset = [
            (
                'keywordA1',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordA2',
                datetime.datetime(2020, 6, 12, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 14, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordA2',
                datetime.datetime(2020, 6, 16, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB1',
                datetime.datetime(2020, 6, 14, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB2',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB3',
                datetime.datetime(2020, 6, 15, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB4',
                datetime.datetime(2020, 6, 14, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 15, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB4',
                datetime.datetime(2020, 6, 17, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB5',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 13, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB5',
                datetime.datetime(2020, 6, 16, 10, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB6',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 13, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB6',
                datetime.datetime(2020, 6, 16, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB7',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 13, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB7',
                datetime.datetime(2020, 6, 15, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB8',
                datetime.datetime(2020, 6, 13, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 13, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ), (
                'keywordB8',
                datetime.datetime(2020, 6, 15, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 6, 15, 23, 59, 59, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB8',
                datetime.datetime(2020, 6, 17, 12, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB9',
                datetime.datetime(2020, 6, 15, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
            (
                'keywordB10',
                datetime.datetime(2020, 6, 15, 0, 0, 1, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
            ),
        ]

    def test_set_search_map_consecutive_search(self):
        """ Test set_search_map method when search history for the keyword has one consecutive search. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordA1']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordA1']
        self.assertEqual(expected, actual)

    def test_set_search_map_nonconsecutive_search(self):
        """ Test set_search_map method when search history for the keyword has one non-consecutive search. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordA2']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordA2']
        with self.subTest('first_period'):
            self.assertEqual(expected[0], actual[0])
        with self.subTest('second_period'):
            self.assertEqual(expected[1], actual[1])

    def test_set_search_map_empty_consecutive_search(self):
        """ Test set_search_map method when search history for the keyword has one consecutive search with no hits. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB1']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB1']
        self.assertEqual(expected, actual)

    def test_set_search_map_no_searches(self):
        """ Test set_search_map method when search history for the keyword has no searches. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB2']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB2']
        self.assertEqual(expected, actual)

    def test_set_search_map_two_consecutive_searches(self):
        """ Test set_search_map method when search history for the keyword has two consecutive searches with no hits."""
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB3']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB3']
        self.assertEqual(expected, actual)

    def test_set_search_map_two_nonconsecutive_searches(self):
        """ Test set_search_map method when search history for the keyword has two searches that are two days apart. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB4']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB4']
        self.assertEqual(expected, actual)

    def test_set_search_map_three_partially_overlapping_searches(self):
        """ Test set_search_map method when search history for the keyword has three partially overlapping searches. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB5']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB5']
        self.assertEqual(expected, actual)

    def test_set_search_map_two_fully_overlapping_searches(self):
        """ Test set_search_map method when search history for the keyword has two fully overlapping searches. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB6']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB6']
        self.assertEqual(expected, actual)

    def test_set_search_map_two_identical_searches(self):
        """ Test set_search_map method when search history for the keyword has two identical searches. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB7']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB7']
        self.assertEqual(expected, actual)

    def test_set_search_map_single_search_and_two_overlapping(self):
        """ Test set_search_map method when search history for the keyword has one single search and two overlapping."""
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB8']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB8']
        self.assertEqual(expected, actual)

    def test_set_search_map_two_adjacent_searches(self):
        """ Test set_search_map method when search history for the keyword has two adjacent searches. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB9']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB9']
        self.assertEqual(expected, actual)

    def test_set_search_map_searches_separated_by_1_second(self):
        """ Test set_search_map method when search history for the keyword has 2 searches
        separated by 1 second from one another and from date_since_relevant. """
        expected = [item for item in self.expected_dataset if item[0] == 'keywordB10']
        actual = [item for item in self.actual_dataset if item[0] == 'keywordB10']
        self.assertEqual(expected, actual)


class TestSearchYTByKeywordSave(unittest.TestCase):
    keyword_info: list

    @staticmethod
    def get_actual_data(query):
        with db_helpers.connect_to_test_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                actual = cursor.fetchall()
        return actual

    @classmethod
    @patch('src.vtc.db_yt_interface.datetime.datetime', wraps=datetime.datetime)
    def setUpClass(cls, mock_datetime_datetime):
        mock_datetime_datetime.now.return_value = datetime.datetime(
            2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
        json_response = """{
          "kind": "youtube#searchListResponse",
          "etag": "0wxr2Fwj4AVkl5m8J7kKbdp1icg",
          "nextPageToken": "CAIQAA",
          "regionCode": "US",
          "pageInfo": {
            "totalResults": 33412,
            "resultsPerPage": 2
          },
          "items": [
            {
              "kind": "youtube#searchResult",
              "etag": "oQ5Bs_APBe24BR7HmXwTEf07Gzw",
              "id": {
                "kind": "youtube#video",
                "videoId": "XD0p0Dj0LXc"
              },
              "snippet": {
                "publishedAt": "2024-08-08T22:46:14Z",
                "channelId": "UC58YRkZ2cMedl0AVv_rNoZw",
                "title": "Kronii Laughing so Hard at Her Own Flower Building in Minecraft [Kaela/Kronii]",
                "description": "In this video, kronii laughing hard at her own building flower = 【Minecraft】holoID Cup: Timesmith PRACTICE time!",
                "thumbnails": {
                  "default": {
                    "url": "https://i.ytimg.com/vi/XD0p0Dj0LXc/default.jpg",
                    "width": 120,
                    "height": 90
                  },
                  "medium": {
                    "url": "https://i.ytimg.com/vi/XD0p0Dj0LXc/mqdefault.jpg",
                    "width": 320,
                    "height": 180
                  },
                  "high": {
                    "url": "https://i.ytimg.com/vi/XD0p0Dj0LXc/hqdefault.jpg",
                    "width": 480,
                    "height": 360
                  }
                },
                "channelTitle": "Dvlprm",
                "liveBroadcastContent": "none",
                "publishTime": "2024-08-08T22:46:14Z"
              }
            },
            {
              "kind": "youtube#searchResult",
              "etag": "3LHmKewqgxTiTusEO__osYvqhho",
              "id": {
                "kind": "youtube#video",
                "videoId": "IwhkBhUH0lc"
              },
              "snippet": {
                "publishedAt": "2024-08-08T17:06:06Z",
                "channelId": "UCAnUBKzIF_oR4yNUfqIkCqw",
                "title": "Ame and Ina Can&#39;t Stop Teasing Kronii~ (Hololive)",
                "description": "Enjoy! Thanks For Watching~ I'm not a native English speaker but I'm trying my best~ Please support the main channel of Hololive ...",
                "thumbnails": {
                  "default": {
                    "url": "https://i.ytimg.com/vi/IwhkBhUH0lc/default.jpg",
                    "width": 120,
                    "height": 90
                  },
                  "medium": {
                    "url": "https://i.ytimg.com/vi/IwhkBhUH0lc/mqdefault.jpg",
                    "width": 320,
                    "height": 180
                  },
                  "high": {
                    "url": "https://i.ytimg.com/vi/IwhkBhUH0lc/hqdefault.jpg",
                    "width": 480,
                    "height": 360
                  }
                },
                "channelTitle": "Whatopia",
                "liveBroadcastContent": "none",
                "publishTime": "2024-08-08T17:06:06Z"
              }
            }
          ]
        }
        """

        setup_test_db.reset_for_save()
        with db_helpers.connect_to_test_db() as connection:
            search_instance = db_yt_interface.SearchYTByKeyword(
                connection=connection,
                api_service=PrepareAPI(filepath='../state/test_api_quota_state.json', delay=False)
            )
            search_instance.response = json.loads(json_response)

            search_instance.cursor.execute("SELECT * FROM keyword")
            cls.keyword_info = search_instance.cursor.fetchall()

        search_instance.search_map = [(
            cls.keyword_info[0][0],
            cls.keyword_info[0][1],
            datetime.datetime(2020, 6, 13, 0, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 6, 13, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )]

        search_instance.keyword_id = (cls.keyword_info[0][0],)
        search_instance.published_after = datetime.datetime(2024, 8, 8, 0, 0, 0, tzinfo=datetime.timezone.utc)
        search_instance.published_before = datetime.datetime(2024, 8, 8, 23, 59, 59, tzinfo=datetime.timezone.utc)
        search_instance.search_query = search_instance.search_map[0][1]

        search_instance.save()

    def test_save_youtube_channel(self):
        query = """
SET TIME ZONE 'UTC';
SELECT * FROM youtube_channel;
"""
        actual = self.get_actual_data(query)
        expected = [
            (
                None,  # talent id
                None,
                None,
                None,  # video_list_last_updated
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # channel info last updated
                "Dvlprm",  # channel title
                None,  # channel description
                None,  # custom url
                None,  # published at
                None,  # YT channel thumbnail
                None,  # country
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at
                "UC58YRkZ2cMedl0AVv_rNoZw",  # YT channel id
                None,
                "UU58YRkZ2cMedl0AVv_rNoZw",  # playlist_id
                None,
                True  # playlist_available
            ),
            (
                None,  # talent id
                None,
                None,
                None,  # video_list_last_updated
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # channel info last updated
                "Whatopia",  # channel title
                None,  # channel description
                None,  # custom url
                None,  # published at
                None,  # YT channel thumbnail
                None,  # country
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at
                "UCAnUBKzIF_oR4yNUfqIkCqw",  # YT channel id
                None,
                "UUAnUBKzIF_oR4yNUfqIkCqw",  # playlist_id
                None,
                True,  # playlist_available
            ),
        ]
        self.assertEqual(expected, actual)

    def test_save_youtube_video(self):
        query = """
SET TIME ZONE 'UTC';
SELECT * FROM youtube_video;
"""
        actual = self.get_actual_data(query)
        expected = [
            (
                "XD0p0Dj0LXc",  # youtube_video_id
                "UC58YRkZ2cMedl0AVv_rNoZw",  # youtube_channel_id
                None,  # duration
                None,  # actual_start_time
                None,  # actual_end_time
                None,  # scheduled_start_time
                datetime.datetime.fromisoformat("2024-08-08T22:46:14+00:00"),  # published_at
                "In this video, kronii laughing hard at her own building flower = 【Minecraft】"
                "holoID Cup: Timesmith PRACTICE time!",  # description_trimmed
                None,  # category_id
                "none",  # live_broadcast_content
                None,  # localized_title
                None,  # localized_description
                None,  # default_audio_language
                None,  # upload_status
                None,  # privacy_status
                None,  # license
                None,  # embeddable
                None,  # public_stats_viewable
                None,  # made_for_kids
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # updated_at
                None,  # tags
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at
                None,
                "Kronii Laughing so Hard at Her Own Flower Building in Minecraft [Kaela/Kronii]",
                None
            ),
            (
                "IwhkBhUH0lc",  # youtube_video_id
                "UCAnUBKzIF_oR4yNUfqIkCqw",  # youtube_channel_id
                None,  # duration
                None,  # actual_start_time
                None,  # actual_end_time
                None,  # scheduled_start_time
                datetime.datetime.fromisoformat("2024-08-08T17:06:06+00:00"),  # published_at
                "Enjoy! Thanks For Watching~ I'm not a native English speaker but I'm trying my best~ "
                "Please support the main channel of Hololive ...",  # description_trimmed
                None,  # category_id
                "none",  # live_broadcast_content
                None,  # localized_title
                None,  # localized_description
                None,  # default_audio_language
                None,  # upload_status
                None,  # privacy_status
                None,  # license
                None,  # embeddable
                None,  # public_stats_viewable
                None,  # made_for_kids
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # updated_at
                None,  # tags
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at
                None,
                "Ame and Ina Can't Stop Teasing Kronii~ (Hololive)",
                None
            )
        ]
        self.assertEqual(expected, actual)

    def test_save_search_yt(self):
        query = """
SET TIME ZONE 'UTC';
SELECT * FROM search_yt;
"""
        actual = self.get_actual_data(query)
        expected = [
            (
                ANY,  # search_yt_id
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # searched_at
                datetime.datetime(2024, 8, 8, 0, 0, 0, tzinfo=datetime.timezone.utc),  # published_after
                datetime.datetime(2024, 8, 8, 23, 59, 59, tzinfo=datetime.timezone.utc),  # published_before
                50,  # results_per_page_max
                None,  # prev_page_token
                "CAIQAA",  # next_page_token
                33412,  # total_results
                "US",  # region_code
                2,  # results_per_page
                None,  # page_num
                "test_keyword_for_save",  # q (searched text)
                "youtube#searchListResponse",  # kind
                1,  # layer
                None,  # parent id
                False  # is_q_quoted
            )
        ]
        self.assertEqual(expected, actual)

    def test_save_keyword_search_yt(self):
        query = """
SET TIME ZONE 'UTC';
SELECT * FROM keyword_search_yt;
"""
        actual = self.get_actual_data(query)
        expected = [
            (
                ANY,  # search_yt_id
                self.keyword_info[0][0]  # keyword_id
            )
        ]
        self.assertEqual(expected, actual)

    def test_save_search_yt_youtube_video(self):
        query = """
SET TIME ZONE 'UTC';
SELECT * FROM search_yt_youtube_video;
"""
        actual = self.get_actual_data(query)
        expected = [
            (
                ANY,  # search_yt_id
                "XD0p0Dj0LXc"  # youtube_video_id
            ),
            (
                ANY,  # search_yt_id
                "IwhkBhUH0lc"  # youtube_video_id
            )
        ]
        self.assertEqual(expected, actual)

    def test_search_yt_id_consistency(self):
        query_search_yt = "SELECT search_yt_id FROM search_yt;"
        query_keyword_search_yt = "SELECT search_yt_id FROM keyword_search_yt;"
        query_search_yt_youtube_video = "SELECT search_yt_id FROM search_yt_youtube_video;"
        actual = (self.get_actual_data(query_search_yt)
                  + self.get_actual_data(query_keyword_search_yt)
                  + self.get_actual_data(query_search_yt_youtube_video))
        self.assertTrue(
            all(x == actual[0] for x in actual),
            "The same search has search_id value that is different in different tables")


class TestPrepareAPI(unittest.TestCase):
    def setUp(self) -> None:
        """ Create proper .json file with necessary info inside """
        filepath = "../state/test_api_quota_state.json"
        self.quotas_test_values = {
            "API_key0": {
                "max": 10000,
                "available": 5500,
                "reserve": 4500,
                "purpose": "test",
                "coefficient": 1
            },
            "API_key1": {
                "max": 10000,
                "available": 3100,
                "reserve": 6900,
                "purpose": "universal",
                "coefficient": 1
            },
            "API_key2": {
                "max": 10000,
                "available": 7800,
                "reserve": 2200,
                "purpose": "universal",
                "coefficient": 1
            }
        }
        file_content = {
            "API_quotas": self.quotas_test_values,
            "last_reset_at": "2024-01-01T07:00:00+00:00",
            "last_update_at": "2024-01-01T01:00:00+00:00"
        }
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(file_content, file)
        with patch.dict(os.environ, {'API_keys': 'key0,key1,key2'}), \
            patch.object(PrepareAPI,
                         "current_time_utc",
                         return_value=datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00")), \
            patch.object(PrepareAPI,
                         "needs_reset",
                         return_value=False):
                quota_points = 10000
                self.instance = PrepareAPI(quota_points=quota_points, filepath=filepath, delay=False)

    def test_load_api_keys(self):
        expected = {
            "API_key0": "key0",
            "API_key1": "key1",
            "API_key2": "key777"
        }
        with patch.dict(os.environ, {'API_keys': 'key0,key1,key777'}):
            actual = self.instance.load_api_keys()
        self.assertEqual(expected, actual)

    # todo: error here
    def test_load_api_quotas_info(self):
        expected = (
            {
                "API_key0": 10000,
                "API_key1": 10000,
                "API_key2": 10000
            },
            datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"),
            datetime.datetime.fromisoformat("2024-01-01T01:00:00+00:00")
        )
        expected = (
            self.quotas_test_values,
            datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"),
            datetime.datetime.fromisoformat("2024-01-01T01:00:00+00:00")
        )
        self.instance.load_api_quotas_info()
        actual = (self.instance.api_quotas, self.instance.last_reset_at, self.instance.last_update_at)
        self.assertEqual(expected, actual)

    def test_save_api_quotas_info(self):
        last_reset_at_str = "2024-01-01T07:00:00+00:00"
        last_update_at_str = "2024-01-01T01:00:00+00:00"
        quotas = self.quotas_test_values
        last_reset_at = datetime.datetime.fromisoformat(last_reset_at_str)
        last_update_at = datetime.datetime.fromisoformat(last_update_at_str)
        expected = {"API_quotas": quotas} \
                   | {"last_reset_at": last_reset_at_str} \
                   | {"last_update_at": last_update_at_str}

        self.instance.save_api_quotas_info(
            quotas,
            last_reset_at,
            last_update_at
        )
        with open(self.instance.filepath, "r", encoding="utf-8") as file:
            actual = json.load(file)
        self.assertEqual(expected, actual, "Quotas didn't save properly to the file.")

    def test_get_api_key_min(self):
        self.instance.api_quotas = {
            "API_key0": {
                "max": 10000,
                "available": 5500,
                "reserve": 4500,
                "purpose": "universal",
                "coefficient": 1
            },
            "API_key1": {
                "max": 10000,
                "available": 100,
                "reserve": 6900,
                "purpose": "universal",
                "coefficient": 1
            },
            "API_key2": {
                "max": 10000,
                "available": 10,
                "reserve": 2200,
                "purpose": "universal",
                "coefficient": 1
            }
        }
        expected = "key1"
        with patch('src.vtc.db_yt_interface.datetime.datetime', wraps=datetime.datetime) as mock_object:
            mock_object.now.return_value=datetime.datetime.fromisoformat("2023-01-01T09:33:00+00:00")
            actual = self.instance.get_api_key(random_key=False)
        self.assertEqual(expected, actual)


    def test_get_api_key_purpose(self):
        self.instance.api_quotas = {
            "API_key0": {
                "max": 10000,
                "available": 5500,
                "reserve": 4500,
                "purpose": "universal",
                "coefficient": 1
            },
            "API_key1": {
                "max": 10000,
                "available": 100,
                "reserve": 6900,
                "purpose": "wrong",
                "coefficient": 1
            },
            "API_key2": {
                "max": 10000,
                "available": 10,
                "reserve": 2200,
                "purpose": "universal",
                "coefficient": 1
            }
        }
        expected = "key0"
        with patch('src.vtc.db_yt_interface.datetime.datetime', wraps=datetime.datetime) as mock_object:
            mock_object.now.return_value=datetime.datetime.fromisoformat("2023-01-01T09:33:00+00:00")
            actual = self.instance.get_api_key(random_key=False)
        self.assertEqual(expected, actual)

    def test_change_quota_file(self):
        with patch.object(
                PrepareAPI,
                "current_time_utc",
                return_value=datetime.datetime.fromisoformat("2024-01-01T01:00:00+00:00")
        ):
            self.instance.change_quota("key2", -500)
        expected = {
            "API_quotas": {
                "API_key0": {
                    "max": 10000,
                    "available": 5500,
                    "reserve": 4500,
                    "purpose": "test",
                    "coefficient": 1
                },
                "API_key1": {
                    "max": 10000,
                    "available": 3100,
                    "reserve": 6900,
                    "purpose": "universal",
                    "coefficient": 1
                },
                "API_key2": {
                    "max": 10000,
                    "available": 7300,
                    "reserve": 2200,
                    "purpose": "universal",
                    "coefficient": 1
                }
            },
            "last_reset_at": "2024-01-01T07:00:00+00:00",
            "last_update_at": "2024-01-01T01:00:00+00:00"
        }
        with open(self.instance.filepath, "r", encoding="utf-8") as file:
            actual = json.load(file)
        self.assertEqual(expected, actual, "Quota in the file didn't update properly.")
        print()

    def test_change_quota_instance(self):
        with patch.object(
                PrepareAPI,
                "current_time_utc",
                return_value=datetime.datetime.fromisoformat("2024-01-01T01:00:00+00:00")
        ):
            self.instance.change_quota("key2", -500)
        expected = (
            {
                "API_key0": {
                    "max": 10000,
                    "available": 5500,
                    "reserve": 4500,
                    "purpose": "test",
                    "coefficient": 1
                },
                "API_key1": {
                    "max": 10000,
                    "available": 3100,
                    "reserve": 6900,
                    "purpose": "universal",
                    "coefficient": 1
                },
                "API_key2": {
                    "max": 10000,
                    "available": 7300,
                    "reserve": 2200,
                    "purpose": "universal",
                    "coefficient": 1
                }
            },
            datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"),
            datetime.datetime.fromisoformat("2024-01-01T01:00:00+00:00")
        )
        self.assertEqual(
            expected,
            (self.instance.api_quotas, self.instance.last_reset_at, self.instance.last_update_at),
            "Quota in the PrepareAPI instance didn't update properly after quota change."
        )

    def test__reset_quotas(self):
        with open(self.instance.filepath, "w", encoding="utf-8") as file:
            json.dump({"API_key0": 9999}, file)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {'API_keys': 'key0,key1,key2'}))
            stack.enter_context(patch.object(db_yt_interface, 'randint', side_effect=[55, 31, 78]))
            stack.enter_context(patch.object(
                PrepareAPI,
                "current_time_utc",
                return_value=datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"))
            )
            self.instance._reset_quotas()
        expected = {
            "API_quotas": self.quotas_test_values,
            "last_reset_at": "2024-01-01T07:00:00+00:00",
            "last_update_at": "2024-01-01T07:00:00+00:00"
        }
        with open(self.instance.filepath, "r", encoding="utf-8") as file:
            actual = json.load(file)
        self.assertEqual(expected, actual, "Data in the file didn't update properly after reset")

    def test_reset_and_reload_quotas_instance(self):
        with open(self.instance.filepath, "w", encoding="utf-8") as file:
            json.dump({"API_key0": 9999}, file)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {'API_keys': 'key0,key1,key2'}))
            stack.enter_context(patch.object(db_yt_interface, 'randint', side_effect=[55, 31, 78]))
            stack.enter_context(patch.object(
                PrepareAPI,
                "current_time_utc",
                return_value=datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"))
            )
            self.instance.reset_and_reload_quotas()
        expected = {
            "API_quotas": self.quotas_test_values,
            "last_reset_at": datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"),
            "last_update_at": datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00")
        }
        self.assertEqual(
            expected['API_quotas'],
            self.instance.api_quotas,
            "Quotas in the PrepareAPI instance didn't update properly after reset")
        self.assertEqual(
            (expected["last_reset_at"], expected["last_update_at"]),
            (self.instance.last_reset_at, self.instance.last_update_at),
            "Datetimes in the PrepareAPI didn't update properly after reset")

    def test_reset_and_reload_quotas_file(self):
        with open(self.instance.filepath, "w", encoding="utf-8") as file:
            json.dump({"API_key0": 9999}, file)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {'API_keys': 'key0,key1,key2'}))
            stack.enter_context(patch.object(db_yt_interface, 'randint', side_effect=[55, 31, 78]))
            stack.enter_context(patch.object(
                PrepareAPI,
                "current_time_utc",
                return_value=datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00"))
            )
            self.instance.reset_and_reload_quotas()
        expected = {
            "API_quotas": self.quotas_test_values,
            "last_reset_at": "2024-01-01T07:00:00+00:00",
            "last_update_at": "2024-01-01T07:00:00+00:00"
        }
        with open(self.instance.filepath, "r", encoding="utf-8") as file:
            actual = json.load(file)
        self.assertEqual(expected, actual, "Data in the file didn't update properly after reset adn reload. ")


class TestSearchYTByKeywordCalculateSearchInterval(unittest.TestCase):
    """ Test SearchYTByKeyword.calculate_search_interval method. """

    connection = None

    @classmethod
    def setUpClass(cls) -> None:
        setup_test_db.reset_for_interval()
        cls.connection = db_helpers.connect_to_test_db()
        cls.instance = db_yt_interface.SearchYTByKeyword(
            cls.connection,
            api_service=PrepareAPI(filepath='../state/test_api_quota_state.json', delay=False)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.connection.close()

    def test_calculate_search_interval_first_search(self):
        date = datetime.datetime.fromisoformat('2025-01-01 00:00:00+00:00')
        keyword = 'keyword_10'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=1, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_post_debut_zero_matches(self):
        date = datetime.datetime.fromisoformat('2024-01-05 00:00:00+00:00')
        keyword = 'keyword_3'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=6, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_post_debut_1to10_big(self):
        date = datetime.datetime.fromisoformat('2024-01-12 00:00:00+00:00')
        keyword = 'keyword_4'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=6, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_post_debut_1to10_medium(self):
        date = datetime.datetime.fromisoformat('2024-01-07 00:00:00+00:00')
        keyword = 'keyword_5'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=3, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_11to40(self):
        date = datetime.datetime.fromisoformat('2024-01-09 00:00:00+00:00')
        keyword = 'keyword_6'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=3, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_41to50_big(self):
        date = datetime.datetime.fromisoformat('2024-01-07 00:00:00+00:00')
        keyword = 'keyword_7'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=1, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_old_search(self):
        date = datetime.datetime.fromisoformat('2024-01-07 00:00:01+00:00')
        keyword = 'keyword_8'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=1, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_41to50_small(self):
        date = datetime.datetime.fromisoformat('2024-01-05 00:00:00+00:00')
        keyword = 'keyword_9'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=0, hours=23, minutes=59, seconds=59), interval)


class TestSearchYTByKeywordSubsearch(unittest.TestCase):
    connection = None
    instance = None
    cursor = None
    searches = {
        'search_1': {
            'searched_at': '2025-01-10 00:00:01+00:00',
            'published_after': '2025-01-10 00:00:00+00:00',
            'published_before': '2025-01-11 23:59:59+00:00',
            'q': 'keyword_1',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': None,
            'results_per_page': 50,
            'total_results': 100,
            'results_per_page_max': 50
        },
        'search_2': {
            'searched_at': '2025-01-10 00:00:02+00:00',
            'published_after': '2025-01-10 00:00:00+00:00',
            'published_before': '2025-01-11 23:59:59+00:00',
            'q': 'keyword_2',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': None,
            'results_per_page': 50,
            'total_results': 100,
            'results_per_page_max': 50
        },
        'search_3': {
            'searched_at': '2025-01-10 00:00:03+00:00',
            'published_after': '2025-01-10 00:00:00+00:00',
            'published_before': '2025-01-11 23:59:59+00:00',
            'q': 'keyword_3',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': None,
            'results_per_page': 50,
            'total_results': 100,
            'results_per_page_max': 50
        },
    }
    subsearches = {
        'search_1_subsearch_1': {
            'searched_at': '2025-01-10 00:00:11+00:00',
            'published_after': '2025-01-10 00:00:00+00:00',
            'published_before': '2025-01-10 23:59:59+00:00',
            'q': 'keyword_1',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': 1,
            'results_per_page': 30,
            'total_results': 100,
            'results_per_page_max': 50
        },
        'search_1_subsearch_2': {
            'searched_at': '2025-01-10 00:00:21+00:00',
            'published_after': '2025-01-11 00:00:00+00:00',
            'published_before': '2025-01-11 23:59:59+00:00',
            'q': 'keyword_1',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': 1,
            'results_per_page': 30,
            'total_results': 100,
            'results_per_page_max': 50
        },
        'search_2_subsearch_1': {
            'searched_at': '2025-01-10 00:00:12+00:00',
            'published_after': '2025-01-10 00:00:00+00:00',
            'published_before': '2025-01-10 23:59:59+00:00',
            'q': 'keyword_2',
            'region_code': 'US',
            'search_layer': 1,
            'parent_id': 2,
            'results_per_page': 30,
            'total_results': 100,
            'results_per_page_max': 50
        },
    }

    def populate_search_yt(self, search_ids, subsearch_ids):
        query = """
        INSERT INTO search_yt (
            searched_at,
            published_after,
            published_before,
            q,
            region_code,
            search_layer,
            parent_id,
            results_per_page,
            total_results,
            results_per_page_max
        )
        VALUES (
            %(searched_at)s,
            %(published_after)s,
            %(published_before)s,
            %(q)s,
            %(region_code)s,
            %(search_layer)s,
            %(parent_id)s,
            %(results_per_page)s,
            %(total_results)s,
            %(results_per_page_max)s
        )
        RETURNING search_yt_id;
        """
        dataset = [self.searches[search_id] for search_id in search_ids]
        ids = []
        for data in dataset:
            self.cursor.execute(query, data)
            ids.append(self.cursor.fetchone()[0])

        dataset = [self.subsearches[subsearch_id] for subsearch_id in subsearch_ids]
        id_ = ids.pop()
        for data in dataset:
            data['parent_id'] = id_
            self.cursor.execute(query, data)


    @classmethod
    def setUpClass(cls) -> None:
        cls.connection = db_helpers.connect_to_test_db()
        cls.cursor = cls.connection.cursor()
        cls.instance = db_yt_interface.SearchYTByKeyword(
            cls.connection,
            api_service=PrepareAPI(filepath='../state/test_api_quota_state.json', delay=False)
        )
        while True:
            success = cls.instance.subsearch_next_and_save()
            if not success:
                break

    @classmethod
    def tearDownClass(cls) -> None:
        cls.cursor.execute('TRUNCATE TABLE search_yt CASCADE;')
        cls.cursor.close()
        cls.connection.close()

    def setUp(self) -> None:
        self.cursor.execute('TRUNCATE TABLE search_yt CASCADE;')

    def test_subsearch_two_subsearches(self):
        search_ids = ['search_1', ]
        subsearch_ids = ['search_1_subsearch_1', 'search_1_subsearch_2', ]
        self.populate_search_yt(search_ids, subsearch_ids)
        success = self.instance.set_subsearch_map()
        self.assertFalse(success, 'Should not create map under those conditions')

class TestPlaylistItems(unittest.TestCase):
    connection = None
    cursor = None

    def rows_in_tables_qty(self) -> dict:
        with self.connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM playlist_items_request;")
            pir_rows_qty = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM playlist_items_request_youtube_video")
            piryv_rows_qty = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM youtube_video")
            yv_rows_qty = cur.fetchone()[0]
        return {'pir': pir_rows_qty, 'piryv': piryv_rows_qty, 'yv':yv_rows_qty}

    def setUp(self) -> None:
        self.connection = db_helpers.connect_to_test_db()
        db_helpers.truncate_all(self.connection)
        self.cursor = self.connection.cursor()
        setup_test_db.reset_for_playlist_items_request()
        self.playlist_items = db_yt_interface.PlaylistItems(
            connection=self.connection,
            only_talents=False,
            api_service=db_yt_interface.PrepareAPI(filepath='../state/test_api_quota_state.json'),
            cooldown_period=datetime.timedelta(days=0)
        )
        self.fake_response = {
            "kind": "youtube#playlistItemListResponse",
            "etag": "GNPrWxCKsLNrFefUvZJrwcqWsV8",
            "nextPageToken": "EAAaHlBUOkNBVWlFRE0zTTBSRU1FUXdRekkwTnpjMk9URQ",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "fhZ-UPviRH2-h4-QH_9OvpTrIlk",
                    "id": "VVVURUtrRFg3bGFmUVZuSnJxdTU1anJBLlBKVHFCNFRQZG4w",
                    "snippet": {
                        "publishedAt": "2025-05-25T15:00:40Z",
                        "channelId": "UCTEKkDX7lafQVnJrqu55jrA",
                        "title": "Gura Was This Close to Working for Children's Television",
                        "description": "Check out the Full Stream source:\n\u25c6\u3010POWERWASH SIMULATOR\u3011time for your bath, stinklord\nhttps://www.youtube.com/live/Jvvc3nc_TPw?si=ckJmAU1nxgGRvIwD\n\nTalent:\n\u25cf Gawr Gura\nhttps://www.youtube.com/@GawrGura\n\n-----------------------------------------------------------------\n\n\u2605Thumbnail Art: DDOLBANG (\ub618\ubc29) (@DDOLBANG11)\nhttps://x.com/DDOLBANG11\nhttps://www.pixiv.net/en/users/38810706\n\n-----------------------------------------------------------------\n\nSashimi Twitter\nhttps://x.com/Sashimi_Clips\n\n-----------------------------------------------------------------\n\u25c7DOVA-SYNDROME HP\uff1ahttps://dova-s.jp\n#gawrgura\n#hololive\u200b #hololiveEnglish\u200b #holoMyth #shorts",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Sashimi Clips",
                        "playlistId": "UUTEKkDX7lafQVnJrqu55jrA",
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": "video_id_0"
                        },
                        "videoOwnerChannelTitle": "Sashimi Clips",
                        "videoOwnerChannelId": "channel_id_0_full_upd_and_tal"
                    },
                    "contentDetails": {
                        "videoId": "video_id_0",
                        "videoPublishedAt": "2025-05-25T15:00:40Z"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                },
                {
                    "kind": "youtube#playlistItem",
                    "etag": "1SdNpCP6LiUS84wEC-Amp_McFTo",
                    "id": "VVVURUtrRFg3bGFmUVZuSnJxdTU1anJBLnhtWXhEeU9ZM180",
                    "snippet": {
                        "publishedAt": "2025-05-24T16:01:25Z",
                        "channelId": "UCTEKkDX7lafQVnJrqu55jrA",
                        "title": "Why Raora Doesn't Like The Italian Brainrot Meme \u3010Raora Panthra / HololiveEN\u3011",
                        "description": "Check out the Full Stream source:\n\u25c6\u3010HADES\u3011The Gods are watching and I am embarassing myself\u3010#2\u3011\nhttps://www.youtube.com/live/dGVc6mmT5LY?si=UV2eePeZL1iNMfOx\n\nTalent:\n\u25cf Raora Panthera\nhttps://www.youtube.com/@holoen_raorapanthera\n\n-----------------------------------------------------------------\n\n\u2605Thumbnail Art: Gardavwar (@Gardavwar)\nhttps://x.com/Gardavwar\nhttps://www.pixiv.net/en/users/19990655\n\n-----------------------------------------------------------------\n\nSashimi Twitter\nhttps://x.com/Sashimi_Clips\n\n-----------------------------------------------------------------\n\u25c7DOVA-SYNDROME HP\uff1ahttps://dova-s.jp\n\n#hololive\u200b #hololiveEnglish\u200b #holoJustice",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/xmYxDyOY3_4/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/xmYxDyOY3_4/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/xmYxDyOY3_4/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/xmYxDyOY3_4/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/xmYxDyOY3_4/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Sashimi Clips",
                        "playlistId": "UUTEKkDX7lafQVnJrqu55jrA",
                        "position": 1,
                        "resourceId": {
                            "kind": "youtube#channel",
                            "videoId": "video_id_1"
                        },
                        "videoOwnerChannelTitle": "Sashimi Clips",
                        "videoOwnerChannelId": "channel_id_0_full_upd_and_tal"
                    },
                    "contentDetails": {
                        "videoId": "video_id_1",
                        "videoPublishedAt": "2025-05-24T16:01:25Z"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                },
                {
                    "kind": "youtube#playlistItem",
                    "etag": "NmtvEt34eeEZKtsXf3svWskQUMM",
                    "id": "VVVURUtrRFg3bGFmUVZuSnJxdTU1anJBLjFEc3prWkdKV09z",
                    "snippet": {
                        "publishedAt": "2025-05-24T11:30:01Z",
                        "channelId": "UCTEKkDX7lafQVnJrqu55jrA",
                        "title": "Why It Took Almost 4 Years for Ina to Get Her 1 Million Sub Gift \u3010Ninomae Ina'nis  / HololiveEN\u3011",
                        "description": "Check out the Full Stream source:\n\u25c6\u3010CHAT\u3011YUUSHA INA ON DUTY\nhttps://www.youtube.com/live/VWokgqvijRA?si=TQCcr1-f6SeVPtrV\n\nTalent:\n\u25cf Ninomae Ina'nis \nhttps://www.youtube.com/@NinomaeInanis\n\n-----------------------------------------------------------------\n\n\u2605Thumbnail Art: DDOLBANG (\ub618\ubc29) (@DDOLBANG11)\nhttps://x.com/DDOLBANG11\nhttps://www.pixiv.net/en/users/38810706\n\n-----------------------------------------------------------------\n\nSashimi Twitter\nhttps://x.com/Sashimi_Clips\n\n-----------------------------------------------------------------\n\u25c7DOVA-SYNDROME HP\uff1ahttps://dova-s.jp\n\n#hololive\u200b #hololiveEnglish\u200b #holoMyth",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/1DszkZGJWOs/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/1DszkZGJWOs/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/1DszkZGJWOs/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/1DszkZGJWOs/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/1DszkZGJWOs/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Sashimi Clips",
                        "playlistId": "UUTEKkDX7lafQVnJrqu55jrA",
                        "position": 2,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": "video_id_2"
                        },
                        "videoOwnerChannelTitle": "Sashimi Clips",
                        "videoOwnerChannelId": "channel_id_0_full_upd_and_tal"
                    },
                    "contentDetails": {
                        "videoId": "video_id_2",
                        "videoPublishedAt": "2025-05-24T11:30:01Z"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 4432,
                "resultsPerPage": 3
            }
        }

    def tearDown(self) -> None:
        self.cursor.close()
        self.connection.rollback()
        self.connection.close()

    def test_get_new_playlist_items_stop_on_inner_method_fail(self):
        self.playlist_items.next_page_token = 'placeholder_next_page_token'
        self.playlist_items._do_request_and_save = MagicMock(side_effect=[True, True, False])
        self.playlist_items._update_next_page_token = MagicMock()

        try:
            is_success = self.playlist_items.get_new_playlist_items()
        except StopIteration:
            self.fail(msg="didn't stop on _do_request_and_save failure")

        self.assertEqual(3, self.playlist_items._do_request_and_save.call_count, msg='called wrong amount of times')
        self.assertFalse(is_success, msg='should be False to mark unsuccessful run')

    def test_get_new_playlist_items_stop_on_no_next_page_token(self):
        def upd_next_page_token():
            try:
                self.playlist_items.next_page_token = next(page_token_gen)
            except StopIteration:
                self.fail(msg="didn't stop on no next_page_token")

        self.playlist_items._do_request_and_save = MagicMock(return_value=True)
        page_token_gen = (token for token in ['token1', 'token2', None])
        self.playlist_items._update_next_page_token = MagicMock(side_effect=upd_next_page_token)

        is_success = self.playlist_items.get_new_playlist_items()

        self.assertEqual(3, self.playlist_items._do_request_and_save.call_count, msg='called wrong amount of times')
        self.assertEqual(3, self.playlist_items._update_next_page_token.call_count, msg='called wrong amount of times')
        self.assertTrue(is_success, msg='should be True to mark successful run')

    def test__do_request_and_save_success(self):
        def prepare_test_db():
            with self.connection.cursor() as cur:
                setup_test_db.truncate_all(self.connection, cur)
                query = """
                INSERT INTO youtube_channel (
                    channel_info_last_updated,
                    title,
                    added_at,
                    youtube_channel_id,
                    playlist_id
                )
                VALUES (
                    '2024-01-01T00:00:00Z',
                    'channel_5_title',
                    '2024-01-01T00:00:00Z',
                    'channel_id_5',
                    'playlist_id_5'
                );
                """
                cur.execute(query)

        prepare_test_db()
        self.playlist_items.playlist_id = 'playlist_id_5'
        self.playlist_items.response = self.fake_response
        for i in range(len(self.playlist_items.response['items'])):
            self.playlist_items.response['items'][i]['snippet']['channelId'] = 'channel_id_5'
            self.playlist_items.response['items'][i]['snippet']['videoOwnerChannelId'] = 'channel_id_5'
        self.playlist_items._do_request = MagicMock()

        rows_before = self.rows_in_tables_qty()
        is_success = self.playlist_items._do_request_and_save()
        rows_after = self.rows_in_tables_qty()

        self.assertNotEqual(rows_before, rows_after, msg='the qty of rows should be different')
        self.assertTrue(is_success, msg='should be True')
        self.assertEqual(1, rows_after['pir'] - rows_before['pir'],
                         msg='wrong qty of new rows in playlist_items_request table')
        self.assertEqual(2, rows_after['piryv'] - rows_before['piryv'],
                         msg='wrong qty of new rows in playlist_items_request_youtube_video table')
        self.assertEqual(2, rows_after['yv'] - rows_before['yv'],
                         msg='wrong qty of new rows in youtube_video table')

    def test__do_request_and_save_failure(self):
        self.playlist_items.playlist_id = None
        self.playlist_items._set_playlist_id = MagicMock(side_effect=DatabaseError('test case'))
        with self.assertRaises(DatabaseError):
            with self.assertLogs(logger='src.vtc.db_yt_interface', level="ERROR") as cm:
                is_success = self.playlist_items._do_request_and_save()

    def test__set_playlist_id_ongoing(self):
        self.playlist_items._set_playlist_id()
        self.assertEqual('playlist_id_1_parsh_upd_no_tal', self.playlist_items.playlist_id)

    def test__set_playlist_id_not_searched(self):
        # Exclude a row from the db to prepare data
        query = """
        UPDATE youtube_channel
        SET is_other = TRUE
        WHERE youtube_channel_id = 'channel_id_1_parsh_upd_no_tal'
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
            self.connection.commit()

        self.playlist_items._set_playlist_id()
        self.assertEqual('playlist_id_2_no_upd_no_tal', self.playlist_items.playlist_id)

    def test__set_playlist_id_oldest(self):
        query = """
        UPDATE youtube_channel
        SET is_other = TRUE
        WHERE youtube_channel_id IN ('channel_id_1_parsh_upd_no_tal', 'channel_id_2_no_upd_no_tal')
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
        self.playlist_items._set_playlist_id()
        self.assertEqual('playlist_id_0_full_upd_and_tal', self.playlist_items.playlist_id)

    def test__set_playlist_id_only_talents(self):
        self.playlist_items.only_talents = True
        self.playlist_items._set_playlist_id()
        self.assertEqual('playlist_id_0_full_upd_and_tal', self.playlist_items.playlist_id)

    def test__prepare_request(self):
        self.playlist_items._prepare_request()
        self.assertNotEqual(None, self.playlist_items.api_key)

    def test__update_quota_after_request(self):
        self.playlist_items._prepare_request()
        quota_before = self.playlist_items.api_service.get_quota_left(self.playlist_items.api_key)
        self.playlist_items._update_quota_after_request()
        quota_after = self.playlist_items.api_service.get_quota_left(self.playlist_items.api_key)
        quota_change = quota_before - quota_after
        self.assertEqual(1, quota_change)

    def test__filter_response(self):
        self.playlist_items.response = self.fake_response
        items_before = len(self.playlist_items.response['items'])
        self.playlist_items._filter_response()
        items_after = len(self.playlist_items.response['items'])
        items_change = items_before - items_after
        self.assertEqual(1, items_change)

    def test__update_next_page_token_none(self):
        self.playlist_items.playlist_id = 'playlist_id_2_no_upd_no_tal'
        self.playlist_items._update_next_page_token()
        self.assertEqual(None, self.playlist_items.next_page_token)

    def test__update_next_page_token_not_none(self):
        self.playlist_items.playlist_id = 'playlist_id_1_parsh_upd_no_tal'
        self.playlist_items._update_next_page_token()
        self.assertEqual('playlist_id_1_next_page_token_0', self.playlist_items.next_page_token)

    def test__save_commit(self):
        """Test if changes are properly saved and committed to the db"""
        self.playlist_items.response = self.fake_response
        self.playlist_items.response['items'][0]['snippet']['resourceId']['videoId'] = 'video_id_3'
        self.playlist_items.response['items'][1]['snippet']['resourceId']['videoId'] = 'video_id_4'
        self.playlist_items.response['items'][2]['snippet']['resourceId']['videoId'] = 'video_id_5'
        self.playlist_items.playlist_id = 'playlist_id_1_parsh_upd_no_tal'
        rows_before = self.rows_in_tables_qty()

        self.playlist_items._save()

        rows_after = self.rows_in_tables_qty()

        self.assertEqual(1, rows_after['pir'] - rows_before['pir'],
                         msg='wrong qty of new rows in playlist_items_request table')
        self.assertEqual(3, rows_after['piryv'] - rows_before['piryv'],
                         msg='wrong qty of new rows in playlist_items_request_youtube_video table')
        self.assertEqual(3, rows_after['yv'] - rows_before['yv'],
                         msg='wrong qty of new rows in youtube_video table')

    def test__save_rollback(self):
        """Test if changes are properly rolled back"""
        self.playlist_items.response = self.fake_response
        self.playlist_items.response['items'][0]['snippet']['resourceId']['videoId'] = 'video_id_3'
        self.playlist_items.response['items'][1]['snippet']['resourceId']['videoId'] = 'video_id_4'
        self.playlist_items.response['items'][2]['snippet']['resourceId']['videoId'] = 'video_id_5'
        self.playlist_items.playlist_id = 'playlist_id_1_parsh_upd_no_tal'
        rows_before = self.rows_in_tables_qty()

        self.playlist_items._save_youtube_video = MagicMock(side_effect=DatabaseError(""))
        with self.assertLogs(logger='src.vtc.db_yt_interface', level="ERROR") as cm:
            self.playlist_items._save()

        rows_after = self.rows_in_tables_qty()

        self.assertEqual(0, rows_after['pir'] - rows_before['pir'],
                         msg='wrong qty of new rows in playlist_items_request table')
        self.assertEqual(0, rows_after['piryv'] - rows_before['piryv'],
                         msg='wrong qty of new rows in playlist_items_request_youtube_video table')
        self.assertEqual(0, rows_after['yv'] - rows_before['yv'],
                         msg='wrong qty of new rows in youtube_video table')

    def test__save_playlist_items_request(self):
        self.playlist_items.response = self.fake_response
        self.playlist_items.playlist_id = 'playlist_save_playlist_items_request'
        self.playlist_items.datetime_now = datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        self.playlist_items.max_results = 50

        query_channel_setup = """
        INSERT INTO youtube_channel (
        channel_info_last_updated,
        title,
        added_at,
        youtube_channel_id,
        playlist_id
        )
        VALUES (%s, %s, %s, %s, %s);
        """
        values_channel_setup = [
            datetime.datetime(2024, 1, 1, 0, 0, 0),
            'title_save_playlist_items_request',
            datetime.datetime(2024, 1, 1, 0, 0, 0),
            'channel_save_playlist_items_request',
            self.playlist_items.playlist_id
            ]

        with self.connection.cursor() as cur:
            cur.execute(query_channel_setup, values_channel_setup)
        self.connection.commit()

        self.playlist_items._save_playlist_items_request()

        query_test = """
        SELECT
            playlist_id,
            requested_at,
            max_results,
            total_results,
            results_per_page,
            prev_page_token,
            next_page_token,
            etag
        FROM playlist_items_request
        ORDER BY playlist_items_request_id DESC
        LIMIT 1;
        """
        with self.connection.cursor() as cur:
            cur.execute(query_test)
            row = cur.fetchone()
        self.assertEqual(self.playlist_items.playlist_id, row[0], msg='wrong playlist id')
        self.assertEqual(self.playlist_items.datetime_now, row[1], msg='wrong request time')
        self.assertEqual(self.playlist_items.max_results, row[2], msg='wrong max results')
        self.assertEqual(self.playlist_items.response['pageInfo']['totalResults'], row[3], msg='wrong total results')
        self.assertEqual(self.playlist_items.response['pageInfo']['resultsPerPage'], row[4], msg='wrong results qty')
        self.assertEqual(None, row[5], msg='wrong prev page token')
        self.assertEqual(self.playlist_items.response['nextPageToken'], row[6], msg='wrong next page token')
        self.assertEqual(self.playlist_items.response['etag'], row[7], msg='wrong etag')

    def test__save_playlist_items_request_youtube_video(self):
        self.playlist_items.response = self.fake_response
        self.playlist_items.playlist_items_request_id = 1
        video_ids = ['video_id_0', 'video_id_1', 'video_id_2']
        self.playlist_items._save_playlist_items_request_youtube_video()

        query = """
        SELECT playlist_items_request_id, youtube_video_id
        FROM playlist_items_request_youtube_video
        ORDER BY youtube_video_id ASC;
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.assertEqual((self.playlist_items.playlist_items_request_id, video_ids[0]), rows[0], msg='wrong row 0')
        self.assertEqual((self.playlist_items.playlist_items_request_id, video_ids[1]), rows[1], msg='wrong row 1')
        self.assertEqual((self.playlist_items.playlist_items_request_id, video_ids[2]), rows[2], msg='wrong row 2')

    def test__save_youtube_video(self):
        channel_id = 'channel_id_0_full_upd_and_tal'
        self.playlist_items.datetime_now = datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        self.playlist_items.response = {
            "kind": "youtube#playlistItemListResponse",
            "etag": "GNPrWxCKsLNrFefUvZJrwcqWsV8",
            "nextPageToken": "EAAaHlBUOkNBVWlFRE0zTTBSRU1FUXdRekkwTnpjMk9URQ",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "fhZ-UPviRH2-h4-QH_9OvpTrIlk",
                    "id": "VVVURUtrRFg3bGFmUVZuSnJxdTU1anJBLlBKVHFCNFRQZG4w",
                    "snippet": {
                        "publishedAt": "2025-05-25T15:00:40Z",
                        "channelId": "UCTEKkDX7lafQVnJrqu55jrA",
                        "title": "Gura Was This Close to Working for Children's Television",
                        "description": "Check out the Full Stream source:\n\u25c6\u3010POWERWASH SIMULATOR\u3011time for your bath, stinklord\nhttps://www.youtube.com/live/Jvvc3nc_TPw?si=ckJmAU1nxgGRvIwD\n\nTalent:\n\u25cf Gawr Gura\nhttps://www.youtube.com/@GawrGura\n\n-----------------------------------------------------------------\n\n\u2605Thumbnail Art: DDOLBANG (\ub618\ubc29) (@DDOLBANG11)\nhttps://x.com/DDOLBANG11\nhttps://www.pixiv.net/en/users/38810706\n\n-----------------------------------------------------------------\n\nSashimi Twitter\nhttps://x.com/Sashimi_Clips\n\n-----------------------------------------------------------------\n\u25c7DOVA-SYNDROME HP\uff1ahttps://dova-s.jp\n#gawrgura\n#hololive\u200b #hololiveEnglish\u200b #holoMyth #shorts",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/PJTqB4TPdn0/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Sashimi Clips",
                        "playlistId": "UUTEKkDX7lafQVnJrqu55jrA",
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": "video_id_3"
                        },
                        "videoOwnerChannelTitle": "Sashimi Clips",
                        "videoOwnerChannelId": "channel_id_0_full_upd_and_tal"
                    },
                    "contentDetails": {
                        "videoId": "video_id_3",
                        "videoPublishedAt": "2025-05-25T15:00:40Z"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 4432,
                "resultsPerPage": 1
            }
        }
        self.playlist_items._save_youtube_video()

        query = """
        SELECT
            youtube_video_id,
            youtube_channel_id,
            published_at,
            updated_at,
            added_at
        FROM youtube_video;
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        saved_row = next(row for row in rows if row[0] == 'video_id_3')
        source_item = next(item for item in self.playlist_items.response['items'] if item['snippet']['resourceId']['videoId'] == 'video_id_3')
        self.assertEqual(4, len(rows), msg='wrong row qty')
        self.assertEqual(source_item['snippet']['resourceId']['videoId'], saved_row[0], msg='wrong youtube_video_id')
        self.assertEqual(source_item['snippet']['videoOwnerChannelId'], saved_row[1], msg='wrong youtube_channel_id')
        self.assertEqual(
            datetime.datetime.fromisoformat(source_item['contentDetails']['videoPublishedAt'].replace('Z', '+00:00')),
            saved_row[2],
            msg='wrong published_at'
        )
        self.assertEqual(self.playlist_items.datetime_now, saved_row[3], msg='wrong updated_at')
        self.assertEqual(self.playlist_items.datetime_now, saved_row[4], msg='wrong added_at')

    # def _do_request(self):
    # def _update_datetime_now(self):

if __name__ == 'main':
    unittest.main()
