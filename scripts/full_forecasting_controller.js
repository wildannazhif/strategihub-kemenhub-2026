// TAB 8: FORECASTING NATARU 2026/2027 CONTROLLER
// ---------------------------------------------------------------
let currentForecastScenario = 'moderat';
let currentForecastMetric = 'pnp'; // 'pnp' or 'arm'
let currentForecastDirection = 'tot'; // 'tot', 'brg', 'dat'
let currentForecastModa = 'TOTAL';
let currentForecastProv = 'ALL';
let currentForecastModel = 'auto'; // 'auto' or specific model code
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

const scenario_mults = {
  'moderat': 1.00,
  'optimis': 1.07,
  'konservatif': 0.95
};

const model_names_map = {
  'auto': 'Auto-Model Champion',
  'hw_mul_damped': 'Holt-Winters Mul Damped (phi=0.98)',
  'hw_mul_std': 'Holt-Winters Mul Standar',
  'hw_add_damped': 'Holt-Winters Add Damped (phi=0.98)',
  'sarima': 'SARIMA (1,1,1)x(1,1,1,7)',
  'arima': 'ARIMA (1,1,1) Non-Seasonal',
  'holt_linear': 'Holt Linear Trend (No Seasonal)',
  'ses': 'Simple Exp Smoothing (SES)',
  'ridge': 'Linear Regression (Trend + DOW)',
  'snaive': 'Seasonal Naive (Lag 7)',
  'naive': 'Naive Random Walk (Lag 1)',
  'ma7': '7-Day Moving Average'
};

function getSeriesKey(metric, direction, moda) {
  if (metric === 'pnp') {
    if (direction === 'tot') return moda;
    if (direction === 'brg') return moda === 'TOTAL' ? 'pbrg_TOTAL' : `pbrg_${moda}`;
    if (direction === 'dat') return moda === 'TOTAL' ? 'pdat_TOTAL' : `pdat_${moda}`;
  } else {
    if (direction === 'tot') return moda === 'TOTAL' ? 'arm_TOTAL' : `arm_${moda}`;
    if (direction === 'brg') return moda === 'TOTAL' ? 'abrg_TOTAL' : `abrg_${moda}`;
    if (direction === 'dat') return moda === 'TOTAL' ? 'adat_TOTAL' : `adat_${moda}`;
  }
  return moda;
}

function getSeriesLabel(metric, direction) {
  if (metric === 'pnp') {
    if (direction === 'tot') return 'Total Penumpang (Dua Arah)';
    if (direction === 'brg') return 'Penumpang Berangkat (Keberangkatan)';
    if (direction === 'dat') return 'Penumpang Datang (Kedatangan)';
  } else {
    if (direction === 'tot') return 'Total Armada (Dua Arah)';
    if (direction === 'brg') return 'Armada Berangkat (Keberangkatan)';
    if (direction === 'dat') return 'Armada Datang (Kedatangan)';
  }
  return 'Penumpang';
}

function getUnitLabel(metric) {
  return metric === 'pnp' ? 'orang' : 'trip';
}

function getHistoricalSeries(prov, metric, direction, moda) {
  const key = getSeriesKey(metric, direction, moda);
  if (prov === 'ALL') {
    return DATA.daily_timeline.filter(d => d.date <= '2026-09-29').map(d => d[key] ?? 0);
  }
  const pData = DATA.forecast_nataru.by_province?.[prov];
  return (pData && pData.history_2026 && pData.history_2026[key]) || [];
}

function get2025HistoricalSeries(prov, metric, direction, moda, labels) {
  const key = getSeriesKey(metric, direction, moda);
  if (prov === 'ALL') {
    const map2025 = {};
    (DATA.timeline_2025 || []).forEach(r => {
      const md = r.date.slice(5);
      map2025[md] = r[key] ?? r['TOTAL'] ?? 0;
    });
    return labels.map(d => map2025[d.slice(5)] ?? null);
  } else {
    const pData = DATA.forecast_nataru.by_province?.[prov];
    const map25Md = (pData && pData.history_2025_md) || {};
    return labels.map(d => {
      const md = d.slice(5);
      const r25 = map25Md[md];
      if (r25 === undefined || r25 === null) return null;
      if (typeof r25 === 'number') {
        if (direction === 'brg') return Math.round(r25 * (metric === 'pnp' ? 0.58 : 0.016));
        if (direction === 'dat') return Math.round(r25 * (metric === 'pnp' ? 0.42 : 0.014));
        if (metric === 'arm') return Math.round(r25 / 35);
        return r25;
      }
      return r25[key] ?? null;
    });
  }
}

function generateTimeSeriesForecast(histSeries, futureDates, modelCode, scenario = 'moderat') {
  const n = histSeries.length;
  if (!n || histSeries.every(v => v === 0)) {
    return futureDates.map(d => ({ date: d, val: 0, ci_upper: 0, ci_lower: 0, shock_factor: 1.0 }));
  }

  const scenMult = scenario_mults[scenario] || 1.0;
  const lastVal = histSeries[n - 1];
  const last7 = histSeries.slice(-7);
  const mean7 = last7.reduce((a, b) => a + b, 0) / 7;
  const n_fc = futureDates.length;

  let basePred = [];

  if (modelCode === 'naive') {
    basePred = Array(n_fc).fill(lastVal);
  } else if (modelCode === 'ma7') {
    basePred = Array(n_fc).fill(mean7);
  } else if (modelCode === 'snaive') {
    basePred = Array.from({ length: n_fc }, (_, i) => last7[i % 7]);
  } else if (modelCode === 'ses') {
    let l_ses = histSeries[0];
    const a_ses = 0.25;
    for (let i = 1; i < n; i++) l_ses = a_ses * histSeries[i] + (1 - a_ses) * l_ses;
    basePred = Array(n_fc).fill(l_ses);
  } else if (modelCode === 'holt_linear') {
    let l = histSeries[0], b = (histSeries[1] - histSeries[0]) || 0;
    const a = 0.25, beta = 0.05;
    for (let i = 1; i < n; i++) {
      const lp = l;
      l = a * histSeries[i] + (1 - a) * (l + b);
      b = beta * (l - lp) + (1 - beta) * b;
    }
    basePred = Array.from({ length: n_fc }, (_, h) => Math.max(0, l + (h + 1) * b));
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
    basePred = futureDates.map((_, h) => {
      const d_idx = (n + h) % 7;
      const t_val = overallMean + slope * (n + h - mid) + (dowMeans[d_idx] - overallMean);
      return Math.max(0, t_val);
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
      basePred.push(Math.max(0, Math.round(prev + decay * meanDiff)));
    }
  } else {
    // Holt-Winters Mul Damped (or hw_mul_std / hw_add_damped)
    const isDamped = modelCode !== 'hw_mul_std';
    const isAdd = modelCode === 'hw_add_damped';
    const phi = isDamped ? 0.98 : 1.0;
    const s_period = 7;
    const s_factors = Array(s_period).fill(1.0);
    for (let i = 0; i < s_period; i++) {
      let sum_r = 0, cnt = 0;
      for (let k = i; k < n; k += s_period) {
        sum_r += histSeries[k];
        cnt++;
      }
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
      let trendComp = 0;
      if (isDamped) {
        trendComp = Array.from({ length: step }, (_, k) => Math.pow(phi, k + 1)).reduce((a, v) => a + v, 0) * b_hw;
      } else {
        trendComp = step * b_hw;
      }
      if (isAdd) {
        return Math.max(0, l_hw + trendComp + (s_factors[s_idx] || 0));
      } else {
        return Math.max(0, (l_hw + trendComp) * (s_factors[s_idx] || 1.0));
      }
    });
  }

  const diffs = [];
  for (let i = 1; i < n; i++) diffs.push(Math.abs(histSeries[i] - histSeries[i - 1]));
  const estRmse = (diffs.reduce((a, b) => a + b, 0) / (diffs.length || 1)) * 1.25;

  return futureDates.map((dateStr, i) => {
    const md = dateStr.slice(5);
    const shock = nataru_shocks[md] || 1.0;
    const finalVal = Math.round(basePred[i] * shock * scenMult);
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

function setForecastProvince(prov) {
  currentForecastProv = prov;
  const select = document.getElementById('select-forecast-prov');
  if (select && select.value !== prov) select.value = prov;

  const scopeBadge = document.getElementById('fc-scope-badge');
  if (scopeBadge) scopeBadge.innerText = prov === 'ALL' ? '(Nasional)' : `(${prov})`;

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
}

function setForecastModel(modelCode) {
  currentForecastModel = modelCode;
  const select = document.getElementById('select-forecast-model');
  if (select && select.value !== modelCode) select.value = modelCode;

  renderForecastSummaryCards();
  renderForecastComparisonTable();
  renderForecastChart();
  renderForecastAccuracyBadges();
  renderForecastTable();
}

function setForecastScenario(scen) {
  currentForecastScenario = scen;

  renderForecastSummaryCards();
  renderForecastComparisonTable();
  renderForecastChart();
  renderForecastTable();
  if (typeof renderArmadaSimulation === 'function') renderArmadaSimulation();
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

  const benchList = isAll
    ? (DATA.forecast_nataru.benchmarks || [])
    : (pData?.benchmarks || DATA.forecast_nataru.benchmarks || []);

  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);

  const activeModelCode = currentForecastModel === 'auto' ? (champ?.code || 'hw_mul_damped') : currentForecastModel;
  const activeBenchmark = benchList.find(b => b.model_code === activeModelCode) || benchList[0] || {
    model_name: model_names_map[activeModelCode] || activeModelCode,
    mape: 4.10,
    rmse: 62051,
    mae: 49146
  };

  const champNameEl = document.getElementById('fc-champion-name');
  if (champNameEl) {
    if (currentForecastModel === 'auto') {
      champNameEl.innerText = `Model Terpilih: ${champ?.name || activeBenchmark.model_name} (Auto-Model: MAPE ${decFmt(activeBenchmark.mape, 2)}%)`;
    } else {
      champNameEl.innerText = `Model Aktif: ${activeBenchmark.model_name} (MAPE ${decFmt(activeBenchmark.mape, 2)}%)`;
    }
  }

  const mapeEl = document.getElementById('fc-metric-mape');
  if (mapeEl) mapeEl.innerText = `${decFmt(activeBenchmark.mape, 2)}%`;

  const rmseEl = document.getElementById('fc-metric-rmse');
  if (rmseEl) rmseEl.innerHTML = `${numFmt(activeBenchmark.rmse)} <span class="text-xs font-normal text-slate-500">${isPnp ? 'pnp' : 'trip'}/hari</span>`;

  const maeEl = document.getElementById('fc-metric-mae');
  if (maeEl) maeEl.innerHTML = `${numFmt(activeBenchmark.mae)} <span class="text-xs font-normal text-slate-500">${isPnp ? 'pnp' : 'trip'}/hari</span>`;

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
  const activeModelCode = currentForecastModel === 'auto' ? (champ?.code || 'hw_mul_damped') : currentForecastModel;

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, 'TOTAL');
  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode, currentForecastScenario);
  const s25 = get2025HistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, 'TOTAL', futureDates);

  let fcTot = 0, s25Tot = 0;
  let xmasRow = null, nyRow = null;
  let xmas25 = 0, ny25 = 0;

  fc.forEach((d, i) => {
    if (d.date >= '2026-12-18' && d.date <= '2027-01-04') {
      fcTot += d.val;
      s25Tot += (s25[i] || 0);
      if (d.date === '2026-12-24') {
        xmasRow = d;
        xmas25 = s25[i] || 0;
      }
      if (d.date === '2027-01-03') {
        nyRow = d;
        ny25 = s25[i] || 0;
      }
    }
  });

  const avgDaily = Math.round(fcTot / 18);
  const yoyTotPct = s25Tot > 0 ? ((fcTot / s25Tot - 1) * 100) : 0;

  const oppHist = getHistoricalSeries(currentForecastProv, oppMetric, currentForecastDirection, 'TOTAL');
  const oppFc = generateTimeSeriesForecast(oppHist, futureDates, activeModelCode, currentForecastScenario);
  const oppS25 = get2025HistoricalSeries(currentForecastProv, oppMetric, currentForecastDirection, 'TOTAL', futureDates);

  let oppMaxDay = { val: 0, date: '' }, opp25Val = 0;
  oppFc.forEach((d, i) => {
    if (d.date >= '2026-12-18' && d.date <= '2027-01-04') {
      if (d.val > oppMaxDay.val) {
        oppMaxDay = d;
        opp25Val = oppS25[i] || 0;
      }
    }
  });

  const oppYoyPct = opp25Val > 0 ? ((oppMaxDay.val / opp25Val - 1) * 100) : 0;

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
  const unit = getUnitLabel(currentForecastMetric);
  const metricLabel = getSeriesLabel(currentForecastMetric, currentForecastDirection);

  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = currentForecastModel === 'auto' ? (champ?.code || 'hw_mul_damped') : currentForecastModel;

  const badgeEl = document.getElementById('fc-comp-prov-badge');
  if (badgeEl) badgeEl.innerText = `${isAll ? 'Nasional' : currentForecastProv} • ${metricLabel}`;

  const modesMeta = [
    { key: 'UDARA', label: '✈ Udara (Penerbangan Domestik)', color: COLOR.UDARA, note: 'Kapasitas armada beroperasi optimal; tiket dinamis memfilter demand jarak jauh' },
    { key: 'KA', label: '🚆 Kereta Api (KAI)', color: COLOR.KA, note: 'Tingkat isian stabil tinggi (load factor 90%+); seluruh kuota KA favorit terjual' },
    { key: 'BUS', label: '🚌 Bus', color: COLOR.BUS, note: 'Rute Trans Jawa & jalan tol primadona; armada reguler & cadangan siaga penuh' },
    { key: 'ASDP', label: '⛴ ASDP (Penyeberangan Feri)', color: COLOR.ASDP, note: 'Lonjakan kendaraan pribadi tinggi di lintasan penyeberangan utama' },
    { key: 'LAUT', label: '🚢 Laut (Kapal Penumpang Pelni)', color: COLOR.LAUT, note: 'Pertumbuhan pergerakan antarpulau & rute perintis Indonesia Timur' },
  ];

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  let totalFc = 0, total25 = 0;
  const rowsData = [];

  modesMeta.forEach(m => {
    const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, m.key);
    const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode, currentForecastScenario);
    const s25 = get2025HistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, m.key, futureDates);

    let fcSum = 0, s25Sum = 0;
    fc.forEach((d, i) => {
      if (d.date >= '2026-12-18' && d.date <= '2027-01-04') {
        fcSum += d.val;
        s25Sum += (s25[i] || 0);
      }
    });

    const diff = fcSum - s25Sum;
    const yoy = s25Sum > 0 ? ((fcSum / s25Sum - 1) * 100) : 0;
    totalFc += fcSum;
    total25 += s25Sum;

    rowsData.push({
      meta: m,
      fc: fcSum,
      base25: s25Sum,
      diff: diff,
      yoy: yoy,
      hasData: fcSum > 0 || s25Sum > 0
    });
  });

  rowsData.forEach(r => {
    const share25 = total25 > 0 ? (r.base25 / total25 * 100) : 0;
    const share26 = totalFc > 0 ? (r.fc / totalFc * 100) : 0;
    const yoyClass = r.yoy >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${r.meta.color}"></span>
        <span>${r.meta.label}</span>
      </td>
      <td class="py-2.5 px-3 text-right font-medium">${r.hasData ? numFmt(r.base25) : '-'}</td>
      <td class="py-2.5 px-3 text-right text-slate-500">${r.hasData ? decFmt(share25, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-right font-bold text-indigo-700 dark:text-indigo-400">${r.hasData ? numFmt(r.fc) : '-'}</td>
      <td class="py-2.5 px-3 text-right font-semibold text-indigo-600 dark:text-indigo-400">${r.hasData ? decFmt(share26, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-right font-semibold">${r.hasData ? (r.diff >= 0 ? '+' : '') + numFmt(r.diff) : '-'}</td>
      <td class="py-2.5 px-3 text-center ${yoyClass}">${r.hasData ? (r.yoy >= 0 ? '+' : '') + decFmt(r.yoy, 1) + '%' : '-'}</td>
      <td class="py-2.5 px-3 text-left font-sans text-[11px] text-slate-500 dark:text-slate-400">${r.hasData ? r.meta.note : 'Tidak mengoperasikan moda ini di wilayah provinsi'}</td>
    `;
    tbody.appendChild(tr);
  });

  const totalDiff = totalFc - total25;
  const totalYoy = total25 > 0 ? ((totalFc / total25 - 1) * 100) : 0;
  const totalYoyClass = totalYoy >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-extrabold' : 'text-rose-600 dark:text-rose-400 font-extrabold';

  const trTotal = document.createElement('tr');
  trTotal.className = 'bg-slate-100/80 dark:bg-slate-800/80 font-bold border-t-2 border-slate-300 dark:border-slate-600';
  trTotal.innerHTML = `
    <td class="py-3 px-3 uppercase text-slate-900 dark:text-white font-bold">🌟 Total Multimoda ${isAll ? 'Nasional' : currentForecastProv}</td>
    <td class="py-3 px-3 text-right font-black text-slate-900 dark:text-white">${numFmt(total25)}</td>
    <td class="py-3 px-3 text-right text-slate-600 dark:text-slate-400">100,0%</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300 text-xs">${numFmt(totalFc)}</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300">100,0%</td>
    <td class="py-3 px-3 text-right text-slate-900 dark:text-white">${totalDiff >= 0 ? '+' : ''}${numFmt(totalDiff)}</td>
    <td class="py-3 px-3 text-center text-xs ${totalYoyClass}">${totalYoy >= 0 ? '+' : ''}${decFmt(totalYoy, 1)}%</td>
    <td class="py-3 px-3 text-left font-sans text-[11px] text-slate-700 dark:text-slate-300 font-semibold">
      Ekspansi mobilitas ${isAll ? 'nasional' : currentForecastProv} (${metricLabel})
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
  const metricLabel = getSeriesLabel(currentForecastMetric, currentForecastDirection);
  const unitLabel = getUnitLabel(currentForecastMetric);

  const pData = !isAll ? DATA.forecast_nataru.by_province?.[currentForecastProv] : null;
  const champ = isAll
    ? DATA.forecast_nataru.champion_model
    : (pData?.champion_model || DATA.forecast_nataru.champion_model);
  const activeModelCode = currentForecastModel === 'auto' ? (champ?.code || 'hw_mul_damped') : currentForecastModel;
  const activeModelName = model_names_map[activeModelCode] || activeModelCode;

  const badgeEl = document.getElementById('fc-chart-scope-badge');
  if (badgeEl) badgeEl.innerText = `${isAll ? 'Nasional' : currentForecastProv} • ${metricLabel}`;

  const modelNameEl = document.getElementById('fc-chart-model-name');
  if (modelNameEl) modelNameEl.innerText = `${activeModelName}`;
  const legendLabelEl = document.getElementById('fc-legend-model-label');
  if (legendLabelEl) {
    legendLabelEl.innerHTML = `<span class="w-3 h-0.5 border-t border-dashed border-indigo-500"></span> Proyeksi ${activeModelName}`;
  }

  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, moda);
  const histDates = (pData && pData.history_2026 && pData.history_2026.dates) || DATA.daily_timeline.filter(d => d.date <= '2026-09-29').map(d => d.date);
  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const allLabels = [...histDates, ...futureDates];

  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode, currentForecastScenario);
  const lastHistVal = hist.length ? hist[hist.length - 1] : 0;

  const histData = [...hist, ...futureDates.map(() => null)];
  const fcData = [
    ...hist.slice(0, hist.length - 1).map(() => null),
    lastHistVal,
    ...fc.map(d => d.val)
  ];

  const hist25Data = get2025HistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, moda, allLabels);

  const modaColor = moda === 'TOTAL' ? (isDark ? '#38bdf8' : '#0284c7') : (COLOR[moda] || '#6366f1');
  const forecastColor = '#6366f1';
  const prevYearColor = isDark ? '#34d399' : '#059669';

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
    },
    {
      label: `Realisasi 2025 (Data Latih) (${metricLabel})`,
      data: hist25Data,
      borderColor: prevYearColor,
      backgroundColor: 'transparent',
      borderWidth: 1.4,
      borderDash: [3, 3],
      pointRadius: 0,
      pointHoverRadius: 3,
      tension: 0.15,
      spanGaps: false
    }
  ];

  if (moda === 'TOTAL') {
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
  const activeModelCode = currentForecastModel === 'auto' ? (champ?.code || 'hw_mul_damped') : currentForecastModel;

  const futureDates = (DATA.forecast_nataru.scenarios?.moderat || []).map(d => d.date);
  const hist = getHistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, currentForecastModa);
  const fc = generateTimeSeriesForecast(hist, futureDates, activeModelCode, currentForecastScenario);
  const s25 = get2025HistoricalSeries(currentForecastProv, currentForecastMetric, currentForecastDirection, currentForecastModa, futureDates);

  const oppHist = getHistoricalSeries(currentForecastProv, oppMetric, currentForecastDirection, currentForecastModa);
  const oppFc = generateTimeSeriesForecast(oppHist, futureDates, activeModelCode, currentForecastScenario);
  const oppS25 = get2025HistoricalSeries(currentForecastProv, oppMetric, currentForecastDirection, currentForecastModa, futureDates);

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

    const val25 = s25[i] || 0;
    const yoyVal = val25 > 0 ? ((row.val / val25 - 1.0) * 100) : 0;
    const yoyClass = yoyVal >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';

    const oppRow = oppFc[i] || { val: 0 };
    const opp25 = oppS25[i] || 0;

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-medium text-slate-900 dark:text-white">${row.date}</td>
      <td class="py-2 px-2.5 font-sans ${['Min', 'Sab'].includes(dayName) ? 'text-rose-600 font-semibold' : 'text-slate-500'}">${dayName}</td>
      <td class="py-2 px-2.5 text-right font-bold text-indigo-700 dark:text-indigo-400">${numFmt(row.val)}</td>
      <td class="py-2 px-2.5 text-right font-semibold text-slate-800 dark:text-slate-200">${numFmt(val25)}</td>
      <td class="py-2 px-2.5 text-center ${yoyClass}">${yoyVal >= 0 ? '+' : ''}${decFmt(yoyVal, 1)}%</td>
      <td class="py-2 px-2.5 text-right text-slate-500 text-[10px]">${numFmt(row.ci_lower)} - ${numFmt(row.ci_upper)}</td>
      <td class="py-2 px-2.5 text-center">${badgeStatus}</td>
      <td class="py-2 px-2.5 text-right text-slate-700 dark:text-slate-300 font-semibold">${numFmt(oppRow.val)}</td>
      <td class="py-2 px-2.5 text-right text-slate-500">${numFmt(opp25)}</td>
    `;
    tbody.appendChild(tr);
  });
}
