import { chartBuilders } from './chart-builders.js';

const charts = {};

let resizeTimer;
window.addEventListener('resize', () => {
clearTimeout(resizeTimer);
resizeTimer = setTimeout(() => {
  Object.values(charts).forEach(c => c && c.resize && c.resize());
}, 100);
});

function clearCharts() {
Object.values(charts).forEach(chart => {
if (chart) chart.dispose();  // frees memory, removes event listeners
});
Object.keys(charts).forEach(k => delete charts[k]);  // clear references
}

(function(){
// === Config / endpoints ===
const ENDPOINTS = {
  header: '/header-info',         // GET -> { text: "..." } or raw string
  cards: '/overview'  //'/cards?tab=',           // GET -> [ { id, title, chartOption } , ... ]
};

// === Header info fetch ===
const headerEl = document.getElementById('header-info');
async function loadHeader() {
  try {
    const res = await fetch(ENDPOINTS.header, {cache: 'no-cache'});
    if (!res.ok) throw new Error('Header fetch failed');
    const contentType = res.headers.get('content-type') || '';
    let txt = '';
    if (contentType.includes('application/json')) {
      const json = await res.json();
      txt = (json.text ?? JSON.stringify(json));
    } else {
      txt = await res.text();
    }
    headerEl.textContent = txt;
  } catch (e) {
    headerEl.textContent = '—';
    console.warn('Header load error', e);
  }
}
loadHeader();

// === Tabs + cards logic ===
const tabsWrapper = document.getElementById('tabs-wrapper');
const cardsArea = document.getElementById('cards-area');
let currentTab = 'overview';
let currentFetchController = null; // used to cancel slow fetches

// helper: clear active tab classes
function setActiveTab(buttonEl) {
  const buttons = tabsWrapper.querySelectorAll('[data-tab]');
  buttons.forEach(b => b.classList.toggle('tab-active', b === buttonEl));
}

// skeleton generator: create N skeleton card placeholders
function showSkeletons(count = 3) {
  cardsArea.innerHTML = '';
  for (let i=0;i<count;i++) {
    const sk = document.createElement('article');
    sk.className = 'card p-4 animate-fade fade-enter';
    sk.innerHTML = `
      <div class="flex justify-between items-center mb-3">
        <div class="h-4 w-40 rounded skeleton"></div>
        <div class="h-4 w-20 rounded skeleton"></div>
      </div>
      <div class="h-64 rounded-lg skeleton"></div>
    `;
    cardsArea.appendChild(sk);
  }
}

// render cards from server response
// expected cardsData: [ {id, title, chartOption}, ... ]
async function renderCards(cardsData) {
  cardsArea.innerHTML = '';
  for (const card of cardsData) {
    const cardEl = document.createElement('article');
    cardEl.className = 'card bg-base-200/40 border border-base-200 p-4 shadow-sm transition-opacity fade';
    cardEl.style.opacity = '0';
    // card layout: title + chart container with loading overlay
    cardEl.innerHTML = `
      <div class="relative">
        <div id="chart-${card.id}" class="w-full" style="height:512px;"></div>
        <div id="loader-${card.id}" class="absolute inset-0 flex items-center justify-center">
          <div class="h-10 w-10 rounded-full skeleton"></div>
        </div>
      </div>
    `;
    cardsArea.appendChild(cardEl);

    // small enter animation
    requestAnimationFrame(() => {
      cardEl.style.opacity = '1';
    });

    // initialize chart from provided option object (server-side)
    // server may return full echarts option in card.chartOption
    try {
      // wait a tick so DOM paints loader
      await tick(10);
      const chartDiv = document.getElementById(`chart-${card.id}`);
      if (!chartDiv) continue;
      // initialize echarts
      let chart;
      if (localStorage.getItem("theme") === "dark") {
        chart = echarts.init(chartDiv, 'dark');
        chart.setOption({ backgroundColor: '#1b2127' }, { notMerge: true });
      } else {
        chart = echarts.init(chartDiv);
      }
      charts[card.id] = chart;
      const chartOption = chartBuilders[card.builder](card.data)
      // chartOption should be provided by server (so server controls chart content)
      if (chartOption) {
        chart.setOption(chartOption);
      } else if (card.chartConfigEndpoint) {
        // optional: server provided endpoint to fetch config per-chart
        const cfgRes = await fetch(card.chartConfigEndpoint);
        const cfg = await cfgRes.json();
        chart.setOption(cfg);
      } else {
        // no config: show empty state
        chart.showLoading();
        chart.hideLoading();
      }
    console.log("LOGchart.getOption().series", chart.getOption().series)
    console.log("LOGchart.getOption().xaxis", chart.getOption().xAxis)
    console.log("asdf", chart.getOption().series.length)
    } catch (e) {
      console.warn('Chart init failed for card.id ', card.id, e);
    } finally {
      // hide loader overlay
      const loader = document.getElementById(`loader-${card.id}`);
      if (loader) loader.style.display = 'none';
    }
  }
}

// utility: make a short delay (ms)
function tick(ms=0){ return new Promise(r => setTimeout(r, ms)); }

// escape HTML minimal
function escapeHtml(s='') {
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

// fetch cards for a tab and render; simple abort logic to handle rapid tab clicks
async function loadTab(tabId) {
  // cancel previous fetch (simple fast-click protection)
  if (currentFetchController) {
    try { currentFetchController.abort(); } catch(e){}
  }
  currentFetchController = new AbortController();
  const signal = currentFetchController.signal;

  clearCharts();
  // show skeletons while loading (number can be adjusted)
  showSkeletons(2);
    // this is set up for use with /blabla=tabs? type of endpoint
    // and it should be. I need to change my fastapi endpoint to reflect that.
    // or maybe i need to rethink this part. Like it is now, all charts will be handled by a single endpoint.
    // I cound probably easily change it to a separate endpoint for each tab
    // Since I already have encodeURIComponent(tabId bit here
  try {
  // const res = await fetch(ENDPOINTS.cards + encodeURIComponent(tabId), {signal, cache: 'no-cache'});
    const res = await fetch('/' + encodeURIComponent(tabId), {signal, cache: 'no-cache'});
    //const res = await fetch(ENDPOINTS.cards, {signal, cache: 'no-cache'});
    console.log('loadTab:', tabId, res.ok, res);
    if (!res.ok) throw new Error('cards fetch failed');
    const cardsData = await res.json();
    // expected: array of objects { id, title, chartOption }
    await renderCards(cardsData);
  } catch (err) {
    if (err.name === 'AbortError') {
      // fetch was aborted due to a new tab click -- silently ignore
      return;
    }
    console.error('Load tab failed:', err);
    cardsArea.innerHTML = `<div class="text-warning">Failed to load content.</div>`;
  } finally {
    currentFetchController = null;
  }
}

// attach tab click handlers
tabsWrapper.addEventListener('click', (ev) => {
  const btn = ev.target.closest('[data-tab]');
  if (!btn) return;
  const tabId = btn.getAttribute('data-tab');
  if (!tabId || tabId === currentTab) return;
  currentTab = tabId;
  setActiveTab(btn);
  loadTab(tabId);
});

// load default tab on page load
document.addEventListener('DOMContentLoaded', () => {
  // set Tab 1 active (first button)
  const firstBtn = tabsWrapper.querySelector('[data-tab]');
  if (firstBtn) setActiveTab(firstBtn);
  // initial load for default tab (tab1)
  loadTab(currentTab);
});

// Toggle logic
document.getElementById("theme-toggle").addEventListener("change", (e) => {
  const theme = e.target.checked ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  window.__dashboard.loadTab(currentTab);
});

// expose some functions for debug in console (optional)
window.__dashboard = { loadTab, loadHeader };
})();
