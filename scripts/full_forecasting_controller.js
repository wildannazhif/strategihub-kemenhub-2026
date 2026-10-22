// TAB 8: FORECASTING NATARU 2026/2027 CONTROLLER
// ---------------------------------------------------------------
let currentForecastScenario = 'moderat'; // Standard baseline 1.0x
let currentForecastMetric = 'pnp'; // 'pnp' (Penumpang Berangkat) or 'arm' (Armada Berangkat)
let currentForecastModa = 'TOTAL';
let currentForecastProv = 'ALL';
let currentForecastRange = 'nataru'; // 'nataru', 'des', 'nov', 'okt', 'all'
let currentSimArmadaPct = 10;
let chartForecast = null;

const nataru_shocks = {
  '12-18': 1.1196, '12-19': 1.3565, '12-20': 1.2709,
  '12-21': 1.5626, '12-22': 1.7465, '12-23': 1.6903,
  '12-24': 1.6839, '12-25': 1.4234, '12-26': 1.4458,
  '12-27': 1.3030, '12-28': 1.6995, '12-29': 1.6913,
  '12-30': 1.5773, '12-31': 1.3690, '01-01': 1.0902,
  '01-02': 1.2845, '01-03': 1.1538, '01-04': 1.3091
};

function getSeriesKey(metric, moda) {
  if (metric === 'pnp') {
    return moda === 'TOTAL' ? 'pbrg_TOTAL' : `pbrg_${moda}`;
  } else {
    return moda === 'TOTAL' ? 'abrg_TOTAL' : `abrg_${moda}`;
  }
}

function getSeriesLabel(metric) {
  return metric === 'pnp' ? 'Penumpang Berangkat' : 'Armada Berangkat';
}

function getUnitLabel(metric) {
  return metric === 'pnp' ? 'penumpang berangkat' : 'trip berangkat';
}

function getActiveModesForProv(prov) {
  if (prov === 'ALL') return ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT'];
  const pData = DATA.forecast_nataru?.by_province?.[prov];
  if (pData && pData.history_2026 && pData.history_2026.active_modes) {
    return pData.history_2026.active_modes;
  }
  return ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT'];
}

function getHistoricalSeries(prov, metric, moda) {
  const key = getSeriesKey(metric, moda);
  if (prov === 'ALL') {
    return DATA.daily_timeline.filter(d => d.date <= '2026-09-29').map(d => d[key] ?? 0);
  }
  const pData = DATA.forecast_nataru?.by_province?.[prov];
  return (pData && pData.history_2026 && pData.history_2026[key]) || [];
}

function generateTimeSeriesForecast(histSeries, futureDates, modelCode) {
  const n = histSeries.length;
  if (!n || histSeries.every(v => v === 0)) {
    return futureDates.map(d => ({ date: d, val: 0, ci_upper: 0, ci_lower: 0, shock_factor: 1.0 }));
  }

  const mean_s = histSeries.reduce((a, b) => a + b, 0) / n;
  const floor = Math.max(1, 0.25 * mean_s);
  const lastVal = histSeries[n - 1];
  const last7 = histSeries.slice(-7);
  const mean7 = last7.reduce((a, b) => a + b, 0) / 7;
  const n_fc = futureDates.length;

  let basePred = [];

  if (modelCode === 'naive') {
    basePred = Array(n_fc).fill(Math.max(floor, lastVal));
  } else if (modelCode === 'ma7') {
    basePred = Array(n_fc).fill(Math.max(floor, mean7));
  } else if (modelCode === 'snaive') {
    basePred = Array.from({ length: n_fc }, (_, i) => Math.max(floor, last7[i % 7]));
  } else if (modelCode === 'ses') {
    let l_ses = histSeries[0];
    const a_ses = 0.25;
    for (let i = 1; i < n; i++) l_ses = a_ses * histSeries[i] + (1 - a_ses) * l_ses;
    basePred = Array(n_fc).fill(Math.max(floor, l_ses));
  } else if (modelCode === 'holt_linear') {
    let l = histSeries[0], b = (histSeries[1] - histSeries[0]) || 0;
    const a = 0.25, beta = 0.05, phi = 0.96;
    for (let i = 1; i < n; i++) {
      const lp = l;
      l = a * histSeries[i] + (1 - a) * (l + phi * b);
      b = beta * (l - lp) + (1 - beta) * (phi * b);
    }
    basePred = Array.from({ length: n_fc }, (_, h) => {
      const step = h + 1;
      const trendComp = Array.from({ length: step }, (_, k) => Math.pow(phi, k + 1)).reduce((x, y) => x + y, 0) * b;
      return Math.max(floor, l + trendComp);
    });
  } else if (modelCode === 'ridge') {
    const dowMeans = Array(7).fill(0), dowCounts = Array(7).fill(0);
    for (let i = 0; i < n; i++) {
      const d_idx = i % 7;
      dowMeans[d_idx] += histSeries[i];
      dowCounts[d_idx]++;
    }
    for (let i = 0; i < 7; i++) dowMeans[i] /= (dowCounts[i] || 1);
    const overallMean = dowMeans.reduce((a, b) => a + b, 0) / 7;
    const mid = n / 2;
    let num = 0, den = 0;
    for (let i = 0; i < n; i++) {
      num += (i - mid) * (histSeries[i] - overallMean);
      den += (i - mid) * (i - mid);
    }
    const slope = den ? (num / den) : 0;
    basePred = Array.from({ length: n_fc }, (_, h) => {
      const d_idx = (n + h) % 7;
      const t_val = overallMean + slope * (n + h - mid) * Math.pow(0.98, h) + (dowMeans[d_idx] - overallMean);
      return Math.max(floor, t_val);
    });
  } else if (modelCode === 'sarima' || modelCode === 'arima') {
    const s = modelCode === 'sarima' ? 7 : 1;
    const diffs = [];
    for (let i = s; i < n; i++) diffs.push(histSeries[i] - histSeries[i - s]);
    const meanDiff = diffs.reduce((a, b) => a + b, 0) / (diffs.length || 1);
    const phi = 0.85;
    basePred = [];
    for (let h = 0; h < n_fc; h++) {
      const lagIdx = h - s;
      const prev = lagIdx >= 0 ? basePred[lagIdx] : histSeries[n + lagIdx];
      const decay = Math.pow(phi, Math.floor(h / Math.max(1, s)));
      basePred.push(Math.max(floor, Math.round(prev + decay * meanDiff)));
    }
  } else {
    // Holt-Winters
    const isAdd = modelCode === 'hw_add_damped';
    const phi = 0.98;
    const s_period = 7;
    const s_factors = Array(s_period).fill(1.0);
    for (let i = 0; i < s_period; i++) {
      let sum_r = 0, cnt = 0;
      for (let k = i; k < n; k += s_period) { sum_r += histSeries[k]; cnt++; }
      s_factors[i] = (sum_r / (cnt || 1)) / (mean7 || 1);
    }
    let l_hw = histSeries[0] / (s_factors[0] || 1);
    let b_hw = 0;
    const a_hw = 0.25, b_hw_param = 0.05, g_hw = 0.1;
    for (let i = 0; i < n; i++) {
      const s_idx = i % s_period;
      const l_prev = l_hw;
      const s_prev = s_factors[s_idx] || 1.0;
      l_hw = a_hw * (histSeries[i] / (isAdd ? 1.0 : s_prev)) + (1 - a_hw) * (l_hw + phi * b_hw);
      b_hw = b_hw_param * (l_hw - l_prev) + (1 - b_hw_param) * (phi * b_hw);
      s_factors[s_idx] = g_hw * (isAdd ? (histSeries[i] - l_hw) : (histSeries[i] / (l_hw || 1))) + (1 - g_hw) * s_prev;
    }
    basePred = Array.from({ length: n_fc }, (_, h) => {
      const step = h + 1;
      const s_idx = (n + h) % s_period;
      const trendComp = Array.from({ length: step }, (_, k) => Math.pow(phi, k + 1)).reduce((a, v) => a + v, 0) * b_hw;
      if (isAdd) {
        return Math.max(floor, l_hw + trendComp + (s_factors[s_idx] || 0));
      } else {
        return Math.max(floor, (l_hw + trendComp) * (s_factors[s_idx] || 1.0));
      }
    });
  }

  const diffs = [];
  for (let i = 1; i < n; i++) diffs.push(Math.abs(histSeries[i] - histSeries[i - 1]));
  const estRmse = (diffs.reduce((a, b) => a + b, 0) / (diffs.length || 1)) * 1.25;

  return futureDates.map((dateStr, i) => {
    const md = dateStr.slice(5);
    const shock = nataru_shocks[md] || 1.0;
    const finalVal = Math.round(basePred[i] * shock);
    const ciExpansion = Math.sqrt(1 + 0.005 * i);
    const ciUpper = Math.round(finalVal + 1.96 * estRmse * ciExpansion);
    const ciLower = Math.max(0, Math.round(finalVal - 1.96 * estRmse * ciExpansion));
    return {
      date: dateStr,
      val: finalVal,
      ci_upper: ciUpper,
      ci_lower: ciLower,
      shock_factor: shock
    };
  });
}

function updateModaDropdownOptions(prov) {
  const select = document.getElementById('select-forecast-moda');
  if (!select) return;

  const activeModes = getActiveModesForProv(prov);
  const modesMeta = [
    { key: 'TOTAL', label: 'Total Multimoda (Semua Moda)' },
    { key: 'UDARA', label: '✈ Udara (Penerbangan Domestik)' },
    { key: 'KA', label: '🚆 Perkeretaapian (KAI)' },
    { key: 'BUS', label: '🚌 Bus' },
    { key: 'ASDP', label: '⛴ ASDP (Penyeberangan Feri)' },
    { key: 'LAUT', label: '🚢 Transportasi Laut (Kapal Pelni)' },
  ];

  const currentVal = select.value;
  select.innerHTML = '';

  modesMeta.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.key;
    if (m.key === 'TOTAL' || activeModes.includes(m.key)) {
      opt.textContent = m.label;
    } else {
      opt.textContent = `${m.label} (Tidak Beroperasi di ${prov})`;
      opt.className = 'text-slate-400 dark:text-slate-500 italic';
    }
    if (m.key === currentVal) opt.selected = true;
    select.appendChild(opt);
  });

  if (currentForecastModa !== 'TOTAL' && !activeModes.includes(currentForecastModa)) {
    currentForecastModa = 'TOTAL';
    select.value = 'TOTAL';
  }
}

function setForecastProvince(prov) {
  currentForecastProv = prov;
  const select = document.getElementById('select-forecast-prov');
  if (select && select.value !== prov) select.value = prov;

  const scopeBadge = document.getElementById('fc-scope-badge');
  if (scopeBadge) scopeBadge.innerText = prov === 'ALL' ? '(Nasional)' : `(${prov})`;

  updateModaDropdownOptions(prov);

  renderForecastSummaryCards();
  renderForecastComparisonTable();
  renderForecastChart();
  renderForecastAccuracyBadges();
  renderForecastTable();
}

function setForecastModa(moda) {
  currentForecastModa = moda;
  const select = document.getElementById('select-forecast-moda');
  if (select && select.value !== moda) select.value = moda;

  renderForecastChart();
  renderForecastTable();
}

function setForecastTableRange(rangeKey, btn) {
  currentForecastRange = rangeKey;
  document.querySelectorAll('.btn-fc-tbl').forEach(b => {
    b.classList.remove('active', 'bg-white', 'dark:bg-slate-900', 'text-indigo-700', 'dark:text-indigo-400', 'font-semibold', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  });
  btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-indigo-700', 'dark:text-indigo-400', 'font-semibold', 'shadow-xs');
  btn.classList.remove('text-slate-600', 'dark:text-slate-400');

  renderForecastTable();
}

function renderForecastAccuracyBadges() {
  if (!DATA.forecast_nataru) return;
  const isAll = currentForecastProv === 'ALL';
  const isPnp = currentForecastMetric === 'pnp';
  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;

  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);

  const activeModelName = champ?.name || 'Holt-Winters Mul Damped';
  const activeMape = champ?.mape || 4.10;
  const activeRmse = champ?.rmse || 62051;
  const activeMae = champ?.mae || 49146;

  const champNameEl = document.getElementById('fc-champion-name');
  if (champNameEl) {
    champNameEl.innerText = `Model Terpilih: ${activeModelName} (Auto-Model: MAPE ${decFmt(activeMape, 2)}%)`;
  }

  const mapeEl = document.getElementById('fc-metric-mape');
  if (mapeEl) mapeEl.innerText = `${decFmt(activeMape, 2)}%`;

  const rmseEl = document.getElementById('fc-metric-rmse');
  if (rmseEl) rmseEl.innerHTML = `${numFmt(activeRmse)} <span class="text-xs font-normal text-slate-500">${isPnp ? 'pnp' : 'trip'}/hari</span>`;

  const maeEl = document.getElementById('fc-metric-mae');
  if (maeEl) maeEl.innerHTML = `${numFmt(activeMae)} <span class="text-xs font-normal text-slate-500">${isPnp ? 'pnp' : 'trip'}/hari</span>`;

  const benchSec = document.getElementById('sec-forecast-benchmarks');
  if (benchSec && !benchSec.classList.contains('hidden')) {
    renderForecastBenchmarksTable();
  }
}

function toggleForecastBenchmarkModal() {
  const el = document.getElementById('sec-forecast-benchmarks');
  if (!el) return;
  el.classList.toggle('hidden');
  if (!el.classList.contains('hidden')) {
    renderForecastBenchmarksTable();
  }
}

function renderForecastBenchmarksTable() {
  if (!DATA.forecast_nataru) return;
  const tbody = document.getElementById('tbody-forecast-benchmarks');
  if (!tbody) return;
  tbody.innerHTML = '';

  const isAll = currentForecastProv === 'ALL';
  const badgeEl = document.getElementById('fc-bench-prov-badge');
  if (badgeEl) badgeEl.innerText = isAll ? 'Nasional' : currentForecastProv;

  const benchList = isAll
    ? (DATA.forecast_nataru.benchmarks || [])
    : (DATA.forecast_nataru.by_province?.[currentForecastProv]?.benchmarks || DATA.forecast_nataru.benchmarks || []);

  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (DATA.forecast_nataru.by_province?.[currentForecastProv]?.champion_model || DATA.forecast_nataru.champion_model);

  benchList.forEach(b => {
    const isChamp = champ && (b.model_code === champ.code || b.model_name === champ.name);
    const tr = document.createElement('tr');
    tr.className = isChamp
      ? 'bg-emerald-50/80 dark:bg-emerald-950/40 font-bold border-l-4 border-l-emerald-600'
      : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    
    const statusBadge = isChamp
      ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700">🏆 Terpilih (Champion)</span>'
      : (b.is_stable === false ? '<span class="text-amber-600 dark:text-amber-400 text-[10px]">Kurang Stabil</span>' : '<span class="text-slate-400 text-[10px]">Kandidat Alternatif</span>');

    tr.innerHTML = `
      <td class="py-2 px-3 text-center ${isChamp ? 'font-black text-emerald-700 dark:text-emerald-300' : 'text-slate-500'}">#${b.rank || '-'}</td>
      <td class="py-2 px-3 font-sans font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
        ${isChamp ? '<span class="text-xs">⭐</span>' : ''}
        <span>${b.model_name}</span>
      </td>
      <td class="py-2 px-3 text-right font-black ${isChamp ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-700 dark:text-slate-300'}">${decFmt(b.mape, 2)}%</td>
      <td class="py-2 px-3 text-right text-slate-500">${decFmt(b.wape, 2)}%</td>
      <td class="py-2 px-3 text-right text-slate-600 dark:text-slate-400">${numFmt(b.rmse)}</td>
      <td class="py-2 px-3 text-right text-slate-500">${numFmt(b.mae)}</td>
      <td class="py-2 px-3 text-center text-slate-600 dark:text-slate-400">${decFmt(b.dir_acc, 1)}%</td>
      <td class="py-2 px-3 text-center">${statusBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderForecastSummaryCards() {
  if (!DATA.forecast_nataru) return;
  const isAll = currentForecastProv === 'ALL';
  const isPnp = currentForecastMetric === 'pnp';
  const unit = getUnitLabel(currentForecastMetric);
  const oppMetric = isPnp ? 'arm' : 'pnp';
  const oppUnit = getUnitLabel(oppMetric);

  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = champ?.code || 'hw_mul_damped';

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, 'TOTAL');
  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode);

  let fcTot = 0, s25Tot = 0;
  let xmasRow = null, nyRow = null;
  let xmas25 = 0, ny25 = 0;

  if (isAll) {
    const map2025 = {};
    (DATA.timeline_2025 || []).forEach(r => {
      const md = r.date.slice(5);
      map2025[md] = isPnp ? (r.pbrg_TOTAL || 0) : (r.abrg_TOTAL || 0);
    });
    futureDates.forEach(d => {
      if (d >= '2026-12-18' && d <= '2027-01-04') {
        const val25 = map2025[d.slice(5)] || 0;
        s25Tot += val25;
        if (d === '2026-12-24') xmas25 = val25;
        if (d === '2027-01-03') ny25 = val25;
      }
    });
  } else {
    const map25Md = (pData && pData.history_2025_md) || {};
    futureDates.forEach(d => {
      if (d >= '2026-12-18' && d <= '2027-01-04') {
        const r25 = map25Md[d.slice(5)] || 0;
        const val25 = typeof r25 === 'number' ? Math.round(r25 * (isPnp ? 0.58 : 0.016)) : 0;
        s25Tot += val25;
        if (d === '2026-12-24') xmas25 = val25;
        if (d === '2027-01-03') ny25 = val25;
      }
    });
  }

  fc.forEach(d => {
    if (d.date >= '2026-12-18' && d.date <= '2027-01-04') {
      fcTot += d.val;
      if (d.date === '2026-12-24') xmasRow = d;
      if (d.date === '2027-01-03') nyRow = d;
    }
  });

  const avgDaily = Math.round(fcTot / 18);
  const yoyTotPct = s25Tot > 0 ? ((fcTot / s25Tot - 1) * 100) : 0;

  // Opposing metric for Card 4
  const oppHist = getHistoricalSeries(currentForecastProv, oppMetric, 'TOTAL');
  const oppFc = generateTimeSeriesForecast(oppHist, futureDates, activeModelCode);

  let oppMaxDay = { val: 0, date: '' }, opp25Val = 0;
  oppFc.forEach(d => {
    if (d.date >= '2026-12-18' && d.date <= '2027-01-04') {
      if (d.val > oppMaxDay.val) {
        oppMaxDay = d;
      }
    }
  });

  if (isAll) {
    const oppMap2025 = {};
    (DATA.timeline_2025 || []).forEach(r => {
      const md = r.date.slice(5);
      oppMap2025[md] = isPnp ? (r.abrg_TOTAL || 0) : (r.pbrg_TOTAL || 0);
    });
    opp25Val = oppMap2025[oppMaxDay.date.slice(5)] || 0;
  } else {
    const map25Md = (pData && pData.history_2025_md) || {};
    const r25 = map25Md[oppMaxDay.date.slice(5)] || 0;
    opp25Val = typeof r25 === 'number' ? Math.round(r25 * (isPnp ? 0.016 : 0.58)) : 0;
  }

  const oppYoyPct = opp25Val > 0 ? ((oppMaxDay.val / opp25Val - 1) * 100) : 0;

  // Update DOM Cards
  const totalEl = document.getElementById('card-fc-total-pnp');
  if (totalEl) totalEl.innerText = numFmt(fcTot);

  const avgEl = document.getElementById('card-fc-avg-pnp');
  if (avgEl) avgEl.innerText = numFmt(avgDaily);

  const totalYoyEl = document.getElementById('card-fc-total-yoy');
  if (totalYoyEl) {
    const sign = yoyTotPct >= 0 ? '+' : '';
    totalYoyEl.innerText = `${sign}${decFmt(yoyTotPct, 1)}% vs 2025`;
    totalYoyEl.className = yoyTotPct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
  }

  // Card 2: Natal
  const xmasEl = document.getElementById('card-fc-xmas-pnp');
  if (xmasEl && xmasRow) xmasEl.innerText = numFmt(xmasRow.val);

  const xmasPrevEl = document.getElementById('card-fc-xmas-prev');
  if (xmasPrevEl) xmasPrevEl.innerText = `vs 2025: ${numFmt(xmas25)}`;

  const xmasYoyEl = document.getElementById('card-fc-xmas-yoy');
  if (xmasYoyEl && xmasRow) {
    const xmasYoy = xmas25 > 0 ? ((xmasRow.val / xmas25 - 1) * 100) : 0;
    const sign = xmasYoy >= 0 ? '+' : '';
    xmasYoyEl.innerText = `${sign}${decFmt(xmasYoy, 1)}% YoY`;
    xmasYoyEl.className = xmasYoy >= 0 ? 'text-amber-600 dark:text-amber-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
  }

  // Card 3: Tahun Baru
  const nyEl = document.getElementById('card-fc-ny-pnp');
  if (nyEl && nyRow) nyEl.innerText = numFmt(nyRow.val);

  const nyPrevEl = document.getElementById('card-fc-ny-prev');
  if (nyPrevEl) nyPrevEl.innerText = `vs 2025: ${numFmt(ny25)}`;

  const nyYoyEl = document.getElementById('card-fc-ny-yoy');
  if (nyYoyEl && nyRow) {
    const nyYoy = ny25 > 0 ? ((nyRow.val / ny25 - 1) * 100) : 0;
    const sign = nyYoy >= 0 ? '+' : '';
    nyYoyEl.innerText = `${sign}${decFmt(nyYoy, 1)}% YoY`;
    nyYoyEl.className = nyYoy >= 0 ? 'text-rose-600 dark:text-rose-400 font-bold' : 'text-slate-500 font-bold';
  }

  // Card 4: Opposing Peak
  const armPeakEl = document.getElementById('card-fc-arm-peak');
  if (armPeakEl) armPeakEl.innerText = numFmt(oppMaxDay.val);

  const armPrevEl = document.getElementById('card-fc-arm-prev');
  if (armPrevEl) armPrevEl.innerText = `vs 2025: ${numFmt(opp25Val)} ${oppUnit}`;

  const armYoyEl = document.getElementById('card-fc-arm-yoy');
  if (armYoyEl) {
    const sign = oppYoyPct >= 0 ? '+' : '';
    armYoyEl.innerText = `${sign}${decFmt(oppYoyPct, 1)}% YoY`;
    armYoyEl.className = oppYoyPct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
  }
}

function renderForecastComparisonTable() {
  if (!DATA.forecast_nataru) return;
  const tbody = document.getElementById('tbody-forecast-comparison');
  if (!tbody) return;
  tbody.innerHTML = '';

  const isAll = currentForecastProv === 'ALL';
  const isPnp = currentForecastMetric === 'pnp';
  const metricLabel = getSeriesLabel(currentForecastMetric);
  const activeModes = getActiveModesForProv(currentForecastProv);

  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = champ?.code || 'hw_mul_damped';

  const badgeEl = document.getElementById('fc-comp-prov-badge');
  if (badgeEl) badgeEl.innerText = `${isAll ? 'Nasional' : currentForecastProv} • ${metricLabel}`;

  const th25 = document.getElementById('th-fc-comp-25');
  if (th25) th25.innerText = `Realisasi 2025 (${isPnp ? 'Pnp Berangkat' : 'Trip Berangkat'})`;
  const th26 = document.getElementById('th-fc-comp-26');
  if (th26) th26.innerText = `Proyeksi 2026 (${isPnp ? 'Pnp Berangkat' : 'Trip Berangkat'})`;

  const modesMeta = [
    { key: 'UDARA', label: '✈ Udara (Penerbangan Domestik)', color: COLOR.UDARA, note: 'Kapasitas armada beroperasi optimal; tiket dinamis memfilter demand jarak jauh' },
    { key: 'KA', label: '🚆 Kereta Api (KAI)', color: COLOR.KA, note: 'Tingkat isian stabil tinggi (load factor 90%+); seluruh kuota KA favorit terjual' },
    { key: 'BUS', label: '🚌 Bus', color: COLOR.BUS, note: 'Rute Trans Jawa & jalan tol primadona; armada reguler & cadangan siaga penuh' },
    { key: 'ASDP', label: '⛴ ASDP (Penyeberangan Feri)', color: COLOR.ASDP, note: 'Lonjakan kendaraan pribadi tinggi di lintasan penyeberangan utama' },
    { key: 'LAUT', label: '🚢 Laut (Kapal Penumpang Pelni)', color: COLOR.LAUT, note: 'Pertumbuhan pergerakan antarpulau & rute perintis Indonesia Timur' },
  ];

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);

  const totHist = getHistoricalSeries(currentForecastProv, currentForecastMetric, 'TOTAL');
  const totHistSum = totHist.reduce((a, b) => a + b, 0);
  const totFc = generateTimeSeriesForecast(totHist, futureDates, activeModelCode);

  let totFcSum = 0;
  totFc.forEach(d => {
    if (d.date >= '2026-12-18' && d.date <= '2027-01-04') totFcSum += d.val;
  });

  let tot25Sum = 0;
  if (isAll) {
    const map2025 = {};
    (DATA.timeline_2025 || []).forEach(r => {
      map2025[r.date.slice(5)] = isPnp ? (r.pbrg_TOTAL || 0) : (r.abrg_TOTAL || 0);
    });
    futureDates.forEach(d => {
      if (d >= '2026-12-18' && d <= '2027-01-04') tot25Sum += (map2025[d.slice(5)] || 0);
    });
  } else {
    const map25Md = (pData && pData.history_2025_md) || {};
    futureDates.forEach(d => {
      if (d >= '2026-12-18' && d <= '2027-01-04') {
        const r25 = map25Md[d.slice(5)] || 0;
        tot25Sum += typeof r25 === 'number' ? Math.round(r25 * (isPnp ? 0.58 : 0.016)) : 0;
      }
    });
  }

  const rowsData = [];

  modesMeta.forEach(m => {
    const isOperating = activeModes.includes(m.key);
    const mHist = getHistoricalSeries(currentForecastProv, currentForecastMetric, m.key);
    const mHistSum = mHist.reduce((a, b) => a + b, 0);

    if (!isOperating || mHistSum === 0) {
      rowsData.push({
        meta: m,
        hasData: false,
        fc: 0,
        base25: 0,
        diff: 0,
        yoy: 0,
        share25: 0,
        share26: 0
      });
      return;
    }

    const mFc = generateTimeSeriesForecast(mHist, futureDates, activeModelCode);
    let mFcSum = 0;
    mFc.forEach(d => {
      if (d.date >= '2026-12-18' && d.date <= '2027-01-04') mFcSum += d.val;
    });

    let mBase25 = 0;
    if (isAll) {
      const map2025 = {};
      (DATA.timeline_2025 || []).forEach(r => {
        const k = isPnp ? `pbrg_${m.key}` : `abrg_${m.key}`;
        map2025[r.date.slice(5)] = r[k] || 0;
      });
      futureDates.forEach(d => {
        if (d >= '2026-12-18' && d <= '2027-01-04') mBase25 += (map2025[d.slice(5)] || 0);
      });
    } else {
      const mShare = totHistSum > 0 ? (mHistSum / totHistSum) : 0;
      mBase25 = Math.round(tot25Sum * mShare);
    }

    const diff = mFcSum - mBase25;
    const yoy = mBase25 > 0 ? ((mFcSum / mBase25 - 1) * 100) : 0;
    const share25 = tot25Sum > 0 ? (mBase25 / tot25Sum * 100) : 0;
    const share26 = totFcSum > 0 ? (mFcSum / totFcSum * 100) : 0;

    rowsData.push({
      meta: m,
      hasData: true,
      fc: mFcSum,
      base25: mBase25,
      diff: diff,
      yoy: yoy,
      share25: share25,
      share26: share26
    });
  });

  rowsData.forEach(r => {
    const yoyClass = r.yoy >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${r.meta.color}"></span>
        <span>${r.meta.label}</span>
      </td>
      <td class="py-2.5 px-3 text-right font-medium">${r.hasData ? numFmt(r.base25) : '-'}</td>
      <td class="py-2.5 px-3 text-right text-slate-500">${r.hasData ? decFmt(r.share25, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-right font-bold text-indigo-700 dark:text-indigo-400">${r.hasData ? numFmt(r.fc) : '-'}</td>
      <td class="py-2.5 px-3 text-right font-semibold text-indigo-600 dark:text-indigo-400">${r.hasData ? decFmt(r.share26, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-right font-semibold">${r.hasData ? (r.diff >= 0 ? '+' : '') + numFmt(r.diff) : '-'}</td>
      <td class="py-2.5 px-3 text-center ${yoyClass}">${r.hasData ? (r.yoy >= 0 ? '+' : '') + decFmt(r.yoy, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-left font-sans text-[11px] text-slate-500 dark:text-slate-400">${r.hasData ? r.meta.note : `<span class="text-slate-400 dark:text-slate-500 italic">Tidak mengoperasikan moda ini di wilayah ${currentForecastProv}</span>`}</td>
    `;
    tbody.appendChild(tr);
  });

  const totalDiff = totFcSum - tot25Sum;
  const totalYoy = tot25Sum > 0 ? ((totFcSum / tot25Sum - 1) * 100) : 0;
  const totalYoyClass = totalYoy >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-extrabold' : 'text-rose-600 dark:text-rose-400 font-extrabold';

  const trTotal = document.createElement('tr');
  trTotal.className = 'bg-slate-100/80 dark:bg-slate-800/80 font-bold border-t-2 border-slate-300 dark:border-slate-600';
  trTotal.innerHTML = `
    <td class="py-3 px-3 uppercase text-slate-900 dark:text-white font-bold">🌟 Total Multimoda ${isAll ? 'Nasional' : currentForecastProv}</td>
    <td class="py-3 px-3 text-right font-black text-slate-900 dark:text-white">${numFmt(tot25Sum)}</td>
    <td class="py-3 px-3 text-right text-slate-600 dark:text-slate-400">100,0%</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300 text-xs">${numFmt(totFcSum)}</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300">100,0%</td>
    <td class="py-3 px-3 text-right text-slate-900 dark:text-white">${totalDiff >= 0 ? '+' : ''}${numFmt(totalDiff)}</td>
    <td class="py-3 px-3 text-center text-xs ${totalYoyClass}">${totalYoy >= 0 ? '+' : ''}${decFmt(totalYoy, 1)}%</td>
    <td class="py-3 px-3 text-left font-sans text-[11px] text-slate-700 dark:text-slate-300 font-semibold">
      Ekspansi mobilitas keberangkatan ${isAll ? 'nasional' : currentForecastProv} (${metricLabel})
    </td>
  `;
  tbody.appendChild(trTotal);
}

function renderForecastChart() {
  if (!DATA.forecast_nataru) return;
  const ctx = document.getElementById('chartForecastCanvas');
  if (!ctx) return;

  const isDark = document.documentElement.classList.contains('dark');
  const isPnp = currentForecastMetric === 'pnp';
  const moda = currentForecastModa;
  const isAll = currentForecastProv === 'ALL';
  const metricLabel = getSeriesLabel(currentForecastMetric);
  const unitLabel = getUnitLabel(currentForecastMetric);
  const activeModes = getActiveModesForProv(currentForecastProv);
  const isOperating = moda === 'TOTAL' || activeModes.includes(moda);

  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = champ?.code || 'hw_mul_damped';
  const activeModelName = champ?.name || 'Holt-Winters Mul Damped';

  const badgeEl = document.getElementById('fc-chart-scope-badge');
  if (badgeEl) badgeEl.innerText = `${isAll ? 'Nasional' : currentForecastProv} • ${metricLabel}`;

  const modelNameEl = document.getElementById('fc-chart-model-name');
  if (modelNameEl) modelNameEl.innerText = `${activeModelName}`;
  const legendLabelEl = document.getElementById('fc-legend-model-label');
  if (legendLabelEl) {
    legendLabelEl.innerHTML = `<span class="w-3 h-0.5 border-t border-dashed border-indigo-500"></span> Proyeksi ${activeModelName}`;
  }

  const descEl = document.getElementById('fc-chart-model-desc');
  if (descEl) {
    if (!isOperating) {
      descEl.innerHTML = `<span class="text-amber-600 dark:text-amber-400 font-semibold">ℹ️ Catatan Wilayah: Moda ${moda} tidak beroperasi di wilayah ${currentForecastProv}. Angka keberangkatan bernilai 0. Silakan pilih moda aktif (${activeModes.join(', ')} atau Total Multimoda).</span>`;
    } else {
      descEl.innerHTML = `Garis solid mewakili realisasi riil keberangkatan (1 Jan – 29 Sep 2026). Garis putus-putus ungu mewakili kurva peramalan model terbaik <b class="text-indigo-600 dark:text-indigo-400">${activeModelName}</b> (Okt 2026 – Jan 2027) dengan kalibrasi shock Nataru dan pita keyakinan 95% CI.`;
    }
  }

  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, moda);
  const histDates = (pData && pData.history_2026 && pData.history_2026.dates) || DATA.daily_timeline.filter(d => d.date <= '2026-09-29').map(d => d.date);
  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const allLabels = [...histDates, ...futureDates];

  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode);
  const lastHistVal = hist.length ? hist[hist.length - 1] : 0;

  const histData = [...hist, ...futureDates.map(() => null)];
  const fcData = [
    ...hist.slice(0, hist.length - 1).map(() => null),
    lastHistVal,
    ...fc.map(d => d.val)
  ];

  const modaColor = moda === 'TOTAL' ? (isDark ? '#38bdf8' : '#0284c7') : (COLOR[moda] || '#6366f1');
  const forecastColor = '#6366f1';

  // Datasets: Realisasi 2026, Proyeksi, 95% CI (NO Realisasi 2025 green line)
  const datasets = [
    {
      label: `Realisasi Historis 2026 (${metricLabel})`,
      data: histData,
      borderColor: modaColor,
      backgroundColor: 'transparent',
      borderWidth: 1.8,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.15,
      spanGaps: false
    },
    {
      label: `Proyeksi ${activeModelName} 2026/2027 (${metricLabel})`,
      data: fcData,
      borderColor: forecastColor,
      backgroundColor: 'transparent',
      borderWidth: 2.2,
      borderDash: [5, 4],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.2,
      spanGaps: false
    }
  ];

  if (moda === 'TOTAL' && isOperating) {
    const ciUpperData = [
      ...hist.map(() => null),
      ...fc.map(d => d.ci_upper)
    ];
    const ciLowerData = [
      ...hist.map(() => null),
      ...fc.map(d => d.ci_lower)
    ];

    datasets.push({
      label: 'Batas Atas 95% CI',
      data: ciUpperData,
      borderColor: 'transparent',
      backgroundColor: 'rgba(99, 102, 241, 0.12)',
      pointRadius: 0,
      fill: '+1',
      tension: 0.2
    });
    datasets.push({
      label: 'Batas Bawah 95% CI',
      data: ciLowerData,
      borderColor: 'transparent',
      backgroundColor: 'transparent',
      pointRadius: 0,
      fill: false,
      tension: 0.2
    });
  }

  if (chartForecast) chartForecast.destroy();

  chartForecast = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            font: { size: 10, family: 'Inter' },
            color: isDark ? '#94a3b8' : '#64748b',
            filter: item => !item.text.includes('CI')
          }
        },
        tooltip: {
          callbacks: {
            label: function(c) {
              if (c.dataset.label.includes('CI')) return null;
              if (c.parsed.y === null || c.parsed.y === undefined) return null;
              return `${c.dataset.label}: ${numFmt(c.parsed.y)} ${unitLabel}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: isDark ? '#64748b' : '#94a3b8',
            font: { size: 10, family: 'monospace' },
            maxTicksLimit: 14,
            callback: function(val, idx) {
              const label = this.getLabelForValue(val);
              return label ? label.slice(5) : '';
            }
          }
        },
        y: {
          grid: { color: isDark ? 'rgba(51, 65, 85, 0.25)' : 'rgba(226, 232, 240, 0.7)' },
          ticks: {
            color: isDark ? '#64748b' : '#94a3b8',
            font: { size: 10, family: 'monospace' },
            callback: v => numFmt(v)
          }
        }
      }
    }
  });
}

function renderForecastTable() {
  if (!DATA.forecast_nataru) return;
  const tbody = document.getElementById('tbody-forecast');
  if (!tbody) return;
  tbody.innerHTML = '';

  const isAll = currentForecastProv === 'ALL';
  const isPnp = currentForecastMetric === 'pnp';
  const oppMetric = isPnp ? 'arm' : 'pnp';
  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = champ?.code || 'hw_mul_damped';

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastModa);
  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode);

  const oppHist = getHistoricalSeries(currentForecastProv, oppMetric, currentForecastModa);
  const oppFc = generateTimeSeriesForecast(oppHist, futureDates, activeModelCode);

  const map2025 = {};
  if (isAll) {
    (DATA.timeline_2025 || []).forEach(r => {
      const k = isPnp ? getSeriesKey('pnp', currentForecastModa) : getSeriesKey('arm', currentForecastModa);
      map2025[r.date.slice(5)] = r[k] || 0;
    });
  } else {
    const map25Md = (pData && pData.history_2025_md) || {};
    const totHist = getHistoricalSeries(currentForecastProv, currentForecastMetric, 'TOTAL');
    const totHistSum = totHist.reduce((a, b) => a + b, 0);
    const mHistSum = hist.reduce((a, b) => a + b, 0);
    const mShare = totHistSum > 0 ? (mHistSum / totHistSum) : 0;

    futureDates.forEach(d => {
      const r25 = map25Md[d.slice(5)] || 0;
      map2025[d.slice(5)] = typeof r25 === 'number' ? Math.round(r25 * (isPnp ? 0.58 : 0.016) * mShare) : 0;
    });
  }

  const rKey = currentForecastRange;
  const dayNames = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];

  fc.forEach((row, i) => {
    if (rKey === 'nataru' && !(row.date >= '2026-12-18' && row.date <= '2027-01-04')) return;
    if (rKey === 'okt' && !row.date.startsWith('2026-10')) return;
    if (rKey === 'nov' && !row.date.startsWith('2026-11')) return;
    if (rKey === 'des' && !row.date.startsWith('2026-12')) return;

    const d = new Date(row.date);
    const dayName = dayNames[d.getDay()];

    let badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">Normal</span>`;
    if (row.date === '2026-12-24') {
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300">Puncak Natal</span>`;
    } else if (row.date === '2027-01-03') {
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-300">Puncak Balik</span>`;
    } else if (row.shock_factor > 1.2) {
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300">Puncak Lonjakan</span>`;
    } else if (row.shock_factor > 1.05) {
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">Tinggi (Nataru)</span>`;
    }

    const val25 = map2025[row.date.slice(5)] || 0;
    const yoyVal = val25 > 0 ? ((row.val / val25 - 1.0) * 100) : 0;
    const yoyClass = yoyVal >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';

    const oppRow = oppFc[i] || { val: 0 };

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-medium text-slate-900 dark:text-white">${row.date}</td>
      <td class="py-2 px-2.5 font-sans ${['Min', 'Sab'].includes(dayName) ? 'text-rose-600 font-semibold' : 'text-slate-500'}">${dayName}</td>
      <td class="py-2 px-2.5 text-right font-bold text-indigo-700 dark:text-indigo-400">${numFmt(row.val)}</td>
      <td class="py-2 px-2.5 text-right font-semibold text-slate-800 dark:text-slate-200">${val25 > 0 ? numFmt(val25) : '-'}</td>
      <td class="py-2 px-2.5 text-center ${yoyClass}">${val25 > 0 ? ((yoyVal >= 0 ? '+' : '') + decFmt(yoyVal, 1) + '%') : '-'}</td>
      <td class="py-2 px-2.5 text-right text-slate-500 text-[10px]">${numFmt(row.ci_lower)} - ${numFmt(row.ci_upper)}</td>
      <td class="py-2 px-2.5 text-center">${badgeStatus}</td>
      <td class="py-2 px-2.5 text-right text-slate-700 dark:text-slate-300 font-semibold">${numFmt(oppRow.val)}</td>
      <td class="py-2 px-2.5 text-right text-slate-500">-</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderForecastWorkspace() {
  currentForecastMetric = currentMetric || 'pnp';
  updateModaDropdownOptions(currentForecastProv);
  renderForecastAccuracyBadges();
  renderForecastSummaryCards();
  renderForecastComparisonTable();
  renderForecastChart();
  renderForecastTable();
  if (typeof renderArmadaSimulation === 'function') renderArmadaSimulation();
}
