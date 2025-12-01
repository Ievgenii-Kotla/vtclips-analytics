from fastapi import Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="src/api/templates")

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

def sample_chart():
    return {
        'id': 1,
        'title': 'sample chart',
        'chartOption': {

          "title": {
            "text": 'Stacked Area Chart'
          },
          "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
              "type": 'cross',
              "label": {
                "backgroundColor": '#ff0000'
              }
            }
          },
          "legend": {
            "data": ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
          },
          "toolbox": {
            "feature": {
              "saveAsImage": {}
            }
          },
          "xAxis": [
            {
              "type": 'category',
              "boundaryGap": False,
              "data": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            }
          ],
          "yAxis": [
            {
              "type": 'value'
            }
          ],
          "series": [
            {
              "name": 'Email',
              "type": 'line',
              "stack": 'Total',
              "areaStyle": {},
              "emphasis": {
                "focus": 'series'
              },
              "data": [120, 132, 101, 134, 90, 230, 210]
            },
            {
              "name": 'Union Ads',
              "type": 'line',
              "stack": 'Total',
              "areaStyle": {},
              "emphasis": {
                "focus": 'series'
              },
              "data": [220, 182, 191, 234, 290, 330, 310]
            },
            {
              "name": 'Video Ads',
              "type": 'line',
              "stack": 'Total',
              "areaStyle": {},
              "emphasis": {
                "focus": 'series'
              },
              "data": [150, 232, 201, 154, 190, 330, 410]
            },
            {
              "name": 'Direct',
              "type": 'line',
              "stack": 'Total',
              "areaStyle": {},
              "emphasis": {
                "focus": 'series'
              },
              "data": [320, 332, 301, 334, 390, 330, 320]
            },
            {
              "name": 'Search Engine',
              "type": 'line',
              "stack": 'Total',
              "label": {
                "show": True,
                "position": 'top'
              },
              "areaStyle": {},
              "emphasis": {
                "focus": 'series'
              },
              "data": [820, 932, 901, 934, 1290, 1330, 1320]
            }
          ]
        }
    }
