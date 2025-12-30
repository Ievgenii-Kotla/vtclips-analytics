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
      "text": "Daily Video Uploads (HoloEn)"
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
        "name": "Videos",
        "type": "bar",
        "data": chartData.series
      }
    ]
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
};
``