import os
import json
import pandas as pd

data_dir = r"c:\Users\USER\Documents\PUSDATIN\data_clean"
output_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Siasati_Multimoda_2026.html"

# Load clean data
with open(os.path.join(data_dir, "descriptive_summary.json"), "r", encoding="utf-8") as f:
    summary_data = json.load(f)

with open(os.path.join(data_dir, "prasarana_map_nodes.json"), "r", encoding="utf-8") as f:
    map_nodes = json.load(f)

df_stats = pd.read_csv(os.path.join(data_dir, "descriptive_statistics_table.csv"))
df_daily = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_daily.csv"))
df_monthly = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_monthly.csv"))
df_dow = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_dow.csv"))
df_top = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_top_prasarana.csv"))
df_prov = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_provinsi.csv"))

# Prepare data payload for JS
stats_json = df_stats.to_dict(orient="records")
daily_json = df_daily.to_dict(orient="records")
monthly_json = df_monthly.to_dict(orient="records")
dow_json = df_dow.to_dict(orient="records")
top_json = df_top.head(250).to_dict(orient="records")
prov_top = df_prov.groupby("provinsi")["total_penumpang"].sum().reset_index().sort_values(by="total_penumpang", ascending=False).head(15).to_dict(orient="records")

# Find top peak days
daily_national = df_daily.groupby("tanggal")["total_penumpang"].sum().reset_index().sort_values(by="total_penumpang", ascending=False).head(10)
daily_national["tanggal"] = daily_national["tanggal"].astype(str)
peak_days_json = daily_national.to_dict(orient="records")

html_base = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Multimoda Transportasi Nasional 2026 — Siasati Kemenhub</title>
<!-- Leaflet CSS & JS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #070d19;
  --bg2: #0d172a;
  --card: #13223f;
  --card2: #182b50;
  --line: #233862;
  --txt: #f1f5f9;
  --mut: #94a3b8;
  --mut2: #64748b;
  --acc: #38bdf8;
  --udara: #0284c7;
  --asdp: #10b981;
  --bus: #f59e0b;
  --laut: #0f766e;
  --ka: #8b5cf6;
  --ok: #22c55e;
  --warn: #eab308;
  --bad: #ef4444;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: radial-gradient(1400px 700px at 80% -10%, #152e59 0%, var(--bg) 60%);
  color: var(--txt);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
}
.wrap { max-width: 1560px; margin: 0 auto; padding: 18px 24px 60px; }

header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  padding: 12px 0 20px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}
.logo {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; box-shadow: 0 4px 16px rgba(14,165,233,.4);
}
.title-box h1 { font-size: 22px; font-weight: 800; letter-spacing: -0.2px; }
.title-box .sub { color: var(--mut); font-size: 13px; margin-top: 3px; }
.badges { margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }
.bdg {
  background: rgba(56,189,248,.12); border: 1px solid rgba(56,189,248,.35);
  color: var(--acc); border-radius: 999px; padding: 5px 14px; font-size: 12px; font-weight: 600;
}
.bdg.ok { background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.35); color: var(--ok); }

/* Navigation Tabs */
nav {
  display: flex; gap: 8px; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 6px; margin-bottom: 20px;
  position: sticky; top: 10px; z-index: 500;
  box-shadow: 0 10px 30px rgba(2,8,23,.6);
}
nav button {
  border: 0; background: transparent; color: var(--mut);
  font: 600 13.5px/1 'Segoe UI', sans-serif;
  padding: 11px 18px; border-radius: 10px; cursor: pointer;
  transition: all .2s; display: flex; align-items: center; gap: 7px;
}
nav button:hover { color: var(--txt); background: rgba(56,189,248,.1); }
nav button.on {
  background: linear-gradient(135deg, rgba(14,165,233,.3), rgba(99,102,241,.3));
  color: #fff; box-shadow: inset 0 0 0 1px rgba(56,189,248,.5);
}

/* Sections */
section.tab { display: none; }
section.tab.on { display: block; animation: fadeIn .25s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

/* KPI Cards Grid */
.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin-bottom: 20px;
}
.kpi {
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 16px; padding: 18px 20px;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,.25);
}
.kpi::after {
  content: ""; position: absolute; inset: 0 0 auto 0; height: 3px;
  background: linear-gradient(90deg, var(--acc), #818cf8);
}
.kpi.udara::after { background: var(--udara); }
.kpi.asdp::after { background: var(--asdp); }
.kpi.bus::after { background: var(--bus); }
.kpi.laut::after { background: var(--laut); }
.kpi.ka::after { background: var(--ka); }

.kpi .lbl { font-size: 12px; color: var(--mut); font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
.kpi .val { font-size: 26px; font-weight: 800; margin-top: 6px; letter-spacing: -.5px; }
.kpi .ftr { font-size: 12px; color: var(--mut2); margin-top: 5px; }

/* Cards & Layout */
.grid { display: grid; gap: 16px; }
.two { grid-template-columns: 1fr 1fr; }
.three { grid-template-columns: 1fr 1fr 1fr; }
@media(max-width: 1080px) { .two, .three { grid-template-columns: 1fr; } }

.card {
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 16px; padding: 20px;
  box-shadow: 0 6px 24px rgba(0,0,0,.25);
}
.card h3 { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.card .subh { font-size: 12.5px; color: var(--mut); margin-top: 3px; font-weight: 400; }
.chart-box { position: relative; margin-top: 14px; min-height: 280px; }

/* Table */
table.tbl { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 12px; }
table.tbl th {
  color: var(--mut); text-align: right; font-weight: 600; padding: 10px 12px;
  border-bottom: 1px solid var(--line); background: rgba(13,23,42,.6);
}
table.tbl th:first-child, table.tbl td:first-child { text-align: left; }
table.tbl td {
  padding: 9px 12px; border-bottom: 1px solid rgba(35,56,98,.4);
  text-align: right;
}
table.tbl tr:hover td { background: rgba(56,189,248,.06); }
.scroll { max-height: 480px; overflow: auto; border-radius: 10px; margin-top: 8px; }
.scroll::-webkit-scrollbar { width: 8px; height: 8px; }
.scroll::-webkit-scrollbar-thumb { background: var(--line); border-radius: 8px; }

/* Map */
#map { height: 600px; border-radius: 14px; z-index: 1; border: 1px solid var(--line); }
.map-controls { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; align-items: center; }
.btn-filter {
  background: var(--bg2); border: 1px solid var(--line); color: var(--mut);
  padding: 7px 14px; border-radius: 8px; font: 600 12.5px 'Segoe UI'; cursor: pointer; transition: .2s;
}
.btn-filter:hover { color: var(--txt); border-color: var(--acc); }
.btn-filter.active { background: var(--acc); color: #000; font-weight: 700; border-color: var(--acc); }

/* Pill badges */
.tag { display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
.tag.udara { background: rgba(2,132,199,.2); color: #38bdf8; border: 1px solid rgba(2,132,199,.4); }
.tag.asdp { background: rgba(16,185,129,.2); color: #34d399; border: 1px solid rgba(16,185,129,.4); }
.tag.bus { background: rgba(245,158,11,.2); color: #fbbf24; border: 1px solid rgba(245,158,11,.4); }
.tag.laut { background: rgba(15,118,110,.2); color: #2dd4bf; border: 1px solid rgba(15,118,110,.4); }
.tag.ka { background: rgba(139,92,246,.2); color: #c084fc; border: 1px solid rgba(139,92,246,.4); }

/* Search box */
.search-inp {
  background: var(--bg2); border: 1px solid var(--line); color: var(--txt);
  padding: 8px 14px; border-radius: 8px; font-size: 13px; outline: none; width: 260px;
}
.search-inp:focus { border-color: var(--acc); }

/* Insight Box */
.alert-box {
  background: rgba(56,189,248,.08); border-left: 4px solid var(--acc);
  padding: 12px 16px; border-radius: 0 10px 10px 0; margin-top: 14px; font-size: 13px; line-height: 1.6;
}
.alert-box.warn {
  background: rgba(245,158,11,.08); border-left-color: var(--warn);
}
</style>
</head>
<body>

<div class="wrap">
  <!-- Header -->
  <header>
    <div class="logo">🚆</div>
    <div class="title-box">
      <h1>Dashboard Analitik Multimoda Transportasi Nasional 2026</h1>
      <div class="sub">Integrasi Data Operasional 5 Moda: Bus, ASDP, Udara, Laut, dan Kereta Api — SIASATI Kemenhub</div>
    </div>
    <div class="badges">
      <div class="bdg ok">● Data Operasional: Jan – 25 Sep 2026</div>
      <div class="bdg">298.284 Data Records</div>
      <div class="bdg">1.300 Simpul Prasarana</div>
    </div>
  </header>

  <!-- Navigation -->
  <nav>
    <button class="on" onclick="openTab('tab1', this)">📊 Ringkasan Eksekutif</button>
    <button onclick="openTab('tab2', this)">📈 Tren & Dinamika Waktu</button>
    <button onclick="openTab('tab3', this)">🏢 Peringkat Simpul Prasarana</button>
    <button onclick="openTab('tab4', this)">🗺️ Peta Spasial Multimoda</button>
    <button onclick="openTab('tab5', this)">🔍 Profil & Kualitas Data</button>
  </nav>

  <!-- Top KPIs -->
  <div class="kpis">
    <div class="kpi">
      <div class="lbl">Total Penumpang Nasional</div>
      <div class="val" style="color:var(--acc);">370,4 Juta</div>
      <div class="ftr">Akumulasi 5 moda (268 hari)</div>
    </div>
    <div class="kpi">
      <div class="lbl">Total Pergerakan Armada</div>
      <div class="val" style="color:var(--ok);">3,21 Juta</div>
      <div class="ftr">Trip bus, kapal, pesawat, KA</div>
    </div>
    <div class="kpi">
      <div class="lbl">Rata-rata Penumpang Harian</div>
      <div class="val">1,38 Juta</div>
      <div class="ftr">Orang / hari secara nasional</div>
    </div>
    <div class="kpi udara">
      <div class="lbl">Moda Pangsa Pasar Terbesar</div>
      <div class="val" style="color:#38bdf8;">Udara (31,7%)</div>
      <div class="ftr">117,2 Juta penumpang</div>
    </div>
    <div class="kpi asdp">
      <div class="lbl">Moda Terpadat ke-2</div>
      <div class="val" style="color:#34d399;">ASDP (23,5%)</div>
      <div class="ftr">87,1 Juta penumpang ferry</div>
    </div>
  </div>

  <!-- TAB 1: RINGKASAN EKSEKUTIF -->
  <section id="tab1" class="tab on">
    <div class="grid two">
      <div class="card">
        <h3><span>🥧</span> Pangsa Pasar Volume Penumpang (Modal Split)</h3>
        <div class="subh">Komposisi pembagian penumpang antar 5 moda transportasi nasional (Jan–Sep 2026)</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartModalSplit"></canvas>
        </div>
      </div>
      <div class="card">
        <h3><span>📊</span> Perbandingan Volume per Moda Transportasi</h3>
        <div class="subh">Total akumulasi penumpang (juta orang) dan pergerakan armada (ribu trip)</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartBarSplit"></canvas>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h3><span>📅</span> Tren Pertumbuhan Volume Bulanan Antarmoda (Januari – September 2026)</h3>
      <div class="subh">Pergerakan total penumpang setiap bulan memperlihatkan lonjakan signifikan pada periode Lebaran (April) dan Libur Sekolah (Juni-Juli)</div>
      <div class="chart-box" style="height:340px;">
        <canvas id="chartMonthlyMulti"></canvas>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h3><span>📋</span> Tabel Rekapitulasi Multimoda Nasional 2026</h3>
      <div class="subh">Ringkasan statistik agregat kinerja operasional masing-masing moda</div>
      <div class="scroll">
        <table class="tbl">
          <thead>
            <tr>
              <th>Moda Transportasi</th>
              <th>Total Penumpang</th>
              <th>Pangsa (%)</th>
              <th>Penumpang Datang</th>
              <th>Penumpang Berangkat</th>
              <th>Total Armada</th>
              <th>Load Proxy (Org/Armada)</th>
              <th>Observasi</th>
            </tr>
          </thead>
          <tbody id="tblSummaryBody"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TAB 2: TREN TEMPORAL & MUSIMAN -->
  <section id="tab2" class="tab">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
          <h3><span>📈</span> Dinamika Deret Waktu Harian Antarmoda (Daily Time Series)</h3>
          <div class="subh">Visualisasi tren harian volume penumpang dari 1 Januari hingga 25 September 2026</div>
        </div>
        <div class="map-controls" style="margin:0;">
          <button class="btn-filter active" onclick="toggleDailySeries('ALL', this)">Semua Moda</button>
          <button class="btn-filter" onclick="toggleDailySeries('UDARA', this)">Udara</button>
          <button class="btn-filter" onclick="toggleDailySeries('ASDP', this)">ASDP</button>
          <button class="btn-filter" onclick="toggleDailySeries('BUS', this)">Bus</button>
          <button class="btn-filter" onclick="toggleDailySeries('LAUT', this)">Laut</button>
          <button class="btn-filter" onclick="toggleDailySeries('KA', this)">KA</button>
        </div>
      </div>
      <div class="chart-box" style="height:380px;">
        <canvas id="chartDailyTrend"></canvas>
      </div>
      <div class="alert-box">
        💡 <b>Analisis Puncak (Peak Days):</b> Lonjakan tertinggi terjadi pada tanggal <b>21–23 April 2026</b> (H+2 s/d H+4 Idul Fitri 1447H) dengan total pergerakan melebihi <b>2,1 Juta penumpang/hari</b>. Puncak kedua terjadi pada pekan ke-27 (awal Juli 2026) saat masa puncak liburan sekolah.
      </div>
    </div>

    <div class="grid two" style="margin-top:16px;">
      <div class="card">
        <h3><span>🗓️</span> Distribusi Volume Berdasarkan Hari dalam Seminggu</h3>
        <div class="subh">Analisis pengaruh pola Weekday vs Weekend pada preferensi moda transportasi</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartDow"></canvas>
        </div>
      </div>
      <div class="card">
        <h3><span>🏆</span> 10 Hari Operasional Tersibuk Nasional 2026</h3>
        <div class="subh">Hari-hari dengan beban lalu lintas penumpang tertinggi di seluruh Indonesia</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>Peringkat</th>
                <th>Tanggal</th>
                <th>Hari</th>
                <th>Total Penumpang</th>
                <th>Keterangan Momentum</th>
              </tr>
            </thead>
            <tbody id="tblPeakDays"></tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 3: SIMPUL PRASARANA -->
  <section id="tab3" class="tab">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
          <h3><span>🏢</span> Peringkat Simpul Prasarana Transportasi Terpadat 2026</h3>
          <div class="subh">Peringkat bandara, stasiun, terminal bus, pelabuhan ASDP, dan pelabuhan laut tersibuk</div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <input type="text" id="prasaranaSearch" class="search-inp" placeholder="Cari simpul atau provinsi..." onkeyup="filterPrasaranaTable()">
          <div class="map-controls" style="margin:0;">
            <button class="btn-filter active" onclick="filterPrasaranaByMode('ALL', this)">Semua</button>
            <button class="btn-filter" onclick="filterPrasaranaByMode('UDARA', this)">Udara</button>
            <button class="btn-filter" onclick="filterPrasaranaByMode('ASDP', this)">ASDP</button>
            <button class="btn-filter" onclick="filterPrasaranaByMode('BUS', this)">Bus</button>
            <button class="btn-filter" onclick="filterPrasaranaByMode('LAUT', this)">Laut</button>
            <button class="btn-filter" onclick="filterPrasaranaByMode('KA', this)">KA</button>
          </div>
        </div>
      </div>

      <div class="scroll" style="max-height:560px; margin-top:14px;">
        <table class="tbl">
          <thead>
            <tr>
              <th>Peringkat</th>
              <th>Nama Simpul / Prasarana</th>
              <th>Moda</th>
              <th>Provinsi</th>
              <th>Total Penumpang</th>
              <th>Penumpang Datang</th>
              <th>Penumpang Berangkat</th>
              <th>Total Armada</th>
              <th>Rata-rata/Hari</th>
            </tr>
          </thead>
          <tbody id="tblPrasaranaBody"></tbody>
        </table>
      </div>
    </div>

    <div class="grid two" style="margin-top:16px;">
      <div class="card">
        <h3><span>🗺️</span> 15 Provinsi dengan Pergerakan Penumpang Tertinggi</h3>
        <div class="subh">Konsentrasi arus penumpang lintas moda per provinsi</div>
        <div class="chart-box" style="height:360px;">
          <canvas id="chartTopProv"></canvas>
        </div>
      </div>
      <div class="card">
        <h3><span>⚖️</span> Rasio Muatan Proxy per Gerakan Armada (Org / Armada)</h3>
        <div class="subh">Efisiensi pengangkutan rata-rata per moda (penumpang per armada beroperasi)</div>
        <div class="chart-box" style="height:360px;">
          <canvas id="chartRatioLoad"></canvas>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 4: PETA SPASIAL LEAFLET -->
  <section id="tab4" class="tab">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
        <div>
          <h3><span>🗺️</span> Peta Sebaran Simpul Prasarana Multimoda Indonesia</h3>
          <div class="subh">Sebaran 1.300 simpul transportasi (Bandara, Stasiun, Pelabuhan, Terminal) beserta intensitas volume</div>
        </div>
        <div class="map-controls" style="margin:0;">
          <button class="btn-filter active" onclick="filterMapMode('ALL', this)">Semua Simpul</button>
          <button class="btn-filter" onclick="filterMapMode('UDARA', this)">✈️ Udara</button>
          <button class="btn-filter" onclick="filterMapMode('ASDP', this)">⛴️ ASDP</button>
          <button class="btn-filter" onclick="filterMapMode('BUS', this)">🚌 Bus</button>
          <button class="btn-filter" onclick="filterMapMode('LAUT', this)">⚓ Laut</button>
          <button class="btn-filter" onclick="filterMapMode('KA', this)">🚆 KA</button>
        </div>
      </div>

      <div id="map"></div>

      <div style="display:flex; gap:16px; flex-wrap:wrap; margin-top:14px; font-size:12.5px; color:var(--mut);">
        <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#0284c7;margin-right:6px;"></span><b>Udara:</b> Bandara Internasional & Domestik</div>
        <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#10b981;margin-right:6px;"></span><b>ASDP:</b> Pelabuhan Penyeberangan Ferry</div>
        <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#f59e0b;margin-right:6px;"></span><b>Bus:</b> Terminal Bus Tipe A/B/C</div>
        <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#0f766e;margin-right:6px;"></span><b>Laut:</b> Pelabuhan Samudera & Nusantara</div>
        <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#8b5cf6;margin-right:6px;"></span><b>KA:</b> Stasiun Kereta Api</div>
      </div>
    </div>
  </section>

  <!-- TAB 5: AUDIT KUALITAS DATA & DESKRIPTIF DETAIL -->
  <section id="tab5" class="tab">
    <div class="card">
      <h3><span>🔍</span> Tabel Parameter Statistik Deskriptif Multimoda Siasati 2026</h3>
      <div class="subh">Parameter ukuran pemusatan (Mean, Median), dispersi (Std Dev, IQR), dan bentuk distribusi (Skewness)</div>
      <div class="scroll" style="margin-top:12px;">
        <table class="tbl">
          <thead>
            <tr>
              <th>Moda</th>
              <th>Observasi</th>
              <th>Total Penumpang</th>
              <th>Mean (Hari/Simpul)</th>
              <th>Median</th>
              <th>Std Dev</th>
              <th>IQR</th>
              <th>Min</th>
              <th>Max</th>
              <th>Skewness</th>
            </tr>
          </thead>
          <tbody id="tblStatsBody"></tbody>
        </table>
      </div>
    </div>

    <div class="grid two" style="margin-top:16px;">
      <div class="card">
        <h3><span>⚠️</span> Audit Kualitas Data & Temuan Teknis Siasati</h3>
        <div class="subh">Dokumentasi anomali dan karakteristik bawaan dataset API Siasati 2026</div>
        
        <div class="alert-box warn" style="margin-top:14px;">
          <b>1. Anomali Kolom Penumpang Berangkat Kereta Api (KA):</b><br>
          Pada dataset dm_ka_2026, kolom penumpang_berangkat memiliki nilai rata-rata 6.23 dan maksimum 139 yang <b>identik 100%</b> dengan kolom kereta_berangkat (jumlah trip kereta). Hal ini menunjukkan adanya kesalahan pemetaan field (data entry mapping error) pada sistem hulu Siasati KA. Oleh sebab itu, indikator pergerakan KA menggunakan penumpang_datang sebagai proksi utama.
        </div>

        <div class="alert-box" style="margin-top:12px;">
          <b>2. Sifat Simetri Data Penyeberangan (ASDP):</b><br>
          Data pelabuhan ASDP mencatat arus datang dan berangkat secara simetris (1:1), karena pelaporan ASDP berbasis lintasan trip pulang-pergi (round-trip per lintasan dermaga).
        </div>

        <div class="alert-box" style="margin-top:12px;">
          <b>3. Kelengkapan Koordinat Prasarana Spasial:</b><br>
          Sebanyak 98,4% simpul prasarana memiliki koordinat lintang/bujur valid. Melalui algoritma pembersihan data master, 1.300 simpul unik berhasil dipetakan secara akurat ke seluruh nusantara.
        </div>
      </div>

      <div class="card">
        <h3><span>💡</span> Rekomendasi Pengelolaan Data untuk Pusdatin Kemenhub</h3>
        <div class="subh">Usulan teknis tata kelola data guna mendukung monitoring berkelanjutan</div>
        <ul style="margin:14px 0 0 20px; font-size:13.5px; line-height:1.7; color:var(--txt);">
          <li><b>Validasi Skema Otomatis (Schema Enforcement):</b> Terapkan validasi rentang nilai pada endpoint Siasati agar field penumpang KA tidak terisi jumlah armada.</li>
          <li><b>Standardisasi Naming Convention:</b> Seragamkan penamaan kolom antar sub-sektor (misal: nama_prasarana dan provinsi agar konsisten antara Ditjen KA, Hubdat, Hubla, dan Hubud).</li>
          <li><b>Pencatatan Jam Puncak (Hourly Breakdown):</b> Mengembangkan pelaporan berbasis jam operasional pada periode Angkutan Lebaran dan Nataru untuk mengidentifikasi lonjakan mikro.</li>
          <li><b>Geocoding Master Registry:</b> Menyimpan tabel referensi master simpul nasional terpadu dengan koordinat GPS baku, kelas fasilitas, dan operator pengelola.</li>
        </ul>
      </div>
    </div>
  </section>

</div>

<script>
// PAYLOAD DATA DARI PYTHON
const summaryData = __SUMMARY_DATA__;
const statsData = __STATS_DATA__;
const dailyData = __DAILY_DATA__;
const monthlyData = __MONTHLY_DATA__;
const dowData = __DOW_DATA__;
const topPrasarana = __TOP_PRASARANA__;
const provData = __PROV_DATA__;
const peakDays = __PEAK_DAYS__;
const mapNodes = __MAP_NODES__;

// Color Map
const colors = {
  'UDARA': '#0284c7',
  'ASDP': '#10b981',
  'BUS': '#f59e0b',
  'LAUT': '#0f766e',
  'KA': '#8b5cf6'
};

// Tab Navigation
function openTab(tabId, btn) {
  document.querySelectorAll('section.tab').forEach(s => s.classList.remove('on'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('on'));
  document.getElementById(tabId).classList.add('on');
  btn.classList.add('on');
  if (tabId === 'tab4') {
    setTimeout(() => { if (window.myMap) window.myMap.invalidateSize(); }, 200);
  }
}

// Populate Summary Table
function renderSummaryTable() {
  const tbody = document.getElementById('tblSummaryBody');
  let html = '';
  const totalP = summaryData.total_penumpang;
  statsData.forEach(d => {
    const pct = ((d.Total_Penumpang / totalP) * 100).toFixed(1);
    const tagClass = d.Moda.toLowerCase();
    html += `<tr>
      <td><span class="tag ${tagClass}">${d.Moda}</span></td>
      <td><b>${d.Total_Penumpang.toLocaleString('id-ID')}</b></td>
      <td><b>${pct}%</b></td>
      <td>${d.Total_Penumpang_Datang.toLocaleString('id-ID')}</td>
      <td>${d.Total_Penumpang_Berangkat.toLocaleString('id-ID')}</td>
      <td>${d.Total_Armada.toLocaleString('id-ID')}</td>
      <td>${d.Rasio_Penumpang_per_Armada} org</td>
      <td>${d.Jumlah_Observasi.toLocaleString('id-ID')}</td>
    </tr>`;
  });
  tbody.innerHTML = html;
}

// Populate Peak Days Table
function renderPeakDaysTable() {
  const tbody = document.getElementById('tblPeakDays');
  let html = '';
  const hariNames = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
  peakDays.forEach((d, idx) => {
    const dateObj = new Date(d.tanggal);
    const dayName = hariNames[dateObj.getDay()];
    let note = "Reguler";
    if (d.tanggal.startsWith("2026-04")) note = "Puncak Arus Balik / Mudik Lebaran";
    else if (d.tanggal.startsWith("2026-07")) note = "Puncak Liburan Sekolah";
    html += `<tr>
      <td><b>#${idx + 1}</b></td>
      <td><b>${d.tanggal}</b></td>
      <td>${dayName}</td>
      <td style="color:var(--acc); font-weight:bold;">${d.total_penumpang.toLocaleString('id-ID')}</td>
      <td>${note}</td>
    </tr>`;
  });
  tbody.innerHTML = html;
}

// Populate Stats Table
function renderStatsTable() {
  const tbody = document.getElementById('tblStatsBody');
  let html = '';
  statsData.forEach(d => {
    const tagClass = d.Moda.toLowerCase();
    html += `<tr>
      <td><span class="tag ${tagClass}">${d.Moda}</span></td>
      <td>${d.Jumlah_Observasi.toLocaleString('id-ID')}</td>
      <td><b>${d.Total_Penumpang.toLocaleString('id-ID')}</b></td>
      <td>${d.Rata_Penumpang_per_Simpul_Hari.toLocaleString('id-ID')}</td>
      <td>${d.Median_Penumpang.toLocaleString('id-ID')}</td>
      <td>${d.Std_Penumpang.toLocaleString('id-ID')}</td>
      <td>${d.IQR_Penumpang.toLocaleString('id-ID')}</td>
      <td>${d.Min_Penumpang}</td>
      <td>${d.Max_Penumpang.toLocaleString('id-ID')}</td>
      <td>${d.Skewness_Penumpang}</td>
    </tr>`;
  });
  tbody.innerHTML = html;
}

// Render Prasarana Table
let currentPrasaranaMode = 'ALL';
function renderPrasaranaTable() {
  const query = (document.getElementById('prasaranaSearch').value || '').toLowerCase();
  const tbody = document.getElementById('tblPrasaranaBody');
  let filtered = topPrasarana.filter(d => {
    if (currentPrasaranaMode !== 'ALL' && d.moda !== currentPrasaranaMode) return false;
    if (query) {
      const matchName = (d.nama_prasarana || '').toLowerCase().includes(query);
      const matchProv = (d.provinsi || '').toLowerCase().includes(query);
      return matchName || matchProv;
    }
    return true;
  });

  let html = '';
  filtered.slice(0, 60).forEach((d, idx) => {
    const tagClass = d.moda.toLowerCase();
    html += `<tr>
      <td><b>#${idx + 1}</b></td>
      <td><b>${d.nama_prasarana}</b></td>
      <td><span class="tag ${tagClass}">${d.moda}</span></td>
      <td>${d.provinsi}</td>
      <td style="color:var(--acc); font-weight:bold;">${d.total_penumpang.toLocaleString('id-ID')}</td>
      <td>${d.penumpang_datang.toLocaleString('id-ID')}</td>
      <td>${d.penumpang_berangkat.toLocaleString('id-ID')}</td>
      <td>${d.total_armada.toLocaleString('id-ID')}</td>
      <td>${d.rata_penumpang_harian.toLocaleString('id-ID')}</td>
    </tr>`;
  });
  tbody.innerHTML = html || '<tr><td colspan="9" style="text-align:center; padding:20px;">Tidak ada prasarana yang cocok.</td></tr>';
}

function filterPrasaranaByMode(mode, btn) {
  currentPrasaranaMode = mode;
  btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderPrasaranaTable();
}

function filterPrasaranaTable() {
  renderPrasaranaTable();
}

// -------------------------------------------------------------
// CHARTS INITIALIZATION
// -------------------------------------------------------------
function initCharts() {
  // Chart 1: Modal Split Donut
  new Chart(document.getElementById('chartModalSplit'), {
    type: 'doughnut',
    data: {
      labels: statsData.map(d => d.Moda),
      datasets: [{
        data: statsData.map(d => d.Total_Penumpang),
        backgroundColor: statsData.map(d => colors[d.Moda]),
        borderWidth: 2,
        borderColor: '#13223f'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { weight: 'bold' } } },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const val = ctx.raw;
              const total = summaryData.total_penumpang;
              const pct = ((val / total) * 100).toFixed(1);
              return ctx.label + ': ' + (val/1e6).toFixed(1) + ' Juta (' + pct + '%)';
            }
          }
        }
      }
    }
  });

  // Chart 2: Bar Comparison
  new Chart(document.getElementById('chartBarSplit'), {
    type: 'bar',
    data: {
      labels: statsData.map(d => d.Moda),
      datasets: [{
        label: 'Volume Penumpang (Juta Orang)',
        data: statsData.map(d => (d.Total_Penumpang / 1e6).toFixed(2)),
        backgroundColor: statsData.map(d => colors[d.Moda]),
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ctx.raw + ' Juta Penumpang'
          }
        }
      },
      scales: {
        x: { ticks: { color: '#cbd5e1', font: { weight: 'bold' } } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' } }
      }
    }
  });

  // Chart 3: Monthly Multi-mode
  const months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September"];
  const modesList = ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA'];
  const monthlyDatasets = modesList.map(m => {
    const vals = months.map(mon => {
      const row = monthlyData.find(r => r.nama_bulan === mon && r.moda === m);
      return row ? (row.total_penumpang / 1e6).toFixed(2) : 0;
    });
    return {
      label: m,
      data: vals,
      backgroundColor: colors[m],
      borderRadius: 4
    };
  });

  new Chart(document.getElementById('chartMonthlyMulti'), {
    type: 'bar',
    data: {
      labels: months,
      datasets: monthlyDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { color: '#cbd5e1' } }
      },
      scales: {
        x: { stacked: false, ticks: { color: '#cbd5e1' } },
        y: {
          stacked: false,
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255,255,255,0.06)' },
          title: { display: true, text: 'Juta Penumpang', color: '#94a3b8' }
        }
      }
    }
  });

  // Chart 4: Daily Trend Line Chart
  renderDailyChart('ALL');

  // Chart 5: Day of Week
  const hariOrder = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
  const dowDatasets = modesList.map(m => {
    const vals = hariOrder.map(h => {
      const row = dowData.find(r => r.hari === h && r.moda === m);
      return row ? (row.total_penumpang / 1e6).toFixed(2) : 0;
    });
    return {
      label: m,
      data: vals,
      backgroundColor: colors[m],
      borderRadius: 4
    };
  });

  new Chart(document.getElementById('chartDow'), {
    type: 'bar',
    data: {
      labels: hariOrder,
      datasets: dowDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { color: '#cbd5e1' } } },
      scales: {
        x: { ticks: { color: '#cbd5e1', font: { weight: 'bold' } } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' } }
      }
    }
  });

  // Chart 6: Top Provinces
  new Chart(document.getElementById('chartTopProv'), {
    type: 'bar',
    data: {
      labels: provData.map(d => d.provinsi),
      datasets: [{
        label: 'Volume Penumpang (Juta)',
        data: provData.map(d => (d.total_penumpang / 1e6).toFixed(1)),
        backgroundColor: '#0284c7',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' } },
        y: { ticks: { color: '#cbd5e1', font: { size: 11 } } }
      }
    }
  });

  // Chart 7: Load Ratio
  new Chart(document.getElementById('chartRatioLoad'), {
    type: 'bar',
    data: {
      labels: statsData.map(d => d.Moda),
      datasets: [{
        label: 'Penumpang per Armada',
        data: statsData.map(d => d.Rasio_Penumpang_per_Armada),
        backgroundColor: statsData.map(d => colors[d.Moda]),
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' } },
        y: { ticks: { color: '#cbd5e1', font: { weight: 'bold' } } }
      }
    }
  });
}

// Daily Chart Filter Logic
let dailyChartInstance = null;
function renderDailyChart(selectedMode) {
  const ctx = document.getElementById('chartDailyTrend');
  if (dailyChartInstance) dailyChartInstance.destroy();

  // Extract dates
  const dates = [...new Set(dailyData.map(d => d.tanggal))].sort();
  const modesList = ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA'];

  let datasets = [];
  if (selectedMode === 'ALL') {
    modesList.forEach(m => {
      const mapMode = {};
      dailyData.filter(d => d.moda === m).forEach(d => { mapMode[d.tanggal] = d.total_penumpang / 1e3; });
      datasets.push({
        label: m,
        data: dates.map(dt => mapMode[dt] || 0),
        borderColor: colors[m],
        backgroundColor: colors[m],
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.2
      });
    });
  } else {
    const mapMode = {};
    dailyData.filter(d => d.moda === selectedMode).forEach(d => { mapMode[d.tanggal] = d.total_penumpang / 1e3; });
    datasets.push({
      label: selectedMode,
      data: dates.map(dt => mapMode[dt] || 0),
      borderColor: colors[selectedMode],
      backgroundColor: colors[selectedMode],
      borderWidth: 2.2,
      pointRadius: 1,
      tension: 0.2,
      fill: false
    });
  }

  dailyChartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels: dates, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { color: '#cbd5e1' } },
        tooltip: {
          callbacks: {
            label: (ctx) => ctx.dataset.label + ': ' + parseFloat(ctx.raw).toLocaleString('id-ID') + ' Ribu Penumpang'
          }
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', maxTicksLimit: 12 }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' }, title: { display: true, text: 'Ribu Penumpang / Hari', color: '#94a3b8' } }
      }
    }
  });
}

function toggleDailySeries(mode, btn) {
  btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderDailyChart(mode);
}

// -------------------------------------------------------------
// LEAFLET MAP
// -------------------------------------------------------------
let map = null;
let markersLayer = null;
let currentMapMode = 'ALL';

function initMap() {
  map = L.map('map').setView([-2.5, 118], 5);
  window.myMap = map;

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO &copy; OpenStreetMap',
    maxZoom: 18
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
  renderMapMarkers();
}

function renderMapMarkers() {
  markersLayer.clearLayers();
  
  const filtered = mapNodes.filter(n => {
    if (currentMapMode !== 'ALL' && n.m !== currentMapMode) return false;
    return true;
  });

  filtered.forEach(n => {
    const color = colors[n.m] || '#38bdf8';
    const rad = Math.min(22, Math.max(4, Math.sqrt(n.tot_p) / 450));

    const circle = L.circleMarker([n.lat, n.lon], {
      radius: rad,
      fillColor: color,
      color: '#ffffff',
      weight: 1.2,
      opacity: 0.9,
      fillOpacity: 0.75
    });

    const popupHtml = `
      <div style="font-family:sans-serif; min-width:210px; color:#0f172a;">
        <div style="font-size:11px; font-weight:bold; color:${color}; text-transform:uppercase;">${n.m} • ${n.t || 'Fasilitas'}</div>
        <div style="font-size:14px; font-weight:800; margin:2px 0 6px;">${n.nama}</div>
        <div style="font-size:11.5px; color:#475569; margin-bottom:8px;">Provinsi: <b>${n.p}</b></div>
        <div style="background:#f1f5f9; padding:8px 10px; border-radius:6px; font-size:12px; line-height:1.6;">
          <div>Total Penumpang: <b>${n.tot_p.toLocaleString('id-ID')}</b></div>
          <div>Datang: ${n.p_dat.toLocaleString('id-ID')} | Berangkat: ${n.p_brg.toLocaleString('id-ID')}</div>
          <div>Total Armada: <b>${n.tot_a.toLocaleString('id-ID')}</b> trip</div>
          <div>Rata-rata Harian: <b>${n.avg_p.toLocaleString('id-ID')}</b> org/hari</div>
        </div>
      </div>
    `;
    circle.bindPopup(popupHtml);
    markersLayer.addLayer(circle);
  });
}

function filterMapMode(mode, btn) {
  currentMapMode = mode;
  btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderMapMarkers();
}

// Run on page load
window.addEventListener('DOMContentLoaded', () => {
  renderSummaryTable();
  renderPeakDaysTable();
  renderStatsTable();
  renderPrasaranaTable();
  initCharts();
  initMap();
});
</script>
</body>
</html>
"""

# Replace placeholders
final_html = html_base.replace("__SUMMARY_DATA__", json.dumps(summary_data, ensure_ascii=False))
final_html = final_html.replace("__STATS_DATA__", json.dumps(stats_json, ensure_ascii=False))
final_html = final_html.replace("__DAILY_DATA__", json.dumps(daily_json, ensure_ascii=False))
final_html = final_html.replace("__MONTHLY_DATA__", json.dumps(monthly_json, ensure_ascii=False))
final_html = final_html.replace("__DOW_DATA__", json.dumps(dow_json, ensure_ascii=False))
final_html = final_html.replace("__TOP_PRASARANA__", json.dumps(top_json, ensure_ascii=False))
final_html = final_html.replace("__PROV_DATA__", json.dumps(prov_top, ensure_ascii=False))
final_html = final_html.replace("__PEAK_DAYS__", json.dumps(peak_days_json, ensure_ascii=False))
final_html = final_html.replace("__MAP_NODES__", json.dumps(map_nodes, ensure_ascii=False))

print(f"Menulis file Dashboard ke: {output_html}...")
with open(output_html, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"[SELESAI] File Dashboard HTML berhasil dibangun! Ukuran: {os.path.getsize(output_html)/1024:.1f} KB")
