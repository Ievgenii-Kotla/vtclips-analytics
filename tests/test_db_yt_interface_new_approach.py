"""
Tests for the db_yt_interface module.
Uses a better approach to writing tests. Cleaner and easier to read.

"""

import unittest
from unittest.mock import patch, MagicMock
import datetime
from dotenv import load_dotenv

from src.vtc import db_yt_interface
from src.vtc.db_yt_interface import PrepareAPI
import db_helpers

load_dotenv("../.env.test")


class TestSearchYTByKeywordMisc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db_helpers.connect_to_test_db()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        self.search = db_yt_interface.SearchYTByKeyword(
            connection=self.conn,
            api_service=PrepareAPI(filepath='../state/test_api_quota_state.json', delay=False)
        )

    def test_prepare_subsearch_query_one_subsearch(self):
        db_helpers.insert_youtube_channel(self.conn)
        db_helpers.insert_search_yt(self.conn)
        for i in range(1, 51):
            db_helpers.insert_youtube_video(
                self.conn,
                youtube_video_id=f'video_id_{i}',
                published_at=datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
                             + datetime.timedelta(days=i-1),
            )
            db_helpers.insert_search_yt_youtube_video(self.conn, youtube_video_id=f'video_id_{i}')

        self.search.subsearch_map = [
            (
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 2, 20, 23, 59, 59, tzinfo=datetime.timezone.utc),
                'keyword',
                'US',
                1,
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 25, 23, 59, 59, tzinfo=datetime.timezone.utc),
                1,
                True
            ),
        ]
        expected_start = datetime.datetime(2025, 1, 26, 0, 0, 0, tzinfo=datetime.timezone.utc)
        expected_end = datetime.datetime(2025, 2, 20, 23, 59, 59, tzinfo=datetime.timezone.utc)

        self.search.prepare_subsearch_query()

        self.assertEqual(expected_start, self.search.published_after.astimezone(datetime.timezone.utc))
        self.assertEqual(expected_end, self.search.published_before.astimezone(datetime.timezone.utc))

    def test_prepare_subsearch_query_zero_subsearch(self):
        db_helpers.insert_youtube_channel(self.conn)
        db_helpers.insert_search_yt(self.conn)
        for i in range(1, 51):
            db_helpers.insert_youtube_video(
                self.conn,
                youtube_video_id=f'video_id_{i}',
                published_at=datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
                             + datetime.timedelta(days=i-1),
            )
            db_helpers.insert_search_yt_youtube_video(self.conn, youtube_video_id=f'video_id_{i}')

        self.search.subsearch_map = [
            (
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 2, 20, 23, 59, 59, tzinfo=datetime.timezone.utc),
                'keyword',
                'US',
                1,
                0,
                None,
                None,
                1,
                True
            ),
        ]
        expected_start = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        expected_end = datetime.datetime(2025, 1, 25, 23, 59, 59, tzinfo=datetime.timezone.utc)

        self.search.prepare_subsearch_query()

        self.assertEqual(expected_start, self.search.published_after.astimezone(datetime.timezone.utc))
        self.assertEqual(expected_end, self.search.published_before.astimezone(datetime.timezone.utc))

    def test_prepare_subsearch_query_search_with_no_videos_zero_subsearch(self):
        db_helpers.insert_search_yt(self.conn)
        self.search.subsearch_map = [
            (
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 2, 23, 59, 59, tzinfo=datetime.timezone.utc),
                'keyword',
                'US',
                1,
                0,
                None,
                None,
                1,
                True
            ),
        ]
        expected_start = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        expected_end = datetime.datetime(2025, 1, 1, 23, 59, 59, tzinfo=datetime.timezone.utc)
        self.search.prepare_subsearch_query()

        self.assertEqual(expected_start, self.search.published_after.astimezone(datetime.timezone.utc))
        self.assertEqual(expected_end, self.search.published_before.astimezone(datetime.timezone.utc))

    def test_prepare_subsearch_query_search_with_no_videos_one_subsearch(self):
        db_helpers.insert_search_yt(self.conn)
        self.search.subsearch_map = [
            (
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 2, 23, 59, 59, tzinfo=datetime.timezone.utc),
                'keyword',
                'US',
                1,
                1,
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 1, 23, 59, 59, tzinfo=datetime.timezone.utc),
                1,
                True
            ),
        ]
        expected_start = datetime.datetime(2025, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
        expected_end = datetime.datetime(2025, 1, 2, 23, 59, 59, tzinfo=datetime.timezone.utc)
        self.search.prepare_subsearch_query()

        self.assertEqual(expected_start, self.search.published_after.astimezone(datetime.timezone.utc))
        self.assertEqual(expected_end, self.search.published_before.astimezone(datetime.timezone.utc))

    @patch('src.vtc.db_yt_interface.time.sleep')
    def test_prepare_subsearch_query_invalid_boundaries(self, mock_sleep):
        db_helpers.insert_search_yt(self.conn)
        self.search.subsearch_map = [
            (
                1,
                datetime.datetime(2025, 1, 2, 23, 59, 59, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                'keyword',
                'US',
                1,
                0,
                None,
                None,
                1,
                True
            ),
        ]
        with self.assertLogs(logger='src.vtc.db_yt_interface', level="ERROR") as cm:
            self.search.prepare_subsearch_query()


    @patch('src.vtc.db_yt_interface.PrepareAPI.get_quota_left')
    @patch('src.vtc.db_yt_interface.PrepareAPI.change_quota')
    @patch('src.vtc.db_yt_interface.PrepareAPI.get_api_key')
    @patch('src.vtc.db_yt_interface.build')
    def test_filter_response_1_relevant_title(
            self, mock_build, mock_get_api_key, mock_change_quota, mock_get_quota_left):

        fake_response_data = {
            "kind": "youtube#videoListResponse",
            "etag": "YKyBruZycggREVDQ9AIKVbNzly0",
            "items": [
                {
                    "kind": "youtube#video",
                    "etag": "u0Ewqzjm6xmbl5iUrazekqaMU9w",
                    "id": "-XRR-a6u7Ec",
                    "snippet": {
                        "publishedAt": "2020-11-19T05:05:01Z",
                        "channelId": "UC3gXLkh5SFIqGeKdaXtdrGg",
                        "title": "title test_keyword",
                        "description": "description",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Hunterreach",
                        "tags": [
                            "tag1",
                            "tag2"
                        ],
                        "categoryId": "1",
                        "liveBroadcastContent": "none",
                        "localized": {
                            "title": "loc title",
                            "description": "loc description"
                        },
                        "defaultAudioLanguage": "en"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.search.response = {
            "kind": "youtube#searchListResponse",
            "etag": "E8I1zVexC-aShpujQa2N-HM_Tw8",
            "regionCode": "US",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            },
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "xNFddJH8Yfz_1AfZZePk77LedRI",
                    "id": {
                        "kind": "youtube#video",
                        "videoId": "-XRR-a6u7Ec"
                    },
                    "snippet": {
                        "publishedAt": "2024-07-06T10:00:00Z",
                        "channelId": "UCgnfPPb9JI3e9A4cXHnWbyg",
                        "title": "talk",
                        "description": "desc",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            }
                        },
                        "channelTitle": "hololive-EN",
                        "liveBroadcastContent": "none",
                        "publishTime": "2024-07-06T10:00:00Z"
                    }
                }
            ]
        }
        self.search.search_query = "test_keyword"
        youtube_mock = mock_build.return_value
        youtube_mock.videos().list().execute.return_value = fake_response_data

        self.search.filter_response()
        self.assertEqual(1, len(self.search.response["items"]), "Should be 1 relevant video")

    @patch('src.vtc.db_yt_interface.PrepareAPI.get_quota_left')
    @patch('src.vtc.db_yt_interface.PrepareAPI.change_quota')
    @patch('src.vtc.db_yt_interface.PrepareAPI.get_api_key')
    @patch('src.vtc.db_yt_interface.build')
    def test_filter_response_1_relevant_description(
            self, mock_build, mock_get_api_key, mock_change_quota, mock_get_quota_left):

        fake_response_data = {
            "kind": "youtube#videoListResponse",
            "etag": "YKyBruZycggREVDQ9AIKVbNzly0",
            "items": [
                {
                    "kind": "youtube#video",
                    "etag": "u0Ewqzjm6xmbl5iUrazekqaMU9w",
                    "id": "-XRR-a6u7Ec",
                    "snippet": {
                        "publishedAt": "2020-11-19T05:05:01Z",
                        "channelId": "UC3gXLkh5SFIqGeKdaXtdrGg",
                        "title": "title",
                        "description": "description test_keyword",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Hunterreach",
                        "tags": [
                            "tag1",
                            "tag2"
                        ],
                        "categoryId": "1",
                        "liveBroadcastContent": "none",
                        "localized": {
                            "title": "loc title",
                            "description": "loc description"
                        },
                        "defaultAudioLanguage": "en"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.search.response = {
            "kind": "youtube#searchListResponse",
            "etag": "E8I1zVexC-aShpujQa2N-HM_Tw8",
            "regionCode": "US",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            },
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "xNFddJH8Yfz_1AfZZePk77LedRI",
                    "id": {
                        "kind": "youtube#video",
                        "videoId": "-XRR-a6u7Ec"
                    },
                    "snippet": {
                        "publishedAt": "2024-07-06T10:00:00Z",
                        "channelId": "UCgnfPPb9JI3e9A4cXHnWbyg",
                        "title": "talk",
                        "description": "desc",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            }
                        },
                        "channelTitle": "hololive-EN",
                        "liveBroadcastContent": "none",
                        "publishTime": "2024-07-06T10:00:00Z"
                    }
                }
            ]
        }
        self.search.search_query = "test_keyword"
        youtube_mock = mock_build.return_value
        youtube_mock.videos().list().execute.return_value = fake_response_data

        self.search.filter_response()
        self.assertEqual(1, len(self.search.response["items"]), "Should be 1 relevant video")

    @patch('src.vtc.db_yt_interface.PrepareAPI.get_quota_left')
    @patch('src.vtc.db_yt_interface.PrepareAPI.change_quota')
    @patch('src.vtc.db_yt_interface.PrepareAPI.get_api_key')
    @patch('src.vtc.db_yt_interface.build')
    def test_filter_response_1_relevant_tag(
            self, mock_build, mock_get_api_key, mock_change_quota, mock_get_quota_left):

        fake_response_data = {
            "kind": "youtube#videoListResponse",
            "etag": "YKyBruZycggREVDQ9AIKVbNzly0",
            "items": [
                {
                    "kind": "youtube#video",
                    "etag": "u0Ewqzjm6xmbl5iUrazekqaMU9w",
                    "id": "-XRR-a6u7Ec",
                    "snippet": {
                        "publishedAt": "2020-11-19T05:05:01Z",
                        "channelId": "UC3gXLkh5SFIqGeKdaXtdrGg",
                        "title": "title",
                        "description": "description",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Hunterreach",
                        "tags": [
                            "tag1 test_keyword",
                            "tag2"
                        ],
                        "categoryId": "1",
                        "liveBroadcastContent": "none",
                        "localized": {
                            "title": "loc title",
                            "description": "loc description"
                        },
                        "defaultAudioLanguage": "en"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.search.response = {
            "kind": "youtube#searchListResponse",
            "etag": "E8I1zVexC-aShpujQa2N-HM_Tw8",
            "regionCode": "US",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            },
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "xNFddJH8Yfz_1AfZZePk77LedRI",
                    "id": {
                        "kind": "youtube#video",
                        "videoId": "-XRR-a6u7Ec"
                    },
                    "snippet": {
                        "publishedAt": "2024-07-06T10:00:00Z",
                        "channelId": "UCgnfPPb9JI3e9A4cXHnWbyg",
                        "title": "talk",
                        "description": "desc",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            }
                        },
                        "channelTitle": "hololive-EN",
                        "liveBroadcastContent": "none",
                        "publishTime": "2024-07-06T10:00:00Z"
                    }
                }
            ]
        }
        self.search.search_query = "test_keyword"
        youtube_mock = mock_build.return_value
        youtube_mock.videos().list().execute.return_value = fake_response_data

        self.search.filter_response()
        self.assertEqual(1, len(self.search.response["items"]), "Should be 1 relevant video")

    @patch('src.vtc.db_yt_interface.PrepareAPI.get_quota_left')
    @patch('src.vtc.db_yt_interface.PrepareAPI.change_quota')
    @patch('src.vtc.db_yt_interface.PrepareAPI.get_api_key')
    @patch('src.vtc.db_yt_interface.build')
    def test_filter_response_0_relevant_tag(
            self, mock_build, mock_get_api_key, mock_change_quota, mock_get_quota_left):

        fake_response_data = {
            "kind": "youtube#videoListResponse",
            "etag": "YKyBruZycggREVDQ9AIKVbNzly0",
            "items": [
                {
                    "kind": "youtube#video",
                    "etag": "u0Ewqzjm6xmbl5iUrazekqaMU9w",
                    "id": "-XRR-a6u7Ec",
                    "snippet": {
                        "publishedAt": "2020-11-19T05:05:01Z",
                        "channelId": "UC3gXLkh5SFIqGeKdaXtdrGg",
                        "title": "title",
                        "description": "description",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Hunterreach",
                        "tags": [
                            "tag1",
                            "tag2"
                        ],
                        "categoryId": "1",
                        "liveBroadcastContent": "none",
                        "localized": {
                            "title": "loc title",
                            "description": "loc description"
                        },
                        "defaultAudioLanguage": "en"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.search.response = {
            "kind": "youtube#searchListResponse",
            "etag": "E8I1zVexC-aShpujQa2N-HM_Tw8",
            "regionCode": "US",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            },
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "xNFddJH8Yfz_1AfZZePk77LedRI",
                    "id": {
                        "kind": "youtube#video",
                        "videoId": "-XRR-a6u7Ec"
                    },
                    "snippet": {
                        "publishedAt": "2024-07-06T10:00:00Z",
                        "channelId": "UCgnfPPb9JI3e9A4cXHnWbyg",
                        "title": "talk",
                        "description": "desc",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            }
                        },
                        "channelTitle": "hololive-EN",
                        "liveBroadcastContent": "none",
                        "publishTime": "2024-07-06T10:00:00Z"
                    }
                }
            ]
        }
        self.search.search_query = "test_keyword"
        youtube_mock = mock_build.return_value
        youtube_mock.videos().list().execute.return_value = fake_response_data

        self.search.filter_response()
        self.assertEqual(0, len(self.search.response["items"]), "Should be 0 relevant videos")


    @patch('src.vtc.db_yt_interface.PrepareAPI.get_quota_left')
    @patch('src.vtc.db_yt_interface.PrepareAPI.change_quota')
    @patch('src.vtc.db_yt_interface.PrepareAPI.get_api_key')
    @patch('src.vtc.db_yt_interface.build')
    def test_filter_response_add_full_description(
            self, mock_build, mock_get_api_key, mock_change_quota, mock_get_quota_left):

        fake_response_data = {
            "kind": "youtube#videoListResponse",
            "etag": "YKyBruZycggREVDQ9AIKVbNzly0",
            "items": [
                {
                    "kind": "youtube#video",
                    "etag": "u0Ewqzjm6xmbl5iUrazekqaMU9w",
                    "id": "-XRR-a6u7Ec",
                    "snippet": {
                        "publishedAt": "2020-11-19T05:05:01Z",
                        "channelId": "UC3gXLkh5SFIqGeKdaXtdrGg",
                        "title": "title",
                        "description": "full description test_keyword",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/sddefault.jpg",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "https://i.ytimg.com/vi/AUzLpfUy_bI/maxresdefault.jpg",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "Hunterreach",
                        "tags": [
                            "tag1",
                            "tag2"
                        ],
                        "categoryId": "1",
                        "liveBroadcastContent": "none",
                        "localized": {
                            "title": "loc title",
                            "description": "loc description"
                        },
                        "defaultAudioLanguage": "en"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.search.response = {
            "kind": "youtube#searchListResponse",
            "etag": "E8I1zVexC-aShpujQa2N-HM_Tw8",
            "regionCode": "US",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            },
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "xNFddJH8Yfz_1AfZZePk77LedRI",
                    "id": {
                        "kind": "youtube#video",
                        "videoId": "-XRR-a6u7Ec"
                    },
                    "snippet": {
                        "publishedAt": "2024-07-06T10:00:00Z",
                        "channelId": "UCgnfPPb9JI3e9A4cXHnWbyg",
                        "title": "talk",
                        "description": "trimmed description",
                        "thumbnails": {
                            "default": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/default.jpg",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/mqdefault.jpg",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "https://i.ytimg.com/vi/-XRR-a6u7Ec/hqdefault.jpg",
                                "width": 480,
                                "height": 360
                            }
                        },
                        "channelTitle": "hololive-EN",
                        "liveBroadcastContent": "none",
                        "publishTime": "2024-07-06T10:00:00Z"
                    }
                }
            ]
        }
        self.search.search_query = "test_keyword"
        youtube_mock = mock_build.return_value
        youtube_mock.videos().list().execute.return_value = fake_response_data

        self.search.filter_response()
        self.assertEqual("full description test_keyword", self.search.response["items"][0]["snippet"]["full_description"],
                         "'full_description' key should be created and populated'")


    def test_set_search_map_with_cooldown(self):
        db_helpers.insert_keyword(self.conn)
        db_helpers.insert_talent(self.conn)
        db_helpers.insert(self.conn, 'keyword_talent', keyword_id=1, talent_id=1)
        self.search.start_search_datetime = datetime.datetime.now() - datetime.timedelta(hours=12)
        self.search.end_search_datetime = datetime.datetime.now()
        self.search.priority = (1000,)
        self.search.set_search_map()
        self.assertEqual([], self.search.search_map, "Should be empty")

    def test_set_search_map_no_cooldown(self):
        db_helpers.insert_keyword(self.conn)
        db_helpers.insert_talent(self.conn)
        db_helpers.insert(self.conn, 'keyword_talent', keyword_id=1, talent_id=1)
        self.search.end_search_datetime = datetime.datetime.now()
        self.search.priority = (1000,)
        self.search.set_search_map()
        self.assertEqual(1, len(self.search.search_map), "Should have 1 search_period")


class TestPlaylistItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db_helpers.connect_to_test_db()
        with cls.conn.cursor() as cur:
            cur.execute("SET TIME ZONE UTC")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        self.playlist_items = db_yt_interface.PlaylistItems(
            connection=self.conn,
            only_talents=False,
            api_service=db_yt_interface.PrepareAPI(filepath='../state/test_api_quota_state.json'),
            cooldown_period=datetime.timedelta(days=0))
        self.playlist_items.response = {
            "kind": "youtube#playlistItemListResponse",
            "etag": "playlist_items_list_etag",
            "nextPageToken": "next_page_token",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "playlist_item_etag",
                    "id": "playlist_item_id",
                    "snippet": {
                        "publishedAt": "2025-01-01T00:00:01Z",
                        "channelId": "channel_id",
                        "title": "playlist_item_title",
                        "description": "playlist_item_description",
                        "thumbnails": {
                            "default": {
                                "url": "url_default",
                                "width": 120,
                                "height": 90
                            },
                            "medium": {
                                "url": "url_medium",
                                "width": 320,
                                "height": 180
                            },
                            "high": {
                                "url": "url_high",
                                "width": 480,
                                "height": 360
                            },
                            "standard": {
                                "url": "url_standard",
                                "width": 640,
                                "height": 480
                            },
                            "maxres": {
                                "url": "url_maxres",
                                "width": 1280,
                                "height": 720
                            }
                        },
                        "channelTitle": "channel_title",
                        "playlistId": "playlist_id",
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": "video_id"
                        },
                        "videoOwnerChannelTitle": "video_owner_channel_title",
                        "videoOwnerChannelId": "video_owner_channel_id"
                    },
                    "contentDetails": {
                        "videoId": "video_id",
                        "videoPublishedAt": "2025-01-01T00:00:02Z"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                },

            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
        }
        self.default_time_1 = datetime.datetime(2025, 1, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        self.default_time_2 = datetime.datetime(2025, 1, 1, 0, 0, 2, tzinfo=datetime.timezone.utc)

    def tearDown(self):
        self.conn.rollback()

    def test__save_keyword(self):
        self.playlist_items._save_keyword()
        self.conn.commit()
        with self.conn.cursor() as cur:
            cur.execute("SELECT keyword_word, date_since_relevant, priority FROM keyword")
            rows = cur.fetchall()

        self.assertEqual(1, len(rows))
        self.assertEqual(('video_id', self.default_time_2, 99 ), rows[0])

    def test__save_keyword_talent(self):
        keyword = {
            'keyword_word': 'video_id',
            'date_since_relevant': self.default_time_2,
            'priority': 99
        }
        talent = {
            'first_name_eng': 'first_name_eng',
        }
        db_helpers.insert(self.conn, table_name='keyword', **keyword)
        db_helpers.insert(self.conn, table_name='talent', **talent)
        db_helpers.insert_youtube_channel(self.conn)
        db_helpers.insert_youtube_video(self.conn)
        db_helpers.insert(self.conn, table_name='youtube_channel_talent', **{
            'youtube_channel_id': 'channel_id',
            'talent_id': 1
        })

        self.playlist_items._save_keyword_talent()
        self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute('SELECT keyword_id, talent_id FROM keyword_talent')
            rows = cur.fetchall()

        self.assertEqual(1, len(rows))
        self.assertEqual((1, 1), rows[0])

class TestChannelsSave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db_helpers.connect_to_test_db()
        with cls.conn.cursor() as cur:
            cur.execute("SET TIME ZONE UTC")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        db_helpers.insert_youtube_channel(self.conn, title="Nerrev_default", youtube_channel_id="UCUY4NGgaom5tDxhe4b1YX0g")
        self.channels_instance = db_yt_interface.Channels(
            connection=self.conn,
            api_service=db_yt_interface.PrepareAPI(filepath='../state/test_api_quota_state.json'),
            cooldown_period=datetime.timedelta(days=0))
        # set up the test data
        self.channels_instance._datetime_now = db_helpers.DEFAULT_TIME
        self.channels_instance._response = {
            "kind": "youtube#channelListResponse",
            "etag": "VxQX18gaJyCDJXoYUzxGkvdW7dw",
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 5
            },
            "items": [
                {
                    "kind": "youtube#channel",
                    "etag": "9MiczvWNjXDqRV9Wdjh9taIxE4g",
                    "id": "UCUY4NGgaom5tDxhe4b1YX0g",
                    "snippet": {
                        "title": "Nerrev",
                        "description": "I LOVE KRONII\nHello",
                        "customUrl": "@nerrev",
                        "publishedAt": "2021-08-22T20:51:08.287011Z",
                        "thumbnails": {
                            "default": {
                                "url": "https://yt3.ggpht.com/M_QeXObUy0EF5VsNqxVs8NIRw8ZgqDdPxBUlOcQpcm5u4O6uqorUoTINtSjT73uTmNFOjHB9=s88-c-k-c0x00ffffff-no-rj",
                                "width": 88,
                                "height": 88
                            },
                            "medium": {
                                "url": "https://yt3.ggpht.com/M_QeXObUy0EF5VsNqxVs8NIRw8ZgqDdPxBUlOcQpcm5u4O6uqorUoTINtSjT73uTmNFOjHB9=s240-c-k-c0x00ffffff-no-rj",
                                "width": 240,
                                "height": 240
                            },
                            "high": {
                                "url": "https://yt3.ggpht.com/M_QeXObUy0EF5VsNqxVs8NIRw8ZgqDdPxBUlOcQpcm5u4O6uqorUoTINtSjT73uTmNFOjHB9=s800-c-k-c0x00ffffff-no-rj",
                                "width": 800,
                                "height": 800
                            }
                        },
                        "localized": {
                            "title": "Nerrev",
                            "description": "I LOVE KRONII\nHello , I'm new to this\nBut I love Ouro Kronii so much I start doing what I'm doing\nMy goal is to show the world how amazing Ouro Kronii is!\nI upload Kronii clips almost every day, please do consider to subscribe so you won't miss the new uploads!\nAny kind of support is very much appreciated, thank you!\n"
                        }
                    },
                    "statistics": {
                        "viewCount": "91885782",
                        "subscriberCount": "95500",
                        "hiddenSubscriberCount": False,
                        "videoCount": "1634"
                    }
                }
            ]
        }

    def test__save_youtube_channel(self):
        self.channels_instance._save_youtube_channel()
        self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT
                youtube_channel_id,
                title,
                description,
                custom_url,
                published_at,
                thumbnail_default,
                info_fully_updated_at
            FROM youtube_channel
            """)
            rows = cur.fetchall()

        self.assertEqual(1, len(rows))
        self.assertEqual(
            (
                "UCUY4NGgaom5tDxhe4b1YX0g",
                "Nerrev",
                "I LOVE KRONII\nHello",
                "@nerrev",
                datetime.datetime(2021, 8, 22, 20, 51, 8, 287011, tzinfo=datetime.timezone.utc),
                "https://yt3.ggpht.com/M_QeXObUy0EF5VsNqxVs8NIRw8ZgqDdPxBUlOcQpcm5u4O6uqorUoTINtSjT73uTmNFOjHB9=s240-c-k-c0x00ffffff-no-rj",
                db_helpers.DEFAULT_TIME
            ),
            rows[0]
        )

    def test__save_youtube_channel_stats(self):
        self.channels_instance._save_youtube_channel_stats()
        self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT
                youtube_channel_id,
                view_count,
                subscriber_count,
                video_count,
                gathered_at
            FROM youtube_channel_stats
            """)
            rows = cur.fetchall()

        self.assertEqual(1, len(rows))
        self.assertEqual(
            (
                "UCUY4NGgaom5tDxhe4b1YX0g",
                91885782,
                95500,
                1634,
                db_helpers.DEFAULT_TIME
            ),
            rows[0]
        )


class TestChannelsSelectChannels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db_helpers.connect_to_test_db()
        with cls.conn.cursor() as cur:
            cur.execute("SET TIME ZONE UTC")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        db_helpers.insert_youtube_channel(
            self.conn,
            title="never_updated",
            youtube_channel_id="id1",
        )
        db_helpers.insert_youtube_channel(
            self.conn,
            title="updated",
            youtube_channel_id="id2",
            info_fully_updated_at=db_helpers.DEFAULT_TIME_NEW,
        )
        self.conn.commit()

    def test__set_channels_to_update_only_unupdated(self):
        self.channels_instance = db_yt_interface.Channels(
            connection=self.conn,
            api_service=db_yt_interface.PrepareAPI(filepath='../state/test_api_quota_state.json'),
            only_unupdated=True,
            cooldown_period=datetime.timedelta(days=0)
        )
        self.channels_instance._set_channels_to_update()

        self.assertEqual(1, len(self.channels_instance._channel_ids), "Wrong number of selected channels")
        self.assertEqual("id1",
                         self.channels_instance._channel_ids[0],
                         "Wrong channel id selected for the update.")

    def test__set_channels_to_update_all(self):
        self.channels_instance = db_yt_interface.Channels(
            connection=self.conn,
            api_service=db_yt_interface.PrepareAPI(filepath='../state/test_api_quota_state.json'),
            only_unupdated=False,
            cooldown_period=datetime.timedelta(days=0)
        )
        self.channels_instance._set_channels_to_update()

        self.assertEqual(2, len(self.channels_instance._channel_ids), "Wrong number of selected channels")
        self.assertIn("id1",
                      self.channels_instance._channel_ids,
                      "Id should be selected for the update, but is not")
        self.assertIn("id2",
                      self.channels_instance._channel_ids,
                      "Id should be selected for the update, but is not")


