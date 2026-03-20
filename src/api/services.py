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

def mutate_fuwamoco_colors(colors):
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

def mutate_fuwamoco_wide(wide):
    """Remove 'mococo' column and rename fuwawa column"""

    fuwawa_key = [k for k in wide.columns if "fuwawa" in k.lower()]
    mococo_key = [k for k in wide.columns if "mococo" in k.lower()]
    wide = wide.rename(columns={fuwawa_key[0]: "FUWAMOCO"})
    del wide[mococo_key[0]]
    return wide

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
def jinja(request: Request):
    contex = {
        "navigation": [
            {"href": "/home", "caption": "Home"},
            {"href": "/about", "caption": "About"},
        ],
        "a_variable": "value from a_variable in jinja template",
        "request": request,

    }
    return templates.TemplateResponse("home.html", contex)


def daisy(request: Request):
    return templates.TemplateResponse("daisy.html", {"request": request})


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

def tab_2025(conn):
    talent_id = 6
    charts = [
        all_clips_daily(conn),
        active_clippers_monthly(conn),
        mentions_one_talent_monthly(conn, talent_id=talent_id),
        mentions_one_talent_total(conn, talent_id=talent_id),
    ]
    tab_data = {
        "charts": charts,
        "selector": {
            "options": [
                "kronii",
                "bob"
            ]
        }
    }
    return tab_data

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

    colors = mutate_fuwamoco_colors(colors)
    wide = mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "bar",
            "stack": "total",
            "barWidth": "60%",
            "label": {
                "show": False
            },
            "emphasis": {
                "focus": "series"
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
                "label": {
                  "show": True
                },
                "emphasis": {
                  "focus": "series"
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

    colors = mutate_fuwamoco_colors(colors)
    wide = mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "line",
            "showSymbol": False,
            "emphasis": {
                "focus": "series",
                "label": {
                    "show": True,
                    "formatter": "{a}: {c}"
                }
            },
            "blur": {
                "label": {
                    "show": False
                }
            },
            "label": {
                "show": False
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
    all_dates = pd.date_range(df["pub_date"].min(), df["pub_date"].max(), freq="D").date
    wide = wide.reindex(all_dates).ffill()
    wide = wide.replace([np.nan, np.inf, -np.inf], None)

    colors = mutate_fuwamoco_colors(colors)
    wide = mutate_fuwamoco_wide(wide)

    series = [
        {
            "name": talent,
            "type": "line",
            "showSymbol": False,
            "emphasis": {
                "focus": "series",
                "label": {
                    "show": True,
                    "formatter": "{a}: {c}"
                }
            },
            "blur": {
                "label": {
                    "show": False
                }
            },
            "label": {
                "show": False
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
        CASE WHEN t.d_channel_id IS NULL THEN 'OTHER' ELSE tm.d_channel_title END AS d_channel_title,
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

    order = df.sort_values("d_channel_rank")["d_channel_title"].unique()
    df["d_channel_title"] = pd.Categorical(df["d_channel_title"], categories=order, ordered=True)

    talent_name = df["talent_name"].iloc[0]
    del df["talent_name"]

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
                "color": "#4A4A4A" if d_channel_title == "OTHER" else None
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
            "titleText": f"Monthly count of videos related to {talent_name}",
            "titleSubText": f"{TOP_N} biggest all-time contributors highlighted"
        }
    }
    return chart_data

def mentions_one_talent_total(conn, talent_id=1):
    TOP_N = 15
    query = """
    SELECT 
        d_channel_title, 
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
    print(talent_color)
    del df["talent_color"]

    df = df.sort_values("total_mentions", ascending=True)
    categories = df["d_channel_title"].to_list()
    mentions = df["total_mentions"].to_list()
    series = [{
            "type": "bar",
            "label": {
                "show": True,
                "position": "insideLeft",
                "formatter": "{b}",
                "color": "#fff",
                "textBorderColor": "#333",
                "textBorderWidth": 2
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
            "titleText": f"Channels that made the most videos related to {talent_name}",
            "titleSubText": f"All-time"
        }
    }
    return chart_data
