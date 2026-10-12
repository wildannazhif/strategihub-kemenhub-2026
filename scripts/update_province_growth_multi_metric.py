import json
import re
import os

print("Applying multi-metric province growth support to HTML dashboards...")

# 1. Load updated bundle
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle_json_str = json.dumps(bundle, ensure_ascii=False)
print("Loaded bundle, size:", len(bundle_json_str) / 1024, "KB")

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
    const provInfo = pData.by_province[selectedProvinceForGrowth] || pData.by_province[pData.provinces[0]];
    if (!provInfo) return;

    if (subEl) subEl.innerText = `Tren volume bulanan ${mCfg.verb} di ${provInfo.provinsi}`;
    if (lblStat1) lblStat1.innerText = 'Bulan Puncak';
    if (badgePeak) badgePeak.innerText = `${provInfo.peak_month} 2026`;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(provInfo.peak_vol)} ${mCfg.unit}`;

    if (lblStat2) lblStat2.innerText = 'Lonjakan MoM';
    if (badgeJump) badgeJump.innerText = provInfo.max_jump_pct > 0 ? `+${provInfo.max_jump_pct}%` : `${provInfo.max_jump_pct}%`;
    if (badgeJumpM) badgeJumpM.innerText = `di ${provInfo.max_jump_month}`;

    if (lblStat3) lblStat3.innerText = 'Total YTD (9 Bln)';
    const totVal = provInfo.total !== undefined ? provInfo.total : provInfo.total_brg;
    if (badgeYtd) {
      if (totVal >= 1e6) {
        badgeYtd.innerText = `${(totVal / 1e6).toFixed(2)}M`;
      } else if (totVal >= 1e3) {
        badgeYtd.innerText = `${(totVal / 1e3).toFixed(1)}k`;
      } else {
        badgeYtd.innerText = numFmt(totVal);
      }
    }
    if (badgeYtdSub) badgeYtdSub.innerText = mCfg.short;

    if (findingEl) {
      let insightStr = '';
      if (provInfo.peak_month_num === 3) {
        insightStr = `Aktivitas ${mCfg.verb} di ${provInfo.provinsi} mencapai puncak tahunan pada bulan Maret 2026 (${numFmt(provInfo.peak_vol)} ${mCfg.unit}, naik ${provInfo.max_jump_pct > 0 ? '+' : ''}${provInfo.max_jump_pct}% vs Februari), didorong oleh lonjakan arus mudik Lebaran 1447 H.`;
      } else if (provInfo.peak_month_num === 4) {
        insightStr = `Aktivitas ${mCfg.verb} di ${provInfo.provinsi} mencapai titik tertinggi pada bulan April 2026 (${numFmt(provInfo.peak_vol)} ${mCfg.unit}) sejalan dengan arus balik Lebaran.`;
      } else if (provInfo.peak_month_num === 7 || provInfo.peak_month_num === 8) {
        insightStr = `Aktivitas ${mCfg.verb} di ${provInfo.provinsi} mencapai puncak tahunan pada bulan ${provInfo.peak_month} 2026 (${numFmt(provInfo.peak_vol)} ${mCfg.unit}), didorong oleh mobilitas masa liburan sekolah dan wisata.`;
      } else if (provInfo.peak_month_num === 6) {
        insightStr = `Aktivitas ${mCfg.verb} di ${provInfo.provinsi} mencapai volume tertinggi pada bulan Juni 2026 (${numFmt(provInfo.peak_vol)} ${mCfg.unit}) saat dimulainya liburan sekolah nasional.`;
      } else {
        insightStr = `Aktivitas ${mCfg.verb} di ${provInfo.provinsi} mencapai volume tertinggi pada bulan ${provInfo.peak_month} 2026 (${numFmt(provInfo.peak_vol)} ${mCfg.unit}) dengan kenaikan MoM tertinggi ${provInfo.max_jump_pct > 0 ? '+' : ''}${provInfo.max_jump_pct}% di ${provInfo.max_jump_month}.`;
      }
      findingEl.innerHTML = `<span class="font-bold text-blue-700 dark:text-blue-400">💡 Temuan Kenaikan:</span> ${insightStr}`;
    }

    // Chart: Bar 9 Bulan
    const barColors = provInfo.monthly.map(m => {
      if (m.is_peak) return '#d97706'; // Amber 600 untuk bulan puncak
      if (m.mom !== null && m.mom > 0) return '#0284c7'; // Sky 600 pertumbuhan positif
      return isDark ? '#475569' : '#94a3b8'; // Slate penurunan / awal tahun
    });

    chartProvGrowth = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: provInfo.monthly.map(m => m.short),
        datasets: [{
          label: mCfg.label,
          data: provInfo.monthly.map(m => m.val !== undefined ? m.val : m.brg),
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
                  ` Volume: ${numFmt(ctx.raw)} ${mCfg.unit}`,
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
        <th class="py-2 px-2.5 text-right">${mCfg.label}</th>
        <th class="py-2 px-2.5 text-right">Pertumbuhan (MoM)</th>
        <th class="py-2 px-2.5 text-center">Moda Utama</th>
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

        const mVal = m.val !== undefined ? m.val : m.brg;
        tr.innerHTML = `
          <td class="py-2 px-2.5 font-sans font-medium text-slate-900 dark:text-slate-200">${m.name}</td>
          <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${numFmt(mVal)}</td>
          <td class="py-2 px-2.5 text-right">${momBadge}</td>
          <td class="py-2 px-2.5 text-center text-slate-600 dark:text-slate-400">${m.dom_moda} <span class="text-[10px] text-slate-400">(${m.dom_pct}%)</span></td>
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

    if (subEl) subEl.innerText = `Provinsi dengan volume ${mCfg.verb} tertinggi pada ${monthRank.name} 2026`;
    if (lblStat1) lblStat1.innerText = 'Volume Tertinggi';
    if (badgePeak) badgePeak.innerText = monthRank.top_vol[0].provinsi;
    if (badgePeakVol) badgePeakVol.innerText = `${numFmt(monthRank.top_vol[0].vol)} ${mCfg.unit}`;

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
      const top1 = monthRank.top_vol[0];
      const top2 = monthRank.top_vol[1];
      const top3 = monthRank.top_vol[2];
      const growthNote = (monthRank.top_growth && monthRank.top_growth.length > 0)
        ? ` Kenaikan % tertinggi dialami ${monthRank.top_growth.slice(0, 3).map(x => x.provinsi + ' (+' + x.mom + '%)').join(', ')}.`
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

    // Table: Top 6 Volume di Bulan Ini
    if (theadEl) {
      theadEl.innerHTML = `
        <th class="py-2 px-2.5">Peringkat & Provinsi</th>
        <th class="py-2 px-2.5 text-right">${mCfg.label} (${monthRank.name})</th>
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

    # 2. Update updateDashboardMetricAndDirection to explicitly call renderProvinceGrowthWorkspace()
    html = html.replace(
        "renderTimelineChart();\n  renderMonthlyTable();\n  renderDOWWorkspace();",
        "renderTimelineChart();\n  renderMonthlyTable();\n  renderProvinceGrowthWorkspace();\n  renderDOWWorkspace();"
    )

    # 3. Replace Province Growth Workspace JS block
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
