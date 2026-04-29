const isTouch = navigator.maxTouchPoints > 0;
const formatDate = str => {
  const parts = str.split('-');
  if (parts.length === 3) {
    const date = new Date(parts[0], parts[1] - 1, parts[2]);
    return date.toLocaleString('en-GB', { month: 'long', day: 'numeric', year: 'numeric' });
  } else {
    const date = new Date(parts[0], parts[1] - 1);
    return date.toLocaleString('en-GB', { month: 'long', year: 'numeric' });
  }
};
const defaults = {
  "graphic": {
    "type": "text",
    "left": "right",
    "bottom": 0,
    "style": {
      "text": "holoclipstats.com",
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
      "text": "Video uploads related to HoloEN",
      "subtext": "Clips, animations, news, source videos, etc.",
      "itemGap": 5
    },
    animationThreshold: Infinity, // Force animation. Could be taxing.
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + formatDate(params[0].axisValueLabel) + '<br/>';
        params.forEach(item => {
          result += '<div style="display:flex; justify-content:space-between;">'
            + '<span>' + item.marker + ' ' + 'Channels: ' + '</span>'
            + '<b style="margin-left:15px">' + item.value + '</b></div>';
        });
        return result;
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
            color: '#808080',
            type: 'dashed',
            width: 1
          },
          label: {
            show:true,
            position: 'insideEndTop',
            distance: 0,
            formatter: '{b}',
            color: '#808080',
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
      "text": "Active channels related to HoloEN",
      "subtext": "Channels that posted videos related to HoloEN talents",
      "itemGap": 5
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + formatDate(params[0].axisValueLabel.slice(0, 7)) + '<br/>';
        params.forEach(item => {
          result += '<div style="display:flex; justify-content:space-between;">'
            + '<span>' + item.marker + ' ' + 'Channels: ' + '</span>'
            + '<b style="margin-left:15px">' + item.value + '</b></div>';
        });
        return result;
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
            color: '#808080',
            type: 'dashed',
            width: 1
          },
          label: {
            show:true,
            position: 'insideEndTop',
            distance: 0,
            formatter: '{b}',
            color: '#808080',
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
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      formatter: params => {
        const date = formatDate(params[0].name.slice(0, 7));
        const lines = params
          .filter(p => p.value != null)
          .map(p => `<div style="display:flex; justify-content:space-between;">
            <span>${p.marker} ${p.seriesName}:</span>
            <b style="margin-left:15px">${p.value}</b></div>`)
          .reverse();
        return [date, ...lines].join('');
      }
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
    "series": chartData.series.map((s, index) => ({
      ...s,
      emphasis: { focus: isTouch ? 'none' : 'series' }
    }))
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
        const date = formatDate(params[0].name.slice(0, 7));
        const lines = params
          .filter(p => p.value != null)
          .map(p => `<div style="display:flex; justify-content:space-between;">
            <span>${p.marker} ${p.seriesName}:</span>
            <b style="margin-left:15px">${p.value}%</b></div>`)
          .reverse();
        return [date, ...lines].join('');
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
        show: window.chartWidth > 800
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
        let result = '' + formatDate(params[0].axisValueLabel) + '<br/>';
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
        "minSpan": 1,
        "preventDefaultMouseMove": false,
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
        let result = '' + formatDate(params[0].axisValueLabel.slice(0, 7)) + '<br/>';
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
        "minSpan": 1,
        "preventDefaultMouseMove": false,
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
        let result = '' + formatDate(params[0].axisValueLabel.slice(0, 7)) + '<br/>';
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
    "series": chartData.series.map((s, index) => ({
      ...s,
      "label": { "offset": isTouch ? [0, 0] : [0, 2] }
    }))
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
      "axisPointer": {
        "type": "shadow"
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + params[0].axisValueLabel + '<br/>';
        params.forEach(item => {
          result += '<div style="display:flex; justify-content:space-between;">'
            + '<span>' + item.marker + ' ' + 'Videos: ' + '</span>'
            + '<b style="margin-left:15px">' + item.value + '</b></div>';
        });
        return result;
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
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + formatDate(params[0].axisValueLabel.slice(0, 7)) + '<br/>';
        params.forEach(item => {
          result += '<div style="display:flex; justify-content:space-between;">'
            + '<span>' + item.marker + ' ' + 'Videos: ' + '</span>'
            + '<b style="margin-left:15px">' + item.value + '</b></div>';
        });
        return result;
      }
    },
    "legend": {
      "type": "scroll",
      "top": "bottom",
      "show": false
    },
    "grid": chartData.grid,
    "xAxis": chartData.x_axis.map((d, index) => ({
      ...d,
      "axisTick": {
        "show": true,
        "alignWithLabel": true,
        "interval": (index, value) => value.endsWith('-01-01'),
      },
      "axisLabel": {
        "show": index === 4,
        "interval": (index, value) => value.endsWith('-01-01'),
        "formatter": value => value.slice(0, 4),
        "hideOverlap": true
      }
    })),
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
      },
      "confine": true,
      "formatter": function(params) {
        let result = '' + formatDate(params[0].axisValueLabel.slice(0, 7)) + '<br/>';
        params.forEach(item => {
          result += '<div style="display:flex; justify-content:space-between;">'
            + '<span>' + item.marker + ' ' + 'Videos: ' + '</span>'
            + '<b style="margin-left:15px">' + item.value + '</b></div>';
        });
        return result;
      }
    },
    "legend": {
      "type": "scroll",
      "top": "bottom",
      "show": false
    },
    "grid": chartData.grid,
    "xAxis": chartData.x_axis.map((d, index) => ({
      ...d,
      "axisTick": {
        "show": true,
        "alignWithLabel": true,
        "interval": (index, value) => value.endsWith('-01-01'),
      },
      "axisLabel": {
        "show": index === 4,
        "interval": (index, value) => value.endsWith('-01-01'),
        "formatter": value => value.slice(0, 4),
        "hideOverlap": true
      }
    })),
    "yAxis": chartData.y_axis,
    "series": chartData.series
  }),
  sVideosSingleTalentMonthly: (chartData) => ({
    ...defaults,
    "title": {
      "text": chartData.titleText,
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      },
      formatter: params => {
        const date = formatDate(params[0].name.slice(0, 7));
        const lines = params
          .filter(p => p.value != null)
          .map(p => `<div style="display:flex; justify-content:space-between;">
            <span>${p.marker} ${p.seriesName}:</span>
            <b style="margin-left:15px">${p.value}</b></div>`)
          .reverse();
        return [date, ...lines].join('');
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
    "series": chartData.series
  }),
};
