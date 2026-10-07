import json
import re

print("Starting injection of Province Growth workspace into index.html...")

# 1. Load mobility_data_bundle.json with province_monthly_data
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle_json_str = json.dumps(bundle, ensure_ascii=False)

# 2. Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# =========================================================================
# A. Replace HTML Panel: lines 802-835
# =========================================================================
old_panel_pattern = re.compile(
    r'<!-- Right \(5 Cols\): Day of Week Profile -->.*?'
    r'<canvas id="chartDOWCanvas"></canvas>.*?'
    r'<tbody id="tbody-dow".*?</tbody>\s*</table>\s*</div>\s*</div>',
    re.DOTALL
)

new_panel_html = """<!-- Right (5 Cols): Analisis Tren & Lonjakan Bulanan per Provinsi -->
          <div class="lg:col-span-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
            <div>
              <!-- Header & Mode Toggle -->
              <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="inline-block w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                    <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Tren & Lonjakan Bulanan per Provinsi</h3>
                  </div>
                  <p id="prov-growth-subtitle" class="text-[11px] text-slate-500">Cek di bulan apa suatu provinsi naik tinggi (2026)</p>
                </div>
                
                <!-- View Mode Buttons -->
                <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded border border-slate-200 dark:border-slate-700 text-[11px]">
                  <button id="btn-mode-prov" onclick="switchProvGrowthMode('prov')" class="px-2 py-0.5 rounded font-semibold bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs transition-colors">Per Provinsi</button>
                  <button id="btn-mode-month" onclick="switchProvGrowthMode('month')" class="px-2 py-0.5 rounded font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Per Bulan</button>
                </div>
              </div>

              <!-- Controls Row (Dropdowns & Filters) -->
              <div class="mt-3 flex items-center justify-between gap-2">
                <!-- Dropdown Provinsi (Mode 'prov') -->
                <div id="wrapper-sel-prov" class="flex items-center gap-2 w-full">
                  <label for="sel-prov-growth" class="text-[11px] font-semibold text-slate-600 dark:text-slate-400 shrink-0">Pilih Provinsi:</label>
                  <select id="sel-prov-growth" onchange="onProvinceGrowthSelectChange()" class="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-2.5 py-1.5 text-slate-900 dark:text-slate-100 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs cursor-pointer">
                    <!-- Populated dynamically via JS -->
                  </select>
                </div>

                <!-- Dropdown Bulan (Mode 'month') -->
                <div id="wrapper-sel-month" class="hidden items-center gap-2 w-full">
                  <label for="sel-month-growth" class="text-[11px] font-semibold text-slate-600 dark:text-slate-400 shrink-0">Pilih Bulan:</label>
                  <select id="sel-month-growth" onchange="onMonthGrowthSelectChange()" class="w-full text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-2.5 py-1.5 text-slate-900 dark:text-slate-100 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs cursor-pointer">
                    <option value="3" selected>Maret 2026 (Puncak Mudik Lebaran)</option>
                    <option value="4">April 2026 (Puncak Arus Balik)</option>
                    <option value="5">Mei 2026</option>
                    <option value="6">Juni 2026 (Libur Sekolah Awal)</option>
                    <option value="7">Juli 2026 (Puncak Libur Sekolah)</option>
                    <option value="8">Agustus 2026 (Wisata Musim Panas)</option>
                    <option value="9">September 2026</option>
                    <option value="1">Januari 2026 (Nataru)</option>
                    <option value="2">Februari 2026 (Baseline Normal)</option>
                  </select>
                </div>
              </div>

              <!-- Key Metrics Highlight Strip -->
              <div id="prov-metrics-strip" class="grid grid-cols-3 gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                <div class="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/40 rounded p-2">
                  <span id="label-stat-1" class="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 block tracking-tight">Bulan Puncak</span>
                  <span id="badge-prov-peak" class="font-bold text-slate-900 dark:text-white text-xs num-mono">Maret</span>
                  <span id="badge-prov-peak-vol" class="text-[10px] text-slate-500 dark:text-slate-400 block num-mono">4.68M pnp</span>
                </div>
                <div class="bg-emerald-50/70 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 rounded p-2">
                  <span id="label-stat-2" class="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 block tracking-tight">Lonjakan MoM</span>
                  <span id="badge-prov-jump" class="font-bold text-emerald-600 dark:text-emerald-400 text-xs num-mono">+53.7%</span>
                  <span id="badge-prov-jump-m" class="text-[10px] text-slate-500 dark:text-slate-400 block">vs Februari</span>
                </div>
                <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded p-2">
                  <span id="label-stat-3" class="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400 block tracking-tight">Total YTD</span>
                  <span id="badge-prov-ytd" class="font-bold text-slate-900 dark:text-white text-xs num-mono">34.05M</span>
                  <span id="badge-prov-ytd-sub" class="text-[10px] text-slate-500 dark:text-slate-400 block">Penumpang Brg</span>
                </div>
              </div>

              <!-- Descriptive Finding Callout -->
              <div id="prov-finding-callout" class="mt-2.5 p-2.5 bg-blue-50/50 dark:bg-blue-950/20 border-l-3 border-blue-500 rounded-r text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
                <!-- Dynamic text populated by JS -->
              </div>

              <!-- Chart Area -->
              <div class="relative w-full h-[190px] mt-3">
                <canvas id="chartProvinceGrowthCanvas"></canvas>
              </div>
            </div>

            <!-- Table Area -->
            <div class="overflow-x-auto mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr id="thead-prov-growth">
                    <th class="py-2 px-2.5">Bulan</th>
                    <th class="py-2 px-2.5 text-right">Keberangkatan</th>
                    <th class="py-2 px-2.5 text-right">Pertumbuhan (MoM)</th>
                    <th class="py-2 px-2.5 text-center">Moda Utama</th>
                    <th class="py-2 px-2.5 text-center">Status</th>
                  </tr>
                </thead>
                <tbody id="tbody-prov-growth" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                  <!-- Dynamic rows populated by JS -->
                </tbody>
              </table>
            </div>
          </div>"""

match = old_panel_pattern.search(content)
if not match:
    raise Exception("Pattern for old HTML panel not found!")

content = old_panel_pattern.sub(new_panel_html, content, count=1)
print("1. HTML Panel replaced successfully.")

# =========================================================================
# B. Replace const DATA = ...
# =========================================================================
data_pattern = re.compile(r'const DATA = \{.*?\};\n', re.DOTALL)
if not data_pattern.search(content):
    raise Exception("Pattern for const DATA not found!")

content = data_pattern.sub(f"const DATA = {bundle_json_str};\n", content, count=1)
print("2. const DATA updated with province_monthly_data.")

# =========================================================================
# C. Add chartProvGrowth declaration and resize/update hooks
# =========================================================================
content = content.replace("let chartDOW = null;", "let chartDOW = null;\nlet chartProvGrowth = null;\nlet currentProvGrowthMode = 'prov';\nlet selectedProvinceForGrowth = 'Jawa Timur';\nlet selectedMonthForGrowth = 3;")

content = content.replace("if (chartDOW) chartDOW.resize();", "if (chartDOW) chartDOW.resize();\n    if (chartProvGrowth) chartProvGrowth.resize();")
content = content.replace("if (chartDOW) chartDOW.update();", "if (chartDOW) chartDOW.update();\n    if (chartProvGrowth) chartProvGrowth.update();")

# =========================================================================
# D. Replace renderDOWWorkspace function with new Province Growth logic
# =========================================================================
old_func_pattern = re.compile(
    r'function renderDOWWorkspace\(\)\s*\{.*?'
    r'tbody\.appendChild\(tr\);\s*\}\);\s*\}',
    re.DOTALL
)

new_func_js = """// ===============================================================
// WORKSPACE: ANALISIS TREN & LONJAKAN BULANAN PER PROVINSI
// ===============================================================
function initProvinceGrowthWorkspace() {
  const pData = DATA.province_monthly_data;
  if (!pData) return;

  const selProv = document.getElementById('sel-prov-growth');
  if (selProv && selProv.options.length === 0) {
    pData.provinces.forEach(prov => {
      const opt = document.createElement('option');
      opt.value = prov;
      opt.textContent = prov;
      if (prov === selectedProvinceForGrowth) opt.selected = true;
      selProv.appendChild(opt);
    });
  }
}

function switchProvGrowthMode(mode) {
  currentProvGrowthMode = mode;
  const btnProv = document.getElementById('btn-mode-prov');
  const btnMonth = document.getElementById('btn-mode-month');
  const wrapProv = document.getElementById('wrapper-sel-prov');
  const wrapMonth = document.getElementById('wrapper-sel-month');

  if (mode === 'prov') {
    if (wrapProv) wrapProv.classList.remove('hidden');
    if (wrapMonth) wrapMonth.classList.add('hidden');
    if (btnProv) {
      btnProv.className = 'px-2 py-0.5 rounded font-semibold bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs transition-colors';
    }
    if (btnMonth) {
      btnMonth.className = 'px-2 py-0.5 rounded font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors';
    }
  } else {
    if (wrapProv) wrapProv.classList.add('hidden');
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

function onMonthGrowthSelectChange() {
  const el = document.getElementById('sel-month-growth');
  if (el) {
    selectedMonthForGrowth = parseInt(el.value, 10);
    renderProvinceGrowthWorkspace();
  }
}

function renderProvinceGrowthWorkspace() {
  initProvinceGrowthWorkspace();
  const pData = DATA.province_monthly_data;
  if (!pData) return;

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
  const theadEl = document.getElementById('thead-prov-growth');
  const tbodyEl = document.getElementById('tbody-prov-growth');

  const lblStat1 = document.getElementById('label-stat-1');
  const lblStat2 = document.getElementById('label-stat-2');
  const lblStat3 = document.getElementById('label-stat-3');
  const badgePeak = document.getElementById('badge-prov-peak');
  const badgePeakVol = document.getElementById('badge-prov-peak-vol');
  const badgeJump = document.getElementById('badge-prov-jump');
  const badgeJumpM = document.getElementById('badge-prov-jump-m');
  const badgeYtd = document.getElementById('badge-prov-ytd');
  const badgeYtdSub = document.getElementById('badge-prov-ytd-sub');

  if (currentProvGrowthMode === 'prov') {
    // =========================================================
    // MODE 1: PER PROVINSI
    // =========================================================
    const provInfo = pData.by_province[selectedProvinceForGrowth];
    if (!provInfo) return;

    if (subEl) subEl.innerText = `Tren volume bulanan keberangkatan di ${selectedProvinceForGrowth}`;
    if (lblStat1) lblStat1.innerText = 'Bulan Puncak';
    if (badgePeak) badgePeak.innerText = `${provInfo.peak_month} 2026`;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(provInfo.peak_vol)} pnp`;

    if (lblStat2) lblStat2.innerText = 'Lonjakan MoM';
    if (badgeJump) badgeJump.innerText = provInfo.max_jump_pct > 0 ? `+${provInfo.max_jump_pct}%` : `${provInfo.max_jump_pct}%`;
    if (badgeJumpM) badgeJumpM.innerText = `di ${provInfo.max_jump_month}`;

    if (lblStat3) lblStat3.innerText = 'Total YTD (9 Bln)';
    if (badgeYtd) badgeYtd.innerText = `${(provInfo.total_brg / 1e6).toFixed(2)}M`;
    if (badgeYtdSub) badgeYtdSub.innerText = 'Penumpang Brg';

    if (findingEl) {
      findingEl.innerHTML = `<span class="font-bold text-blue-700 dark:text-blue-400">💡 Temuan Kenaikan:</span> ${provInfo.insight}`;
    }

    // Chart: Bar 9 Bulan
    const barColors = provInfo.monthly.map(m => {
      if (m.is_peak) return '#d97706'; // Amber 600 untuk bulan puncak
      if (m.mom !== null && m.mom >= 15.0) return '#0284c7'; // Sky 600 lonjakan tajam
      if (m.mom !== null && m.mom > 0) return '#38bdf8'; // Sky 400 kenaikan wajar
      return isDark ? '#475569' : '#94a3b8'; // Slate penurunan/normal
    });

    chartProvGrowth = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: provInfo.monthly.map(m => m.short),
        datasets: [{
          label: 'Keberangkatan',
          data: provInfo.monthly.map(m => m.brg),
          backgroundColor: barColors,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const item = provInfo.monthly[ctx.dataIndex];
                const momStr = item.mom !== null ? (item.mom >= 0 ? `+${item.mom}%` : `${item.mom}%`) : 'Baseline';
                return [
                  ` Volume: ${numFmt(ctx.raw)} pnp`,
                  ` Pertumbuhan MoM: ${momStr}`,
                  ` Moda Utama: ${item.dom_moda} (${item.dom_pct}%)`
                ];
              }
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: isDark ? '#94a3b8' : '#64748b' } },
          y: {
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

    // Table: 9 Months
    if (theadEl) {
      theadEl.innerHTML = `
        <th class="py-2 px-2.5">Bulan</th>
        <th class="py-2 px-2.5 text-right">Keberangkatan</th>
        <th class="py-2 px-2.5 text-right">Pertumbuhan (MoM)</th>
        <th class="py-2 px-2.5 text-center">Moda Utama</th>
        <th class="py-2 px-2.5 text-center">Status</th>
      `;
    }

    if (tbodyEl) {
      tbodyEl.innerHTML = '';
      provInfo.monthly.forEach(m => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';

        let momBadge = '<span class="text-slate-400">-</span>';
        if (m.mom !== null) {
          if (m.mom > 0) {
            momBadge = `<span class="text-emerald-600 dark:text-emerald-400 font-bold">▲ +${m.mom}%</span>`;
          } else if (m.mom < 0) {
            momBadge = `<span class="text-rose-600 dark:text-rose-400 font-medium">▼ ${m.mom}%</span>`;
          } else {
            momBadge = `<span class="text-slate-500">0.0%</span>`;
          }
        }

        let statusBadge = '';
        if (m.is_peak) {
          statusBadge = `<span class="bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-amber-300 dark:border-amber-700">🔥 Puncak</span>`;
        } else if (m.mom !== null && m.mom >= 15.0) {
          statusBadge = `<span class="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300 text-[10px] font-semibold px-2 py-0.5 rounded-full">↗ Naik Tajam</span>`;
        } else if (m.mom !== null && m.mom > 0) {
          statusBadge = `<span class="bg-sky-50 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300 text-[10px] px-2 py-0.5 rounded-full">↗ Wajar</span>`;
        } else {
          statusBadge = `<span class="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 text-[10px] px-2 py-0.5 rounded-full">↘ Menurun</span>`;
        }

        tr.innerHTML = `
          <td class="py-2 px-2.5 font-sans font-medium text-slate-900 dark:text-slate-200">${m.name}</td>
          <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${numFmt(m.brg)}</td>
          <td class="py-2 px-2.5 text-right">${momBadge}</td>
          <td class="py-2 px-2.5 text-center text-slate-600 dark:text-slate-400">${m.dom_moda} <span class="text-[10px] text-slate-400">(${m.dom_pct}%)</span></td>
          <td class="py-2 px-2.5 text-center">${statusBadge}</td>
        `;
        tbodyEl.appendChild(tr);
      });
    }

  } else {
    // =========================================================
    // MODE 2: PER BULAN (Deteksi Provinsi Lonjakan Tertinggi)
    // =========================================================
    const monthRank = pData.by_month[selectedMonthForGrowth];
    if (!monthRank) return;

    if (subEl) subEl.innerText = `Provinsi dengan volume & kenaikan tertinggi pada ${monthRank.name} 2026`;
    if (lblStat1) lblStat1.innerText = 'Volume Tertinggi';
    if (badgePeak) badgePeak.innerText = monthRank.top_vol[0].provinsi;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(monthRank.top_vol[0].vol)} pnp`;

    if (lblStat2) lblStat2.innerText = 'Lonjakan % Terbesar';
    if (monthRank.top_growth && monthRank.top_growth.length > 0) {
      if (badgeJump) badgeJump.innerText = `+${monthRank.top_growth[0].mom}%`;
      if (badgeJumpM) badgeJumpM.innerText = monthRank.top_growth[0].provinsi;
    } else {
      if (badgeJump) badgeJump.innerText = '-';
      if (badgeJumpM) badgeJumpM.innerText = 'Awal Tahun';
    }

    if (lblStat3) lblStat3.innerText = 'Fase Periode';
    if (badgeYtd) badgeYtd.innerText = monthRank.name;
    if (badgeYtdSub) badgeYtdSub.innerText = selectedMonthForGrowth === 3 ? 'Puncak Lebaran' : (selectedMonthForGrowth === 4 ? 'Arus Balik' : 'Reguler');

    if (findingEl) {
      let insightStr = '';
      if (selectedMonthForGrowth === 3) {
        insightStr = `Di bulan Maret 2026, arus mudik Lebaran mendorong lonjakan drastis pada <strong>${monthRank.top_vol[0].provinsi}</strong> (${numFmt(monthRank.top_vol[0].vol)} pnp), <strong>${monthRank.top_vol[1].provinsi}</strong>, dan <strong>${monthRank.top_vol[2].provinsi}</strong>. Kenaikan % tertinggi dialami ${monthRank.top_growth.slice(0, 3).map(x => x.provinsi + ' (+' + x.mom + '%)').join(', ')}.`;
      } else if (selectedMonthForGrowth === 4) {
        insightStr = `Di bulan April 2026, mobilitas tetap tinggi karena arus balik Lebaran, dipimpin oleh <strong>${monthRank.top_vol[0].provinsi}</strong> (${numFmt(monthRank.top_vol[0].vol)} pnp) dan <strong>${monthRank.top_vol[1].provinsi}</strong>.`;
      } else if (selectedMonthForGrowth === 7 || selectedMonthForGrowth === 8) {
        insightStr = `Di bulan ${monthRank.name} 2026, pergerakan didominasi liburan sekolah dan wisata, dengan <strong>Bali</strong> dan simpul transit utama di Jawa mempertahankan volume keberangkatan yang sangat tinggi.`;
      } else {
        insightStr = `Di bulan ${monthRank.name} 2026, pergerakan berada dalam ritme operasional rutin bulanan dengan volume terbesar di ${monthRank.top_vol.slice(0, 3).map(x => x.provinsi).join(', ')}.`;
      }
      findingEl.innerHTML = `<span class="font-bold text-blue-700 dark:text-blue-400">💡 Ringkasan Bulan ${monthRank.name}:</span> ${insightStr}`;
    }

    // Chart: Horizontal Bar Top 6 Provinsi di Bulan Ini
    const topVolSlice = monthRank.top_vol.slice(0, 6);
    chartProvGrowth = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topVolSlice.map(x => x.provinsi),
        datasets: [{
          label: `Keberangkatan (${monthRank.name})`,
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
              label: ctx => ` Volume ${monthRank.name}: ${numFmt(ctx.raw)} pnp`
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

    // Table: Top 6 Volume di Bulan Ini
    if (theadEl) {
      theadEl.innerHTML = `
        <th class="py-2 px-2.5">Peringkat & Provinsi</th>
        <th class="py-2 px-2.5 text-right">Keberangkatan (${monthRank.name})</th>
        <th class="py-2 px-2.5 text-right">Lonjakan vs Bulan Lalu</th>
        <th class="py-2 px-2.5 text-center">Status</th>
      `;
    }

    if (tbodyEl) {
      tbodyEl.innerHTML = '';
      topVolSlice.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';

        const gItem = monthRank.top_growth ? monthRank.top_growth.find(g => g.provinsi === item.provinsi) : null;
        let growthBadge = '<span class="text-slate-400">-</span>';
        if (gItem) {
          growthBadge = `<span class="text-emerald-600 dark:text-emerald-400 font-bold">▲ +${gItem.mom}%</span>`;
        }

        tr.innerHTML = `
          <td class="py-2 px-2.5 font-sans font-medium text-slate-900 dark:text-slate-200">
            <span class="inline-block w-4 text-xs font-bold text-slate-400">#${idx + 1}</span> ${item.provinsi}
          </td>
          <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${numFmt(item.vol)}</td>
          <td class="py-2 px-2.5 text-right">${growthBadge}</td>
          <td class="py-2 px-2.5 text-center">
            ${idx === 0 ? '<span class="bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 text-[10px] font-bold px-2 py-0.5 rounded-full">Top Volume</span>' : '<span class="bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 text-[10px] px-2 py-0.5 rounded-full">Tinggi</span>'}
          </td>
        `;
        tbodyEl.appendChild(tr);
      });
    }
  }
}

// Backward compatibility alias for any existing code
function renderDOWWorkspace() {
  renderProvinceGrowthWorkspace();
}"""

match_func = old_func_pattern.search(content)
if not match_func:
    raise Exception("Pattern for renderDOWWorkspace not found!")

content = old_func_pattern.sub(new_func_js, content, count=1)
print("3. JavaScript logic replaced successfully.")

# Save to index.html and Dashboard_Mobilitas_Nasional_2026.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('Dashboard_Mobilitas_Nasional_2026.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("4. Successfully saved to index.html and Dashboard_Mobilitas_Nasional_2026.html!")
