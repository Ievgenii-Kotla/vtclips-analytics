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
      "text": "Daily video uploads · HoloEN",
      "subtext": "Clips, animations, news, source videos, etc. related to talents",
      "itemGap": 5
    },
    animationThreshold: Infinity, // Force animation. Could be taxing.
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
        "type": "value",
        "min": 0,
        "max": Math.ceil(Math.max(...chartData.series) / 100) * 100
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
            fontSize: 14,
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
        "minSpan": 1,
        "preventDefaultMouseMove": false,
      }
    ],
  }),
  activeClippersMonthly: (chartData) => ({
    ...defaults,
    "title": {
      "text": "Active channels per month · HoloEN",
      "subtext": "Channels that posted videos related to HoloEN talents",
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      formatter: params => {
        const date = params[0].name.slice(0, 7); // the x-axis value
        const lines = params.map(p => `${p.marker} ${p.seriesName}: ${p.value}`);
        return [date, ...lines].join('<br/>');
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
        "name": "Channels",
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
            fontSize: 14,
          },
          "data": [
            { "name": 'Myth debut ', "xAxis": '2020-09-01' },
            { "name": 'IRyS debut ', "xAxis": '2021-07-01' },
            { "name": 'Council debut ', "xAxis": '2021-08-01'},
            { "name": 'Advent debut ', "xAxis": '2023-07-01' },
            { "name": 'Justice debut ', "xAxis": '2024-06-01' }
          ]
        }
      }
    ]
  }),
  videosPerTalentMonthly: (chartData) => ({
    ...defaults,
    "title": {
      "text": "Video uploads by HoloEN talent"
    },
    "tooltip": {
      "trigger": "item",
      "axisPointer": {
        "type": "shadow"
      },
      "formatter": "{b}<br/>{a}: {c}"
    },
    "legend": {
      "bottom": 10,
      "type": "scroll",
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
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
    "series": chartData.series
  }),
  videosGroupShareMonthly: (chartData) => ({
    "title": {
      "text": "Video uploads by HoloEN generation",
      "subtext": "Share of total uploads · Each bar adds up to 100%",
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      formatter: params => {
        const date = params[0].name.slice(0, 7); // the x-axis value
        const lines = params
          .filter(p => p.value !== null && p.value !== undefined)
          .map(p => `${p.marker} ${p.seriesName}: ${p.value}%`)
        return [date, ...lines].join('<br/>');
      }
    },
    "legend": {
      "bottom": 10,
      "type": "scroll"
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
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
    "series": chartData.series.map((s, index) => ({
      ...s,
      label: {
        show: window.chartWidth > 600
      }
    }))
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
      "text": "Cumulative source videos by talent",
      "subtext": "Videos posted by the talent.",
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
        "position": function (point, params, dom, rect, size) {
        return ['0%', '-20%'];
      },
      "formatter": function(params) {
        params.sort((a, b) => b.value - a.value);

        let result = '' + params[0].axisValueLabel + '<br/>';
        params.forEach(item => {
          if (typeof item.value === 'number') {
            result += '<div style="display:flex; justify-content:space-between; width:240px">'
              + '<span>' + item.marker + ' ' + item.seriesName + '</span>'
              + '<b style="margin-left:15px">' + item.value + '</b></div>';
          }
        });
        return result;
      }
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
      "containLabel": true
    },
    "legend": {
      "bottom": 10,
      "type": "scroll"
    },
    "xAxis": {
      "type": 'category',
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
      "text": "Cumulative related videos by talent",
      "subtext": "Videos related to the talent.",
      "itemGap": 5
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

        let result = '' + params[0].axisValueLabel.slice(0, 7) + '<br/>';
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
     "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
      "containLabel": true
    },
    "legend": {
      "bottom": 10,
      "type": "scroll"
    },
    "xAxis": {
      "type": 'category',
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
      "subtext": chartData.titleSubText,
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + params[0].axisValueLabel.slice(0, 7) + '<br/>';
        params.forEach(item => {
          if (typeof item.value === 'number') {
            result += '<div style="display:flex; justify-content:space-between;">'
              + '<span>' + item.marker + ' ' + item.seriesName + '</span>'
              + '<b style="margin-left:15px">' + item.value + '</b></div>';
          }
        });
        return result;
      }
    },
    "legend": {
      "bottom": 10,
      "type": "scroll"
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
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
    "series": chartData.series
  }),
  countMentionsOneTalentPerDChannel: (chartData) => ({
    ...defaults,
    "title": {
      "text": chartData.titleText,
      "subtext": chartData.titleSubText,
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "formatter": "{b}<br>Videos: <b>{c}</b>",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll"
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "3%",
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
      "subtext": chartData.titleSubText,
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "legend": {
      "type": "scroll",
      "bottom": 10,
    },
    "grid": {
      "left": "3%",
      "right": "4%",
      "bottom": "8%",
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
