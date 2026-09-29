import json
import os

bundle_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
out_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html"

with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

json_data_str = json.dumps(bundle, ensure_ascii=False)

html_template = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Mobilitas Nasional & Analisis Puncak Lonjakan 2026 - PUSDATIN KEMENHUB</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #070b14;
  --bg-gradient: radial-gradient(1400px 700px at 80% -20%, #172554 0%, #070b14 70%);
  --card-bg: rgba(15, 23, 42, 0.75);
  --card-border: rgba(56, 189, 248, 0.15);
  --card-hover: rgba(30, 41, 59, 0.85);
  --text: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  --cyan: #06b6d4;
  --blue: #3b82f6;
  --indigo: #6366f1;
  --emerald: #10b981;
  --amber: #f59e0b;
  --rose: #f43f5e;
  --purple: #a855f7;
  --moda-udara: #38bdf8;
  --moda-ka: #f59e0b;
  --moda-bus: #10b981;
  --moda-asdp: #8b5cf6;
  --moda-laut: #06b6d4;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg-gradient);
  background-color: var(--bg);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
  padding-bottom: 60px;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px 24px;
}

/* Header */
header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 16px 24px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}
.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}
.brand-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4);
}
.brand-title h1 {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(to right, #ffffff, #93c5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.brand-title p {
  font-size: 13px;
  color: var(--text-muted);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
}
.badge.cyan { border-color: rgba(6, 182, 212, 0.4); color: var(--cyan); background: rgba(6, 182, 212, 0.1); }
.badge.emerald { border-color: rgba(16, 185, 129, 0.4); color: var(--emerald); background: rgba(16, 185, 129, 0.1); }
.badge.amber { border-color: rgba(245, 158, 11, 0.4); color: var(--amber); background: rgba(245, 158, 11, 0.1); }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.kpi-card {
  background: var(--card-bg);
  backdrop-filter: blur(14px);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.35);
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 4px; height: 100%;
}
.kpi-card.c-blue::before { background: var(--blue); }
.kpi-card.c-rose::before { background: var(--rose); }
.kpi-card.c-purple::before { background: var(--purple); }
.kpi-card.c-emerald::before { background: var(--emerald); }
.kpi-card.c-amber::before { background: var(--amber); }

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kpi-val {
  font-size: 26px;
  font-weight: 800;
  margin: 6px 0 2px;
  letter-spacing: -0.02em;
}
.kpi-sub {
  font-size: 12px;
  color: var(--text-dim);
}
.kpi-sub strong {
  color: var(--emerald);
}

/* Tabs Nav */
.tabs-nav {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 2px;
}
.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 600;
  padding: 10px 18px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.tab-btn:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}
.tab-btn.active {
  color: #fff;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.15);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: rgba(15, 23, 42, 0.5);
  padding: 12px 18px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 20px;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}
.btn-preset {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-preset:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}
.btn-preset.active {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}

.search-input {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  outline: none;
  width: 220px;
  transition: border-color 0.2s;
}
.search-input:focus {
  border-color: var(--cyan);
}

/* Grid & Cards */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.card {
  background: var(--card-bg);
  backdrop-filter: blur(14px);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  position: relative;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}
.card-title h3 {
  font-size: 16px;
  font-weight: 700;
}
.card-title p {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
.chart-box {
  position: relative;
  width: 100%;
  height: 340px;
}
.chart-box.tall {
  height: 440px;
}

/* Tables */
.table-wrap {
  width: 100%;
  overflow-x: auto;
}
table.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}
table.styled-table th {
  background: rgba(30, 41, 59, 0.7);
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.05em;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
table.styled-table td {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
table.styled-table tr:hover td {
  background: rgba(255, 255, 255, 0.03);
}
.pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.pill.udara { background: rgba(56, 189, 248, 0.15); color: var(--moda-udara); }
.pill.ka { background: rgba(245, 158, 11, 0.15); color: var(--moda-ka); }
.pill.bus { background: rgba(16, 185, 129, 0.15); color: var(--moda-bus); }
.pill.asdp { background: rgba(139, 92, 246, 0.15); color: var(--moda-asdp); }
.pill.laut { background: rgba(6, 182, 212, 0.15); color: var(--moda-laut); }

.bar-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bar-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 3px;
}

/* Insights Card */
.insight-box {
  background: rgba(30, 41, 59, 0.4);
  border-left: 4px solid var(--cyan);
  padding: 14px 18px;
  border-radius: 0 12px 12px 0;
  margin-bottom: 12px;
}
.insight-box h4 {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}
.insight-box p {
  font-size: 12.5px;
  color: var(--text-muted);
}

/* Lebaran Day Card */
.lebaran-day-strip {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 12px;
  margin-bottom: 14px;
}
.day-card {
  min-width: 140px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.day-card:hover {
  border-color: rgba(56, 189, 248, 0.4);
  transform: translateY(-2px);
}
.day-card.active {
  background: rgba(56, 189, 248, 0.15);
  border-color: var(--cyan);
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.2);
}
.day-card.peak {
  border-color: var(--rose);
  background: rgba(244, 63, 94, 0.1);
}
.day-card.h-day {
  border-color: var(--amber);
  background: rgba(245, 158, 11, 0.1);
}
.day-card .d-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}
.day-card .d-val {
  font-size: 17px;
  font-weight: 800;
  margin: 4px 0 2px;
}
.day-card .d-date {
  font-size: 11px;
  color: var(--text-dim);
}

.day-detail-banner {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* Modals / Sections */
.tab-content { display: none; }
.tab-content.active { display: block; animation: fadeIn 0.25s ease; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
  .brand-title h1 { font-size: 18px; }
}
</style>
</head>
<body>

<div class="container">
  <!-- Header -->
  <header>
    <div class="brand">
      <div class="brand-icon">🚆</div>
      <div class="brand-title">
        <h1>SIASATI MOBILITY INTELLIGENCE 2026</h1>
        <p>Analisis Tren Mobilitas Nasional, Puncak Lonjakan Musiman, dan Dinamika Antar-Moda • PUSDATIN KEMENHUB</p>
      </div>
    </div>
    <div class="header-actions">
      <div class="badge cyan">🗓️ 1 Jan - 28 Sep 2026</div>
      <div class="badge emerald">✅ 283.116 Baris Valid</div>
      <div class="badge amber">🔥 Puncak: 2,42 Juta Pnp/Hari</div>
    </div>
  </header>

  <!-- KPI Hero Cards -->
  <div class="kpi-grid">
    <div class="kpi-card c-blue">
      <div class="kpi-label">
        <span>Total Penumpang Terlayani</span>
        <span>👥</span>
      </div>
      <div class="kpi-val" id="kpi-total-pnp">-</div>
      <div class="kpi-sub">Agregasi 5 moda transportasi nasional (Clean)</div>
    </div>

    <div class="kpi-card c-rose">
      <div class="kpi-label">
        <span>Rekor Puncak Tertinggi</span>
        <span>⚡</span>
      </div>
      <div class="kpi-val" id="kpi-peak-val">2.415.296</div>
      <div class="kpi-sub"><strong>Selasa, 24 Maret 2026</strong> (H+3 Arus Balik)</div>
    </div>

    <div class="kpi-card c-purple">
      <div class="kpi-label">
        <span>Lonjakan Terbesar (Moda)</span>
        <span>🚢</span>
      </div>
      <div class="kpi-val">+252,1%</div>
      <div class="kpi-sub">Moda <strong>ASDP Penyeberangan</strong> (Puncak 445k pnp)</div>
    </div>

    <div class="kpi-card c-emerald">
      <div class="kpi-label">
        <span>Bulan Tersibuk Nasional</span>
        <span>📈</span>
      </div>
      <div class="kpi-val">50,51 Juta</div>
      <div class="kpi-sub"><strong>Maret 2026</strong> (Angkutan Lebaran Idul Fitri)</div>
    </div>

    <div class="kpi-card c-amber">
      <div class="kpi-label">
        <span>Total Armada Beroperasi</span>
        <span>🚌</span>
      </div>
      <div class="kpi-val" id="kpi-total-arm">-</div>
      <div class="kpi-sub">Trip bus, flight, kapal, KA, dan Ro-Ro</div>
    </div>
  </div>

  <!-- Tabs Navigation -->
  <div class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('tab-timeline')">📈 Tren Mobilitas 271 Hari</button>
    <button class="tab-btn" onclick="switchTab('tab-lebaran')">🚀 Anatomi Puncak Lebaran 2026</button>
    <button class="tab-btn" onclick="switchTab('tab-modal-share')">🍰 Dinamika Pangsa Pasar (Modal Share)</button>
    <button class="tab-btn" onclick="switchTab('tab-load-factor')">⚡ Beban & Okupansi Armada</button>
    <button class="tab-btn" onclick="switchTab('tab-top-hubs')">🏆 Top Simpul Transportasi</button>
    <button class="tab-btn" onclick="switchTab('tab-policy')">🧭 Rekomendasi Kebijakan</button>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 1: TIMELINE & SEASONALITY -->
  <!-- ================================================================= -->
  <div id="tab-timeline" class="tab-content active">
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">Preset Periode:</span>
        <button class="btn-preset active" onclick="filterTimelineRange('all', this)">Sepanjang 2026 (Jan - Sep)</button>
        <button class="btn-preset" onclick="filterTimelineRange('lebaran', this)">Puncak Lebaran (10 Mar - 5 Apr)</button>
        <button class="btn-preset" onclick="filterTimelineRange('libur_sekolah', this)">Libur Sekolah (15 Jun - 15 Jul)</button>
        <button class="btn-preset" onclick="filterTimelineRange('tahun_baru', this)">Tahun Baru (1 - 15 Jan)</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">Metrik:</span>
        <button class="btn-preset active" id="btn-metric-pnp" onclick="toggleMetric('pnp')">Penumpang</button>
        <button class="btn-preset" id="btn-metric-arm" onclick="toggleMetric('arm')">Armada</button>
      </div>
    </div>

    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <div class="card-title">
          <h3 id="timeline-chart-title">Grafik Pergerakan Penumpang Harian Multimoda 2026</h3>
          <p>Dinamika harian 5 moda transportasi: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut</p>
        </div>
        <div class="badge cyan" id="timeline-range-badge">271 Hari Pengamatan</div>
      </div>
      <div class="chart-box tall">
        <canvas id="chartTimeline"></canvas>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Agregat Pergerakan Bulanan (Januari s.d. September 2026)</h3>
            <p>Pola musiman: Puncak 1 (Lebaran Maret) dan Puncak 2 (Libur Sekolah Juni-Juli)</p>
          </div>
        </div>
        <div class="chart-box">
          <canvas id="chartMonthly"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Rata-rata Mobilitas per Hari dalam Seminggu (Day-of-Week)</h3>
            <p>Karakteristik akhir pekan vs hari kerja biasa di masing-masing moda</p>
          </div>
        </div>
        <div class="chart-box">
          <canvas id="chartDOW"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 2: ANATOMI PUNCAK LEBARAN 2026 -->
  <!-- ================================================================= -->
  <div id="tab-lebaran" class="tab-content">
    <!-- Day by day selector strip -->
    <div style="margin-bottom: 8px;">
      <h4 style="font-size: 14px; font-weight: 700; color: var(--text-muted); margin-bottom: 8px;">
        PILIH TANGGAL SPESIFIK ANGKUTAN LEBARAN 2026 (H-8 s.d. H+15) UNTUK INSPEKSI:
      </h4>
      <div class="lebaran-day-strip" id="lebaran-strip"></div>
    </div>

    <!-- Interactive Day Detail Banner -->
    <div class="day-detail-banner" id="lebaran-day-banner">
      <div>
        <span class="badge rose" id="banner-tag">★ PUNCAK ARUS MUDIK</span>
        <h3 style="font-size: 18px; font-weight: 800; margin-top: 4px;" id="banner-date">Rabu, 18 Maret 2026</h3>
        <p style="font-size: 12px; color: var(--text-muted);" id="banner-desc">Puncak arus mudik nasional: Penyeberangan ASDP mencapai rekor 445.532 pnp.</p>
      </div>
      <div style="display: flex; gap: 18px; flex-wrap: wrap;" id="banner-pills">
        <!-- Rendered by JS -->
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Kurva Dinamika Arus Mudik vs Arus Balik 2026</h3>
            <p>Perhatikan dual-wave arus balik: Gelombang 1 (Darat/KA) vs Gelombang 2 (Udara/Laut)</p>
          </div>
          <div class="badge rose">Puncak: 2,42 Juta Pnp</div>
        </div>
        <div class="chart-box">
          <canvas id="chartLebaranLine"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Komparasi Lonjakan (Surge %) terhadap Hari Normal</h3>
            <p>Persentase kenaikan penumpang saat Peak Mudik (18 Mar) dan Peak Balik (24 Mar) vs Baseline Februari</p>
          </div>
        </div>
        <div class="chart-box">
          <canvas id="chartSurgeBar"></canvas>
        </div>
      </div>
    </div>

    <!-- Tabel Komparasi Detail -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <h3>Tabel Detail Lonjakan Volume Penumpang Angkutan Lebaran 2026</h3>
          <p>Komparasi data baseline normal harian (Februari) terhadap hari-hari puncak kritis</p>
        </div>
      </div>
      <div class="table-wrap">
        <table class="styled-table" id="table-surge">
          <thead>
            <tr>
              <th>Moda Transportasi</th>
              <th>Normal Harian (Feb)</th>
              <th>Puncak Mudik (18 Mar)</th>
              <th>Lonjakan Mudik (%)</th>
              <th>Puncak Balik 1 (24 Mar)</th>
              <th>Lonjakan Balik 1 (%)</th>
              <th>Puncak Balik 2 (29 Mar)</th>
              <th>Lonjakan Balik 2 (%)</th>
              <th>Karakteristik Kritis</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 3: MODAL SHARE DYNAMICS -->
  <!-- ================================================================= -->
  <div id="tab-modal-share" class="tab-content">
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Pergerakan Pangsa Pasar Bulanan (100% Stacked Modal Share)</h3>
            <p>Perubahan proporsi penggunaan moda dari Januari hingga September 2026</p>
          </div>
        </div>
        <div class="chart-box">
          <canvas id="chartModalShareArea"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Komparasi Proporsi Moda: Normal vs Puncak Lebaran</h3>
            <p>Terlihat pergeseran pangsa ke ASDP dan KA saat Angkutan Lebaran berlangsung</p>
          </div>
        </div>
        <div style="display: flex; gap: 16px; justify-content: space-around; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 220px; text-align: center;">
            <h4 style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;">Baseline Normal (Februari)</h4>
            <div class="chart-box" style="height: 260px;"><canvas id="donutNormal"></canvas></div>
          </div>
          <div style="flex: 1; min-width: 220px; text-align: center;">
            <h4 style="font-size: 13px; color: var(--cyan); margin-bottom: 8px;">Puncak Lebaran (Maret)</h4>
            <div class="chart-box" style="height: 260px;"><canvas id="donutPeak"></canvas></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Insights Modal Shift -->
    <div class="grid-3">
      <div class="insight-box" style="border-left-color: var(--moda-asdp);">
        <h4>Lonjakan Pangsa ASDP (+4,2%)</h4>
        <p>Pangsa pasar penyeberangan naik dari 10,6% di hari biasa menjadi 14,8% saat Lebaran karena tingginya volume pemudik yang membawa kendaraan pribadi via Merak-Bakauheni dan Ketapang-Gilimanuk.</p>
      </div>

      <div class="insight-box" style="border-left-color: var(--moda-ka);">
        <h4>Dominasi Kereta Api Pasca-Lebaran</h4>
        <p>Pangsa Kereta Api meningkat hingga 24,6% di bulan Mei dan tetap tinggi di atas 22% saat arus balik karena kepastian jadwal waktu tempuh bebas macet.</p>
      </div>

      <div class="insight-box" style="border-left-color: var(--moda-laut);">
        <h4>Puncak Maritim di Liburan Sekolah (14,8%)</h4>
        <p>Moda transportasi laut mencapai pangsa pasar tertinggi tahunan pada bulan Juli (14,8%) didorong pariwisata bahari domestik (Bali, Nusa Penida, Labuan Bajo, Kepri).</p>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 4: LOAD FACTOR & ARMADA -->
  <!-- ================================================================= -->
  <div id="tab-load-factor" class="tab-content">
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Rasio Intensitas Penumpang per Armada (Load Factor Proxy)</h3>
            <p>Beban keterisian rata-rata armada: Hari Biasa vs Masa Puncak Lebaran</p>
          </div>
        </div>
        <div class="chart-box">
          <canvas id="chartLoadFactor"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Evaluasi Kepadatan & Batas Kapasitas Operasional</h3>
            <p>Tingkat utilisasi armada dan potensi bottleneck operasional per moda</p>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 10px;">
          <div class="insight-box" style="border-left-color: var(--purple);">
            <h4>ASDP: Kenaikan Beban +121,9% (245,2 Pnp/Trip)</h4>
            <p>Setiap keberangkatan kapal penyeberangan mengangkut lebih dari 2 kali lipat rata-rata penumpang hari biasa. Waktu sandar (port time) dan kapasitas dermaga merupakan titik kritis utama.</p>
          </div>
          <div class="insight-box" style="border-left-color: var(--blue);">
            <h4>UDARA: Seat Load Factor Mendekati 90% (120,7 Pnp/Flight)</h4>
            <p>Penerbangan didominasi armada narrow-body (A320/B737 berkapasitas 150-180 kursi). Kenaikan rasio menandakan hampir seluruh kursi penerbangan reguler dan extra flight terisi penuh.</p>
          </div>
          <div class="insight-box" style="border-left-color: var(--emerald);">
            <h4>BUS: Kenaikan Okupansi +48,3% (17,2 Pnp/Bus)</h4>
            <p>Terjadi pemanfaatan maksimal bus AKAP Antar Kota Antar Provinsi serta program Mudik Gratis Kemenhub dan BUMN.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 5: TOP HUBS & CORRIDORS -->
  <!-- ================================================================= -->
  <div id="tab-top-hubs" class="tab-content">
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">Filter Moda:</span>
        <button class="btn-preset active" onclick="filterTopHubs('ALL', this)">Semua Moda</button>
        <button class="btn-preset" onclick="filterTopHubs('UDARA', this)">Bandara (Udara)</button>
        <button class="btn-preset" onclick="filterTopHubs('KA', this)">Stasiun (KA)</button>
        <button class="btn-preset" onclick="filterTopHubs('BUS', this)">Terminal (Bus)</button>
        <button class="btn-preset" onclick="filterTopHubs('ASDP', this)">Pelabuhan Penyeberangan (ASDP)</button>
        <button class="btn-preset" onclick="filterTopHubs('LAUT', this)">Pelabuhan Laut</button>
      </div>
      <div class="filter-group">
        <input type="text" class="search-input" id="search-hub" placeholder="Cari nama simpul / kota..." onkeyup="onSearchHub(this.value)">
        <button class="btn-preset active" id="btn-hub-peak" onclick="toggleHubPeriod('peak')">Puncak Lebaran (18-29 Mar)</button>
        <button class="btn-preset" id="btn-hub-ytd" onclick="toggleHubPeriod('ytd')">Sepanjang 2026 (YTD)</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <h3 id="hub-table-title">Daftar Simpul Transportasi Terpadat Periode Puncak Lebaran (18-29 Maret 2026)</h3>
          <p id="hub-table-subtitle">Peringkat simpul berdasarkan akumulasi total penumpang yang terlayani</p>
        </div>
      </div>
      <div class="table-wrap">
        <table class="styled-table" id="table-hubs">
          <thead>
            <tr>
              <th style="width: 60px;">Peringkat</th>
              <th>Nama Prasarana / Simpul</th>
              <th>Moda</th>
              <th>Provinsi</th>
              <th>Total Penumpang Terlayani</th>
              <th>Total Armada</th>
              <th style="width: 250px;">Visualisasi Skala Volume</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TAB 6: POLICY & RECOMENDATIONS -->
  <!-- ================================================================= -->
  <div id="tab-policy" class="tab-content">
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>4 Rekomendasi Kebijakan Operasional Berbasis Data</h3>
            <p>Untuk Pimpinan Kementerian Perhubungan, Ditjen Teknis, dan Operator BUMN</p>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 14px;">
          <div class="insight-box" style="border-left-color: var(--purple);">
            <h4>1. Sistem Peringatan Dini Menggunakan Data Tiket ASDP (Lead Time 48 Jam)</h4>
            <p>Data menunjukkan ASDP mencapai puncak lonjakan pada <strong>H-2 (18 Maret)</strong>, mendahului puncak moda Kereta Api dan Udara pada H+3. Pemantauan real-time kuota tiket online Ferizy ASDP harus menjadi <em>leading indicator</em> peringatan dini bagi Korlantas Polri dan BPJT untuk mengaktifkan rekayasa lalu lintas jalan tol arah Merak dan Bakauheni.</p>
          </div>
          <div class="insight-box" style="border-left-color: var(--blue);">
            <h4>2. Antisipasi Strategis Dua Gelombang Arus Balik (Dual-Wave Return)</h4>
            <p>Arus balik Lebaran terbukti tidak terjadi dalam satu hari, melainkan terbelah menjadi <strong>Gelombang 1 (H+3 s.d. H+4, 24-25 Maret)</strong> untuk pekerja sektor formal/darat, dan <strong>Gelombang 2 (H+7 s.d. H+8, 28-29 Maret)</strong> untuk moda Udara dan Laut. Alokasi petugas posko dan diskon tarif tol/tiket harus dibagi merata pada kedua gelombang ini.</p>
          </div>
          <div class="insight-box" style="border-left-color: var(--amber);">
            <h4>3. Penguatan Manajemen Simpul Sekunder di Jawa Tengah & Jawa Timur</h4>
            <p>Stasiun Yogyakarta (307k) dan Purwokerto (200k) serta Terminal Bus Kertonegoro Ngawi (445k) dan Purabaya Surabaya (446k) mengalami kepadatan yang luar biasa saat arus balik. Perluasan ruang tunggu sementara dan ketersediaan armada feeder lokal sangat esensial agar tidak terjadi penumpukan penumpang di luar terminal.</p>
          </div>
          <div class="insight-box" style="border-left-color: var(--emerald);">
            <h4>4. Integrasi Validasi Data Real-Time (Eliminasi Anomali Duplikat)</h4>
            <p>Dengan teridentifikasinya 7.226 baris duplikat sama persis dan 34.229 baris dummy nol pada data SIASATI harian, Pusdatin Kemenhub disarankan memasang filter validasi otomatis pada API penerima data agar tidak terjadi inflasi statistik penumpang resmi kementerian.</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <h3>Matriks Kesiapan Angkutan Lebaran Mendatang</h3>
            <p>Rangkuman faktor kunci keberhasilan operasional per moda</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="styled-table">
            <thead>
              <tr>
                <th>Moda</th>
                <th>Titik Kritis Utama</th>
                <th>Hari Paling Padat</th>
                <th>Solusi Rekomendasi</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span class="pill asdp">ASDP</span></td>
                <td>Antrean Dermaga Merak-Bakauheni</td>
                <td>H-2 Mudik (18 Mar)</td>
                <td>Pemberlakuan Delaying System di Rest Area & Tiketing Berjadwal Ketat</td>
              </tr>
              <tr>
                <td><span class="pill ka">KERETA API</span></td>
                <td>Kapasitas Kursi & Sirkulasi Stasiun</td>
                <td>H+3 Balik (24 Mar)</td>
                <td>Penambahan Kereta Tambahan & Pengaturan Alur Masuk Penumpang</td>
              </tr>
              <tr>
                <td><span class="pill bus">BUS</span></td>
                <td>Kemacetan Jalur Arteri Menuju Terminal</td>
                <td>H+4 Balik (25 Mar)</td>
                <td>Sterilisasi Jalur Keluar-Masuk Terminal Tipe A Jawa Timur & Jateng</td>
              </tr>
              <tr>
                <td><span class="pill udara">UDARA</span></td>
                <td>Kepadatan Check-In & Bagasi Bandara</td>
                <td>H+8 Balik (29 Mar)</td>
                <td>Optimalisasi Self Check-In & Slot Time Malam/Dini Hari</td>
              </tr>
              <tr>
                <td><span class="pill laut">LAUT</span></td>
                <td>Ketersediaan Kapal Rute Kepulauan</td>
                <td>H+8 Balik (29 Mar)</td>
                <td>Penugasan Kapal Cadangan Perintis & Pengawasan Manifest Penumpang</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- DATA SCRIPT & LOGIC -->
<script>
const DATA = """ + json_data_str + """;

// Helper Formatter
const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// State
let currentMetric = 'pnp'; // 'pnp' or 'arm'
let currentTimelineRange = 'all';
let currentHubModa = 'ALL';
let currentHubPeriod = 'peak'; // 'peak' or 'ytd'
let currentSearchTerm = '';

// Charts Holder
let chartTimelineInst = null;
let chartMonthlyInst = null;
let chartDOWInst = null;
let chartLebaranInst = null;
let chartSurgeInst = null;
let chartModalShareAreaInst = null;
let donutNormalInst = null;
let donutPeakInst = null;
let chartLoadFactorInst = null;

// Palette
const COLORS = {
  UDARA: '#38bdf8',
  KA: '#f59e0b',
  BUS: '#10b981',
  ASDP: '#8b5cf6',
  LAUT: '#06b6d4',
  TOTAL: '#ffffff'
};

// -------------------------------------------------------------
// TAB SWITCHER
// -------------------------------------------------------------
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  
  const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
  if (targetBtn) targetBtn.classList.add('active');
  
  const targetContent = document.getElementById(tabId);
  if (targetContent) targetContent.classList.add('active');
  
  // Render charts when visible
  setTimeout(() => {
    if (tabId === 'tab-timeline' && chartTimelineInst) chartTimelineInst.resize();
    if (tabId === 'tab-lebaran') renderLebaranCharts();
    if (tabId === 'tab-modal-share') renderModalShareCharts();
    if (tabId === 'tab-load-factor') renderLoadFactorCharts();
    if (tabId === 'tab-top-hubs') renderHubsTable();
  }, 50);
}

// -------------------------------------------------------------
// TAB 1: TIMELINE
// -------------------------------------------------------------
function getTimelineFilteredData() {
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') {
    return all.filter(d => d.date >= '2026-03-10' && d.date <= '2026-04-05');
  } else if (currentTimelineRange === 'libur_sekolah') {
    return all.filter(d => d.date >= '2026-06-15' && d.date <= '2026-07-15');
  } else if (currentTimelineRange === 'tahun_baru') {
    return all.filter(d => d.date >= '2026-01-01' && d.date <= '2026-01-15');
  }
  return all;
}

function renderTimelineChart() {
  const data = getTimelineFilteredData();
  const ctx = document.getElementById('chartTimeline').getContext('2d');
  
  const labels = data.map(d => d.date);
  const prefix = currentMetric === 'pnp' ? '' : 'arm_';
  
  const datasets = [
    { label: 'Total Penumpang/Armada', data: data.map(d => d[prefix + 'TOTAL']), borderColor: '#ffffff', backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 2.5, pointRadius: 0, fill: false, tension: 0.2 },
    { label: 'Pesawat (Udara)', data: data.map(d => d[prefix + 'UDARA']), borderColor: COLORS.UDARA, backgroundColor: COLORS.UDARA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
    { label: 'Kereta Api (KA)', data: data.map(d => d[prefix + 'KA']), borderColor: COLORS.KA, backgroundColor: COLORS.KA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
    { label: 'Bus Terminal', data: data.map(d => d[prefix + 'BUS']), borderColor: COLORS.BUS, backgroundColor: COLORS.BUS, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
    { label: 'Penyeberangan (ASDP)', data: data.map(d => d[prefix + 'ASDP']), borderColor: COLORS.ASDP, backgroundColor: COLORS.ASDP, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
    { label: 'Kapal Laut', data: data.map(d => d[prefix + 'LAUT']), borderColor: COLORS.LAUT, backgroundColor: COLORS.LAUT, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
  ];

  if (chartTimelineInst) chartTimelineInst.destroy();
  chartTimelineInst = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 11, weight: '600' } } },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(56, 189, 248, 0.3)',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${numFmt(ctx.raw)} ${currentMetric === 'pnp' ? 'penumpang' : 'armada'}`
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', maxTicksLimit: 14 } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v/1e3).toFixed(0) + 'k') } }
      }
    }
  });
}

function filterTimelineRange(range, btn) {
  currentTimelineRange = range;
  document.querySelectorAll('.filter-bar .filter-group:first-child .btn-preset').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  const labelsMap = {
    'all': '271 Hari Pengamatan (Jan - Sep 2026)',
    'lebaran': '27 Hari Periode Angkutan Lebaran 2026',
    'libur_sekolah': '31 Hari Periode Libur Sekolah 2026',
    'tahun_baru': '15 Hari Periode Libur Tahun Baru 2026'
  };
  document.getElementById('timeline-range-badge').innerText = labelsMap[range] || '';
  renderTimelineChart();
}

function toggleMetric(m) {
  currentMetric = m;
  document.getElementById('btn-metric-pnp').classList.toggle('active', m === 'pnp');
  document.getElementById('btn-metric-arm').classList.toggle('active', m === 'arm');
  document.getElementById('timeline-chart-title').innerText = m === 'pnp' ? 'Grafik Pergerakan Penumpang Harian Multimoda 2026' : 'Grafik Pergerakan Armada Harian Multimoda 2026';
  renderTimelineChart();
}

function renderMonthlyChart() {
  const ctx = document.getElementById('chartMonthly').getContext('2d');
  const ms = DATA.monthly_summary;
  
  chartMonthlyInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ms.map(m => m.label),
      datasets: [
        { label: 'Pesawat (Udara)', data: ms.map(m => m.UDARA), backgroundColor: COLORS.UDARA },
        { label: 'Kereta Api (KA)', data: ms.map(m => m.KA), backgroundColor: COLORS.KA },
        { label: 'Bus', data: ms.map(m => m.BUS), backgroundColor: COLORS.BUS },
        { label: 'ASDP Penyeberangan', data: ms.map(m => m.ASDP), backgroundColor: COLORS.ASDP },
        { label: 'Kapal Laut', data: ms.map(m => m.LAUT), backgroundColor: COLORS.LAUT },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 10 } } },
        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${numFmt(ctx.raw)} pnp` } }
      },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
        y: { stacked: true, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => (v/1e6).toFixed(0) + 'M' } }
      }
    }
  });
}

function renderDOWChart() {
  const ctx = document.getElementById('chartDOW').getContext('2d');
  const dow = DATA.dow_summary;
  
  chartDOWInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: dow.map(d => d.dow),
      datasets: [
        { label: 'Total Rata-rata Harian', data: dow.map(d => d.TOTAL), backgroundColor: 'rgba(56, 189, 248, 0.3)', borderColor: 'rgba(56, 189, 248, 0.9)', borderWidth: 1.5 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => `Rata-rata: ${numFmt(ctx.raw)} pnp/hari` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => (v/1e6).toFixed(1) + 'M' } }
      }
    }
  });
}

// -------------------------------------------------------------
// TAB 2: LEBARAN 2026
// -------------------------------------------------------------
function selectLebaranDay(dateStr) {
  const day = DATA.lebaran_daily.find(d => d.date === dateStr);
  if (!day) return;

  document.getElementById('banner-tag').innerText = day.tag;
  document.getElementById('banner-date').innerText = `${day.date} (${day.tag})`;
  document.getElementById('banner-desc').innerText = `${day.desc} — Total Penumpang: ${numFmt(day.TOTAL)} pnp, Armada: ${numFmt(day.arm_TOTAL)}`;
  
  const pillsBox = document.getElementById('banner-pills');
  pillsBox.innerHTML = `
    <div style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:10px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:#38bdf8; font-weight:700;">UDARA</div>
      <div style="font-size:14px; font-weight:800;">${numFmt(day.UDARA)}</div>
    </div>
    <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); border-radius:10px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:#f59e0b; font-weight:700;">KERETA API</div>
      <div style="font-size:14px; font-weight:800;">${numFmt(day.KA)}</div>
    </div>
    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:#10b981; font-weight:700;">BUS</div>
      <div style="font-size:14px; font-weight:800;">${numFmt(day.BUS)}</div>
    </div>
    <div style="background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.3); border-radius:10px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:#8b5cf6; font-weight:700;">ASDP</div>
      <div style="font-size:14px; font-weight:800;">${numFmt(day.ASDP)}</div>
    </div>
    <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); border-radius:10px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:#06b6d4; font-weight:700;">LAUT</div>
      <div style="font-size:14px; font-weight:800;">${numFmt(day.LAUT)}</div>
    </div>
  `;
}

function buildLebaranStrip() {
  const container = document.getElementById('lebaran-strip');
  container.innerHTML = '';
  
  DATA.lebaran_daily.forEach((d) => {
    const card = document.createElement('div');
    card.className = 'day-card' + (d.is_peak_balik1 ? ' active peak' : (d.is_peak_mudik ? ' peak' : (d.is_h_day ? ' h-day' : '')));
    card.innerHTML = `
      <div class="d-tag">${d.tag}</div>
      <div class="d-val">${(d.TOTAL / 1e6).toFixed(2)}M</div>
      <div class="d-date">${d.date.substring(5)} • ${numFmt(d.TOTAL)}</div>
    `;
    card.onclick = () => {
      document.querySelectorAll('.day-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      selectLebaranDay(d.date);
    };
    container.appendChild(card);
  });
  
  // default select 2026-03-24 (Peak All-Time)
  selectLebaranDay('2026-03-24');
}

function renderLebaranCharts() {
  if (chartLebaranInst) return; // already rendered
  buildLebaranStrip();

  // Line Chart
  const ctxLine = document.getElementById('chartLebaranLine').getContext('2d');
  const ld = DATA.lebaran_daily;
  
  chartLebaranInst = new Chart(ctxLine, {
    type: 'line',
    data: {
      labels: ld.map(d => d.date.substring(5) + ' (' + d.tag.split(' ')[0] + ')'),
      datasets: [
        { label: 'Total Penumpang', data: ld.map(d => d.TOTAL), borderColor: '#ffffff', borderWidth: 3, pointRadius: 3, tension: 0.2 },
        { label: 'Pesawat (Udara)', data: ld.map(d => d.UDARA), borderColor: COLORS.UDARA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
        { label: 'Kereta Api (KA)', data: ld.map(d => d.KA), borderColor: COLORS.KA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
        { label: 'Bus', data: ld.map(d => d.BUS), borderColor: COLORS.BUS, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
        { label: 'ASDP Penyeberangan', data: ld.map(d => d.ASDP), borderColor: COLORS.ASDP, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
        { label: 'Kapal Laut', data: ld.map(d => d.LAUT), borderColor: COLORS.LAUT, borderWidth: 1.8, pointRadius: 0, tension: 0.2 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 10 } } },
        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${numFmt(ctx.raw)} pnp` } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', maxRotation: 45, font: { size: 9 } } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => (v/1e3).toFixed(0) + 'k' } }
      }
    }
  });

  // Surge Bar Chart
  const ctxSurge = document.getElementById('chartSurgeBar').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
  const labelsSurge = ['ASDP Penyeberangan', 'Bus AKAP', 'Kereta Api', 'Kapal Laut', 'Pesawat Udara', 'TOTAL NASIONAL'];
  
  chartSurgeInst = new Chart(ctxSurge, {
    type: 'bar',
    data: {
      labels: labelsSurge,
      datasets: [
        { label: 'Lonjakan Mudik 18 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_mudik_pct), backgroundColor: 'rgba(244, 63, 94, 0.7)' },
        { label: 'Lonjakan Balik 24 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik1_pct), backgroundColor: 'rgba(56, 189, 248, 0.7)' },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } },
        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: +${ctx.raw}%` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => '+' + v + '%' } }
      }
    }
  });

  // Populate Table Surge
  const tbody = document.querySelector('#table-surge tbody');
  tbody.innerHTML = '';
  
  const notes = {
    'ASDP': 'Lonjakan paling awal (H-2) & paling ekstrem (+252,1%) karena pergerakan mobil pribadi via Ro-Ro.',
    'BUS': 'Puncak arus balik di 25 Mar (556k pnp), dipicu serapan pemudik yang kembali ke Jabodetabek/Surabaya.',
    'KA': 'Puncak tertinggi pada 24 Mar (565k pnp); keterisian kursi kereta komersial 100%.',
    'LAUT': 'Mencapai puncak arus balik kedua di 29 Mar (295k pnp) pada jalur kepulauan dan pesisir.',
    'UDARA': 'Mencapai volume tertinggi di akhir masa libur (29 Mar, 649k pnp) seiring kembalinya pekerja eksekutif/ASN.',
    'TOTAL': 'Puncak tertinggi nasional all-time pada Selasa, 24 Maret 2026 (2.415.296 penumpang).'
  };

  modas.forEach((m, idx) => {
    const s = DATA.surge_summary[m];
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${labelsSurge[idx]}</strong></td>
      <td>${numFmt(s.baseline)}</td>
      <td><span style="color:var(--rose); font-weight:700;">${numFmt(s.peak_mudik)}</span></td>
      <td><span class="pill" style="background:rgba(244,63,94,0.15); color:var(--rose);">+${s.surge_mudik_pct}%</span></td>
      <td><span style="color:var(--cyan); font-weight:700;">${numFmt(s.peak_balik1)}</span></td>
      <td><span class="pill" style="background:rgba(6,182,212,0.15); color:var(--cyan);">+${s.surge_balik1_pct}%</span></td>
      <td>${numFmt(s.peak_balik2)}</td>
      <td>+${s.surge_balik2_pct}%</td>
      <td style="font-size:12px; color:var(--text-muted);">${notes[m]}</td>
    `;
    tbody.appendChild(tr);
  });
}

// -------------------------------------------------------------
// TAB 3: MODAL SHARE
// -------------------------------------------------------------
function renderModalShareCharts() {
  if (chartModalShareAreaInst) return;

  const ctxArea = document.getElementById('chartModalShareArea').getContext('2d');
  const ms = DATA.monthly_summary;
  
  chartModalShareAreaInst = new Chart(ctxArea, {
    type: 'line',
    data: {
      labels: ms.map(m => m.label),
      datasets: [
        { label: 'Udara', data: ms.map(m => m.share_UDARA), borderColor: COLORS.UDARA, backgroundColor: 'rgba(56, 189, 248, 0.4)', fill: true, tension: 0.3 },
        { label: 'Kereta Api', data: ms.map(m => m.share_KA), borderColor: COLORS.KA, backgroundColor: 'rgba(245, 158, 11, 0.4)', fill: true, tension: 0.3 },
        { label: 'Bus', data: ms.map(m => m.share_BUS), borderColor: COLORS.BUS, backgroundColor: 'rgba(16, 185, 129, 0.4)', fill: true, tension: 0.3 },
        { label: 'ASDP', data: ms.map(m => m.share_ASDP), borderColor: COLORS.ASDP, backgroundColor: 'rgba(139, 92, 246, 0.4)', fill: true, tension: 0.3 },
        { label: 'Laut', data: ms.map(m => m.share_LAUT), borderColor: COLORS.LAUT, backgroundColor: 'rgba(6, 182, 212, 0.4)', fill: true, tension: 0.3 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } },
        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw}% pangsa` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
        y: { stacked: true, max: 100, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b', callback: v => v + '%' } }
      }
    }
  });

  // Donut Normal (Feb) vs Peak (Mar)
  const febShare = ms.find(m => m.bulan === '2026-02');
  const marShare = ms.find(m => m.bulan === '2026-03');
  const donutLabels = ['Udara', 'Kereta Api', 'Bus', 'ASDP', 'Laut'];
  const donutColors = [COLORS.UDARA, COLORS.KA, COLORS.BUS, COLORS.ASDP, COLORS.LAUT];

  const ctxNorm = document.getElementById('donutNormal').getContext('2d');
  donutNormalInst = new Chart(ctxNorm, {
    type: 'doughnut',
    data: {
      labels: donutLabels,
      datasets: [{
        data: [febShare.share_UDARA, febShare.share_KA, febShare.share_BUS, febShare.share_ASDP, febShare.share_LAUT],
        backgroundColor: donutColors,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } }
    }
  });

  const ctxPeak = document.getElementById('donutPeak').getContext('2d');
  donutPeakInst = new Chart(ctxPeak, {
    type: 'doughnut',
    data: {
      labels: donutLabels,
      datasets: [{
        data: [marShare.share_UDARA, marShare.share_KA, marShare.share_BUS, marShare.share_ASDP, marShare.share_LAUT],
        backgroundColor: donutColors,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } }
    }
  });
}

// -------------------------------------------------------------
// TAB 4: LOAD FACTOR
// -------------------------------------------------------------
function renderLoadFactorCharts() {
  if (chartLoadFactorInst) return;

  const ctx = document.getElementById('chartLoadFactor').getContext('2d');
  const lf = DATA.load_factor_stats;
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labels = ['ASDP (pnp/trip)', 'Bus (pnp/bus)', 'KA (pnp/trip)', 'Laut (pnp/kapal)', 'Udara (pnp/flight)'];

  chartLoadFactorInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Hari Normal (Feb)', data: modas.map(m => lf[m].normal_ratio), backgroundColor: 'rgba(148, 163, 184, 0.4)' },
        { label: 'Puncak Lebaran (Maret)', data: modas.map(m => lf[m].peak_ratio), backgroundColor: 'rgba(56, 189, 248, 0.8)' },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } },
        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw} rasio keterisian` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#64748b' } }
      }
    }
  });
}

// -------------------------------------------------------------
// TAB 5: TOP HUBS
// -------------------------------------------------------------
function filterTopHubs(m, btn) {
  currentHubModa = m;
  document.querySelectorAll('#tab-top-hubs .filter-group:first-child .btn-preset').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHubsTable();
}

function toggleHubPeriod(p) {
  currentHubPeriod = p;
  document.getElementById('btn-hub-peak').classList.toggle('active', p === 'peak');
  document.getElementById('btn-hub-ytd').classList.toggle('active', p === 'ytd');
  document.getElementById('hub-table-title').innerText = p === 'peak' ? 'Daftar Simpul Terpadat Periode Puncak Lebaran (18-29 Maret 2026)' : 'Daftar Simpul Terpadat Sepanjang Tahun 2026 (YTD)';
  renderHubsTable();
}

function onSearchHub(term) {
  currentSearchTerm = term.toLowerCase().trim();
  renderHubsTable();
}

function renderHubsTable() {
  const tbody = document.querySelector('#table-hubs tbody');
  tbody.innerHTML = '';
  
  const src = currentHubPeriod === 'peak' ? DATA.top_hubs_peak : DATA.top_hubs_ytd;
  let list = [];
  
  if (currentHubModa === 'ALL') {
    Object.keys(src).forEach(m => {
      src[m].forEach(item => list.push({ ...item, moda: m }));
    });
    list.sort((a, b) => b.pnp - a.pnp);
    list = list.slice(0, 30); // Top 30 Multimoda
  } else {
    list = (src[currentHubModa] || []).map(item => ({ ...item, moda: currentHubModa }));
  }

  // Filter search
  if (currentSearchTerm) {
    list = list.filter(item => 
      (item.nama_prasarana || '').toLowerCase().includes(currentSearchTerm) ||
      (item.provinsi || '').toLowerCase().includes(currentSearchTerm)
    );
  }

  const maxPnp = list.length > 0 ? list[0].pnp : 1;
  const pillClasses = { UDARA: 'udara', KA: 'ka', BUS: 'bus', ASDP: 'asdp', LAUT: 'laut' };

  if (list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:24px; color:var(--text-muted);">Tidak ditemukan simpul transportasi yang cocok dengan pencarian.</td></tr>';
    return;
  }

  list.forEach((item, idx) => {
    const tr = document.createElement('tr');
    const pct = ((item.pnp / maxPnp) * 100).toFixed(0);
    const mColor = COLORS[item.moda] || '#38bdf8';
    
    tr.innerHTML = `
      <td style="font-weight:800; color: ${idx < 3 ? 'var(--amber)' : 'var(--text-muted)'};">#${idx + 1}</td>
      <td><strong>${item.nama_prasarana}</strong></td>
      <td><span class="pill ${pillClasses[item.moda]}">${item.moda}</span></td>
      <td style="color:var(--text-muted);">${item.provinsi || '-'}</td>
      <td style="font-weight:700; color:#fff;">${numFmt(item.pnp)} pnp</td>
      <td style="color:var(--text-muted);">${numFmt(item.arm)} armada</td>
      <td>
        <div class="bar-inline">
          <div class="bar-track">
            <div class="bar-fill" style="width: ${pct}%; background: ${mColor};"></div>
          </div>
          <span style="font-size:11px; color:var(--text-dim); min-width:32px;">${pct}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// -------------------------------------------------------------
// INIT
// -------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {
  // Set KPI Values from DATA.meta
  document.getElementById('kpi-total-pnp').innerText = numFmt(DATA.meta.total_passengers_ytd);
  document.getElementById('kpi-total-arm').innerText = numFmt(DATA.meta.total_armada_ytd);
  
  renderTimelineChart();
  renderMonthlyChart();
  renderDOWChart();
});
</script>
</body>
</html>
"""

with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"File Dashboard Mobilitas berhasil diperbarui: {out_html}")
print(f"Ukuran file: {os.path.getsize(out_html) / 1024:.1f} KB")
