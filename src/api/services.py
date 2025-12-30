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

def apply_chart_defaults(func):
    def wrapper(*args, **kwargs):
        def merge_dicts(d1, d2):
            for key, value in d2.items():
                if isinstance(value, dict) and key in d1 and isinstance(d1[key], dict):
                    merge_dicts(d1[key], value)
                else:
                    if key not in d1:
                        d1[key] = value
            return d1

        path = CHART_TEMPLATE_DIR / "chart_defaults.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chart = func(*args, **kwargs)
        merge_dicts(chart, data)
        return chart
    return wrapper

def mutate_fuwamoco_colors(colors):
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
    ]
    return charts

def tab_2(conn):
    charts = [
        sample_chart(),
    ]
    return charts

def miscellaneous(conn):
    charts = [
        clips_per_channel_distribution(conn),
    ]
    return charts

@apply_chart_defaults
def sample_chart():
  path = CHART_TEMPLATE_DIR / "sample_chart1.json"
  with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
    return data

@apply_chart_defaults
    query = """SELECT * FROM chart_all_clips_day ORDER BY published_at_date;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis_data = []
    series_data = []
    for row in rows:
        x_axis_data.append(row[0].isoformat())
        series_data.append(row[1])

    path = CHART_TEMPLATE_DIR / "all_clips_day_bar.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["chartOption"]["xAxis"][0]["data"] = x_axis_data
    data["chartOption"]["series"][0]["data"] = series_data
    return data

@apply_chart_defaults
def active_clippers_monthly(conn):
    query = """SELECT * FROM chart_active_clippers_monthly ORDER BY published_at_month;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis_data = []
    series_data = []
    for row in rows:
        x_axis_data.append(row[0].isoformat())
        series_data.append(row[1])

    path = CHART_TEMPLATE_DIR / "active_clippers_monthly.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["chartOption"]["xAxis"][0]["data"] = x_axis_data
    data["chartOption"]["series"][0]["data"] = series_data
    return data

@apply_chart_defaults
def clips_per_channel_distribution(conn):
    query = """SELECT * FROM chart_clips_per_channel_distribution ORDER BY clip_count;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    x_axis_data = []
    series_data = []
    for row in rows:
        x_axis_data.append(row[0])
        series_data.append(row[1])

    path = CHART_TEMPLATE_DIR / "clips_per_channel_distribution.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["chartOption"]["xAxis"][0]["data"] = x_axis_data
    data["chartOption"]["series"][0]["data"] = series_data
    return data

@apply_chart_defaults
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
    path = CHART_TEMPLATE_DIR / "videos_per_talent_monthly.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["chartOption"]["series"] = series
    data["chartOption"]["xAxis"][0]["data"] = wide.index.tolist()
    return data

@apply_chart_defaults
def videos_group_share_monthly(conn):
    query = """SELECT * FROM chart_videos_group_share_monthly ORDER BY published_at_month;"""
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=columns)
    order = df.sort_values("order_id")["group_name"].unique()
    df["group_name"] = pd.Categorical(df["group_name"], categories=order, ordered=True)
    x_axis = df["published_at_month"].drop_duplicates().sort_values()
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

    path = CHART_TEMPLATE_DIR / "videos_group_share_monthly.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["chartOption"]["series"] = series
    data["chartOption"]["xAxis"][0]["data"] = x_axis.tolist()
    return data

