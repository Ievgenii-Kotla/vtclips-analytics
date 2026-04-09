const defaults = {
  "graphic": {
    "type": "text",
    "left": "right",
    "bottom": 0,
    "style": {
      "text": "vtc.com",
      "fontSize": 10,
      "fill": "#999",
      "opacity": 0.2
    }
  }
}
export const chartBuilders = {
  allVideosDaily: (chartData) => ({
    ...defaults,
    "title": {
      "text": "Daily Video Uploads (HoloEn)",
      "subtext": "Clips, animations, news, source videos, etc. related to talents",
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "3%",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "show": true,
          "alignWithLabel": true,
          "interval": (index, value) => value.endsWith('-01-01'),
        },
        "axisLabel": {
          "interval": (index, value) => value.endsWith('-01-01'),
          "formatter": value => value.slice(0, 4),
          "hideOverlap": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "series": [
      {
        "name": "Videos",
        "type": "bar",
        "data": chartData.series,
        "markLine": {
          symbol: 'none',
          lineStyle: {
            color: '#888',
            type: 'dashed',
            width: 1
          },
          label: {
            show:true,
            position: 'insideEndTop',
            distance: 0,
            formatter: '{b}',
            color: '#888',
            fontWeight: 'normal',
          },
          "data": [
            { "name": 'Myth debut ', "xAxis": '2020-09-12' },
            { "name": 'IRyS debut ', "xAxis": '2021-07-11' },
            { "name": 'Council debut ', "xAxis": '2021-08-23'},
            { "name": 'Advent debut ', "xAxis": '2023-07-30' },
            { "name": 'Justice debut ', "xAxis": '2024-06-21' }
          ]
        }
      }
    ],
    "dataZoom": [
      {
        "type": "inside",
        "xAxisIndex": 0,
        "moveOnMouseMove": true,
        "moveOnMouseWheel": false,
        "minSpan": 1
      }
    ],
  }),
  activeClippersMonthly: (chartData) => ({
    ...defaults,
    "title": {
      "text": "Active Channels Monthly"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "3%",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "alignWithLabel": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "series": [
      {
        "name": "Channels",
        "type": "bar",
        "data": chartData.series
      }
    ]
  }),
  videosPerTalentMonthly: (chartData) => ({
    ...defaults,
    "title": {
      "text": "Videos Per Talent Monthly"
    },
    "tooltip": {
      "trigger": "item",
      "axisPointer": {
        "type": "shadow"
      },
      "formatter": "{b}<br/>{a}: {c}"
    },
    "legend": {
      "top": 30,
      "type": "scroll"
    },
    "grid": {
      "top": "70",
      "left": "40",
      "right": "20",
      "bottom": "50",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "alignWithLabel": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "series": chartData.series
  }),
  videosGroupShareMonthly: (chartData) => ({
     "title": {
      "text": "Monthly Video Share by Talent Group"
    },
    "tooltip": {
      "trigger": "item",
      "axisPointer": {
        "type": "shadow"
      },
      "formatter": "{b}<br/>{a}: {c} <br/> vids: {videos_num}"
    },
    "legend": {
      "top": 30,
      "type": "scroll"
    },
    "grid": {
      "top": "70",
      "left": "40",
      "right": "20",
      "bottom": "50",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "alignWithLabel": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "series": chartData.series
  }),
  clipsPerChannelDistribution: (chartData) => ({
    "title": {
      "text": "Channel Count by Number of Clips"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "3%",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "alignWithLabel": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "dataZoom": [
        {
            "type": "inside",
            "xAxisIndex": 0,
            "moveOnMouseMove": true,
            "moveOnMouseWheel": false,
            "minSpan": 1
        }
    ],
    "series": [
      {
        "name": "Channels",
        "type": "scatter",
        "data": chartData.series
      }
    ]
  }),
  cumCountSVideosPerTalentDaily: (chartData) => ({
    "title": {
      "text": "Original Videos Per Talent Cumulative"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
        "position": function (point, params, dom, rect, size) {
        return ['0%', '-20%'];
      },
      "formatter": function(params) {
        params.sort((a, b) => b.value - a.value);

        let result = 'Date (YYYY-MM-DD): ' + params[0].axisValueLabel + '<br/>';
        params.forEach(item => {
          if (typeof item.value === 'number') {
            result += '<div style="display:flex; justify-content:space-between; width:250px">'
              + '<span>' + item.marker + ' ' + item.seriesName + '</span>'
              + '<b style="margin-left:15px">' + item.value + '</b></div>';
          }
        });
        return result;
      }
    },
    "legend": {},
    "xAxis": {
      "type": 'category',
      "data": chartData.xLabels
    },
    "yAxis": {
      "type": 'value'
    },
    "dataZoom": [
      {
        "type": "inside",
        "xAxisIndex": 0,
        "moveOnMouseMove": true,
        "moveOnMouseWheel": false,
        "minSpan": 1
      }
    ],
    "series": chartData.series
  }),
  cumCountDVideosPerTalentDaily: (chartData) => ({
    "title": {
      "text": "Clips Per Talent Cumulative"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
        "position": function (point, params, dom, rect, size) {
        return ['0%', '-20%'];
      },
      "formatter": function(params) {
        params.sort((a, b) => b.value - a.value);

        let result = 'Date (YYYY-MM-DD): ' + params[0].axisValueLabel + '<br/>';
        params.forEach(item => {
          if (typeof item.value === 'number') {
            result += '<div style="display:flex; justify-content:space-between; width:250px">'
              + '<span>' + item.marker + ' ' + item.seriesName + '</span>'
              + '<b style="margin-left:15px">' + item.value + '</b></div>';
          }
        });
        return result;
      }
    },
    "legend": {},
    "xAxis": {
      "type": 'category',
      "data": chartData.xLabels
    },
    "yAxis": {
      "type": 'value'
    },
    "dataZoom": [
      {
        "type": "inside",
        "xAxisIndex": 0,
        "moveOnMouseMove": true,
        "moveOnMouseWheel": false,
        "minSpan": 1
      }
    ],
    "series": chartData.series
  }),
    countDVideosAboutTalentPerDChannel: (chartData) => ({
    ...defaults,
    "title": {
      "text": chartData.titleText,
      "subtext": chartData.titleSubText
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll"
    },
    "grid": {
      "top": "70",
      "left": "40",
      "right": "20",
      "bottom": "50",
      "containLabel": true
    },
    "xAxis": [
      {
        "type": "category",
        "data": chartData.xLabels,
        "axisTick": {
          "alignWithLabel": true
        }
      }
    ],
    "yAxis": [
      {
        "type": "value"
      }
    ],
    "series": chartData.series
  }),
  countMentionsOneTalentPerDChannel: (chartData) => ({
    ...defaults,
    "title": {
      "text": chartData.titleText,
      "subtext": chartData.titleSubText
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll"
    },
    "grid": {
      "top": "70",
      "left": "40",
      "right": "20",
      "bottom": "50",
      "containLabel": true
    },
    "xAxis": {
        "type": "value",
    },
    "yAxis": {
        "type": "category",
        "axisLabel": {"show": false},
        "axisTick": {"show": false},
        "data": chartData.yLabels
    },
    "series": chartData.series
  }),
    countMentionsOneTalentPerDedicatedDChannel: (chartData) => ({
    ...defaults,
    "title": {
      "text": chartData.titleText,
      "subtext": chartData.titleSubText
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll"
    },
    "grid": {
      "top": "70",
      "left": "40",
      "right": "20",
      "bottom": "50",
      "containLabel": true
    },
    "xAxis": {
        "type": "value",
    },
    "yAxis": {
        "type": "category",
        "axisLabel": {"show": false},
        "axisTick": {"show": false},
        "data": chartData.yLabels
    },
    "series": chartData.series
  }),
  mentionsOneTalentMonthlyTopByTotal: (chartData) => ({
    ...defaults,
    "title": chartData.titleInfo,
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll",
      "top": "bottom",
      "show": false
    },
    "grid": chartData.grid,
    "xAxis": chartData.x_axis,
    "yAxis": chartData.y_axis,
    "series": chartData.series
  }),
  mentionsOneTalentMonthlyTopByLately: (chartData) => ({
    ...defaults,
    "title": chartData.titleInfo,
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll",
      "top": "bottom",
      "show": false
    },
    "grid": chartData.grid,
    "xAxis": chartData.x_axis,
    "yAxis": chartData.y_axis,
    "series": chartData.series
  }),
};
