""" Set and reset data from the test DB """

from vtc.connect_to_db import connect_to_test_db, connection_close
from datetime import date, datetime, timezone, timedelta
import psycopg2


def _populate_all_for_map(cursor):
    def populate_keyword():
        query = """
INSERT INTO keyword (
    keyword_word,
    date_since_relevant,
    usage_enabled,
    priority,
    purity
)
VALUES (
    %(keyword_word)s,
    %(date_since_relevant)s,
    %(usage_enabled)s,
    %(priority)s,
    %(purity)s
)
RETURNING keyword_id;
"""
        dataset = [
            # Reserved for consecutive search (right after date_since_relevant) with 2 videos
            {
                'keyword_word': 'keywordA1',
                'date_since_relevant': datetime(2020, 6, 12, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for non-consecutive search (3 days after date_since_relevant) with 2 videos
            {
                'keyword_word': 'keywordA2',
                'date_since_relevant': datetime(2020, 6, 12, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for consecutive search
            {
                'keyword_word': 'keywordB1',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for no searches
            {
                'keyword_word': 'keywordB2',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for two consecutive searches
            {
                'keyword_word': 'keywordB3',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for two non-consecutive searches (right after date_since_relevant, two days inbetween searches)
            {
                'keyword_word': 'keywordB4',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for three partially overlapping searches
            {
                'keyword_word': 'keywordB5',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for two fully overlapping searches (one is contained within another)
            # (one day after date_since_relevant)
            {
                'keyword_word': 'keywordB6',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for two identical searches
            {
                'keyword_word': 'keywordB7',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for three searches:
            # one single search in the first group and two overlapping searches in the second group
            {
                'keyword_word': 'keywordB8',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for two searches that are adjacent to themselves and date_since_relevant but not overlapping
            {
                'keyword_word': 'keywordB9',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
            # Reserved for the search that starts 1 second after date_since_relevant
            {
                'keyword_word': 'keywordB10',
                'date_since_relevant': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },

        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_keyword_search_yt(keyword_ids, search_yt_ids):
        query = """
INSERT INTO keyword_search_yt (keyword_id, search_yt_id)
VALUES (%(keyword_id)s, %(search_yt_id)s);
"""
        dataset = [
            {'keyword_id': keyword_ids[0], 'search_yt_id': search_yt_ids[0]},
            {'keyword_id': keyword_ids[1], 'search_yt_id': search_yt_ids[1]},
            {'keyword_id': keyword_ids[2], 'search_yt_id': search_yt_ids[2]},
            {'keyword_id': keyword_ids[4], 'search_yt_id': search_yt_ids[3]},
            {'keyword_id': keyword_ids[4], 'search_yt_id': search_yt_ids[4]},
            {'keyword_id': keyword_ids[5], 'search_yt_id': search_yt_ids[5]},
            {'keyword_id': keyword_ids[5], 'search_yt_id': search_yt_ids[6]},
            {'keyword_id': keyword_ids[6], 'search_yt_id': search_yt_ids[7]},
            {'keyword_id': keyword_ids[6], 'search_yt_id': search_yt_ids[8]},
            {'keyword_id': keyword_ids[6], 'search_yt_id': search_yt_ids[9]},
            {'keyword_id': keyword_ids[7], 'search_yt_id': search_yt_ids[10]},
            {'keyword_id': keyword_ids[7], 'search_yt_id': search_yt_ids[11]},
            {'keyword_id': keyword_ids[8], 'search_yt_id': search_yt_ids[12]},
            {'keyword_id': keyword_ids[8], 'search_yt_id': search_yt_ids[13]},
            {'keyword_id': keyword_ids[9], 'search_yt_id': search_yt_ids[14]},
            {'keyword_id': keyword_ids[9], 'search_yt_id': search_yt_ids[15]},
            {'keyword_id': keyword_ids[9], 'search_yt_id': search_yt_ids[16]},
            {'keyword_id': keyword_ids[10], 'search_yt_id': search_yt_ids[17]},
            {'keyword_id': keyword_ids[10], 'search_yt_id': search_yt_ids[18]},
            {'keyword_id': keyword_ids[11], 'search_yt_id': search_yt_ids[19]},
            {'keyword_id': keyword_ids[11], 'search_yt_id': search_yt_ids[20]},
        ]
        for data in dataset:
            cursor.execute(query, data)

    def populate_keyword_talent(keyword_ids, talent_ids):
        query = """
INSERT INTO keyword_talent (
    keyword_id,
    talent_id
)
VALUES (
    %(keyword_id)s,
    %(talent_id)s
);
"""
        dataset = [
            {'keyword_id': keyword_ids[0], 'talent_id': talent_ids[0]},
            {'keyword_id': keyword_ids[1], 'talent_id': talent_ids[0]},
            {'keyword_id': keyword_ids[2], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[3], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[4], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[5], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[6], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[7], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[8], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[9], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[10], 'talent_id': talent_ids[1]},
            {'keyword_id': keyword_ids[11], 'talent_id': talent_ids[1]},
        ]
        for data in dataset:
            cursor.execute(query, data)

    def populate_search_yt():
        query = """
INSERT INTO search_yt (
    published_after,
    published_before,
    results_per_page_max,
    results_per_page,
    total_results,
    search_layer
)
VALUES (
    %(published_after)s,
    %(published_before)s,
    %(results_per_page_max)s,
    %(results_per_page)s,
    %(total_results)s,
    %(search_layer)s
)
RETURNING search_yt_id;
"""
        dataset = [
            {
                'published_after': datetime(2020, 6, 12, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 16, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 778,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 16, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 17, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 12, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 15, 10, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 16, 10, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 16, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 12, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 16, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 17, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 16, 12, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 17, 12, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 13, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 13, 23, 59, 59, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 14, 23, 59, 59, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 13, 0, 0, 1, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 14, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },
            {
                'published_after': datetime(2020, 6, 14, 0, 0, 1, tzinfo=timezone.utc),
                'published_before': datetime(2020, 6, 15, 0, 0, 0, tzinfo=timezone.utc),
                'results_per_page_max': 5,
                'results_per_page': 2,
                'total_results': 777,
                'search_layer': 1,
            },

        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_search_yt_youtube_video(search_yt_ids, youtube_video_ids):
        query = """
INSERT INTO search_yt_youtube_video (
    search_yt_id,
    youtube_video_id
)
VALUES (
    %(search_yt_id)s,
    %(youtube_video_id)s
)
"""
        dataset = [
            {
                'search_yt_id': search_yt_ids[0],
                'youtube_video_id': youtube_video_ids[0]
            },
            {
                'search_yt_id': search_yt_ids[0],
                'youtube_video_id': youtube_video_ids[1]
            },
            {
                'search_yt_id': search_yt_ids[1],
                'youtube_video_id': youtube_video_ids[2]
            },
            {
                'search_yt_id': search_yt_ids[1],
                'youtube_video_id': youtube_video_ids[3]
            }
        ]
        for data in dataset:
            cursor.execute(query, data)

    def populate_talent():
        query = """
INSERT INTO talent (first_name_eng)
VALUES (%(first_name_eng)s)
RETURNING talent_id
"""
        dataset = [
            {'first_name_eng': 'A'},
            {'first_name_eng': 'B'}
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_youtube_channel():
        query = """
INSERT INTO youtube_channel (
    youtube_channel_id,
    channel_info_last_updated,
    title,
    added_at
)
VALUES (
    %(youtube_channel_id)s,
    %(channel_info_last_updated)s,
    %(title)s,
    %(added_at)s
    )
RETURNING youtube_channel_id;
"""
        dataset = [
            {
                'youtube_channel_id': 'ch_id1',
                'channel_info_last_updated': datetime.now(),
                'title': 'ch_title1',
                'added_at': datetime.now()
            },
            {
                'youtube_channel_id': 'ch_id2',
                'channel_info_last_updated': datetime.now(),
                'title': 'ch_title2',
                'added_at': datetime.now()
            },
            {
                'youtube_channel_id': 'ch_id3',
                'channel_info_last_updated': datetime.now(),
                'title': 'ch_title3',
                'added_at': datetime.now()
            }
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_youtube_channel_stats():
        pass

    def populate_youtube_channel_talent():
        pass

    def populate_youtube_video(youtube_channel_ids):
        query = """
INSERT INTO youtube_video (
    youtube_video_id,
    youtube_channel_id,
    published_at,
    title,
    description_trimmed,
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
VALUES (
    %(youtube_video_id)s,
    %(youtube_channel_id)s,
    %(published_at)s,
    %(title)s,
    %(description_trimmed)s,
    %(updated_at)s,
    %(kind)s,
    %(thumbnail_default_url)s,
    %(thumbnail_default_width)s,
    %(thumbnail_default_height)s,
    %(thumbnail_medium_url)s,
    %(thumbnail_medium_width)s,
    %(thumbnail_medium_height)s,
    %(thumbnail_high_url)s,
    %(thumbnail_high_width)s,
    %(thumbnail_high_height)s,
    %(added_at)s
)
RETURNING youtube_video_id;
"""
        dataset = [
            {
                'youtube_video_id': 'video_id1',
                'youtube_channel_id': youtube_channel_ids[0],
                'published_at': datetime(2020, 6, 12, 6, 0, 0, tzinfo=timezone.utc),
                'title': 'video_title1',
                'description_trimmed': 'description_tr1',
                'updated_at': datetime.now(),
                'kind': 'youtube#video',
                'thumbnail_default_url': 'https://placeholder',
                'thumbnail_default_width': 1,
                'thumbnail_default_height': 1,
                'thumbnail_medium_url': 'https://placeholder',
                'thumbnail_medium_width': 1,
                'thumbnail_medium_height': 1,
                'thumbnail_high_url': 'https://placeholder',
                'thumbnail_high_width': 1,
                'thumbnail_high_height': 1,
                'added_at': datetime.now()
            },
            {
                'youtube_video_id': 'video_id2',
                'youtube_channel_id': youtube_channel_ids[0],
                'published_at': datetime(2020, 6, 12, 18, 0, 0, tzinfo=timezone.utc),
                'title': 'video_title2',
                'description_trimmed': 'description_tr2',
                'updated_at': datetime.now(),
                'kind': 'youtube#video',
                'thumbnail_default_url': 'https://placeholder',
                'thumbnail_default_width': 1,
                'thumbnail_default_height': 1,
                'thumbnail_medium_url': 'https://placeholder',
                'thumbnail_medium_width': 1,
                'thumbnail_medium_height': 1,
                'thumbnail_high_url': 'https://placeholder',
                'thumbnail_high_width': 1,
                'thumbnail_high_height': 1,
                'added_at': datetime.now()

            },
            {
                'youtube_video_id': 'video_id3',
                'youtube_channel_id': youtube_channel_ids[1],
                'published_at': datetime(2020, 6, 15, 7, 0, 0, tzinfo=timezone.utc),
                'title': 'video_title3',
                'description_trimmed': 'description_tr3',
                'updated_at': datetime.now(),
                'kind': 'youtube#video',
                'thumbnail_default_url': 'https://placeholder',
                'thumbnail_default_width': 1,
                'thumbnail_default_height': 1,
                'thumbnail_medium_url': 'https://placeholder',
                'thumbnail_medium_width': 1,
                'thumbnail_medium_height': 1,
                'thumbnail_high_url': 'https://placeholder',
                'thumbnail_high_width': 1,
                'thumbnail_high_height': 1,
                'added_at': datetime.now()

            },
            {
                'youtube_video_id': 'video_id4',
                'youtube_channel_id': youtube_channel_ids[2],
                'published_at': datetime(2020, 6, 15, 19, 0, 0, tzinfo=timezone.utc),
                'title': 'video_title4',
                'description_trimmed': 'description_tr4',
                'updated_at': datetime.now(),
                'kind': 'youtube#video',
                'thumbnail_default_url': 'https://placeholder',
                'thumbnail_default_width': 1,
                'thumbnail_default_height': 1,
                'thumbnail_medium_url': 'https://placeholder',
                'thumbnail_medium_width': 1,
                'thumbnail_medium_height': 1,
                'thumbnail_high_url': 'https://placeholder',
                'thumbnail_high_width': 1,
                'thumbnail_high_height': 1,
                'added_at': datetime.now()
            }
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_youtube_video_keyword():
        pass

    def populate_youtube_video_stats():
        pass

    def populate_youtube_video_youtube_video():
        pass

    keyword_ids = populate_keyword()
    search_yt_ids = populate_search_yt()
    populate_keyword_search_yt(keyword_ids, search_yt_ids)
    talent_ids = populate_talent()
    populate_keyword_talent(keyword_ids, talent_ids)
    youtube_channel_ids = populate_youtube_channel()
    youtube_video_ids = populate_youtube_video(youtube_channel_ids)
    populate_search_yt_youtube_video(search_yt_ids, youtube_video_ids)


def _populate_all_for_save(cursor):
    def populate_keyword():
        query = """
    INSERT INTO keyword (
        keyword_word,
        date_since_relevant,
        usage_enabled,
        priority,
        purity
    )
    VALUES (
        %(keyword_word)s,
        %(date_since_relevant)s,
        %(usage_enabled)s,
        %(priority)s,
        %(purity)s
    )
    RETURNING keyword_id;
    """
        dataset = [
            # Reserved for consecutive search (right after date_since_relevant) with 2 videos
            {
                'keyword_word': 'test_keyword_for_save',
                'date_since_relevant': datetime(2020, 6, 12, 0, 0, 0, tzinfo=timezone.utc),
                'usage_enabled': True,
                'priority': 1,
                'purity': 'pure'
            },
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    populate_keyword()


def _truncate_all(connection, cursor):
    truncate_table_queries = [
        'TRUNCATE TABLE keyword CASCADE;',
        'TRUNCATE TABLE keyword_search_yt CASCADE;',
        'TRUNCATE TABLE keyword_talent CASCADE;',
        'TRUNCATE TABLE search_yt CASCADE;',
        'TRUNCATE TABLE search_yt_youtube_video CASCADE;',
        'TRUNCATE TABLE talent CASCADE;',
        'TRUNCATE TABLE youtube_channel CASCADE;',
        'TRUNCATE TABLE youtube_channel_stats CASCADE;',
        'TRUNCATE TABLE youtube_channel_talent CASCADE;',
        'TRUNCATE TABLE youtube_video CASCADE;',
        'TRUNCATE TABLE youtube_video_keyword CASCADE;',
        'TRUNCATE TABLE youtube_video_stats CASCADE;',
        'TRUNCATE TABLE youtube_video_youtube_video CASCADE;'
    ]
    for query in truncate_table_queries:
        cursor.execute(query)


def _populate_all_for_search_interval(cursor):
    """ Populate test db with all the data necessary for testing calculate_search_interval. """

    def populate_search_yt():
        query = """
        INSERT INTO search_yt (
        published_after,
        published_before,
        results_per_page,
        q,
        results_per_page_max,
        total_results
        )
        VALUES (
        %(published_after)s,
        %(published_before)s,
        %(results_per_page)s,
        %(q)s,
        %(results_per_page_max)s,
        %(total_results)s
        )
        RETURNING search_yt_id;
        """
        dataset = [
            # pre-debut, 5 or less matches per day
            {
                'published_after': '2023-12-01 00:00:00+00:00',
                'published_before': '2023-12-02 23:59:59+00:00',
                'results_per_page': 3,
                'q': 'keyword_1',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # pre-debut, 5 or less matches per day, but right before debut
            {
                'published_after': '2023-12-28 00:00:00+00:00',
                'published_before': '2023-12-29 23:59:59+00:00',
                'results_per_page': 3,
                'q': 'keyword_2',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # post-debut, zero matches
            {
                'published_after': '2024-01-03 00:00:00+00:00',
                'published_before': '2024-01-04 23:59:59+00:00',
                'results_per_page': 0,
                'q': 'keyword_3',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # post-debut, 1 to 10 matches. Big previous search
            {
                'published_after': '2024-01-05 00:00:00+00:00',
                'published_before': '2024-01-11 23:59:59+00:00',
                'results_per_page': 9,
                'q': 'keyword_4',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # post-debut, 1 to 10 matches. Normal previous search
            {
                'published_after': '2024-01-05 00:00:00+00:00',
                'published_before': '2024-01-06 23:59:59+00:00',
                'results_per_page': 9,
                'q': 'keyword_5',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # any period, 11 to 40 matches.
            {
                'published_after': '2024-01-05 00:00:00+00:00',
                'published_before': '2024-01-08 23:59:59+00:00',
                'results_per_page': 25,
                'q': 'keyword_6',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # any period, 41 to 50 matches
            {
                'published_after': '2024-01-04 00:00:00+00:00',
                'published_before': '2024-01-06 23:59:59+00:00',
                'results_per_page': 45,
                'q': 'keyword_7',
                'results_per_page_max': 50,
                'total_results': 1000
            },
            # old search (ended more than 1 second before current search starts)
            {
                'published_after': '2024-01-05 00:00:00+00:00',
                'published_before': '2024-01-06 23:59:59+00:00',
                'results_per_page': 25,
                'q': 'keyword_8',
                'results_per_page_max': 50,
                'total_results': 1000
            },
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_talent():
        query = """
        INSERT INTO talent (
        debut_datetime,
        first_name_eng
        )
        VALUES (
        %(debut_datetime)s,
        %(first_name_eng)s
        )
        RETURNING talent_id;
        """
        dataset = [
            {
                'debut_datetime': '2024-01-01 00:00:00+00:00',
                'first_name_eng': 'talent_name_one'
            },
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_keyword():
        query = """
        INSERT INTO keyword (
        keyword_word,
        priority
        )
        VALUES (
        %(keyword_word)s,
        %(priority)s
        )
        RETURNING keyword_id;
        """
        dataset = [
            {
                'keyword_word': 'keyword_1',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_2',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_3',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_4',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_5',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_6',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_7',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_8',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_9',
                'priority': 1
            },
            {
                'keyword_word': 'keyword_10',  # no searches
                'priority': 1
            },
        ]
        ids = []
        for data in dataset:
            cursor.execute(query, data)
            ids.append(cursor.fetchone()[0])
        return ids

    def populate_keyword_search_yt(keyword_ids, search_yt_ids):
        query = """
        INSERT INTO keyword_search_yt (
        keyword_id,
        search_yt_id
        )
        VALUES (
        %(keyword_id)s,
        %(search_yt_id)s
        );
        """
        for keyword_id, search_yt_id in zip(keyword_ids, search_yt_ids):
            cursor.execute(query, {'keyword_id': keyword_id, 'search_yt_id': search_yt_id})

    def populate_keyword_talent(keyword_ids, talent_ids):
        query = """
        INSERT INTO keyword_talent (
        keyword_id,
        talent_id
        )
        VALUES (
        %(keyword_id)s,
        %(talent_id)s
        );
        """
        for keyword_id in keyword_ids:
            cursor.execute(query, {'keyword_id': keyword_id, 'talent_id': talent_ids[0]})

    search_yt_ids = populate_search_yt()
    talent_ids = populate_talent()
    keyword_ids = populate_keyword()
    populate_keyword_search_yt(keyword_ids, search_yt_ids)
    populate_keyword_talent(keyword_ids, talent_ids)


def reset_for_map():
    connection = connect_to_test_db()
    cursor = connection.cursor()
    _truncate_all(connection, cursor)
    _populate_all_for_map(cursor)
    cursor.close()
    connection.commit()
    connection_close(connection)
    print('Test DB was reset for map testing.')


def reset_for_save():
    connection = connect_to_test_db()
    cursor = connection.cursor()
    _truncate_all(connection, cursor)
    _populate_all_for_save(cursor)
    cursor.close()
    connection.commit()
    connection_close(connection)
    print('Test DB was reset for save() testing.')


def reset_for_interval():
    """ Reset the DB for testing related to the length of the search. """
    connection = connect_to_test_db()
    cursor = connection.cursor()
    _truncate_all(connection, cursor)
    _populate_all_for_search_interval(cursor)
    cursor.close()
    connection.commit()
    connection_close(connection)
    print('Test DB was reset for search interval testing')


if __name__ == '__main__':
    reset_for_map()
    reset_for_save()
    reset_for_interval()
