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
const ENDPOINTS = {
  header: '/api/header-info',
  cards: '/api/tab/overview'  // GET -> [ { id, title, chartOption } , ... ]
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
const linksArea = document.getElementById('links-area');
let currentTab = 'overview';
let currentFetchController = null; // used to cancel slow fetches

// helper: clear active tab classes
function setActiveTab(buttonEl) {
  const buttons = tabsWrapper.querySelectorAll('[data-tab]');
  buttons.forEach(b => b.classList.toggle('tab-active', b === buttonEl));
  currentTab = buttonEl.getAttribute('data-tab');
}

// skeleton generator: create N skeleton card placeholders
function showSkeletons(count = 3) {
  clearCharts()
  linksArea.innerHTML = '';
  cardsArea.innerHTML = '';
  for (let i=0;i<count;i++) {
    const cardEl = document.createElement('article');
    cardEl.className = 'card bg-base-200/40 border border-base-200 p-4 shadow-sm transition-opacity fade';
    cardEl.style.opacity = '0';
    cardEl.innerHTML = `
      <div class="relative">
        <div class="w-full" style="height:512px;"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="h-10 w-10 rounded-full skeleton"></div>
          Loading...
        </div>
      </div>
    `;
    cardsArea.appendChild(cardEl);
    requestAnimationFrame(() => {
      cardEl.style.opacity = '1';
    });
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
    } catch (e) {
      console.warn('Chart init failed for card.id ', card.id, e);
    } finally {
      // hide loader overlay
      const loader = document.getElementById(`loader-${card.id}`);
      if (loader) loader.style.display = 'none';
    }
  }
}

function tick(ms=0){ return new Promise(r => setTimeout(r, ms)); }

function escapeHtml(s='') {
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

async function loadTab(tabId, talentName) {
  if (currentFetchController) {
    try { currentFetchController.abort(); } catch(e){}
  }
  currentFetchController = new AbortController();
  const signal = currentFetchController.signal;

  document.getElementById('controls-area').innerHTML = '';
  showSkeletons(2);
  try {
    if (tabId === 'talent') {
      const res1 = await fetch('/api/talent_selector', {signal, cache: 'no-cache'});
      if (!res1.ok) throw new Error('selector fetch failed');
      const selectorData = await res1.json()
      document.getElementById('controls-area').innerHTML = `
        <select class="select select-bordered" id="talent-selector">
          ${selectorData.options.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join("")}
        </select>
      `;
      const selector = document.getElementById('talent-selector');
      if (selector.value === '') {
        talentName = 'Calliope';
      }
      selector.value = talentName;
      window.history.replaceState({}, '', `/talent?name=${encodeURIComponent(talentName)}`);
    }
    showSkeletons(2);
    const url = talentName == null
      ? `/api/tab/${encodeURIComponent(tabId)}`
      : `/api/tab/${encodeURIComponent(tabId)}?name=${encodeURIComponent(talentName)}`;
    const res = await fetch(url, {signal, cache: 'no-cache'});
    if (!res.ok) throw new Error('tab fetch failed');
    const tabData = await res.json();
    const cardsData = tabData.charts;
    const linksInfo = tabData.linksInfo;

    await renderCards(cardsData);
    if (tabData?.linksInfo) {
      await renderLinks(linksInfo);
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      return;
    }
    console.error('Load tab failed:', err);
    cardsArea.innerHTML = `<div class="text-warning">Failed to load content.</div>`;
  } finally {
    currentFetchController = null;
  }

}

function renderLinks(linksInfo) {
  const html = linksInfo.map(([channelTitle, channelURL, iconUrl]) => `
    <a href="${channelURL}" class="flex items-center gap-3 p-2 hover:bg-base-200 transition-colors" target="_blank" rel="noopener">
      <img src="${iconUrl}" referrerpolicy="no-referrer" class="w-10 h-10 rounded-full object-cover" />
      <span class="text-sm font-medium">${channelTitle}</span>
    </a>
  `).join("");

  const container = document.getElementById('links-area');
  container.innerHTML = `
    <div class="card bg-base-200/40 border border-base-200 shadow-sm flex flex-col divide-y-2 divide-base-content/10">
      <div class="p-2 text-sm font-semibold text-base-content/60">Channel links (opens in a new tab)</div>
      ${html}
    </div> 
    `;
}

function parsePath(pathname, search) {
  const tabId = pathname.slice(1).split('/')[0];
  const params = new URLSearchParams(search);
  return {
    tabId: tabId,
    talentName: params.get('name') || 'Calliope',
    params: params
  }
}

// tab click listener
tabsWrapper.addEventListener('click', (ev) => {
  const btn = ev.target.closest('[data-tab]');
  if (!btn) return;
  const tabId = btn.getAttribute('data-tab');
  if (!tabId || tabId === currentTab) return;
  const query = tabId === 'talent' ? '?name=Calliope' : '';
  window.history.pushState({}, '', `/${encodeURIComponent(tabId)}${query}`);
  setActiveTab(btn);
  loadTab(tabId, 'Calliope');
});

// direct URL listener
document.addEventListener('DOMContentLoaded', async () => {
  const {tabId, talentName, params} = parsePath(window.location.pathname, window.location.search)
  const btn = tabsWrapper.querySelector(`[data-tab="${tabId}"]`);
  if (btn) {
    setActiveTab(btn);
    await loadTab(tabId, talentName);
  } else {
    window.history.replaceState({}, '', '/overview');
    const defaultBtn = tabsWrapper.querySelector(`[data-tab="overview"]`);
    setActiveTab(defaultBtn);
    loadTab('overview');
  }
});

// theme toggle listener
document.getElementById("theme-toggle").addEventListener("change", (e) => {
  const {tabId, talentName, params} = parsePath(window.location.pathname, window.location.search)
  const theme = e.target.checked ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  window.__dashboard.loadTab(tabId, talentName);
});

// history navigation listener
window.addEventListener('popstate', () => {
  const {tabId, talentName, params} = parsePath(window.location.pathname, window.location.search)
  const btn = tabsWrapper.querySelector(`[data-tab="${tabId}"]`);
  setActiveTab(btn)
  loadTab(tabId, talentName);
});

// selector listener
document.getElementById('controls-area').addEventListener('change', async (event) => {
  if (event.target.id === 'talent-selector') {
    const selectedValue = event.target.value;
    showSkeletons(2);
    const res = await fetch('/api/talent_charts_and_links/' + selectedValue, {cache: 'no-cache'});
    window.history.pushState({}, '', `/talent?name=${encodeURIComponent(selectedValue)}`);
    const data = await res.json();
    renderCards(data.charts);
    renderLinks(data.linksInfo);
    console.log('User selected:', selectedValue);
  }
});

// expose some functions for debug in console (optional)
window.__dashboard = { loadTab, loadHeader };
})();
