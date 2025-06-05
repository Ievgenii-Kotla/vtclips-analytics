"""
Tests for the db_yt_interface module.
Uses a better approach to writing tests. Cleaner and easier to read.

"""

import unittest
import datetime
from unittest.mock import patch, ANY, MagicMock
import json
import os
from contextlib import ExitStack

from psycopg2 import DatabaseError

from vtc import connect_to_db, db_yt_interface
from vtc.db_yt_interface import PrepareAPI
from tests.fixtures import setup_test_db
import db_helpers


class TestSearchYTByKeywordMisc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = connect_to_db.connect_to_test_db()

    @classmethod
    def tearDownClass(cls):
        connect_to_db.connection_close(cls.conn)

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        self.search = db_yt_interface.SearchYTByKeyword(
            connection=self.conn,
            api_service=PrepareAPI(filepath='../data/test_api_quota_state.json', delay=False)
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
                1
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
                1
            ),
        ]
        expected_start = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        expected_end = datetime.datetime(2025, 1, 25, 23, 59, 59, tzinfo=datetime.timezone.utc)

        self.search.prepare_subsearch_query()

        self.assertEqual(expected_start, self.search.published_after.astimezone(datetime.timezone.utc))
        self.assertEqual(expected_end, self.search.published_before.astimezone(datetime.timezone.utc))


class TestPlaylistItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = connect_to_db.connect_to_test_db()
        with cls.conn.cursor() as cur:
            cur.execute("SET TIME ZONE UTC")

    @classmethod
    def tearDownClass(cls):
        connect_to_db.connection_close(cls.conn)

    def setUp(self):
        db_helpers.truncate_all(self.conn)
        self.playlist_items = db_yt_interface.PlaylistItems(
            connection=self.conn,
            only_talents=False,
            api_service=db_yt_interface.PrepareAPI(filepath='../data/test_api_quota_state.json'),
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
        self.assertEqual(('video_id', self.default_time_2, 100 ), rows[0])

    def test__save_keyword_talent(self):
        keyword = {
            'keyword_word': 'video_id',
            'date_since_relevant': self.default_time_2,
            'priority': 100
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