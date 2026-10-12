import json
import re
import os

print("Applying unified multi-metric province growth & merged monthly accumulation table...")

# 1. Load updated bundle
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle_json_str = json.dumps(bundle, ensure_ascii=False)
print("Loaded bundle, size:", len(bundle_json_str) / 1024, "KB")

new_panel_html = """<!-- Panel: Analisis Tren & Lonjakan Bulanan per Provinsi & Akumulasi per Moda -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <!-- Header & Mode Toggle -->
          <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-1.5">
                <span class="inline-block w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Tren & Lonjakan Bulanan per Provinsi</h3>
              </div>
              <p id="prov-growth-subtitle" class="text-[11px] text-slate-500">Cek tren pergerakan bulanan dan analisis lonjakan terhadap baseline median (2026)</p>
            </div>
            
            <!-- View Mode Buttons -->
            <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded border border-slate-200 dark:border-slate-700 text-[11px]">
              <button id="btn-mode-prov" onclick="switchProvGrowthMode('prov')" class="px-2 py-0.5 rounded font-semibold bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs transition-colors">Per Provinsi</button>
              <button id="btn-mode-month" onclick="switchProvGrowthMode('month')" class="px-2 py-0.5 rounded font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Per Bulan</button>
            </div>
          </div>

          <!-- Controls Row & Key Metrics Highlight Strip -->
          <div class="mt-3.5 grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">
            <!-- Dropdowns & Filters (Mode 'prov' vs 'month') -->
            <div class="lg:col-span-5">
              <div id="wrapper-sel-prov-group" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <!-- Dropdown Provinsi (Mode 'prov') -->
                <div id="wrapper-sel-prov" class="flex flex-col gap-1 w-full">
                  <label for="sel-prov-growth" class="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400">Pilih Provinsi:</label>
                  <select id="sel-prov-growth" onchange="onProvinceGrowthSelectChange()" class="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-2.5 py-1.5 text-slate-900 dark:text-slate-100 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs cursor-pointer">
                    <!-- Populated dynamically via JS: Default 'ALL' (Seluruh Provinsi), followed by 38 provinces sorted A-Z -->
                  </select>
                </div>

                <!-- Dropdown Moda (Mode 'prov') -->
                <div id="wrapper-sel-moda" class="flex flex-col gap-1 w-full">
                  <label for="sel-moda-growth" class="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400">Pilih Moda:</label>
                  <select id="sel-moda-growth" onchange="onModaGrowthSelectChange()" class="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-2.5 py-1.5 text-slate-900 dark:text-slate-100 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs cursor-pointer">
                    <option value="ALL" selected>Semua Moda (5 Moda)</option>
                    <option value="UDARA">Udara</option>
                    <option value="KA">Kereta Api</option>
                    <option value="BUS">Bus</option>
                    <option value="ASDP">ASDP</option>
                    <option value="LAUT">Laut</option>
                  </select>
                </div>
              </div>

              <!-- Dropdown Bulan (Mode 'month') -->
              <div id="wrapper-sel-month" class="hidden flex flex-col gap-1 w-full">
                <label for="sel-month-growth" class="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400">Pilih Bulan:</label>
                <select id="sel-month-growth" onchange="onMonthGrowthSelectChange()" class="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-2.5 py-1.5 text-slate-900 dark:text-slate-100 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs cursor-pointer">
                  <option value="3" selected>Maret 2026 (Puncak Mudik Lebaran)</option>
                  <option value="4">April 2026 (Puncak Arus Balik)</option>
                  <option value="5">Mei 2026</option>
                  <option value="6">Juni 2026 (Libur Sekolah Awal)</option>
                  <option value="7">Juli 2026 (Puncak Libur Sekolah)</option>
                  <option value="8">Agustus 2026 (Wisata Musim Panas)</option>
                  <option value="9">September 2026</option>
                  <option value="1">Januari 2026 (Nataru)</option>
                  <option value="2">Februari 2026 (Kondisi Reguler)</option>
                </select>
              </div>
            </div>

            <!-- Key Metrics Highlight Strip -->
            <div id="prov-metrics-strip" class="lg:col-span-7 grid grid-cols-3 gap-2 text-xs">
              <div class="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/40 rounded p-2">
                <span id="label-stat-1" class="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 block tracking-tight">Bulan Puncak</span>
                <span id="badge-prov-peak" class="font-bold text-slate-900 dark:text-white text-xs num-mono">Maret</span>
                <span id="badge-prov-peak-vol" class="text-[10px] text-slate-500 dark:text-slate-400 block num-mono">29.23M pnp</span>
              </div>
              <div class="bg-emerald-50/70 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 rounded p-2">
                <span id="label-stat-2" class="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 block tracking-tight">Lonjakan vs Median</span>
                <span id="badge-prov-jump" class="font-bold text-emerald-600 dark:text-emerald-400 text-xs num-mono">+26.5%</span>
                <span id="badge-prov-jump-m" class="text-[10px] text-slate-500 dark:text-slate-400 block">di Maret 2026</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded p-2">
                <span id="label-stat-3" class="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400 block tracking-tight">Total YTD</span>
                <span id="badge-prov-ytd" class="font-bold text-slate-900 dark:text-white text-xs num-mono">209.14M</span>
                <span id="badge-prov-ytd-sub" class="text-[10px] text-slate-500 dark:text-slate-400 block">Semua Moda</span>
              </div>
            </div>
          </div>

          <!-- Descriptive Finding Callout -->
          <div id="prov-finding-callout" class="mt-3 p-2.5 bg-blue-50/50 dark:bg-blue-950/20 border-l-3 border-blue-500 rounded-r text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
            <!-- Dynamic text populated by JS -->
          </div>

          <!-- Chart Area: Full Width (Stacked Bar Chart) -->
          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            <div class="text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1.5 flex items-center justify-between">
              <span id="prov-chart-box-title">Visualisasi Tren Bulanan (Seluruh Indonesia)</span>
              <span id="prov-chart-box-sub" class="text-[10px] text-slate-400 font-mono">5 Moda Transportasi</span>
            </div>
            <div class="relative w-full h-[320px]">
              <canvas id="chartProvinceGrowthCanvas"></canvas>
            </div>
          </div>

          <!-- Tabel Akumulasi Bulanan per Moda Transportasi (Dilebur di sini) -->
          <div class="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-2.5">
              <div>
                <h4 id="monthly-table-title" class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Akumulasi Bulanan per Moda Transportasi</h4>
                <p id="monthly-table-subtitle" class="text-[11px] text-slate-500">Volume pergerakan dari Januari sampai dengan September 2026</p>
              </div>
              <span id="monthly-table-badge" class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded border border-slate-200 dark:border-slate-700">9 Bulan (Jan - Sep)</span>
            </div>

            <div class="overflow-x-auto mt-2">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr id="thead-monthly">
                    <th class="py-2.5 px-3">Bulan</th>
                    <th class="py-2.5 px-3 text-right text-sky-700 dark:text-sky-400">Udara</th>
                    <th class="py-2.5 px-3 text-right text-amber-700 dark:text-amber-400">Kereta Api</th>
                    <th class="py-2.5 px-3 text-right text-green-700 dark:text-green-400">Bus</th>
                    <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400">ASDP</th>
                    <th class="py-2.5 px-3 text-right text-cyan-700 dark:text-cyan-400">Laut</th>
                    <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total</th>
                    <th class="py-2.5 px-3 text-right text-slate-700 dark:text-slate-300">vs Median</th>
                  </tr>
                </thead>
                <tbody id="tbody-monthly" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                </tbody>
              </table>
            </div>

            <!-- Footnote Catatan September* -->
            <div class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-start gap-1.5 text-xs text-slate-500 dark:text-slate-400">
              <span class="font-bold text-amber-600 dark:text-amber-400 shrink-0">* Catatan September:</span>
              <p class="leading-relaxed text-[11px]">
                Data bulan September 2026 merupakan data berjalan s.d. 29 September (29 hari, belum genap satu bulan penuh 30 hari).
              </p>
            </div>
          </div>
        </div>

      </div>"""

new_workspace_js = """// ===============================================================
// WORKSPACE: ANALISIS TREN & LONJAKAN BULANAN PER PROVINSI
// ===============================================================
const METRIC_CONFIG_PROV = {
  'pnp_brg': { label: 'Penumpang Berangkat', short: 'Pnp Brg', unit: 'pnp', fullUnit: 'penumpang berangkat', verb: 'penumpang berangkat' },
  'pnp_dat': { label: 'Penumpang Datang', short: 'Pnp Dat', unit: 'pnp', fullUnit: 'penumpang datang', verb: 'penumpang datang' },
  'pnp_tot': { label: 'Total Penumpang', short: 'Total Pnp', unit: 'pnp', fullUnit: 'penumpang', verb: 'total penumpang' },
  'arm_brg': { label: 'Armada Berangkat', short: 'Arm Brg', unit: 'trip', fullUnit: 'trip keberangkatan armada', verb: 'armada berangkat' },
  'arm_dat': { label: 'Armada Datang', short: 'Arm Dat', unit: 'trip', fullUnit: 'trip kedatangan armada', verb: 'armada datang' },
  'arm_tot': { label: 'Total Armada', short: 'Total Arm', unit: 'trip', fullUnit: 'trip armada', verb: 'total armada' }
};

let currentProvGrowthMode = 'prov';
let selectedProvinceForGrowth = 'ALL';
let selectedModaForGrowth = 'ALL';
let selectedMonthForGrowth = 3;
let chartProvGrowth = null;

function getActiveProvinceGrowthData() {
  const pmd = DATA.province_monthly_data;
  if (!pmd) return null;
  const combo = (currentMetric || 'pnp') + '_' + (currentDirection || 'brg');
  if (pmd[combo]) return pmd[combo];
  if (pmd.by_metric && pmd.by_metric[combo]) return pmd.by_metric[combo];
  return pmd['pnp_brg'] || pmd;
}

function initProvinceGrowthWorkspace() {
  const pData = getActiveProvinceGrowthData();
  if (!pData) return;

  const selProv = document.getElementById('sel-prov-growth');
  if (selProv && selProv.options.length <= 1) {
    selProv.innerHTML = '';
    
    // 1. Opsi Default: Seluruh Provinsi (Nasional)
    const optAll = document.createElement('option');
    optAll.value = 'ALL';
    optAll.textContent = 'Seluruh Provinsi (Nasional)';
    if (selectedProvinceForGrowth === 'ALL') optAll.selected = true;
    selProv.appendChild(optAll);

    // 2. Daftar 38 Provinsi Diurutkan Berdasarkan Alfabet (A-Z)
    const sortedProvs = [...pData.provinces]
      .filter(p => p !== 'ALL' && p !== 'Seluruh Provinsi')
      .sort((a, b) => a.localeCompare('id', { sensitivity: 'base' }));

    sortedProvs.forEach(prov => {
      const opt = document.createElement('option');
      opt.value = prov;
      opt.textContent = prov;
      if (prov === selectedProvinceForGrowth) opt.selected = true;
      selProv.appendChild(opt);
    });
  }

  const selModa = document.getElementById('sel-moda-growth');
  if (selModa && selectedModaForGrowth) {
    selModa.value = selectedModaForGrowth;
  }
}

function switchProvGrowthMode(mode) {
  currentProvGrowthMode = mode;
  const btnProv = document.getElementById('btn-mode-prov');
  const btnMonth = document.getElementById('btn-mode-month');
  const wrapProvGroup = document.getElementById('wrapper-sel-prov-group');
  const wrapMonth = document.getElementById('wrapper-sel-month');

  if (mode === 'prov') {
    if (wrapProvGroup) wrapProvGroup.classList.remove('hidden');
    if (wrapMonth) wrapMonth.classList.add('hidden');
    if (btnProv) {
      btnProv.className = 'px-2 py-0.5 rounded font-semibold bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs transition-colors';
    }
    if (btnMonth) {
      btnMonth.className = 'px-2 py-0.5 rounded font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors';
    }
  } else {
    if (wrapProvGroup) wrapProvGroup.classList.add('hidden');
    if (wrapMonth) wrapMonth.classList.remove('hidden');
    if (btnMonth) {
      btnMonth.className = 'px-2 py-0.5 rounded font-semibold bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs transition-colors';
    }
    if (btnProv) {
      btnProv.className = 'px-2 py-0.5 rounded font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors';
    }
  }
  renderProvinceGrowthWorkspace();
}

function onProvinceGrowthSelectChange() {
  const el = document.getElementById('sel-prov-growth');
  if (el) {
    selectedProvinceForGrowth = el.value;
    renderProvinceGrowthWorkspace();
  }
}

function onModaGrowthSelectChange() {
  const el = document.getElementById('sel-moda-growth');
  if (el) {
    selectedModaForGrowth = el.value;
    renderProvinceGrowthWorkspace();
  }
}

function onMonthGrowthSelectChange() {
  const el = document.getElementById('sel-month-growth');
  if (el) {
    selectedMonthForGrowth = parseInt(el.value, 10);
    renderProvinceGrowthWorkspace();
  }
}

function renderProvinceGrowthWorkspace() {
  initProvinceGrowthWorkspace();
  const pData = getActiveProvinceGrowthData();
  if (!pData) return;

  const combo = (currentMetric || 'pnp') + '_' + (currentDirection || 'brg');
  const mCfg = METRIC_CONFIG_PROV[combo] || METRIC_CONFIG_PROV['pnp_brg'];

  const ctxEl = document.getElementById('chartProvinceGrowthCanvas');
  if (!ctxEl) return;
  const ctx = ctxEl.getContext('2d');
  const isDark = document.documentElement.classList.contains('dark');

  if (chartProvGrowth) {
    chartProvGrowth.destroy();
    chartProvGrowth = null;
  }

  const subEl = document.getElementById('prov-growth-subtitle');
  const findingEl = document.getElementById('prov-finding-callout');
  const boxTitleEl = document.getElementById('prov-chart-box-title');
  const boxSubEl = document.getElementById('prov-chart-box-sub');

  const theadMonthly = document.getElementById('thead-monthly');
  const tbodyMonthly = document.getElementById('tbody-monthly');
  const tableTitle = document.getElementById('monthly-table-title');
  const tableSub = document.getElementById('monthly-table-subtitle');
  const tableBadge = document.getElementById('monthly-table-badge');

  const lblStat1 = document.getElementById('label-stat-1');
  const lblStat2 = document.getElementById('label-stat-2');
  const lblStat3 = document.getElementById('label-stat-3');
  const badgePeak = document.getElementById('badge-prov-peak');
  const badgePeakVol = document.getElementById('badge-prov-peak-vol');
  const badgeJump = document.getElementById('badge-prov-jump');
  const badgeJumpM = document.getElementById('badge-prov-jump-m');
  const badgeYtd = document.getElementById('badge-prov-ytd');
  const badgeYtdSub = document.getElementById('badge-prov-ytd-sub');

  const MODA_NAMES = {
    'UDARA': 'Udara',
    'KA': 'Kereta Api',
    'BUS': 'Bus',
    'ASDP': 'ASDP',
    'LAUT': 'Laut'
  };

  if (currentProvGrowthMode === 'prov') {
    // =========================================================
    // MODE 1: PER PROVINSI (+ FILTER MODA & BASELINE MEDIAN)
    // =========================================================
    const provInfo = pData.by_province[selectedProvinceForGrowth] || pData.by_province['ALL'] || pData.by_province[pData.provinces[0]];
    if (!provInfo) return;

    const isAllModa = (selectedModaForGrowth === 'ALL' || !selectedModaForGrowth);
    const activeModaLabel = isAllModa ? 'Semua Moda' : (MODA_NAMES[selectedModaForGrowth] || selectedModaForGrowth);
    const provLabel = selectedProvinceForGrowth === 'ALL' ? 'Seluruh Indonesia (Nasional)' : provInfo.provinsi;

    // Helper hitung volume per bulan berdasarkan scope moda
    const getMonthVal = (m) => {
      if (isAllModa) {
        return (m.val !== undefined ? m.val : m.brg);
      }
      return (m.modas && m.modas[selectedModaForGrowth] !== undefined) ? m.modas[selectedModaForGrowth] : 0;
    };

    const monthlyVals = provInfo.monthly.map(m => getMonthVal(m));
    const sortedVals = [...monthlyVals].sort((a, b) => a - b);
    const scopeMedian = sortedVals[4] || 0; // Robust Median 9 bulan (posisi ke-5)

    let scopePeakVol = -1;
    let scopePeakIdx = 0;
    monthlyVals.forEach((v, idx) => {
      if (v > scopePeakVol) {
        scopePeakVol = v;
        scopePeakIdx = idx;
      }
    });

    const scopePeakMonth = provInfo.monthly[scopePeakIdx] ? provInfo.monthly[scopePeakIdx].name : 'Maret';
    const scopePeakJumpVsMedian = scopeMedian > 0
      ? (((scopePeakVol - scopeMedian) / scopeMedian) * 100).toFixed(1)
      : '0.0';
    const scopeTotal = monthlyVals.reduce((acc, v) => acc + v, 0);

    // Update Subtitles & Headers
    if (subEl) subEl.innerText = `Tren volume bulanan ${mCfg.verb} di ${provLabel} (${activeModaLabel})`;
    if (lblStat1) lblStat1.innerText = 'Bulan Puncak';
    if (badgePeak) badgePeak.innerText = `${scopePeakMonth} 2026`;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(scopePeakVol)} ${mCfg.unit}`;

    if (lblStat2) lblStat2.innerText = 'Lonjakan vs Median';
    const jumpSign = parseFloat(scopePeakJumpVsMedian) > 0 ? '+' : '';
    if (badgeJump) badgeJump.innerText = `${jumpSign}${scopePeakJumpVsMedian}%`;
    if (badgeJumpM) badgeJumpM.innerText = `di ${scopePeakMonth} 2026`;

    if (lblStat3) lblStat3.innerText = 'Total YTD (9 Bln)';
    if (badgeYtd) {
      if (scopeTotal >= 1e6) {
        badgeYtd.innerText = `${(scopeTotal / 1e6).toFixed(2)}M`;
      } else if (scopeTotal >= 1e3) {
        badgeYtd.innerText = `${(scopeTotal / 1e3).toFixed(1)}k`;
      } else {
        badgeYtd.innerText = numFmt(scopeTotal);
      }
    }
    if (badgeYtdSub) badgeYtdSub.innerText = `${mCfg.short} • ${isAllModa ? '5 Moda' : activeModaLabel}`;

    // Finding Callout
    if (findingEl) {
      let insightStr = '';
      if (scopePeakIdx === 2) {
        insightStr = `Aktivitas ${mCfg.verb} ${activeModaLabel} di <strong>${provLabel}</strong> mencapai puncak tahunan pada bulan <strong>Maret 2026</strong> (${numFmt(scopePeakVol)} ${mCfg.unit}), melonjak <strong>${jumpSign}${scopePeakJumpVsMedian}%</strong> di atas baseline median bulanan (${numFmt(scopeMedian)} ${mCfg.unit}) didorong oleh arus mudik Lebaran 1447 H.`;
      } else if (scopePeakIdx === 3) {
        insightStr = `Aktivitas ${mCfg.verb} ${activeModaLabel} di <strong>${provLabel}</strong> mencapai titik tertinggi pada bulan <strong>April 2026</strong> (${numFmt(scopePeakVol)} ${mCfg.unit}, ${jumpSign}${scopePeakJumpVsMedian}% vs median) sejalan dengan arus balik Lebaran.`;
      } else if (scopePeakIdx === 6 || scopePeakIdx === 7) {
        insightStr = `Aktivitas ${mCfg.verb} ${activeModaLabel} di <strong>${provLabel}</strong> mencapai puncak tahunan pada bulan <strong>${scopePeakMonth} 2026</strong> (${numFmt(scopePeakVol)} ${mCfg.unit}, ${jumpSign}${scopePeakJumpVsMedian}% vs median) didorong oleh mobilitas masa liburan sekolah dan wisata.`;
      } else {
        insightStr = `Aktivitas ${mCfg.verb} ${activeModaLabel} di <strong>${provLabel}</strong> mencapai volume tertinggi pada bulan <strong>${scopePeakMonth} 2026</strong> (${numFmt(scopePeakVol)} ${mCfg.unit}), dengan kenaikan ${jumpSign}${scopePeakJumpVsMedian}% di atas baseline median bulanan (${numFmt(scopeMedian)} ${mCfg.unit}).`;
      }
      findingEl.innerHTML = `<span class="font-bold text-blue-700 dark:text-blue-400">💡 Temuan Kenaikan:</span> ${insightStr}`;
    }

    if (boxTitleEl) boxTitleEl.innerText = isAllModa ? `Visualisasi Tren Bulanan (${provLabel})` : `Tren Bulanan Moda ${activeModaLabel} (${provLabel})`;
    if (boxSubEl) boxSubEl.innerText = `${mCfg.label} • Baseline Median: ${numFmt(scopeMedian)} ${mCfg.unit}`;

    // Datasets Chart
    let datasets = [];
    if (isAllModa) {
      const modaKeys = [
        { key: 'UDARA', label: 'Udara', color: (typeof COLOR !== 'undefined' && COLOR.UDARA) || '#0284c7' },
        { key: 'KA', label: 'Kereta Api', color: (typeof COLOR !== 'undefined' && COLOR.KA) || '#d97706' },
        { key: 'BUS', label: 'Bus', color: (typeof COLOR !== 'undefined' && COLOR.BUS) || '#16a34a' },
        { key: 'ASDP', label: 'ASDP', color: (typeof COLOR !== 'undefined' && COLOR.ASDP) || '#9333ea' },
        { key: 'LAUT', label: 'Laut', color: (typeof COLOR !== 'undefined' && COLOR.LAUT) || '#0891b2' }
      ];
      datasets = modaKeys.map(mInfo => ({
        label: mInfo.label,
        data: provInfo.monthly.map(m => (m.modas && m.modas[mInfo.key]) || 0),
        backgroundColor: mInfo.color,
        borderRadius: 0,
        stack: 'provStack'
      }));
    } else {
      const mColor = (typeof COLOR !== 'undefined' && COLOR[selectedModaForGrowth]) || '#0284c7';
      datasets = [{
        label: activeModaLabel,
        data: monthlyVals,
        backgroundColor: mColor,
        borderRadius: 4
      }];
    }

    chartProvGrowth = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: provInfo.monthly.map(m => m.short),
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: isAllModa,
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 8,
              boxHeight: 8,
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 10,
              color: isDark ? '#94a3b8' : '#64748b',
              font: { size: 10, family: 'Inter, sans-serif' }
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              title: (items) => {
                if (!items || items.length === 0) return '';
                const idx = items[0].dataIndex;
                const item = provInfo.monthly[idx];
                const mVal = monthlyVals[idx];
                const vsMed = scopeMedian > 0 ? (((mVal - scopeMedian) / scopeMedian) * 100).toFixed(1) : '0.0';
                const sign = parseFloat(vsMed) > 0 ? '+' : '';
                return `${item.name} 2026 • ${numFmt(mVal)} ${mCfg.unit} (${sign}${vsMed}% vs Median)`;
              },
              label: (ctx) => {
                const val = ctx.raw || 0;
                if (val === 0 && isAllModa) return null;
                const idx = ctx.dataIndex;
                const totalMonth = provInfo.monthly[idx].val !== undefined ? provInfo.monthly[idx].val : provInfo.monthly[idx].brg;
                const pct = totalMonth > 0 ? ((val / totalMonth) * 100).toFixed(1) : '0.0';
                return ` ${ctx.dataset.label}: ${numFmt(val)} ${mCfg.unit} (${pct}%)`;
              }
            }
          }
        },
        scales: {
          x: {
            stacked: isAllModa,
            grid: { display: false },
            ticks: { color: isDark ? '#94a3b8' : '#64748b' }
          },
          y: {
            stacked: isAllModa,
            grid: { color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' },
            ticks: {
              color: isDark ? '#94a3b8' : '#64748b',
              font: { family: 'JetBrains Mono' },
              callback: v => (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v >= 1e3 ? (v / 1e3).toFixed(0) + 'k' : v))
            }
          }
        }
      }
    });

    // Unified Table Rendering: Akumulasi Bulanan per Moda
    if (tableTitle) tableTitle.innerText = 'Akumulasi Bulanan per Moda Transportasi';
    if (tableSub) tableSub.innerText = `Rincian volume ${mCfg.verb} di ${provLabel} (${activeModaLabel}) Januari s.d. September 2026`;
    if (tableBadge) tableBadge.innerText = `Median: ${numFmt(scopeMedian)} ${mCfg.unit}/bln`;

    if (theadMonthly) {
      theadMonthly.innerHTML = `
        <th class="py-2.5 px-3">Bulan</th>
        <th class="py-2.5 px-3 text-right text-sky-700 dark:text-sky-400 ${selectedModaForGrowth === 'UDARA' ? 'bg-sky-50 dark:bg-sky-950/40 font-bold' : ''}">Udara</th>
        <th class="py-2.5 px-3 text-right text-amber-700 dark:text-amber-400 ${selectedModaForGrowth === 'KA' ? 'bg-amber-50 dark:bg-amber-950/40 font-bold' : ''}">Kereta Api</th>
        <th class="py-2.5 px-3 text-right text-green-700 dark:text-green-400 ${selectedModaForGrowth === 'BUS' ? 'bg-green-50 dark:bg-green-950/40 font-bold' : ''}">Bus</th>
        <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400 ${selectedModaForGrowth === 'ASDP' ? 'bg-purple-50 dark:bg-purple-950/40 font-bold' : ''}">ASDP</th>
        <th class="py-2.5 px-3 text-right text-cyan-700 dark:text-cyan-400 ${selectedModaForGrowth === 'LAUT' ? 'bg-cyan-50 dark:bg-cyan-950/40 font-bold' : ''}">Laut</th>
        <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total</th>
        <th class="py-2.5 px-3 text-right text-slate-700 dark:text-slate-300">vs Median</th>
      `;
    }

    if (tbodyMonthly) {
      tbodyMonthly.innerHTML = '';
      provInfo.monthly.forEach((m, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';

        const rowVal = monthlyVals[idx];
        const vsMedNum = scopeMedian > 0 ? (((rowVal - scopeMedian) / scopeMedian) * 100).toFixed(1) : '0.0';
        let vsMedBadge = '<span class="text-slate-400">0.0%</span>';
        if (parseFloat(vsMedNum) > 0) {
          vsMedBadge = `<span class="text-emerald-600 dark:text-emerald-400 font-bold">▲ +${vsMedNum}%</span>`;
        } else if (parseFloat(vsMedNum) < 0) {
          vsMedBadge = `<span class="text-rose-600 dark:text-rose-400 font-medium">▼ ${vsMedNum}%</span>`;
        }

        const uVal = (m.modas && m.modas.UDARA) || 0;
        const kVal = (m.modas && m.modas.KA) || 0;
        const bVal = (m.modas && m.modas.BUS) || 0;
        const aVal = (m.modas && m.modas.ASDP) || 0;
        const lVal = (m.modas && m.modas.LAUT) || 0;
        const totVal = m.val !== undefined ? m.val : m.brg;

        tr.innerHTML = `
          <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-200">${m.name}</td>
          <td class="py-2.5 px-3 text-right ${selectedModaForGrowth === 'UDARA' ? 'bg-sky-50 dark:bg-sky-950/40 font-bold text-sky-700 dark:text-sky-300' : ''}">${numFmt(uVal)}</td>
          <td class="py-2.5 px-3 text-right ${selectedModaForGrowth === 'KA' ? 'bg-amber-50 dark:bg-amber-950/40 font-bold text-amber-700 dark:text-amber-300' : ''}">${numFmt(kVal)}</td>
          <td class="py-2.5 px-3 text-right ${selectedModaForGrowth === 'BUS' ? 'bg-green-50 dark:bg-green-950/40 font-bold text-green-700 dark:text-green-300' : ''}">${numFmt(bVal)}</td>
          <td class="py-2.5 px-3 text-right ${selectedModaForGrowth === 'ASDP' ? 'bg-purple-50 dark:bg-purple-950/40 font-bold text-purple-700 dark:text-purple-300' : ''}">${numFmt(aVal)}</td>
          <td class="py-2.5 px-3 text-right ${selectedModaForGrowth === 'LAUT' ? 'bg-cyan-50 dark:bg-cyan-950/40 font-bold text-cyan-700 dark:text-cyan-300' : ''}">${numFmt(lVal)}</td>
          <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${numFmt(totVal)}</td>
          <td class="py-2.5 px-3 text-right font-semibold">${vsMedBadge}</td>
        `;
        tbodyMonthly.appendChild(tr);
      });
    }

  } else {
    // =========================================================
    // MODE 2: PER BULAN (Deteksi Provinsi Lonjakan Tertinggi)
    // =========================================================
    const monthRank = pData.by_month[selectedMonthForGrowth];
    if (!monthRank) return;

    if (subEl) subEl.innerText = `Provinsi dengan volume ${mCfg.verb} tertinggi pada ${monthRank.name} 2026`;
    if (lblStat1) lblStat1.innerText = 'Volume Tertinggi';
    if (badgePeak) badgePeak.innerText = monthRank.top_vol[0].provinsi;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(monthRank.top_vol[0].vol)} ${mCfg.unit}`;

    if (lblStat2) lblStat2.innerText = 'Lonjakan vs Median';
    if (monthRank.top_growth && monthRank.top_growth.length > 0) {
      const topG = monthRank.top_growth[0];
      const gSign = topG.vs_median > 0 ? '+' : '';
      if (badgeJump) badgeJump.innerText = `${gSign}${topG.vs_median}%`;
      if (badgeJumpM) badgeJumpM.innerText = topG.provinsi;
    } else {
      if (badgeJump) badgeJump.innerText = '-';
      if (badgeJumpM) badgeJumpM.innerText = 'Reguler';
    }

    if (lblStat3) lblStat3.innerText = 'Fase Periode';
    if (badgeYtd) badgeYtd.innerText = monthRank.name;
    if (badgeYtdSub) badgeYtdSub.innerText = selectedMonthForGrowth === 3 ? 'Puncak Lebaran' : (selectedMonthForGrowth === 4 ? 'Arus Balik' : 'Reguler');

    if (findingEl) {
      let insightStr = '';
      const top1 = monthRank.top_vol[0];
      const top2 = monthRank.top_vol[1];
      const top3 = monthRank.top_vol[2];
      const growthNote = (monthRank.top_growth && monthRank.top_growth.length > 0)
        ? ` Lonjakan vs median tertinggi dialami ${monthRank.top_growth.slice(0, 3).map(x => x.provinsi + ' (+' + x.vs_median + '%)').join(', ')}.`
        : '';
      if (selectedMonthForGrowth === 3) {
        insightStr = `Di bulan Maret 2026, arus mudik Lebaran mendorong lonjakan ${mCfg.verb} tertinggi pada <strong>${top1.provinsi}</strong> (${numFmt(top1.vol)} ${mCfg.unit}), disusul <strong>${top2.provinsi}</strong> dan <strong>${top3.provinsi}</strong>.${growthNote}`;
      } else if (selectedMonthForGrowth === 4) {
        insightStr = `Di bulan April 2026, arus balik Lebaran mempertahankan mobilitas tinggi, dipimpin oleh <strong>${top1.provinsi}</strong> (${numFmt(top1.vol)} ${mCfg.unit}) dan <strong>${top2.provinsi}</strong>.${growthNote}`;
      } else if (selectedMonthForGrowth === 7 || selectedMonthForGrowth === 8) {
        insightStr = `Di bulan ${monthRank.name} 2026, mobilitas didominasi liburan sekolah dan wisata, dengan <strong>${top1.provinsi}</strong> (${numFmt(top1.vol)} ${mCfg.unit}) dan simpul utama mempertahankan volume tinggi.${growthNote}`;
      } else {
        insightStr = `Di bulan ${monthRank.name} 2026, pergerakan berada dalam ritme operasional rutin bulanan dengan volume ${mCfg.verb} terbesar di ${monthRank.top_vol.slice(0, 3).map(x => x.provinsi).join(', ')}.${growthNote}`;
      }
      findingEl.innerHTML = `<span class="font-bold text-blue-700 dark:text-blue-400">💡 Ringkasan Bulan ${monthRank.name}:</span> ${insightStr}`;
    }

    if (boxTitleEl) boxTitleEl.innerText = 'Peringkat Provinsi Tertinggi';
    if (boxSubEl) boxSubEl.innerText = `${mCfg.label} (${monthRank.name})`;

    // Chart: Horizontal Bar Top 6 Provinsi di Bulan Ini
    const topVolSlice = monthRank.top_vol.slice(0, 6);
    chartProvGrowth = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topVolSlice.map(x => x.provinsi),
        datasets: [{
          label: `${mCfg.label} (${monthRank.name})`,
          data: topVolSlice.map(x => x.vol),
          backgroundColor: ['#0284c7', '#0369a1', '#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd'],
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` Volume ${monthRank.name}: ${numFmt(ctx.raw)} ${mCfg.unit}`
            }
          }
        },
        scales: {
          y: { grid: { display: false }, ticks: { color: isDark ? '#94a3b8' : '#64748b' } },
          x: {
            grid: { color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' },
            ticks: {
              color: isDark ? '#94a3b8' : '#64748b',
              font: { family: 'JetBrains Mono' },
              callback: v => (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v >= 1e3 ? (v / 1e3).toFixed(0) + 'k' : v))
            }
          }
        }
      }
    });

    // Table Mode 2: Top 8 Provinsi di Bulan Ini
    if (tableTitle) tableTitle.innerText = `Peringkat Provinsi Teratas Bulan ${monthRank.name} 2026`;
    if (tableSub) tableSub.innerText = `Daftar provinsi dengan volume ${mCfg.verb} dan lonjakan vs median terbesar`;
    if (tableBadge) tableBadge.innerText = `${monthRank.name} 2026`;

    if (theadMonthly) {
      theadMonthly.innerHTML = `
        <th class="py-2.5 px-3">Peringkat & Provinsi</th>
        <th class="py-2.5 px-3 text-right">${mCfg.label} (${monthRank.name})</th>
        <th class="py-2.5 px-3 text-right">Lonjakan vs Median</th>
        <th class="py-2.5 px-3 text-center">Status</th>
      `;
    }

    if (tbodyMonthly) {
      tbodyMonthly.innerHTML = '';
      monthRank.top_vol.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';

        const gItem = monthRank.top_growth ? monthRank.top_growth.find(g => g.provinsi === item.provinsi) : null;
        let growthBadge = '<span class="text-slate-400">-</span>';
        if (gItem) {
          const sign = gItem.vs_median > 0 ? '+' : '';
          growthBadge = `<span class="text-emerald-600 dark:text-emerald-400 font-bold">▲ ${sign}${gItem.vs_median}%</span>`;
        }

        tr.innerHTML = `
          <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-200">
            <span class="inline-block w-4 text-xs font-bold text-slate-400">#${idx + 1}</span> ${item.provinsi}
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${numFmt(item.vol)}</td>
          <td class="py-2.5 px-3 text-right">${growthBadge}</td>
          <td class="py-2.5 px-3 text-center">
            ${idx === 0 ? '<span class="bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 text-[10px] font-bold px-2 py-0.5 rounded-full">Top Volume</span>' : '<span class="bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 text-[10px] px-2 py-0.5 rounded-full">Tinggi</span>'}
          </td>
        `;
        tbodyMonthly.appendChild(tr);
      });
    }
  }
}

// Backward compatibility alias for any existing code
function renderMonthlyTable() {
  renderProvinceGrowthWorkspace();
}

function renderDOWWorkspace() {
  renderProvinceGrowthWorkspace();
}"""

for filename in ['index.html', 'Dashboard_Mobilitas_Nasional_2026.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update const DATA
    start_str = "const DATA = {"
    end_str = ";\n\nconst numFmt ="
    pos1 = html.find(start_str)
    pos2 = html.find(end_str, pos1)
    if pos1 == -1 or pos2 == -1:
        raise Exception(f"Cannot find const DATA block in {filename}")

    html = html[:pos1] + "const DATA = " + bundle_json_str + html[pos2:]

    # 2. Update HTML Panel (merge into single workspace panel)
    start_panel = "<!-- Panel 1: Analisis Tren & Lonjakan Bulanan per Provinsi -->"
    end_panel = "<!-- ========================================================= -->\n      <!-- TAB 2: PUNCAK LEBARAN 2026"
    p1 = html.find(start_panel)
    p2 = html.find(end_panel, p1)
    if p1 != -1 and p2 != -1:
        html = html[:p1] + new_panel_html + "\n\n      " + html[p2:]
    else:
        # Check if already updated to new panel header
        start_panel_new = "<!-- Panel: Analisis Tren & Lonjakan Bulanan per Provinsi & Akumulasi per Moda -->"
        p1_new = html.find(start_panel_new)
        p2_new = html.find(end_panel, p1_new)
        if p1_new != -1 and p2_new != -1:
            html = html[:p1_new] + new_panel_html + "\n\n      " + html[p2_new:]
        else:
            print(f"Warning: Could not find panel markers in {filename}")

    # 3. Update Section 6 formula in methodology modal
    old_formula = '<div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Laju Pertumbuhan Bulanan (Month-over-Month / MoM %):</div>'
    new_formula = '<div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Lonjakan Relatif terhadap Baseline Median (%):</div>'
    html = html.replace(old_formula, new_formula)
    
    html = html.replace(
        '$$\\text{MoM}_{\\text{prov}, t} = \\left( \\frac{P_{\\text{prov}, t} - P_{\\text{prov}, t-1}}{P_{\\text{prov}, t-1}} \\right) \\times 100\\%$$',
        '$$\\text{Deviasi}_{\\text{prov}, t} = \\left( \\frac{P_{\\text{prov}, t} - \\text{Median}(P_{\\text{prov}})}{\\text{Median}(P_{\\text{prov}})} \\right) \\times 100\\%$$'
    )

    # 4. Replace Province Growth Workspace JS block
    start_ws = "// ===============================================================\n// WORKSPACE: ANALISIS TREN & LONJAKAN BULANAN PER PROVINSI"
    end_ws = "// ---------------------------------------------------------------\n// TAB 2: PUNCAK LEBARAN CONTROLLER"
    pos_ws1 = html.find(start_ws)
    pos_ws2 = html.find(end_ws, pos_ws1)
    if pos_ws1 == -1 or pos_ws2 == -1:
        raise Exception(f"Cannot find Province Growth Workspace JS block in {filename}")

    html = html[:pos_ws1] + new_workspace_js + "\n\n" + html[pos_ws2:]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Updated {filename} successfully.")

print("All done!")
