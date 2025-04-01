import unittest
import datetime
from unittest.mock import patch, ANY, MagicMock
import json
import os
from contextlib import ExitStack

from vtc import connect_to_db, db_yt_interface
from vtc.db_yt_interface import PrepareAPI
from tests.fixtures import setup_test_db


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
    @patch('vtc.db_yt_interface.datetime', wraps=datetime)
    def setUpClass(cls, mock_datetime) -> None:
        mock_datetime.datetime.now.return_value = datetime.datetime(
            2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
        setup_test_db.reset_for_map()

        connection = connect_to_db.connect_to_test_db()
        instance = db_yt_interface.SearchYTByKeyword(
            connection=connection,
            api_service=PrepareAPI(filepath='../data/test_api_quota_state.json', delay=False)
        )
        instance.set_search_map()
        connect_to_db.connection_close(connection)

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
        with connect_to_db.connect_to_test_db() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            actual = cursor.fetchall()
        return actual

    @classmethod
    @patch('vtc.db_yt_interface.datetime', wraps=datetime)
    def setUpClass(cls, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime(
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
        connection = connect_to_db.connect_to_test_db()
        search_instance = db_yt_interface.SearchYTByKeyword(
            connection=connection,
            api_service=PrepareAPI(filepath='../data/test_api_quota_state.json', delay=False)
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
        connect_to_db.connection_close(connection)

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
                "UC58YRkZ2cMedl0AVv_rNoZw"  # YT channel id
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
                "UCAnUBKzIF_oR4yNUfqIkCqw"  # YT channel id
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
                "Kronii Laughing so Hard at Her Own Flower Building in Minecraft [Kaela/Kronii]",  # title
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
                None,  # description_full
                "youtube#video",  # kind
                "https://i.ytimg.com/vi/XD0p0Dj0LXc/default.jpg",  # thumbnail_default_url
                120,  # thumbnail_default_width
                90,  # thumbnail_default_height
                "https://i.ytimg.com/vi/XD0p0Dj0LXc/mqdefault.jpg",  # thumbnail_medium_url
                320,  # thumbnail_medium_width
                180,  # thumbnail_medium_height
                "https://i.ytimg.com/vi/XD0p0Dj0LXc/hqdefault.jpg",  # thumbnail_high_url
                480,  # thumbnail_high_width
                360,  # thumbnail_high_height
                None,  # tags
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at
            ),
            (
                "IwhkBhUH0lc",  # youtube_video_id
                "UCAnUBKzIF_oR4yNUfqIkCqw",  # youtube_channel_id
                None,  # duration
                None,  # actual_start_time
                None,  # actual_end_time
                None,  # scheduled_start_time
                datetime.datetime.fromisoformat("2024-08-08T17:06:06+00:00"),  # published_at
                "Ame and Ina Can&#39;t Stop Teasing Kronii~ (Hololive)",  # title
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
                None,  # description_full
                "youtube#video",  # kind
                "https://i.ytimg.com/vi/IwhkBhUH0lc/default.jpg",  # thumbnail_default_url
                120,  # thumbnail_default_width
                90,  # thumbnail_default_height
                "https://i.ytimg.com/vi/IwhkBhUH0lc/mqdefault.jpg",  # thumbnail_medium_url
                320,  # thumbnail_medium_width
                180,  # thumbnail_medium_height
                "https://i.ytimg.com/vi/IwhkBhUH0lc/hqdefault.jpg",  # thumbnail_high_url
                480,  # thumbnail_high_width
                360,  # thumbnail_high_height
                None,  # tags
                datetime.datetime(2024, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc),  # added_at

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
        filepath = "../data/test_api_quota_state.json"
        self.quotas_test_values = {
            "API_key0": {
                "max": 10000,
                "available": 5500,
                "reserve": 4500
            },
            "API_key1": {
                "max": 10000,
                "available": 3100,
                "reserve": 6900
            },
            "API_key2": {
                "max": 10000,
                "available": 7800,
                "reserve": 2200
            }
        }
        file_content = {
            "API_quotas": self.quotas_test_values,
            "last_reset_at": "2024-01-01T07:00:00+00:00",
            "last_update_at": "2024-01-01T01:00:00+00:00"
        }
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(file_content, file)
        with patch.dict(os.environ, {'API_keys': 'key0,key1,key2'}):
            with patch.object(
                    PrepareAPI,
                    "current_time_utc",
                    return_value=datetime.datetime.fromisoformat("2024-01-01T07:00:00+00:00")
            ):
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

    def test_get_api_key(self):
        self.instance.api_quotas = {
            "API_key0": {
                "max": 10000,
                "available": 5500,
                "reserve": 4500
            },
            "API_key1": {
                "max": 10000,
                "available": 100,
                "reserve": 6900
            },
            "API_key2": {
                "max": 10000,
                "available": 10,
                "reserve": 2200
            }
        }
        expected = "key1"
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
                    "reserve": 4500
                },
                "API_key1": {
                    "max": 10000,
                    "available": 3100,
                    "reserve": 6900
                },
                "API_key2": {
                    "max": 10000,
                    "available": 7300,
                    "reserve": 2200
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
                    "reserve": 4500
                },
                "API_key1": {
                    "max": 10000,
                    "available": 3100,
                    "reserve": 6900
                },
                "API_key2": {
                    "max": 10000,
                    "available": 7300,
                    "reserve": 2200
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
        cls.connection = connect_to_db.connect_to_test_db()
        cls.instance = db_yt_interface.SearchYTByKeyword(
            cls.connection,
            api_service=PrepareAPI(filepath='../data/test_api_quota_state.json', delay=False)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        connect_to_db.connection_close(cls.connection)

    def test_calculate_search_interval_first_search(self):
        date = datetime.datetime.fromisoformat('2025-01-01 00:00:00+00:00')
        keyword = 'keyword_10'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=1, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_pre_debut_full(self):
        date = datetime.datetime.fromisoformat('2023-12-03 00:00:00+00:00')
        keyword = 'keyword_1'
        interval = self.instance.calculate_search_interval(keyword, date)
        self.assertEqual(datetime.timedelta(days=6, hours=23, minutes=59, seconds=59), interval)

    def test_calculate_search_interval_pre_debut_short(self):
        date = datetime.datetime.fromisoformat('2023-12-30 00:00:00+00:00')
        keyword = 'keyword_2'
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
        cls.connection = connect_to_db.connect_to_test_db()
        cls.cursor = cls.connection.cursor()
        cls.instance = db_yt_interface.SearchYTByKeyword(
            cls.connection,
            api_service=PrepareAPI(filepath='../data/test_api_quota_state.json', delay=False)
        )
        while True:
            success = cls.instance.subsearch_next_and_save()
            if not success:
                break

    @classmethod
    def tearDownClass(cls) -> None:
        cls.cursor.execute('TRUNCATE TABLE search_yt CASCADE;')
        cls.cursor.close()
        connect_to_db.connection_close(cls.connection)

    def setUp(self) -> None:
        self.cursor.execute('TRUNCATE TABLE search_yt CASCADE;')

    def test_subsearch_no_subsearch(self):
        search_ids = ['search_3', ]
        subsearch_ids = []
        self.populate_search_yt(search_ids, subsearch_ids)
        self.instance.set_subsearch_map()
        self.instance.prepare_subsearch_query()

        self.assertEqual(datetime.datetime.fromisoformat('2025-01-10 00:00:00+00:00'), self.instance.published_after)
        self.assertEqual(datetime.datetime.fromisoformat('2025-01-10 23:59:59+00:00'), self.instance.published_before)

    def test_subsearch_one_subsearch(self):
        search_ids = ['search_2', ]
        subsearch_ids = ['search_2_subsearch_1', ]
        self.populate_search_yt(search_ids, subsearch_ids)
        self.instance.set_subsearch_map()
        self.instance.prepare_subsearch_query()

        self.assertEqual(datetime.datetime.fromisoformat('2025-01-11 00:00:00+00:00'), self.instance.published_after)
        self.assertEqual(datetime.datetime.fromisoformat('2025-01-11 23:59:59+00:00'), self.instance.published_before)

    def test_subsearch_two_subsearches(self):
        search_ids = ['search_1', ]
        subsearch_ids = ['search_1_subsearch_1', 'search_1_subsearch_2', ]
        self.populate_search_yt(search_ids, subsearch_ids)
        success = self.instance.set_subsearch_map()
        self.assertFalse(success, 'Should not create map under those conditions')

    def test_subsearch_order(self):
        search_ids = ['search_3', 'search_2', ]
        subsearch_ids = ['search_2_subsearch_1', ]
        self.populate_search_yt(search_ids, subsearch_ids)
        self.instance.set_subsearch_map()
        self.instance.prepare_subsearch_query()

        self.assertEqual(datetime.datetime.fromisoformat('2025-01-11 00:00:00+00:00'), self.instance.published_after)
        self.assertEqual(datetime.datetime.fromisoformat('2025-01-11 23:59:59+00:00'), self.instance.published_before)


if __name__ == 'main':
    unittest.main()
