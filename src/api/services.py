from fastapi import Request
from fastapi.templating import Jinja2Templates
import json
from pathlib import Path

from pandas.core.groupby.base import groupby_other_methods
from starlette.responses import PlainTextResponse, JSONResponse
from datetime import date
import pandas as pd
import numpy as np

templates = Jinja2Templates(directory="src/api/templates")
BASE_DIR = Path(__file__).resolve().parent
CHART_TEMPLATE_DIR = BASE_DIR / "static" / "chart_templates"

def summary(conn=None):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT 'playlists_parsed', COUNT(*)
        FROM (
            SELECT playlist_id
            FROM playlist_items_request
            GROUP BY playlist_id
        ) as pirpi
        UNION ALL
        SELECT 'channels_exist', COUNT(*)
        FROM youtube_channel
        UNION ALL
        SELECT 'videos_exist', COUNT(*) 
        FROM youtube_video
        UNION ALL
        SELECT 'keywords_parsed', COUNT(*)
        FROM (
            SELECT q
            FROM search_yt
            GROUP BY q
        ) as syq;
        """)
        rows = cur.fetchall()
    return rows

def status():
    with open('/app/collector_info/state/api_quota_state.json', 'r') as f:
        quota_status = f.read()
    with open('/app/collector_info/logs/error.log', 'r') as f:
        error_log = f.read()
    with open('/app/collector_info/logs/warning.log', 'r') as f:
        warning_log = f.read()
    with open('/app/collector_info/logs/info.log', 'r') as f:
        info_log = f.read()

    return PlainTextResponse(
        f"""QUOTA_STATUS:\n {quota_status}\n\n
    ERRORS:\n {error_log}\n\n
    WARNINGS:\n {warning_log}\n\n
    INFO:\n {info_log}
    """
    )

def charts(request: Request):
    return templates.TemplateResponse("charts.html", {"request": request})

def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

def overview(conn):
    charts = [
        all_clips_daily(conn),
        active_clippers_monthly(conn),
        videos_per_talent_monthly(conn),
        videos_group_share_monthly(conn),
        cum_count_svideos_per_talent_daily(conn),
        cum_count_dvideos_per_talent_daily(conn),
    ]
    tab_data = {"charts": charts}
    return tab_data

def talent_tab(conn, talent_name:str):
    if talent_name is None:
        talent_name = 'Calliope'
    selector_options = talent_selector(conn)  # add the option changing when accessing the page with a direct link
    charts, channel_ids = talent_charts(conn, talent_name)
    links_info = talent_dchannel_info(conn, channel_ids)

    tab_data = {
        "charts": charts,
        "selector": selector_options,
        "linksInfo": links_info
    }
    return tab_data

def talent_charts_and_links(conn, talent_name:str):
    charts, channel_ids = talent_charts(conn, talent_name)
    links_info = talent_dchannel_info(conn, channel_ids)
    data = {
        "charts": charts,
        "linksInfo": links_info
    }
    return data

def talent_selector(conn):
    """Return information needed to build the talent selector."""

    query = """
        SELECT 
            first_name_eng, 
            display_name,
            neutral_color AS color 
        FROM talent 
        WHERE talent_id != 21 
        ORDER BY debut_datetime;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    selector = {
        "options": [{"value": row[0], "color": f"#{row[2]}", "label": f"{row[1]}"} for row in rows]
    }
    return selector

def talent_charts(conn, talent_name: str = "Calliope"):
    """Return information needed to build the charts."""
    talent_id = _name_to_id(conn, talent_name)

    charts_and_ids = [
        svideos_single_talent_monthly(conn, talent_id=talent_id),
        mentions_one_talent_monthly(conn, talent_id=talent_id),
        mentions_one_talent_total(conn, talent_id=talent_id),
        mentions_one_talent_dedicated_total(conn, talent_id=talent_id),
        mentions_one_talent_monthly_top_by_total(conn, talent_id=talent_id),
        mentions_one_talent_monthly_top_by_lately(conn, talent_id=talent_id),
    ]
    charts, channel_ids = zip(*charts_and_ids)
    channel_ids = list(set().union(*channel_ids))
    return charts, channel_ids

def talent_dchannel_info(conn, ids):
    query = """
    SELECT title, 'https://www.youtube.com/channel/' || youtube_channel_id, thumbnail_default
    FROM youtube_channel
    WHERE youtube_channel_id = ANY(%(ids)s);
    """
    with conn.cursor() as cur:
        cur.execute(query, {"ids": ids})
        rows = cur.fetchall()
    rows = sorted(rows, key=lambda r: r[0].lstrip())
    return rows

def about():
    data = """
<div>
  <p>
    Data is presented for entertainment purposes only.<br>
  </p>
  <br>
  <p>
    Title and description of a video is used to estimate who the video is about. The accuracy of this method doesn't reach 100%. That being said, the community is very diligent about linking source videos and talents and great effort was put into ensuring that the categorization is as accurate as possible. 
  </p><br>
</div>
<div>
  <p>
    The data is processed in 4 main steps.
  </p>
  <p>
    1. Find YouTube videos that have information in title or description that can point to a talent (VTuber) with high confidence. The keywords include:
    <ul style="list-style: disc; padding-left: 40px;">
      <li>links to a talent's YT channel</li> 
      <li>links to a YT video published by a talent</li>
    </ul>
    All channels and videos that were found are marked for further processing.
  </p>
  <p><br>
    2. Find all videos published by the marked channels and mark them for processing too.<br> 
    This ensures that videos with low confidence are also processed. For example videos or shorts with no links, but with talent's name in the title.
  </p>
  <p><br>
    3. Look through all marked videos and count occurrences of keywords in each video.
    <ul style="list-style: disc; padding-left: 40px;">
      <li>Keywords include: channel ids, channel handles, video ids, first names, last names, middle names, nicknames that are used often.</li>
      <li>Names in both English and Japanese are used.</li>
      <li>Very short keywords (like 'cc', 'gg') and common words (like 'rose', '森') are not used since they give to many false positives. That being said only a small set of keywords that is related to talents is excluded. For example 'ame', 'liz', 'bae' are still used.</li>
    </ul>
  </p>	
  <p><br>
    4. A few filters are applied to the counted keywords:
    <ul style="list-style: disc; padding-left: 40px;">
      <li>Keyword-matches that repeat across many consecutive videos of the same channel are removed.<br>
              This reduces false positives from channels that have a link or block of links that repeats across many videos.<br>
              (video descriptions that mention only 1 talent are left untouched)</li>
      <li>for each video-talent pair a score is calculated based on weights assigned to different keywords. For exampl, high-confidence keywords like IDs score higher than low-confidence keywords, keywords in titles generally score higher than keywords in descriptions. Video-talent pairs with low total score are removed.</li> 
      <li>if a video has more than 3 talents mentioned: video-talent pairs with the score lower than the third pair are removed. If there are more than 3 video-talent pairs that are tied for the third place - they are also removed. To put it simply: videos are matched with no more than 3 talents per video, in some cases no more than 5.</li>
    </ul>
  </p>
  <p><br>
    The data is processed bit by bit continuously over months, and is up to date at the time it is processed.<br> 
    This means that the changes to a video or a channel are not tracked here if they were made after processing. For example, a channel or a video that was deleted might still be in the data.<br>
  </p>
</div>
<br>
<div>
  Data update schedule:<br>
  <ul style="list-style: disc; padding-left: 40px;">
    <li>Searching for links to talent's YT channel - every 2 days. (~55% of the data)<br></li>
    <li>Finding videos published by marked channels - every month.(~45% of the data data)</li>
    <li>Searching for links to YT videos published by the talents - every 3 months.(~5% of the data data)<br></li>
  </ul>
</div>
    """
    return data

def contact():
    data = """
<style>
  .cf { display: flex; flex-direction: column; gap: 1rem; max-width: 420px; margin: 0 auto;}
  .cf label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.875rem; }
  .cf input, .cf textarea {
    font-family: inherit;
    font-size: 0.95rem;
    padding: 0.5rem 0.7rem;
    border: 1px solid #aaa;
    border-radius: 6px;
    background: transparent;
    color: inherit;
    outline: none;
  }
  .cf input:focus, .cf textarea:focus { border-color: currentColor; }
  .cf textarea { resize: vertical; min-height: 110px; }
  .cf button {
    font-family: inherit;
    font-size: 0.95rem;
    padding: 0.6rem;
    border: none;
    border-radius: 6px;
    background: currentColor;
    cursor: pointer;
    opacity: 0.9;
  }
  .cf button:hover { opacity: 0.7; }
  .cf button span { color: var(--bg, #fff); mix-blend-mode: difference; }
</style>

<form class="cf" action="https://api.web3forms.com/submit" method="POST">
  <input type="hidden" name="access_key" value="c8afeb80-cca5-44d8-a64e-67bc133c1d78">
  <label>Name <input type="text" name="name" placeholder="Jane Smith" required></label>
  <label>Email <input type="email" name="email" placeholder="jane@example.com" required></label>
  <label>Message <textarea name="message" placeholder="Your message..." required></textarea></label>
  <button type="submit"><span>Send</span></button>
</form>
    """
    return data

def header_info(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT youtube_video_id) FROM talent_youtube_video;")
        num = cur.fetchone()[0]
    return f"HoloEn related videos:\n {num:,}".replace(",", "\u00a0")

def tab_3(conn):
    charts = [
        videos_per_talent_monthly(conn),
    ]
    tab_data = {"charts": charts}
    return tab_data

def who_clips_my_oshi(conn):
    charts = [
        videos_group_share_monthly(conn),
    ]
    tab_data = {"charts": charts}
    return tab_data

def miscellaneous(conn):
    charts = [
        clips_per_channel_distribution(conn),
    ]
    tab_data = {"charts": charts}
    return tab_data

def sample_chart():
  path = CHART_TEMPLATE_DIR / "sample_chart1.json"
  with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
    return data

def all_clips_daily(conn):
    query = """SELECT * FROM chart_all_clips_day ORDER BY published_at_date;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis = []
    series = []
    for row in rows:
        x_axis.append(row[0].isoformat())
        series.append(row[1])

    chart_data = {
        "id": 1,
        "title": "overview of all clips posted by date",
        "builder": "allVideosDaily",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }

    return chart_data

#@apply_chart_defaults
def active_clippers_monthly(conn):
    query = """SELECT * FROM chart_active_clippers_monthly ORDER BY published_at_month;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis = []
    series = []
    for row in rows:
        x_axis.append(row[0].isoformat())
        series.append(row[1])

    chart_data = {
        "id": 2,
        "title": "clipper channels active monthly",
        "builder": "activeClippersMonthly",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }

    return chart_data

def clips_per_channel_distribution(conn):
    query = """SELECT * FROM chart_clips_per_channel_distribution ORDER BY clip_count;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis = []
    series = []
    for row in rows:
        x_axis.append(row[0])
        series.append(row[1])

    chart_data = {
        "id": 5,
        "title": "clips per channel",
        "builder": "clipsPerChannelDistribution",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }
    return chart_data

def videos_per_talent_monthly(conn):
    query = """SELECT * FROM chart_videos_per_talent_monthly ORDER BY published_at_month;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    order = df.sort_values("order_id")["talent_name"].unique()
    df["talent_name"] = pd.Categorical(df["talent_name"], categories=order, ordered=True)
    colors = (
        df[["talent_name", "color"]]
        .drop_duplicates()
        .assign(color=lambda x: '#' + x["color"])
        .set_index("talent_name")["color"]
        .to_dict()
    )
    wide = df.pivot(index="published_at_month", columns="talent_name", values="videos_num")
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    colors = _mutate_fuwamoco_colors(colors)
    wide = _mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "bar",
            "stack": "total",
            "barWidth": "80%",
            "label": {
                "show": False
            },
            "data": wide[talent].tolist(),
            "itemStyle": {
                "color": colors[talent]
            }
        }
        for talent in wide.columns
    ]
    x_axis = [d.isoformat() for d in wide.index.tolist()]

    chart_data = {
        "id": 3,
        "title": "videos per talent monthly",
        "builder": "videosPerTalentMonthly",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }
    return chart_data

def videos_group_share_monthly(conn):
    query = """SELECT * FROM chart_videos_group_share_monthly ORDER BY published_at_month;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    order = df.sort_values("order_id")["group_name"].unique()
    df["group_name"] = pd.Categorical(df["group_name"], categories=order, ordered=True)
    x_axis = df["published_at_month"].drop_duplicates().sort_values().tolist()
    series = []
    for group_name in df["group_name"].cat.categories:
        group_name_df = (
            df[df["group_name"] == group_name]
            .set_index("published_at_month")
            .reindex(x_axis)
        )
        series.append(
            {
                "name": group_name,
                "type": "bar",
                "stack": "total",
                "stackStrategy": 'all',
                "barWidth": "80%",
                "emphasis": {
                  "focus": "none",
                  "itemStyle": {
                    "borderWidth": 2,
                    "borderColor": '#ffffff',
                    "shadowBlur": 15,
                    "shadowColor": 'rgba(255,255,255,0.4)'
                  }
                },
                "data": [
                    {
                        "value": None if pd.isna(row.pct) else row.pct,
                        "videos_num": 0 if pd.isna(row.videos_num) else row.videos_num
                    }
                    for row in group_name_df.sort_values("published_at_month").itertuples()
                ]
            }
        )

    chart_data = {
        "id": 4,
        "title": "videos group share monthly",
        "builder": "videosGroupShareMonthly",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }
    return chart_data

def cum_count_svideos_per_talent_daily(conn):
    query = """SELECT * FROM chart_cum_count_svideos_per_talent_daily ORDER BY pub_date"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    order = df.sort_values("debut_datetime")["talent_name"].unique()
    df["talent_name"] = pd.Categorical(df["talent_name"], categories=order, ordered=True)
    colors = (
        df[["talent_name", "color"]]
        .drop_duplicates()
        .assign(color=lambda x: '#' + x["color"])
        .set_index("talent_name")["color"]
        .to_dict()
    )
    wide = df.pivot(index="pub_date", columns="talent_name", values="cum_sum")
    all_dates = pd.date_range(df["pub_date"].min(), df["pub_date"].max(), freq="D").date
    wide = wide.reindex(all_dates).ffill()
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    colors = _mutate_fuwamoco_colors(colors)
    wide = _mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "line",
            "showSymbol": False,
            "symbolSize": 8,
            "emphasis": {
                "focus": "series",
                "label": {
                    "show": True,
                    "formatter": "{a}",
                    "textStyle": {
                      "color": '#fff',
                      "fontSize": 12,
                      "fontWeight": 'bold',
                      "opacity": 1,
                      "textBorderColor": '#000',
                      "textBorderWidth": 2,
                      "textShadowColor": '#000',
                      "textShadowBlur": 3,
                    }
                }
            },
            "data": wide[talent].tolist(),
            "itemStyle": {
                "color": colors[talent]
            },
        }
        for talent in wide.columns
    ]
    x_axis = [d.isoformat() for d in wide.index.tolist()]

    chart_data = {
        "id": 5,
        "title": "cum count source videos per talent daily",
        "builder": "cumCountSVideosPerTalentDaily",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }

    return chart_data

def cum_count_dvideos_per_talent_daily(conn):
    query = """SELECT * FROM chart_cum_count_dvideos_per_talent_daily ORDER BY pub_date"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    order = df.sort_values("debut_datetime")["talent_name"].unique()
    df["talent_name"] = pd.Categorical(df["talent_name"], categories=order, ordered=True)
    colors = (
        df[["talent_name", "color"]]
        .drop_duplicates()
        .assign(color=lambda x: '#' + x["color"])
        .set_index("talent_name")["color"]
        .to_dict()
    )
    wide = df.pivot(index="pub_date", columns="talent_name", values="cum_sum")
    all_year_month = pd.date_range(df["pub_date"].min(), df["pub_date"].max(), freq="MS").date
    wide = wide.reindex(all_year_month).ffill()
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    colors = _mutate_fuwamoco_colors(colors)
    wide = _mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "line",
            "showSymbol": False,
            "symbolSize": 8,
            "emphasis": {
                "focus": "series",
                "label": {
                    "show": True,
                    "formatter": "{a}",
                    "textStyle": {
                      "color": '#fff',
                      "fontSize": 12,
                      "fontWeight": 'bold',
                      "opacity": 1,
                      "textBorderColor": '#000',
                      "textBorderWidth": 2,
                      "textShadowColor": '#000',
                      "textShadowBlur": 3,
                    }
                }
            },
            "data": wide[talent].tolist(),
            "itemStyle": {
                "color": colors[talent]
            },
        }
        for talent in wide.columns
    ]
    x_axis = [d.isoformat() for d in wide.index.tolist()]

    chart_data = {
        "id": 6,
        "title": "cum count derivative videos per talent daily",
        "builder": "cumCountDVideosPerTalentDaily",
        "data": {
            "xLabels": x_axis,
            "series": series
        }
    }

    return chart_data

def mentions_one_talent_monthly(conn, talent_id=1):
    TOP_N = 5
    query = """
    WITH top_rank AS (
        SELECT 
            d_channel_id, d_channel_rank
        FROM (
            SELECT 
                d_channel_id,
                RANK() OVER (ORDER BY SUM(talent_mentions_monthly) DESC) AS d_channel_rank
            FROM chart_group_talent_mentions_monthly
            WHERE talent_id = %(talent_id)s
            GROUP BY d_channel_id
        ) ranked
        WHERE d_channel_rank <= %(top_n)s
    ),
    data_window AS (
        SELECT date_trunc('month', (debut_datetime - interval '1 month')) AS data_start
        FROM talent
        WHERE talent_id = %(talent_id)s
    )
    SELECT 
        tm.talent_name,
        MIN(tm.talent_color) AS talent_color,
        CASE WHEN t.d_channel_id IS NULL THEN 'OTHER' ELSE tm.d_channel_title END AS d_channel_title,
        t.d_channel_id,
        t.d_channel_rank,
        tm.year_month,
        SUM(tm.talent_mentions_monthly) AS talent_mentions_monthly
    FROM chart_group_talent_mentions_monthly AS tm
    LEFT JOIN top_rank t USING (d_channel_id)
    WHERE 
        tm.talent_id = %(talent_id)s
        AND year_month < date_trunc('month', CURRENT_DATE)
        AND year_month >= (SELECT data_start FROM data_window)
    GROUP BY 
        tm.talent_id,
        tm.talent_name,
        t.d_channel_id,
        CASE WHEN t.d_channel_id IS NULL THEN 'OTHER' ELSE tm.d_channel_title END,
        t.d_channel_rank,
        tm.year_month
    ORDER BY year_month, t.d_channel_rank NULLS LAST;
    """
    with conn.cursor() as cur:
        cur.execute(query, {"top_n": TOP_N, "talent_id": talent_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)

    channel_ids = df['d_channel_id'].tolist()

    order = df.sort_values("d_channel_rank")["d_channel_title"].unique()
    df["d_channel_title"] = pd.Categorical(df["d_channel_title"], categories=order, ordered=True)

    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["talent_color"].iloc[0]}'
    del df["talent_color"]

    wide = df.pivot(index="year_month", columns="d_channel_title", values="talent_mentions_monthly")
    all_dates = pd.date_range(df["year_month"].min(), df["year_month"].max(), freq="MS").date
    wide = wide.reindex(all_dates)
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    series = [
        {
            "name": d_channel_title,
            "type": "bar",
            "stack": "total",
            "barWidth": "80%",
            "data": wide[d_channel_title].tolist(),
            "itemStyle": {
                "color": _mix_colors('#808080', talent_color, 0.075) if d_channel_title == "OTHER" else None,
            },
        }
        for d_channel_title in wide.columns
    ]
    x_axis = [d.isoformat() for d in wide.index.tolist()]

    chart_data = {
        "id": 7,
        "title": "mentions one talent monthly",
        "builder": "countDVideosAboutTalentPerDChannel",
        "data": {
            "xLabels": x_axis,
            "series": series,
            "titleText": f"Video uploads related to {talent_name}",
            "titleSubText": f"{TOP_N} biggest all-time contributors highlighted"
        }
    }
    return chart_data, channel_ids

def mentions_one_talent_total(conn, talent_id=1):
    TOP_N = 15
    query = """
    SELECT 
        d_channel_title, 
        d_channel_id,
        SUM(talent_mentions_monthly) AS total_mentions,
        MIN(talent_name) AS talent_name,
        MIN(talent_color) AS talent_color
    FROM chart_group_talent_mentions_monthly c
    WHERE talent_id = %(talent_id)s
    GROUP BY d_channel_id, d_channel_title
    ORDER BY total_mentions DESC
    LIMIT %(top_n)s;
    """
    with conn.cursor() as cur:
        cur.execute(query, {"top_n": TOP_N, "talent_id": talent_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["talent_color"].iloc[0]}'
    del df["talent_color"]
    channel_ids = df['d_channel_id'].tolist()
    del df["d_channel_id"]

    df = df.sort_values("total_mentions", ascending=True)
    categories = df["d_channel_title"].to_list()
    mentions = df["total_mentions"].to_list()
    series = [{
            "type": "bar",
            "label": {
                "show": True,
                "position": "insideLeft",
                # "offset": [0, 2],
                "formatter": "{b}",
                "fontSize": 14,
                "color": "#fff",
                "textBorderColor": "#333",
                "textBorderWidth": 2,
                "textShadowColor": 'rgba(0,0,0,0.8)',
                "textShadowBlur": 4,
            },
            "barWidth": "80%",
            "data": mentions,
            "itemStyle": {
                "color": talent_color,
            }
    }]
    y_axis = categories

    chart_data = {
        "id": 8,
        "title": "mentions one talent total",
        "builder": "countMentionsOneTalentPerDChannel",
        "data": {
            "yLabels": y_axis,
            "series": series,
            "titleText": f"Top contributors · {talent_name}",
            "titleSubText": f"By related uploads · All time",
        }
    }
    return chart_data, channel_ids

def mentions_one_talent_dedicated_total(conn, talent_id=1):
    TOP_N = 15
    MENTIONS_THRESHOLD = 10
    RATIO_THRESHOLD = 0.5
    query = """
    WITH data_window AS (
        SELECT date_trunc('month', (debut_datetime - interval '1 month')) AS data_start
        FROM talent
        WHERE talent_id = %(talent_id)s
    ),
    total_mentions AS (
        SELECT 
            d_channel_id,
            SUM(talent_mentions_monthly) AS total_mentions
        FROM chart_group_talent_mentions_monthly
        WHERE 
            talent_id = %(talent_id)s
            AND year_month < date_trunc('month', CURRENT_DATE)
            AND year_month >= (SELECT data_start FROM data_window)
        GROUP BY d_channel_id
        HAVING SUM(talent_mentions_monthly) >= %(mentions_threshold)s
        ORDER BY total_mentions DESC

    ),
    total_videos AS (
        SELECT 
            tv.d_channel_id, 
            SUM(total_videos_monthly) AS total_videos
        FROM (
            SELECT DISTINCT d_channel_id, year_month, total_videos_monthly
            FROM chart_group_talent_mentions_monthly c
            JOIN total_mentions t USING (d_channel_id)
            WHERE 
                year_month < date_trunc('month', CURRENT_DATE)
                AND year_month >= (SELECT data_start FROM data_window)
        ) tv
        GROUP BY d_channel_id
        ORDER BY total_videos
    ),
    main_data AS (
        SELECT 
            tm.d_channel_id,
            tm.total_mentions,
            tv.total_videos,
            tm.total_mentions::numeric / NULLIF(tv.total_videos, 0) AS ratio,
            RANK() OVER (ORDER BY total_mentions DESC, tm.total_mentions::numeric / NULLIF(tv.total_videos, 0) DESC) AS d_channel_rank
        FROM total_mentions tm
        JOIN total_videos tv USING (d_channel_id)
        WHERE tm.total_mentions::numeric / NULLIF(tv.total_videos, 0) > %(ratio_threshold)s
        ORDER BY total_mentions DESC, ratio DESC
        LIMIT %(top_n)s
    )
    SELECT
        c.d_channel_title,
        md.d_channel_id,
        md.total_mentions,
        md.total_videos,
        md.ratio,
        md.d_channel_rank,
        c.talent_name,
        c.talent_color
    FROM main_data md
    LEFT JOIN LATERAL ( 
        SELECT 
            d_channel_title,
            talent_name, 
            talent_color 
        FROM chart_group_talent_mentions_monthly
        WHERE 
            talent_id = %(talent_id)s
            AND d_channel_id = md.d_channel_id
        LIMIT 1
    ) c ON true;
    """
    values = {
        "top_n": TOP_N,
        "talent_id": talent_id,
        "mentions_threshold": MENTIONS_THRESHOLD,
        "ratio_threshold": RATIO_THRESHOLD,
    }
    with conn.cursor() as cur:
        cur.execute(query, values)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["talent_color"].iloc[0]}'
    del df["talent_color"]
    channel_ids = df['d_channel_id'].tolist()
    del df["d_channel_id"]

    df = df.sort_values(["total_mentions", "ratio"], ascending=True)
    categories = df["d_channel_title"].to_list()
    mentions = df["total_mentions"].to_list()
    other_videos = [a - b for a, b in
                    zip(df["total_videos"].to_list(), df["total_mentions"].to_list(), strict=True)]
    series = [
        {
            "name": series["name"],
            "type": "bar",
            "stack": "total",
            "label": {
                "show": series["show_label"],
                "position": "insideLeft",
                "offset": [0, 2],
                "formatter": "{b}",
                "fontSize": 14,
                "color": "#fff",
                "textBorderColor": "#333",
                "textBorderWidth": 2,
                "textShadowColor": 'rgba(0,0,0,0.8)',
                "textShadowBlur": 4,
            },
            "barWidth": "80%",
            "data": series["data"],
            "itemStyle": {
                "color": series["color"],
            }
        }
        for series in (
            {
                "name": f"Videos related to {talent_name}",
                "color": talent_color,
                "data":mentions,
                "show_label": True,
            },
            {
                "name": "Other videos",
                "color": _mix_colors('#808080', talent_color, 0.075),
                "data": other_videos,
                "show_label": False,
            }
        )
    ]
    y_axis = categories

    chart_data = {
        "id": 9,
        "title": "mentions one talent dedicated total",
        "builder": "countMentionsOneTalentPerDedicatedDChannel",
        "data": {
            "yLabels": y_axis,
            "series": series,
            "titleText": f"Most dedicated · {talent_name}",
            "titleSubText": f"By related uploads · {int(RATIO_THRESHOLD*100)}%+ related videos · Since talent's debut",
        }
    }
    return chart_data, channel_ids

def mentions_one_talent_monthly_top_by_total(conn, talent_id=1):
    TOP_N = 5
    query = """
    WITH channel AS (
        SELECT d_channel_id, SUM(talent_mentions_monthly) AS total_mentions 
        FROM chart_group_talent_mentions_monthly c
        WHERE 
            talent_id = %(talent_id)s
            -- AND year_month > DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 MONTH')
        GROUP BY d_channel_id
        ORDER BY total_mentions DESC
        LIMIT %(top_n)s
    )
    SELECT 
        cg.talent_name,
        cg.talent_color,
        cg.d_channel_id,
        cg.d_channel_title,
        cg.talent_mentions_monthly,
        cg.year_month,
        c.total_mentions,
        date_trunc('month', (t.debut_datetime - interval '1 month'))::date AS x_axis_start,
        date_trunc('month', CURRENT_DATE)::date AS x_axis_end
    FROM chart_group_talent_mentions_monthly cg
    JOIN channel c ON cg.d_channel_id = c.d_channel_id AND cg.talent_id = %(talent_id)s
    JOIN talent t ON t.talent_id = %(talent_id)s
    ORDER BY cg.year_month, cg.d_channel_id;
    """
    values = {
        "top_n": TOP_N,
        "talent_id": talent_id,
    }
    with conn.cursor() as cur:
        cur.execute(query, values)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["talent_color"].iloc[0]}'
    del df["talent_color"]
    x_axis_start = f'{df["x_axis_start"].iloc[0]}'
    del df["x_axis_start"]
    x_axis_end = f'{df["x_axis_end"].iloc[0]}'
    del df["x_axis_end"]
    channel_ids = df['d_channel_id'].tolist()
    del df["d_channel_id"]

    order = df.sort_values("total_mentions", ascending=False)["d_channel_title"].unique()
    df["d_channel_title"] = pd.Categorical(df["d_channel_title"], categories=order, ordered=True)

    wide = df.pivot(index="year_month", columns="d_channel_title", values="talent_mentions_monthly")
    all_dates = pd.date_range(x_axis_start, x_axis_end, freq="MS").date
    wide = wide.reindex(all_dates)
    wide = wide.replace([np.nan, np.inf, -np.inf], 0)

    sub_charts_num = len(wide.columns)
    x_axis_labels = [d.isoformat() for d in wide.index.tolist()]

    talent_colored_facets = True
    if not talent_colored_facets:
        talent_color = None

    unified_y_scale = False
    if unified_y_scale:
        y_axis_min = 0
        y_axis_max = max([max(wide[column_name].tolist()) for column_name in  wide.columns])
    else:
        y_axis_min = None
        y_axis_max = None

    grid = [
        {
            "top": f"{((75 // sub_charts_num) + 2 ) * i + 14}%",
            "height": f"{60 // sub_charts_num}%",
            "left": "3%",
            "right": "4%",
            "bottom": "3%"
        }
        for i in range(sub_charts_num)
    ]
    x_axis = [
        {
            "gridIndex": i,
            "type": "category",
            "data": x_axis_labels,
        }
        for i in range(sub_charts_num)
    ]
    y_axis = [
        {
            "gridIndex": i,
            "type": "value",
            "min": y_axis_min,
            "max": y_axis_max,
        }
        for i in range(sub_charts_num)
    ]
    series = [
        {
            "name": d_channel_title,
            "type": "bar",
            "xAxisIndex": i,
            "yAxisIndex": i,
            "data": wide[d_channel_title].tolist(),
            "itemStyle": {
                "color": talent_color,
            },
        }
        for i, d_channel_title in enumerate(wide.columns)
    ]
    title = [
        {
            "text": f"Upload history related to {talent_name}",
            "subtext":  f"{TOP_N} top all-time contributors. Y-axis varies per panel",
            "itemGap": 4
        },
        *[
            {
                "text": d_channel_title,
                "top": f"{((75 // sub_charts_num) + 2) * i + 10.5}%",
                "left": "center",
                "textStyle": {
                    "fontSize": 14,
                }
            }
            for i, d_channel_title in enumerate(wide.columns)
        ]
    ]

    chart_data = {
        "id": 10,
        "title": "mentions_one_talent_monthly_top_by_total",
        "builder": "mentionsOneTalentMonthlyTopByTotal",
        "data": {
            "grid": grid,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "xLabels": x_axis,
            "series": series,
            "titleInfo": title,
        }
    }

    return chart_data, channel_ids

def mentions_one_talent_monthly_top_by_lately(conn, talent_id=1):
    TOP_N = 5
    query = """
    WITH channel AS (
        SELECT d_channel_id, SUM(talent_mentions_monthly) AS total_mentions 
        FROM chart_group_talent_mentions_monthly c
        WHERE 
            talent_id = %(talent_id)s
            AND year_month > DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 MONTH')
        GROUP BY d_channel_id
        ORDER BY total_mentions DESC
        LIMIT %(top_n)s
    )
    SELECT 
        cg.talent_name,
        cg.talent_color,
        cg.d_channel_id,
        cg.d_channel_title,
        cg.talent_mentions_monthly,
        cg.year_month,
        c.total_mentions,
        date_trunc('month', (t.debut_datetime - interval '1 month'))::date AS x_axis_start,
        date_trunc('month', CURRENT_DATE)::date AS x_axis_end
    FROM chart_group_talent_mentions_monthly cg
    JOIN channel c ON cg.d_channel_id = c.d_channel_id AND cg.talent_id = %(talent_id)s
    JOIN talent t ON t.talent_id = %(talent_id)s
    ORDER BY cg.year_month, cg.d_channel_id;
    """
    values = {
        "top_n": TOP_N,
        "talent_id": talent_id,
    }
    with conn.cursor() as cur:
        cur.execute(query, values)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    if not rows:
        return [], []

    df = pd.DataFrame(rows, columns=columns)
    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["talent_color"].iloc[0]}'
    del df["talent_color"]
    x_axis_start = f'{df["x_axis_start"].iloc[0]}'
    del df["x_axis_start"]
    x_axis_end = f'{df["x_axis_end"].iloc[0]}'
    del df["x_axis_end"]
    channel_ids = df['d_channel_id'].tolist()
    del df["d_channel_id"]

    order = df.sort_values("total_mentions", ascending=False)["d_channel_title"].unique()
    df["d_channel_title"] = pd.Categorical(df["d_channel_title"], categories=order, ordered=True)

    wide = df.pivot(index="year_month", columns="d_channel_title", values="talent_mentions_monthly")
    all_dates = pd.date_range(x_axis_start, x_axis_end, freq="MS").date
    wide = wide.reindex(all_dates)
    wide = wide.replace([np.nan, np.inf, -np.inf], 0)

    sub_charts_num = len(wide.columns)
    x_axis_labels = [d.isoformat() for d in wide.index.tolist()]

    talent_colored_facets = True
    if not talent_colored_facets:
        talent_color = None

    unified_y_scale = False
    if unified_y_scale:
        y_axis_min = 0
        y_axis_max = max([max(wide[column_name].tolist()) for column_name in  wide.columns])
    else:
        y_axis_min = None
        y_axis_max = None

    grid = [
        {
            "top": f"{((75 // sub_charts_num) + 2 ) * i + 14}%",
            "height": f"{60 // sub_charts_num}%",
            "left": "3%",
            "right": "4%",
            "bottom": "3%"
        }
        for i in range(sub_charts_num)
    ]
    x_axis = [
        {
            "gridIndex": i,
            "type": "category",
            "data": x_axis_labels,
        }
        for i in range(sub_charts_num)
    ]
    y_axis = [
        {
            "gridIndex": i,
            "type": "value",
            "min": y_axis_min,
            "max": y_axis_max,
        }
        for i in range(sub_charts_num)
    ]
    series = [
        {
            "name": d_channel_title,
            "type": "bar",
            "xAxisIndex": i,
            "yAxisIndex": i,
            "data": wide[d_channel_title].tolist(),
            "itemStyle": {
                "color": talent_color,
            },
        }
        for i, d_channel_title in enumerate(wide.columns)
    ]
    title = [
        {
            "text": f"Upload history related to {talent_name}",
            "subtext": f"{TOP_N} top contributors in the last 3 month. Y-axis varies per panel",
            "itemGap": 4
        },
        *[
            {
                "text": d_channel_title,
                "top": f"{((75 // sub_charts_num) + 2) * i + 10.5}%",
                "left": "center",
                "textStyle": {
                    "fontSize": 14,
                }
            }
            for i, d_channel_title in enumerate(wide.columns)
        ]
    ]

    chart_data = {
        "id": 11,
        "title": "mentions_one_talent_monthly_top_by_lately",
        "builder": "mentionsOneTalentMonthlyTopByLately",
        "data": {
            "grid": grid,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "xLabels": x_axis,
            "series": series,
            "titleInfo": title,
        }
    }

    return chart_data, channel_ids

def svideos_single_talent_monthly(conn, talent_id=1):
    query = """
        SELECT * 
        FROM chart_videos_per_talent_monthly 
        WHERE order_id = %(talent_id)s
            AND published_at_month < date_trunc('month', CURRENT_DATE)
        ORDER BY published_at_month;
    """
    with conn.cursor() as cur:
        cur.execute(query, {"talent_id": talent_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]
    talent_color = f'#{df["color"].iloc[0]}'
    del df["color"]

    wide = df.pivot(index="published_at_month", columns="order_id", values="videos_num")
    # hide incomplete data of the current month
    today = date.today()
    if today.month > 1:
        end_date = today.replace(month=today.month - 1, day=1)
    else:
        end_date = today.replace(year=today.year - 1, month=12, day=1)

    full_range = pd.date_range(
        start=wide.index.min(),
        end=end_date,
        freq="MS"
    ).date
    wide = wide.reindex(full_range)
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    series = [
        {
            "name": talent_name,
            "type": "bar",
            "label": {
                "show": False
            },
            "data": wide[talent].tolist(),
            "itemStyle": {
                "color": talent_color
            }
        }
        for talent in wide.columns
    ]
    x_axis = [d.isoformat() for d in wide.index.tolist()]

    # regression all-time
    y = wide[talent_id].fillna(0).to_numpy(dtype=float)
    index = max([i if v else 0 for i, v in enumerate(y, start=1)])
    # exclude the last two months of activity for graduated talents
    if index < len(wide.index) - 1:
        index -= 2
    x = np.arange(index)
    y = y[:index]

    mask = ~np.isnan(y)
    m, b = np.polyfit(x[mask], y[mask], 1)
    y_pred = m * x + b
    y_pred = [round(v, 1) if v >= 0 and np.isfinite(v) else None for v in y_pred]

    regression_series_all = {
        "name": f"{talent_name} (trend)",
        "label": { "show": False },
        "color": "#808080",
        "type": "line",
        "smooth": True,
        "symbol": "none",
        "data": y_pred,
        "lineStyle": {
            "type": "dashed",
            "width": 1
        },
        "tooltip": {
            "show": True
        }
    }
    series.append(regression_series_all)

    # regression lately
    # x = x[-24:]
    # y = y[-24:]
    # mask = ~np.isnan(y)
    # m, b = np.polyfit(x[mask], y[mask], 1)
    # y_pred_lately = m * x + b
    # y_pred_lately = [v if v >= 0 and np.isfinite(v) else None for v in y_pred_lately]
    #
    # regression_series_lately = {
    #     "name": f"{talent_name} (trend)",
    #     "label": { "show": False },
    #     "color": "#808080",
    #     "type": "line",
    #     "smooth": True,
    #     "symbol": "none",
    #     "data": y_pred_lately,
    #     "lineStyle": {
    #         "type": "dashed",
    #         "width": 2
    #     },
    #     "tooltip": {
    #         "show": False
    #     }
    # }
    # series.append(regression_series_lately)

    chart_data = {
        "id": 12,
        "title": "source videos per single talent monthly",
        "builder": "sVideosSingleTalentMonthly",
        "data": {
            "xLabels": x_axis,
            "series": series,
            "titleText": f"Video uploads by {talent_name}",
        }
    }
    return chart_data, []

def _mutate_fuwamoco_colors(colors):
    """Replace fuwamoco related hex-value colors with ECharts friendly gradient of the two colors"""

    fuwawa_key = [k for k in colors.keys() if "fuwawa" in k.lower()]
    mococo_key = [k for k in colors.keys() if "mococo" in k.lower()]
    if fuwawa_key and mococo_key:
        fuwawa_color = colors[fuwawa_key[0]]
        mococo_color = colors[mococo_key[0]]

        color = {
            "color": {
                "type": "linear",
                "x": 0,
                "y": 0,
                "x2": 1,
                "y2": 0,
                "colorStops": [
                    { "offset": 0, "color": fuwawa_color},
                    { "offset": 0.30, "color": fuwawa_color},
                    { "offset": 0.70, "color": mococo_color},
                    { "offset": 1, "color": mococo_color}
                ],
                "global": False
            }
        }
        colors["FUWAMOCO"] = color["color"]
        del colors[mococo_key[0]]
        del colors[fuwawa_key[0]]
    return colors

def _mutate_fuwamoco_wide(wide):
    """Remove 'mococo' column and rename fuwawa column"""

    fuwawa_key = [k for k in wide.columns if "fuwawa" in k.lower()]
    mococo_key = [k for k in wide.columns if "mococo" in k.lower()]
    wide = wide.rename(columns={fuwawa_key[0]: "FUWAMOCO"})
    del wide[mococo_key[0]]
    return wide

def _name_to_id(conn, talent_name:str):
    with conn.cursor() as cur:
        cur.execute("SELECT talent_id FROM talent WHERE first_name_eng ILIKE %(talent_name)s;",
                    {"talent_name": talent_name})
        row = cur.fetchone()
        if row:
            talent_id = row[0]
        else:
            talent_id = 5
    return talent_id


def _mix_colors(color1: str, color2: str, t: float = 0.5) -> str:
    """
    Mix two hex colors.
    t=0.0 returns color1, t=1.0 returns color2, t=0.5 returns midpoint.
    """
    color1 = color1.lstrip('#')
    color2 = color2.lstrip('#')

    r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
    r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)

    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)

    return f'#{r:02x}{g:02x}{b:02x}'
