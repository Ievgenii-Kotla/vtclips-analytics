import logging
import traceback
import pandas as pd
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

class DBCalculations:
    @staticmethod
    def map_keywords_once(conn, batch_size=10000, verbose=True):
        """Map keyword-video pairs for a single batch of not fully mapped videos."""
        query = """
            DROP INDEX IF EXISTS idx_temp_title_normalized;
            DROP INDEX IF EXISTS idx_temp_description_normalized;
            DROP TABLE IF EXISTS temp_video_to_count;
            
            CREATE TEMP TABLE temp_video_to_count AS
            WITH newest_keyword AS (
                SELECT MAX(added_at) AS added_at
                FROM keyword
            ),
            -- SELECT videos that where counted before the latest keyword was added
            video_to_count AS (
                SELECT youtube_video_id, keywords_counted_at
                FROM youtube_video_statuses
                WHERE keywords_counted_at IS NULL 
                    OR keywords_counted_at <= (SELECT added_at FROM newest_keyword)
                LIMIT %(batch_size)s
            ),
            video_to_count_data AS (
                SELECT 
                    yv.youtube_video_id, 
                    yv.description_normalized,
                    yv.title_normalized,
                    yv.published_at,
                    vtc.keywords_counted_at
                FROM video_to_count vtc
                JOIN youtube_video yv ON vtc.youtube_video_id = yv.youtube_video_id
            )
            SELECT * FROM video_to_count_data;
            
            CREATE INDEX idx_temp_title_normalized ON temp_video_to_count USING gin(title_normalized gin_trgm_ops);
            CREATE INDEX idx_temp_description_normalized ON temp_video_to_count USING gin(description_normalized gin_trgm_ops);
            
            WITH video_keyword_pair AS (
                SELECT 
                    tvtc.youtube_video_id,
                    k.keyword_id, 
                    CASE 
                        WHEN tvtc.description_normalized IS NOT NULL 
                            THEN regexp_count(
                                tvtc.description_normalized, 
                                '(?<![a-zA-Z])' || k.keyword_word || '(?![a-zA-Z])', 
                                1, 
                                'i'
                            )
                            ELSE 0
                    END AS description_count,
                    regexp_count(
                        tvtc.title_normalized, 
                        '(?<![a-zA-Z])' || k.keyword_word || '(?![a-zA-Z])', 
                        1, 
                        'i'
                    ) AS title_count,
                    k.keyword_word
                FROM keyword AS k
                JOIN temp_video_to_count AS tvtc ON
                    -- exclude pairs where the video was published before the keyword became relevant
                    tvtc.published_at + interval '1 week' >= k.date_since_relevant 
                    -- exclude pairs where the keyword was already counted before
                    AND (k.added_at >= tvtc.keywords_counted_at OR tvtc.keywords_counted_at IS NULL)
                    -- exclude pairs with zero matches 
                    AND (
                        tvtc.title_normalized ILIKE '%%'||k.keyword_word||'%%'
                        OR tvtc.description_normalized ILIKE '%%'||k.keyword_word||'%%' 
                    )
                WHERE k.priority NOT IN(13, 14)
            ),
            ins_youtube_video_keyword AS (
                INSERT INTO youtube_video_keyword (
                    youtube_video_id, 
                    keyword_id, 
                    matches_in_description_qty, 
                    matches_in_title_qty, 
                    updated_at
                )
                SELECT 
                    youtube_video_id,
                    keyword_id,
                    description_count,
                    title_count,
                    CURRENT_TIMESTAMP(0)
                FROM video_keyword_pair
                WHERE (title_count + description_count) > 0
                RETURNING youtube_video_id
            ),
            upd_youtube_video_statuses AS (
                UPDATE youtube_video_statuses AS yvs
                SET keywords_counted_at = CURRENT_TIMESTAMP(0)
                FROM (SELECT DISTINCT youtube_video_id FROM temp_video_to_count) tvtk
                WHERE yvs.youtube_video_id = tvtk.youtube_video_id
                RETURNING yvs.youtube_video_id
            )
            SELECT 
                (SELECT COUNT(*) FROM ins_youtube_video_keyword) AS youtube_video_keyword_inserted,
                (SELECT COUNT(DISTINCT youtube_video_id) FROM ins_youtube_video_keyword) AS unique_videos,
                (SELECT COUNT(*) FROM temp_video_to_count) AS video_to_count_selected;
        """
        with conn.cursor() as cursor:
            try:
                cursor.execute(query, {'batch_size': batch_size})
            except Exception as e:
                traceback.print_exc()
                conn.rollback()
                logger.error(f"An error occurred while updating keywords count: {e} \nTransaction rolled back. ")
                raise
            else:
                rows = cursor.fetchall()
                conn.commit()

        pairs_inserted = rows[0][0]
        related_videos = rows[0][1]
        videos_selected = rows[0][2]
        if verbose:
            logger.info(f"Vid-word pairs: {pairs_inserted}, "
                        f"related vids: {related_videos}, "
                        f"vids selected: {videos_selected}")

        if batch_size > videos_selected:
            logger.info(f"Finished updating keywords count. Batch size ({batch_size}) is larger than videos selected.")
            return True, pairs_inserted, related_videos, videos_selected
        else:
            return False, pairs_inserted, related_videos, videos_selected

    @staticmethod
    def map_keywords_all(conn, batch_size=10000, verbose=True):
        """Map keyword-video pairs for all not fully mapped videos."""
        pairs_inserted_total = 0
        related_videos_total = 0
        videos_selected_total = 0
        while True:
            result = DBCalculations.map_keywords_once(conn, batch_size, verbose)
            finished, pairs_inserted, related_videos, videos_selected = result
            pairs_inserted_total += pairs_inserted
            related_videos_total += related_videos
            videos_selected_total += videos_selected
            if finished:
                logger.info(f"Session totals:")
                logger.info(f"Vid-word pairs: {pairs_inserted_total}, "
                            f"related vids: {related_videos_total}, "
                            f"vids selected: {videos_selected_total}")
                break


    @staticmethod
    def videos_to_count(conn):
        query = """
            WITH newest_keyword AS (
                SELECT MAX(added_at) AS added_at
                FROM keyword
            )
            SELECT COUNT(*)
            FROM youtube_video
            WHERE 
                keywords_counted_at IS NULL 
                OR keywords_counted_at <= (SELECT added_at FROM newest_keyword)
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            video_qty = row[0]
            logger.info(f"Number of videos to count keyword(s) in: {video_qty}")
            return video_qty
        else:
            logger.error(f"Something quietly went wrong with videos_to_count estimation query. ")
            return None

class MapTV:
    def __init__(self, conn, youtube_video_id: str = None, cleanup_pool_size: int = 6, batch_size: int = 10000):
        self.connection = conn
        self.youtube_video_id: str = youtube_video_id
        self.cleanup_pool_size: int = cleanup_pool_size
        self.batch_size: int = batch_size
        self.dataset: pd.DataFrame | None = None
        self.cleaned_dataset: pd.DataFrame | None = None

    def map_talents_to_video_all(self):
        self.dataset: pd.DataFrame | None = None
        self.cleaned_dataset: pd.DataFrame | None = None

        videos_mapped_total = 0
        talent_video_pairs_mapped_total = 0
        talents_mapped_total = {}
        while True:
            vm, tvpm, tm = self.map_talents_to_video()
            videos_mapped_total += vm
            talent_video_pairs_mapped_total += tvpm
            talents_mapped_total = self.upd_stats_talents_mapped(talents_mapped_total, tm)
            if vm < self.batch_size:
                break

        sorted_talents_mapped_total = {k: talents_mapped_total[k] for k in sorted(talents_mapped_total)}
        logger.info(f"Session totals:")
        logger.info(f"Videos mapped: {videos_mapped_total}")
        logger.info(f"Talent-video pairs mapped: {talent_video_pairs_mapped_total}")
        logger.info(f"Talents mapped: {sorted_talents_mapped_total}")


    def map_talents_to_video(self):
        """Map talents that appear to be mentioned in videos to the videos. Update the DB data."""

        batch_size = self.batch_size
        videos_mapped = 0
        talent_video_pairs_mapped = 0
        talents_mapped = {}

        while True:
            self._set_video_to_map()
            if self.youtube_video_id is None:
                logger.info("No more videos to map talents to.")
                break

            self._get_dataset_for_cleanup()
            # check if the target video is in the dataset (it is not in it if it had no keywords matched)
            if not (self.dataset['youtube_video_id'] == self.youtube_video_id).any():
                self.dataset = self.dataset.iloc[0:0]

            if not self.dataset.empty:
                self._talent_video_map_alg1()
            try:
                self._save_talent_video_data()
            except Exception as e :
                logger.error(f"An error occurred while updating talents: {e} \nTransaction rolled back. ")
                self.connection.rollback()
                raise
            else:
                self.connection.commit()

            talent_video_pairs_mapped += len(self.dataset)
            new_talents_mapped = {talent_id: 1 for talent_id in self.dataset['talent_id'].astype(int)}
            talents_mapped = self.upd_stats_talents_mapped(talents_mapped, new_talents_mapped)

            videos_mapped += 1
            batch_size -= 1
            if batch_size == 0:
                break
        sorted_talents_mapped = {k: talents_mapped[k] for k in sorted(talents_mapped)}
        logger.info(f"Videos mapped: {videos_mapped} relationships mapped: {talent_video_pairs_mapped}")
        logger.info(f"Talents mapped (t:qty): {sorted_talents_mapped}")
        return videos_mapped, talent_video_pairs_mapped, talents_mapped

    def _set_video_to_map(self):
        """Select a video eligible for mapping talents to."""

        query = """
            SELECT youtube_video_id
            FROM youtube_video_statuses
            WHERE algorithm1_classified_at IS NULL
            LIMIT 1;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            video_id = row[0] if row else None
        self.youtube_video_id = video_id

    def _get_dataset_for_cleanup(self):
        """Prepare a data set that is necessary for cleanup of keywords that are copy-pasted across multiple videos"""

        query = """
            -- select all videos from the same channel as the target video
            WITH channel_video AS (
                SELECT youtube_video_id, published_at
                FROM youtube_video
                WHERE youtube_channel_id = (
                    SELECT youtube_channel_id
                    FROM youtube_video
                    WHERE youtube_video_id = %(video_id)s
                    LIMIT 1
                )
                ORDER BY published_at DESC
            ),
            -- number rows for future row trimming 
            numbered_video AS (
                SELECT *, row_number() OVER(ORDER BY published_at DESC) AS row_num
                FROM channel_video
            ),
            -- add repeated variables 
            vars AS (
                SELECT (
                    SELECT row_num 
                    FROM numbered_video 
                    WHERE youtube_video_id = %(video_id)s 
                ) AS target_row_num,
                (
                    SELECT MAX(row_num)
                    FROM numbered_video
                ) AS last_row_num,
                %(video_set_len)s AS video_set_len 
            ),
            -- calculate boundary for trimming
            boundary AS (
                SELECT 
                    LEAST(target_row_num, last_row_num - (video_set_len - 1)) AS lower_boundary,
                    LEAST(last_row_num, target_row_num + (video_set_len - 1)) AS upper_boundary
                FROM vars
            ),
            -- trim video set
            video_set AS (
                SELECT *
                FROM numbered_video nv
                CROSS JOIN boundary b
                WHERE nv.row_num >= b.lower_boundary AND nv.row_num <= b.upper_boundary
                LIMIT %(video_set_len)s
            )
            -- add the columns necessary for the cleanup
            SELECT 
                vs.youtube_video_id, 
                yvk.keyword_id,
                k.priority,
                yvk.matches_in_title_qty,
                yvk.matches_in_description_qty,
                kt.talent_id
            FROM video_set vs
            JOIN youtube_video_keyword yvk USING (youtube_video_id)
            JOIN keyword k USING (keyword_id)
            JOIN keyword_talent kt USING (keyword_id)
            WHERE k.priority NOT IN(13, 14);
            ;
        """
        values = {'video_id': self.youtube_video_id, 'video_set_len': self.cleanup_pool_size}
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            rows = cursor.fetchall()
        columns = [
            'youtube_video_id',
            'keyword_id',
            'priority',
            'matches_in_title_qty',
            'matches_in_description_qty',
            'talent_id',
        ]
        self.dataset = pd.DataFrame(rows, columns=columns)

    def _cleanup_keyword_counts(self, cross_video=True):
        """Cleanup keyword counts for the target video

        1. Remove keywords copied-pasted across multiple videos
        2. Keep video-keyword pairs only for the target video"""
        dataset = self.dataset.copy()
        if cross_video:
            # Remove keywords copied-pasted across multiple videos
            keyword_groups = dataset.groupby('keyword_id').agg(
                vids_with_keyword=('youtube_video_id', 'count'),
                min_matches_in_description=('matches_in_description_qty', 'min'),
            )
            bad_data = keyword_groups.loc[
                keyword_groups['vids_with_keyword'] >= self.cleanup_pool_size
            ]
            sub_description_map = bad_data['min_matches_in_description']
            dataset['matches_in_description_qty'] -= (
                dataset['keyword_id']
                .map(sub_description_map)
                .fillna(0)
                .astype(int)
            )

        # Keep video-keyword pairs only for the target video
        self.cleaned_dataset = dataset.loc[dataset['youtube_video_id'] == self.youtube_video_id]

    def _talent_video_map_alg1(self):
        """Algorithmically map talents that appear to be mentioned in the video"""

        def map_t_v(dataset):
            """Map talents to the videos using weights"""
            """
                0 - channel's handle
                1 - channel's ID (str of seemingly random characters)
                2 - first name middle name last name (no space)
                3 - last name middle name first name (no space)
                4 - first name middle name last name (with space inbetween)
                5 - last name middle name first name (with space inbetween)
                6 - first name
                7 - last name
                8 - middle name
                9 - nicknames popular
                10 - nicknames somewhat common
                11 - nicknames rare
                12 - channel handle without '@'
                13 - group name
                14 - branch name (holoen, hololiveEN, etc.)
                26 - first name in japanese
                27 - last name in japanese
                99 - video_id of a video made by a talent'
            """

            # priority weights
            #  0: not use, 3: solid indicator, 2: good indicator, 1: medium indicator,
            weights = [
                {'priority': 0, 'title': 0, 'description': 4},
                {'priority': 1, 'title': 0, 'description': 4},
                {'priority': 2, 'title': 7, 'description': 3},
                {'priority': 3, 'title': 7, 'description': 3},
                {'priority': 4, 'title': 7, 'description': 2},
                {'priority': 5, 'title': 7, 'description': 2},
                {'priority': 6, 'title': 4, 'description': 2},
                {'priority': 7, 'title': 4, 'description': 2},
                {'priority': 8, 'title': 0, 'description': 0},
                {'priority': 9, 'title': 4, 'description': 2},
                {'priority': 10, 'title': 2, 'description': 1},
                {'priority': 11, 'title': 2, 'description': 1},
                {'priority': 12, 'title': 2, 'description': 1},
                {'priority': 13, 'title': 0, 'description': 0},
                {'priority': 14, 'title': 0, 'description': 0},
                {'priority': 26, 'title': 3, 'description': 2},
                {'priority': 27, 'title': 3, 'description': 2},
                {'priority': 99, 'title': 0, 'description': 5},
            ]
            weights = pd.DataFrame(weights).set_index('priority')
            dataset['total_score'] = (
                dataset['matches_in_title_qty'] * dataset['priority'].map(weights['title'])
                + dataset['matches_in_description_qty'] * dataset['priority'].map(weights['description'])
            )
            dataset = dataset.loc[:, ['talent_id', 'total_score']]
            dataset = dataset.groupby('talent_id', as_index=False).agg(total_score=('total_score', 'sum'))
            return dataset

        self._cleanup_keyword_counts(cross_video=True)
        cross_video = map_t_v(self.cleaned_dataset)
        self._cleanup_keyword_counts(cross_video=False)
        single_video = map_t_v(self.cleaned_dataset)
        # When cross video keyword cleaning reduces mapped talents for target video by exactly one talent
        #  - we keep the talent in the resulting talent_video_map
        #  This is a special case for clippers that clip mostly a single talent
        if len(cross_video) == len(single_video) - 1:
            self.dataset = single_video
        else:
            self.dataset = cross_video
        # maybe a filter should be applied here to keep only talents with the highest total scores
        cut_off_score = 2
        soft_talent_limit = 3

        self.dataset = self.dataset[self.dataset['total_score'] > cut_off_score]
        self.dataset = self.dataset.sort_values(by='total_score', ascending=False).reset_index(drop=True)
        if len(self.dataset) > soft_talent_limit:
            total_score_cutoff = self.dataset['total_score'].iloc[soft_talent_limit - 1]
            # keep talents tied with soft_talent_limit place
            self.dataset = self.dataset[self.dataset['total_score'] >= total_score_cutoff]
            # remove tied talents if there are too many of them
            if len(self.dataset) > soft_talent_limit + 2:
                self.dataset = self.dataset[self.dataset['total_score'] != total_score_cutoff]

    def _save_talent_video_data(self):
        """Update the DB data regarding target video - talents pairs"""

        del_old_pairs_query = """
            DELETE FROM talent_youtube_video
            WHERE youtube_video_id = %(youtube_video_id)s;
        """
        del_old_pairs_values = {'youtube_video_id': self.youtube_video_id}
        with self.connection.cursor() as cursor:
            cursor.execute(del_old_pairs_query, del_old_pairs_values)

        if not self.dataset.empty:
            insert_video_talent_pairs_query = """
            INSERT INTO talent_youtube_video (
                youtube_video_id,
                talent_id,
                algorithm
            )
            VALUES %s;
            """
            insert_video_talent_pairs_values = [
                [
                    self.youtube_video_id,
                    int(talent_id),
                    1
                ]
                for talent_id in self.dataset['talent_id'].astype(int)
            ]
            with self.connection.cursor() as cursor:
                execute_values(
                    cursor,
                    insert_video_talent_pairs_query,
                    insert_video_talent_pairs_values,
                    template="(%s, %s, %s)"
                )

        update_status_query = """
            UPDATE youtube_video_statuses AS yvs
            SET algorithm1_classified_at = CURRENT_TIMESTAMP(0)
            WHERE yvs.youtube_video_id = %(youtube_video_id)s;
        """
        update_status_values = {'youtube_video_id': self.youtube_video_id}
        with self.connection.cursor() as cursor:
            cursor.execute(update_status_query, update_status_values)

    @staticmethod
    def upd_stats_talents_mapped(talents_mapped_old: dict, talents_mapped_new: dict) -> dict:
        """Update details about talents mapped to videos.

        format for dictionaries: key = talent_id, value = number of times the talent was mapped to a video"""

        if isinstance(talents_mapped_new, dict):
            for key, value in talents_mapped_new.items():
                talents_mapped_old[key] = talents_mapped_old.get(key, 0) + value
        else:
            raise ValueError(f"Invalid type for talents_mapped_new: {type(talents_mapped_new)}")

        return talents_mapped_old
