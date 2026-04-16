import {chartBuilders} from './chart-builders.js';

const charts = {};

function parsePath(pathname, search) {
  const tabId = pathname.slice(1).split('/')[0];
  const params = new URLSearchParams(search);
  return {
    tabId: tabId,
    talentName: params.get('name') || 'Calliope',
    params: params
  }
}

function clearCharts() {
  Object.values(charts).forEach(chart => { if (chart) chart.dispose();});
  Object.keys(charts).forEach(k => delete charts[k]);
}

function clearTabContent() {
  document.getElementById('controls-area').innerHTML = '';
  clearCharts();
  document.getElementById('cards-area').innerHTML = '';
  document.getElementById('links-area').innerHTML = '';
  document.getElementById('about-area').innerHTML = '';
  document.getElementById('contact-area').innerHTML = '';
}

(function () {
  const ENDPOINTS = {
    header: '/api/header-info',
    cards: '/api/tab/overview'
  };

  function tick(ms = 0) {
    return new Promise(r => setTimeout(r, ms));
  }

  function escapeHtml(s = '') {
    return String(s).replace(/[&<>"']/g, m => ({'&': '&amp;', '<': '&lt;', '>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function getCSSVar(name) {
  const color = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return `oklch(${color})`;
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
    <div class="card bg-base-200 border border-base-200 shadow-sm flex flex-col divide-y-2 divide-base-content/10">
      <div class="p-2 text-sm font-semibold text-base-content/60">Channel links (opens in a new tab)</div>
      ${html}
    </div> 
    `;
}

function updateSelectorColor(){
  const selector = document.getElementById('talent-selector');
  const selectedOption = selector.options[selector.selectedIndex];
  const color = selectedOption.dataset.color;

  selector.style.borderColor = `${color}`;
  selector.style.boxShadow = `0 0 0 2px ${color}40`;
  selector.style.outlineColor = `${color}00`;
}

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

const tabsWrapper = document.getElementById('tabs-wrapper');
const cardsArea = document.getElementById('cards-area');
const linksArea = document.getElementById('links-area');
let currentTab = 'overview';
let currentFetchController = null; // used to cancel slow fetches

function setActiveTab(buttonEl) {
  const buttons = tabsWrapper.querySelectorAll('[data-tab]');
  if (!buttonEl) {
    buttons.forEach(b => b.classList.remove('tab-active'));
    currentTab = null;
    return;
  }
  buttons.forEach(b => b.classList.toggle('tab-active', b === buttonEl));
  currentTab = buttonEl.getAttribute('data-tab');
}

function showSkeletons(count = 3) {
  clearCharts()
  linksArea.innerHTML = '';
  cardsArea.innerHTML = '';
  for (let i=0;i<count;i++) {
    const cardEl = document.createElement('article');
    cardEl.className = 'card bg-base-200 border border-base-200 p-4 shadow-sm transition-opacity fade';
    cardEl.style.opacity = '0';
    cardEl.innerHTML = `
      <div class="relative">
        <div class="w-full" style="height:512px;"></div>
        <div class="flex flex-col absolute inset-0 items-center justify-center">
          <span class="loading loading-dots loading-xl mr-2"></span>
          This might take a few seconds...
        </div>
      </div>
    `;
    cardsArea.appendChild(cardEl);
    requestAnimationFrame(() => {
      cardEl.style.opacity = '1';
    });
  }
}

async function renderCards(cardsData) {
  cardsArea.innerHTML = '';
  for (const card of cardsData) {
    const cardEl = document.createElement('article');
    cardEl.className = 'card bg-base-200 border border-base-200 p-2 shadow-sm';
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
    requestAnimationFrame(() => {
      cardEl.style.opacity = '1';
    });

    try {
      await tick(10);
      const chartDiv = document.getElementById(`chart-${card.id}`);
      if (!chartDiv) continue;
      let chart;
      if (localStorage.getItem("theme") === "dark") {
        chart = echarts.init(chartDiv, 'dark');
        chart.setOption({ backgroundColor: getCSSVar('--b2') }, { notMerge: true });
      } else {
        chart = echarts.init(chartDiv);
      }
      charts[card.id] = chart;
      const chartOption = chartBuilders[card.builder](card.data)
      if (chartOption) {
        chart.setOption(chartOption);
      } else if (card.chartConfigEndpoint) {
        const cfgRes = await fetch(card.chartConfigEndpoint);
        const cfg = await cfgRes.json();
        chart.setOption(cfg);
      } else {
        chart.showLoading();
        chart.hideLoading();
      }
    } catch (e) {
      console.warn('Chart init failed for card.id ', card.id, e);
    } finally {
      const loader = document.getElementById(`loader-${card.id}`);
      if (loader) loader.style.display = 'none';
    }
    window.chartWidth = Object.values(charts).find(c => c)?.getWidth() ?? 300;
  }
}

async function loadTab(tabId, talentName) {
  if (currentFetchController) {
    try { currentFetchController.abort(); } catch(e){}
  }
  currentFetchController = new AbortController();
  const signal = currentFetchController.signal;

  clearTabContent();
  try {
    if (tabId === 'about') {
      const res = await fetch('/api/about', {signal, cache: 'no-cache'});
      if (!res.ok) throw new Error('about_the_data fetch failed');
      const data = await res.text();
      document.getElementById('about-area').innerHTML = data;
      return
    }
    if (tabId === 'contact') {
      const res = await fetch('/api/contact', {signal, cache: 'no-cache'});
      if (!res.ok) throw new Error('contact fetch failed');
      const data = await res.text();
      document.getElementById('contact-area').innerHTML = data;
      return
    }
    showSkeletons(2);
    if (tabId === 'talent') {
      const res1 = await fetch('/api/talent_selector', {signal, cache: 'no-cache'});
      if (!res1.ok) throw new Error('selector fetch failed');
      const selectorData = await res1.json()
      document.getElementById('controls-area').innerHTML = `
        <select class="select select-bordered w-full text-center text-lg font-semibold" style="padding-left: 2.4rem"  id="talent-selector">
          ${selectorData.options.map(opt => `
            <option value="${opt.value}" data-color="${opt.color}">${opt.label}</option>`).join("")}
        </select>
      `;
      const selector = document.getElementById('talent-selector');
      if (selector.value === '') {
        talentName = 'Calliope';
      }
      selector.value = talentName;
      window.history.replaceState({}, '', `/talent?name=${encodeURIComponent(talentName)}`);
      updateSelectorColor();
    }

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
  const tabs = ["overview", "talent", "about", "contact"];
  const isTab = tabs.includes(tabId);
  const btn = tabsWrapper.querySelector(`[data-tab="${tabId}"]`);
  if (isTab) {
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
    updateSelectorColor()
    const selectedValue = event.target.value;
    window.history.pushState({}, '', `/talent?name=${encodeURIComponent(selectedValue)}`);
    showSkeletons(2);
    const res = await fetch('/api/talent_charts_and_links/' + selectedValue, {cache: 'no-cache'});
    const data = await res.json();
    renderCards(data.charts);
    renderLinks(data.linksInfo);
    console.log('User selected:', selectedValue);
  }
});

// resize listener
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    Object.values(charts).forEach(c => c && c.resize && c.resize());
  }, 100);
});

// 'about the data' link listener
document.getElementById('about-link').addEventListener('click', (e) => {
  e.preventDefault();
  setActiveTab();
  clearTabContent();
  loadTab('about');
  window.history.pushState({}, '', `/about`);
});

// 'message me' link listener
document.getElementById('contact-link').addEventListener('click', (e) => {
  e.preventDefault();
  setActiveTab();
  clearTabContent();
  loadTab('contact');
  window.history.pushState({}, '', `/contact`);
});

// expose some functions for debug in console
window.__dashboard = { loadTab, loadHeader };
})();
