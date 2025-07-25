--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.4

-- Started on 2025-07-10 16:56:17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
--SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- TOC entry 5047 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


--
-- TOC entry 2 (class 3079 OID 18490221)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- TOC entry 907 (class 1247 OID 18490303)
-- Name: addition_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.addition_status AS ENUM (
    'added_earlier',
    'newly_added'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 18490307)
-- Name: keyword; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keyword (
    keyword_id integer NOT NULL,
    keyword_word text NOT NULL,
    date_since_relevant timestamp with time zone,
    purity_pct integer,
    usage_enabled boolean DEFAULT true NOT NULL,
    priority integer NOT NULL,
    purity text DEFAULT 'pure'::text,
    purity_pct_updated_at timestamp with time zone
);


--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE keyword; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.keyword IS 'Keywords that can be used to find or identify videos related to a talent.
Guidelines:
0 - channel''s handle
1 - channel"s ID (str of seemingly random characters)
2 - first name last name
3 - last name fisrt name
4 - first name
5 - last name
6 - middle name
7 - channel''s handle without ''@''
8 - nicknames popular
9 - nicknames somewhat common
10 - nicknames rare
11 - ids of videos published by talents
12 - titles of videos published by talents
13 - group names
14 - branch names (holoen, hololiveEN, etc.)
';


--
-- TOC entry 225 (class 1259 OID 18490314)
-- Name: keyword_keyword_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.keyword ALTER COLUMN keyword_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.keyword_keyword_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 226 (class 1259 OID 18490315)
-- Name: keyword_search_yt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keyword_search_yt (
    search_yt_id integer NOT NULL,
    keyword_id integer NOT NULL
);


--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE keyword_search_yt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.keyword_search_yt IS 'Junction table.';


--
-- TOC entry 227 (class 1259 OID 18490318)
-- Name: keyword_talent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keyword_talent (
    keyword_id integer NOT NULL,
    talent_id integer NOT NULL
);


--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE keyword_talent; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.keyword_talent IS 'Junction table';


--
-- TOC entry 228 (class 1259 OID 18490321)
-- Name: playlist_items_request; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.playlist_items_request (
    playlist_items_request_id integer NOT NULL,
    playlist_id text NOT NULL,
    requested_at timestamp with time zone NOT NULL,
    max_results integer NOT NULL,
    total_results integer NOT NULL,
    results_per_page integer NOT NULL,
    prev_page_token text,
    next_page_token text,
    etag text
);


--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE playlist_items_request; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.playlist_items_request IS 'History of ''playlist'' requests.';


--
-- TOC entry 229 (class 1259 OID 18490326)
-- Name: playlist_items_request_youtube_video; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.playlist_items_request_youtube_video (
    playlist_items_request_id integer NOT NULL,
    youtube_video_id text NOT NULL
);


--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE playlist_items_request_youtube_video; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.playlist_items_request_youtube_video IS 'Junction table for ''playlist_request'' and ''youtube_video'' tables';


--
-- TOC entry 230 (class 1259 OID 18490331)
-- Name: playlist_request_playlist_request_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.playlist_items_request ALTER COLUMN playlist_items_request_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.playlist_request_playlist_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 231 (class 1259 OID 18490332)
-- Name: search_yt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_yt (
    search_yt_id integer NOT NULL,
    searched_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_after timestamp with time zone NOT NULL,
    published_before timestamp with time zone NOT NULL,
    results_per_page_max integer NOT NULL,
    prev_page_token text,
    next_page_token text,
    total_results integer NOT NULL,
    region_code text,
    results_per_page integer NOT NULL,
    page_num integer,
    q text,
    kind text,
    search_layer integer,
    parent_id integer,
    is_q_quoted boolean
);


--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE search_yt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.search_yt IS 'History of searches. ';


--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN search_yt.searched_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.search_yt.searched_at IS 'Time at which the search was conducted.';


--
-- TOC entry 5057 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN search_yt.published_after; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.search_yt.published_after IS 'Attribute of YT search request.';


--
-- TOC entry 5058 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN search_yt.published_before; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.search_yt.published_before IS 'Attribute of YT search request.';


--
-- TOC entry 5059 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN search_yt.q; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.search_yt.q IS 'A string that represents the text that was searched on youtube.
Named after the corresponding search attribute in the Youtube search request API.';


--
-- TOC entry 232 (class 1259 OID 18490338)
-- Name: search_search_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.search_yt ALTER COLUMN search_yt_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.search_search_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 233 (class 1259 OID 18490339)
-- Name: search_yt_youtube_video; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_yt_youtube_video (
    search_yt_id integer NOT NULL,
    youtube_video_id text NOT NULL
);


--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE search_yt_youtube_video; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.search_yt_youtube_video IS 'Junction table.
Joins ''search_yt'' and ''youtube_video'' tables.';


--
-- TOC entry 234 (class 1259 OID 18490344)
-- Name: talent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.talent (
    talent_id integer NOT NULL,
    first_name_eng text NOT NULL,
    last_name_eng text,
    face_picture text,
    group_name text,
    debut_datetime timestamp with time zone,
    graduation_date timestamp with time zone
);


--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE talent; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.talent IS 'Content creators who provide original source materials ("let''s play", "karaoke" etc videos).
e.g. Ouro Kronii, Gawr Gura, IRyS';


--
-- TOC entry 235 (class 1259 OID 18490349)
-- Name: talent_talent_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.talent ALTER COLUMN talent_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.talent_talent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 236 (class 1259 OID 18490350)
-- Name: youtube_channel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_channel (
    talent_id integer,
    is_clipper boolean,
    is_other boolean,
    video_list_last_updated timestamp with time zone,
    channel_info_last_updated timestamp with time zone NOT NULL,
    title text NOT NULL,
    description text,
    custom_url text,
    published_at timestamp with time zone,
    thumbnail_default text,
    country text,
    added_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    youtube_channel_id text NOT NULL,
    etag text,
    playlist_id text,
    playlist_etag text,
    playlist_available boolean DEFAULT true NOT NULL
);


--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE youtube_channel; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_channel IS 'Info about a youtube channel';


--
-- TOC entry 5063 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN youtube_channel.published_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_channel.published_at IS 'When the channel was created on YouTube.';


--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN youtube_channel.added_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_channel.added_at IS 'When a channel was added to the DB.';


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN youtube_channel.playlist_available; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_channel.playlist_available IS 'Availability when trying to access a playlist on yt.
FALSE - playlist got 404 on API call';


--
-- TOC entry 237 (class 1259 OID 18490357)
-- Name: youtube_channel_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_channel_stats (
    youtube_channel_stats_id integer NOT NULL,
    youtube_channel_id text NOT NULL,
    view_count integer NOT NULL,
    subscriber_count integer NOT NULL,
    video_count integer NOT NULL,
    gathered_at timestamp with time zone NOT NULL
);


--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE youtube_channel_stats; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_channel_stats IS 'Youtube channel statistics that regularly change.';


--
-- TOC entry 238 (class 1259 OID 18490362)
-- Name: youtube_channel_stats_youtube_channel_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.youtube_channel_stats ALTER COLUMN youtube_channel_stats_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.youtube_channel_stats_youtube_channel_stats_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 239 (class 1259 OID 18490363)
-- Name: youtube_channel_talent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_channel_talent (
    talent_id integer NOT NULL,
    youtube_channel_id text NOT NULL
);


--
-- TOC entry 5067 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE youtube_channel_talent; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_channel_talent IS 'Junction table
Linking talents to their respective channels';


--
-- TOC entry 240 (class 1259 OID 18490368)
-- Name: youtube_video; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_video (
    youtube_video_id text NOT NULL,
    youtube_channel_id text NOT NULL,
    duration interval,
    actual_start_time timestamp with time zone,
    actual_end_time timestamp with time zone,
    scheduled_start_time timestamp with time zone,
    published_at timestamp with time zone NOT NULL,
    title text NOT NULL,
    description_trimmed text,
    category_id text,
    live_broadcast_content text,
    localized_title text,
    localized_description text,
    default_audio_language text,
    upload_status text,
    privacy_status text,
    license text,
    embeddable boolean,
    public_stats_viewable boolean,
    made_for_kids boolean,
    updated_at timestamp with time zone NOT NULL,
    description_full text,
    kind text NOT NULL,
    thumbnail_default_url text NOT NULL,
    thumbnail_default_width integer DEFAULT 120 NOT NULL,
    thumbnail_default_height integer DEFAULT 90 NOT NULL,
    thumbnail_medium_url text NOT NULL,
    thumbnail_medium_width integer DEFAULT 320 NOT NULL,
    thumbnail_medium_height integer DEFAULT 180 NOT NULL,
    thumbnail_high_url text NOT NULL,
    thumbnail_high_width integer DEFAULT 480 NOT NULL,
    thumbnail_high_height integer DEFAULT 360 NOT NULL,
    tags text,
    added_at timestamp with time zone NOT NULL,
    thumbnail_standard_url text,
    thumbnail_standard_width integer DEFAULT 640,
    thumbnail_standard_height integer DEFAULT 480,
    thumbnail_maxres_url text,
    thumbnail_maxres_width integer DEFAULT 1280,
    thumbnail_maxres_height integer DEFAULT 720,
    etag text,
    playlist_item_id text,
    playlist_item_etag text,
    playlist_item_position integer,
    playlist_item_published_at timestamp with time zone,
    title_normalized text,
    description_normalized text
);


--
-- TOC entry 5068 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE youtube_video; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_video IS 'Info about a youtube video';


--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN youtube_video.youtube_video_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_video.youtube_video_id IS 'Identification key that youtube and DB uses to identify videos.';


--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN youtube_video.kind; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_video.kind IS 'Stores ''kind'' field from youtube search request.';


--
-- TOC entry 5071 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN youtube_video.added_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.youtube_video.added_at IS 'When a video was added to the DB.';


--
-- TOC entry 241 (class 1259 OID 18490383)
-- Name: youtube_video_keyword; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_video_keyword (
    youtube_video_keyword_id integer NOT NULL,
    youtube_video_id text NOT NULL,
    keyword_id integer NOT NULL,
    matches_in_title_qty integer NOT NULL,
    matches_in_description_qty integer NOT NULL,
    matches_in_tags_qty integer NOT NULL,
    matches_in_subs_qty integer,
    updated_on timestamp with time zone NOT NULL
);


--
-- TOC entry 5072 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE youtube_video_keyword; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_video_keyword IS 'Post-analysis of possible best keywords.
Also a junstion table.';


--
-- TOC entry 242 (class 1259 OID 18490388)
-- Name: youtube_video_keyword_youtube_video_keyword_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.youtube_video_keyword ALTER COLUMN youtube_video_keyword_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.youtube_video_keyword_youtube_video_keyword_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 243 (class 1259 OID 18490389)
-- Name: youtube_video_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_video_stats (
    youtube_video_stats_id integer NOT NULL,
    youtube_video_id text NOT NULL,
    view_count integer NOT NULL,
    like_count integer NOT NULL,
    comment_count integer NOT NULL,
    gathered_at timestamp with time zone NOT NULL
);


--
-- TOC entry 5073 (class 0 OID 0)
-- Dependencies: 243
-- Name: TABLE youtube_video_stats; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_video_stats IS 'Youtube video statistics that regularly change.';


--
-- TOC entry 244 (class 1259 OID 18490394)
-- Name: youtube_video_stats_youtube_video_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.youtube_video_stats ALTER COLUMN youtube_video_stats_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.youtube_video_stats_youtube_video_stats_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 245 (class 1259 OID 18490395)
-- Name: youtube_video_youtube_video; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.youtube_video_youtube_video (
    source text NOT NULL,
    clip text NOT NULL
);


--
-- TOC entry 5074 (class 0 OID 0)
-- Dependencies: 245
-- Name: TABLE youtube_video_youtube_video; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.youtube_video_youtube_video IS 'Junction table that shows source-clip relations of youtube videos.';


--
-- TOC entry 4829 (class 2606 OID 21250055)
-- Name: keyword enum_purity; Type: CHECK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.keyword
    ADD CONSTRAINT enum_purity CHECK ((purity = ANY (ARRAY['pure'::text, 'mixed'::text, 'dirty'::text]))) NOT VALID;


--
-- TOC entry 4832 (class 2606 OID 21250057)
-- Name: keyword pk_keyword; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword
    ADD CONSTRAINT pk_keyword PRIMARY KEY (keyword_id);


--
-- TOC entry 4836 (class 2606 OID 21250059)
-- Name: keyword_search_yt pk_keyword_search_yt; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_search_yt
    ADD CONSTRAINT pk_keyword_search_yt PRIMARY KEY (search_yt_id, keyword_id);


--
-- TOC entry 4840 (class 2606 OID 21250061)
-- Name: keyword_talent pk_keyword_talent; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_talent
    ADD CONSTRAINT pk_keyword_talent PRIMARY KEY (keyword_id, talent_id);


--
-- TOC entry 4849 (class 2606 OID 21250063)
-- Name: search_yt pk_search_yt; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_yt
    ADD CONSTRAINT pk_search_yt PRIMARY KEY (search_yt_id);


--
-- TOC entry 4852 (class 2606 OID 21250065)
-- Name: search_yt_youtube_video pk_search_yt_youtube_video; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_yt_youtube_video
    ADD CONSTRAINT pk_search_yt_youtube_video PRIMARY KEY (search_yt_id, youtube_video_id);


--
-- TOC entry 4854 (class 2606 OID 21250067)
-- Name: talent pk_talent; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.talent
    ADD CONSTRAINT pk_talent PRIMARY KEY (talent_id);


--
-- TOC entry 4856 (class 2606 OID 21250069)
-- Name: youtube_channel pk_youtube_channel; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel
    ADD CONSTRAINT pk_youtube_channel PRIMARY KEY (youtube_channel_id);


--
-- TOC entry 4860 (class 2606 OID 21250071)
-- Name: youtube_channel_stats pk_youtube_channel_stats; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_stats
    ADD CONSTRAINT pk_youtube_channel_stats PRIMARY KEY (youtube_channel_stats_id);


--
-- TOC entry 4862 (class 2606 OID 21250073)
-- Name: youtube_channel_talent pk_youtube_channel_talent; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_talent
    ADD CONSTRAINT pk_youtube_channel_talent PRIMARY KEY (talent_id, youtube_channel_id);


--
-- TOC entry 4867 (class 2606 OID 21250075)
-- Name: youtube_video pk_youtube_video; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video
    ADD CONSTRAINT pk_youtube_video PRIMARY KEY (youtube_video_id);


--
-- TOC entry 4872 (class 2606 OID 21250082)
-- Name: youtube_video_keyword pk_youtube_video_keyword; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_keyword
    ADD CONSTRAINT pk_youtube_video_keyword PRIMARY KEY (youtube_video_keyword_id);


--
-- TOC entry 4875 (class 2606 OID 21250084)
-- Name: youtube_video_stats pk_youtube_video_stats; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_stats
    ADD CONSTRAINT pk_youtube_video_stats PRIMARY KEY (youtube_video_stats_id);


--
-- TOC entry 4877 (class 2606 OID 21250086)
-- Name: youtube_video_youtube_video pk_youtube_video_youtube_video; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_youtube_video
    ADD CONSTRAINT pk_youtube_video_youtube_video PRIMARY KEY (source, clip);


--
-- TOC entry 4844 (class 2606 OID 21250088)
-- Name: playlist_items_request playlist_items_request_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.playlist_items_request
    ADD CONSTRAINT playlist_items_request_pkey PRIMARY KEY (playlist_items_request_id);


--
-- TOC entry 4847 (class 2606 OID 21250090)
-- Name: playlist_items_request_youtube_video playlist_items_request_youtube_video_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.playlist_items_request_youtube_video
    ADD CONSTRAINT playlist_items_request_youtube_video_pkey PRIMARY KEY (playlist_items_request_id, youtube_video_id);


--
-- TOC entry 4830 (class 2606 OID 21250091)
-- Name: talent talent_group_name_check; Type: CHECK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.talent
    ADD CONSTRAINT talent_group_name_check CHECK ((group_name = ANY (ARRAY['myth'::text, 'promise'::text, 'advent'::text, 'justice'::text, 'council'::text]))) NOT VALID;


--
-- TOC entry 4838 (class 2606 OID 21250093)
-- Name: keyword_search_yt unique_keyword_id_search_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_search_yt
    ADD CONSTRAINT unique_keyword_id_search_id UNIQUE (keyword_id, search_yt_id);


--
-- TOC entry 4842 (class 2606 OID 21250095)
-- Name: keyword_talent unique_keyword_id_talent_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_talent
    ADD CONSTRAINT unique_keyword_id_talent_id UNIQUE (keyword_id, talent_id);


--
-- TOC entry 4834 (class 2606 OID 21250097)
-- Name: keyword unique_keyword_word; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword
    ADD CONSTRAINT unique_keyword_word UNIQUE (keyword_word);


--
-- TOC entry 4864 (class 2606 OID 21250099)
-- Name: youtube_channel_talent unique_talent_id_youtube_channel_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_talent
    ADD CONSTRAINT unique_talent_id_youtube_channel_id UNIQUE (talent_id, youtube_channel_id);


--
-- TOC entry 4858 (class 2606 OID 21250101)
-- Name: youtube_channel youtube_channel_yt_playlist_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel
    ADD CONSTRAINT youtube_channel_yt_playlist_id_key UNIQUE (playlist_id);


--
-- TOC entry 4850 (class 1259 OID 21250102)
-- Name: fki_fk_search_youtube_youtube_video_youtube_video; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_fk_search_youtube_youtube_video_youtube_video ON public.search_yt_youtube_video USING btree (youtube_video_id);


--
-- TOC entry 4870 (class 1259 OID 21250103)
-- Name: fki_fk_youtube_video_keyword_youtube_video_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_fk_youtube_video_keyword_youtube_video_id ON public.youtube_video_keyword USING btree (youtube_video_id);


--
-- TOC entry 4873 (class 1259 OID 21250104)
-- Name: fki_fk_youtube_video_stats_youtube_video_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_fk_youtube_video_stats_youtube_video_id ON public.youtube_video_stats USING btree (youtube_video_id);


--
-- TOC entry 4865 (class 1259 OID 21250105)
-- Name: fki_fk_youtube_video_youtube_channel_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_fk_youtube_video_youtube_channel_id ON public.youtube_video USING btree (youtube_channel_id);


--
-- TOC entry 4845 (class 1259 OID 21250106)
-- Name: fki_playlist_items_request_youtube_video_youtube_video_id_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_playlist_items_request_youtube_video_youtube_video_id_fkey ON public.playlist_items_request_youtube_video USING btree (youtube_video_id);


--
-- TOC entry 4868 (class 1259 OID 21250107)
-- Name: youtube_video_description_normalized_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX youtube_video_description_normalized_idx ON public.youtube_video USING gin (description_normalized public.gin_trgm_ops);


--
-- TOC entry 4869 (class 1259 OID 21250108)
-- Name: youtube_video_title_normalized_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX youtube_video_title_normalized_idx ON public.youtube_video USING gin (title_normalized public.gin_trgm_ops);


--
-- TOC entry 4878 (class 2606 OID 21250109)
-- Name: keyword_search_yt fk_keyword_search_yt_keyword; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_search_yt
    ADD CONSTRAINT fk_keyword_search_yt_keyword FOREIGN KEY (keyword_id) REFERENCES public.keyword(keyword_id);


--
-- TOC entry 4879 (class 2606 OID 21250114)
-- Name: keyword_search_yt fk_keyword_search_yt_search_yt; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_search_yt
    ADD CONSTRAINT fk_keyword_search_yt_search_yt FOREIGN KEY (search_yt_id) REFERENCES public.search_yt(search_yt_id);


--
-- TOC entry 4880 (class 2606 OID 21250119)
-- Name: keyword_talent fk_keyword_talent_keyword; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_talent
    ADD CONSTRAINT fk_keyword_talent_keyword FOREIGN KEY (keyword_id) REFERENCES public.keyword(keyword_id);


--
-- TOC entry 4881 (class 2606 OID 21250124)
-- Name: keyword_talent fk_keyword_talent_talent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keyword_talent
    ADD CONSTRAINT fk_keyword_talent_talent FOREIGN KEY (talent_id) REFERENCES public.talent(talent_id);


--
-- TOC entry 4886 (class 2606 OID 21250129)
-- Name: search_yt_youtube_video fk_search_youtube_youtube_video_youtube_video; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_yt_youtube_video
    ADD CONSTRAINT fk_search_youtube_youtube_video_youtube_video FOREIGN KEY (youtube_video_id) REFERENCES public.youtube_video(youtube_video_id) ON DELETE CASCADE;


--
-- TOC entry 4885 (class 2606 OID 21250134)
-- Name: search_yt fk_search_yt_parent_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_yt
    ADD CONSTRAINT fk_search_yt_parent_id FOREIGN KEY (parent_id) REFERENCES public.search_yt(search_yt_id);


--
-- TOC entry 4887 (class 2606 OID 21250139)
-- Name: search_yt_youtube_video fk_search_yt_youtube_video_search_yt; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_yt_youtube_video
    ADD CONSTRAINT fk_search_yt_youtube_video_search_yt FOREIGN KEY (search_yt_id) REFERENCES public.search_yt(search_yt_id);


--
-- TOC entry 4888 (class 2606 OID 21250144)
-- Name: youtube_channel_stats fk_youtube_channel_stats_youtube_channel; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_stats
    ADD CONSTRAINT fk_youtube_channel_stats_youtube_channel FOREIGN KEY (youtube_channel_id) REFERENCES public.youtube_channel(youtube_channel_id);


--
-- TOC entry 4889 (class 2606 OID 21250149)
-- Name: youtube_channel_talent fk_youtube_channel_talent_talent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_talent
    ADD CONSTRAINT fk_youtube_channel_talent_talent FOREIGN KEY (talent_id) REFERENCES public.talent(talent_id);


--
-- TOC entry 4890 (class 2606 OID 21250154)
-- Name: youtube_channel_talent fk_youtube_channel_talent_youtube_channel; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_channel_talent
    ADD CONSTRAINT fk_youtube_channel_talent_youtube_channel FOREIGN KEY (youtube_channel_id) REFERENCES public.youtube_channel(youtube_channel_id);


--
-- TOC entry 4892 (class 2606 OID 21250159)
-- Name: youtube_video_keyword fk_youtube_video_keyword_keyword; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_keyword
    ADD CONSTRAINT fk_youtube_video_keyword_keyword FOREIGN KEY (keyword_id) REFERENCES public.keyword(keyword_id);


--
-- TOC entry 4893 (class 2606 OID 21250164)
-- Name: youtube_video_keyword fk_youtube_video_keyword_youtube_video_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_keyword
    ADD CONSTRAINT fk_youtube_video_keyword_youtube_video_id FOREIGN KEY (youtube_video_id) REFERENCES public.youtube_video(youtube_video_id) ON DELETE CASCADE;


--
-- TOC entry 4894 (class 2606 OID 21250169)
-- Name: youtube_video_stats fk_youtube_video_stats_youtube_video_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_stats
    ADD CONSTRAINT fk_youtube_video_stats_youtube_video_id FOREIGN KEY (youtube_video_id) REFERENCES public.youtube_video(youtube_video_id) ON DELETE CASCADE;


--
-- TOC entry 4891 (class 2606 OID 21250174)
-- Name: youtube_video fk_youtube_video_youtube_channel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video
    ADD CONSTRAINT fk_youtube_video_youtube_channel_id FOREIGN KEY (youtube_channel_id) REFERENCES public.youtube_channel(youtube_channel_id) ON DELETE CASCADE;


--
-- TOC entry 4895 (class 2606 OID 21250179)
-- Name: youtube_video_youtube_video fk_youtube_video_youtube_video_clip; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_youtube_video
    ADD CONSTRAINT fk_youtube_video_youtube_video_clip FOREIGN KEY (clip) REFERENCES public.youtube_video(youtube_video_id);


--
-- TOC entry 4896 (class 2606 OID 21250184)
-- Name: youtube_video_youtube_video fk_youtube_video_youtube_video_source; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.youtube_video_youtube_video
    ADD CONSTRAINT fk_youtube_video_youtube_video_source FOREIGN KEY (source) REFERENCES public.youtube_video(youtube_video_id);


--
-- TOC entry 4882 (class 2606 OID 21250189)
-- Name: playlist_items_request playlist_items_request_playlist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.playlist_items_request
    ADD CONSTRAINT playlist_items_request_playlist_id_fkey FOREIGN KEY (playlist_id) REFERENCES public.youtube_channel(playlist_id);


--
-- TOC entry 4883 (class 2606 OID 21250194)
-- Name: playlist_items_request_youtube_video playlist_items_request_youtube_video_playlist_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.playlist_items_request_youtube_video
    ADD CONSTRAINT playlist_items_request_youtube_video_playlist_request_id_fkey FOREIGN KEY (playlist_items_request_id) REFERENCES public.playlist_items_request(playlist_items_request_id);


--
-- TOC entry 4884 (class 2606 OID 21250199)
-- Name: playlist_items_request_youtube_video playlist_items_request_youtube_video_youtube_video_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.playlist_items_request_youtube_video
    ADD CONSTRAINT playlist_items_request_youtube_video_youtube_video_id_fkey FOREIGN KEY (youtube_video_id) REFERENCES public.youtube_video(youtube_video_id) ON DELETE CASCADE;


--
-- TOC entry 5048 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: -
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2025-07-10 16:56:19

--
-- PostgreSQL database dump complete
--

