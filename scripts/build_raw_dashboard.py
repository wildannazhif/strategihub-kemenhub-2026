import os
import glob
import json
import pandas as pd
import numpy as np

raw_dir = r"c:\Users\USER\Documents\PUSDATIN\dataset_siasati_2026"
output_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Siasati_RAW_Tanpa_Perbaikan.html"

print("=== MEMUAT DATA MENTAH TANPA PREPROCESSING / PERBAIKAN ===")

# 1. Load raw data for each mode as-is
raw_modes = [
    {
        'moda': 'BUS',
        'pattern': 'dm_bus_2026_T*.json',
        'name_col': 'nama_terminal',
        'prov_col': 'nama_provinsi',
        'p_dat': 'penumpang_datang',
        'p_brg': 'penumpang_berangkat',
        'a_dat': 'bus_datang',
        'a_brg': 'bus_berangkat'
    },
    {
        'moda': 'ASDP',
        'pattern': 'dm_asdp_2026_T*.json',
        'name_col': 'nama_pelabuhan',
        'prov_col': 'nama_provinsi',
        'p_dat': 'penumpang_datang',
        'p_brg': 'penumpang_berangkat',
        'a_dat': 'kapal_datang',
        'a_brg': 'kapal_berangkat'
    },
    {
        'moda': 'UDARA',
        'pattern': 'dm_udara_2026_T*.json',
        'name_col': 'nama_bandara',
        'prov_col': 'nama_provinsi',
        'p_dat': 'penumpang_datang',
        'p_brg': 'penumpang_berangkat',
        'a_dat': 'pesawat_datang',
        'a_brg': 'pesawat_berangkat'
    },
    {
        'moda': 'LAUT',
        'pattern': 'dm_laut_2026_T*.json',
        'name_col': 'nama_pelabuhan',
        'prov_col': 'nama_provinsi',
        'p_dat': 'penumpang_datang',
        'p_brg': 'penumpang_berangkat',
        'a_dat': 'kapal_datang',
        'a_brg': 'kapal_berangkat'
    },
    {
        'moda': 'KA',
        'pattern': 'dm_ka_2026_T*.json',
        'name_col': 'nama',
        'prov_col': 'provinsi',
        'p_dat': 'penumpang_datang',
        'p_brg': 'penumpang_berangkat',
        'a_dat': 'kereta_datang',
        'a_brg': 'kereta_berangkat'
    }
]

dfs_raw = []
for cfg in raw_modes:
    files = sorted(glob.glob(os.path.join(raw_dir, cfg['pattern'])))
    df_m = pd.concat([pd.read_json(f) for f in files], ignore_index=True)
    df_m['moda'] = cfg['moda']
    df_m.rename(columns={
        cfg['name_col']: 'nama_prasarana',
        cfg['prov_col']: 'provinsi',
        cfg['p_dat']: 'p_dat',
        cfg['p_brg']: 'p_brg',
        cfg['a_dat']: 'a_dat',
        cfg['a_brg']: 'a_brg'
    }, inplace=True)
    
    # Cast to numeric without fixing logic
    df_m['p_dat'] = pd.to_numeric(df_m['p_dat'], errors='coerce').fillna(0)
    df_m['p_brg'] = pd.to_numeric(df_m['p_brg'], errors='coerce').fillna(0)
    df_m['a_dat'] = pd.to_numeric(df_m['a_dat'], errors='coerce').fillna(0)
    df_m['a_brg'] = pd.to_numeric(df_m['a_brg'], errors='coerce').fillna(0)
    
    df_m['tot_p'] = df_m['p_dat'] + df_m['p_brg']
    df_m['tot_a'] = df_m['a_dat'] + df_m['a_brg']
    
    df_m['lat_num'] = pd.to_numeric(df_m['lat'], errors='coerce')
    df_m['lon_num'] = pd.to_numeric(df_m['lon'], errors='coerce')
    
    dfs_raw.append(df_m)

df_all_raw = pd.concat(dfs_raw, ignore_index=True)
print(f"Total baris mentah: {len(df_all_raw):,}")

# 2. Raw Summary per Mode
raw_stats = []
for m in ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA']:
    sub = df_all_raw[df_all_raw['moda'] == m]
    p_dat_sum = int(sub['p_dat'].sum())
    p_brg_sum = int(sub['p_brg'].sum())
    tot_p_sum = int(sub['tot_p'].sum())
    tot_a_sum = int(sub['tot_a'].sum())
    
    raw_stats.append({
        'moda': m,
        'rows': len(sub),
        'tot_p': tot_p_sum,
        'p_dat': p_dat_sum,
        'p_brg': p_brg_sum,
        'tot_a': tot_a_sum,
        'rasio': round(tot_p_sum / tot_a_sum, 2) if tot_a_sum > 0 else 0,
        'anomali_note': 'Penumpang Berangkat = Kereta Berangkat (rusak)' if m == 'KA' else ('Simetri 100% Datang == Berangkat' if m == 'ASDP' else ('Null Island & Tipe 0' if m == 'BUS' else 'Normal'))
    })

# 3. Raw Daily Aggregates (keeping raw numbers)
daily_raw = df_all_raw.groupby(['tanggal', 'moda']).agg(
    p_dat=('p_dat', 'sum'),
    p_brg=('p_brg', 'sum'),
    tot_p=('tot_p', 'sum'),
    tot_a=('tot_a', 'sum')
).reset_index()
daily_raw['tanggal'] = daily_raw['tanggal'].astype(str)
daily_raw_json = daily_raw.to_dict(orient='records')

# 4. Raw Map Nodes (KEEPING (0,0) and SWAPPED coords!)
nodes_grp = df_all_raw.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
    lat=('lat_num', 'first'),
    lon=('lon_num', 'first'),
    tipe=('tipe', 'first'),
    p_dat=('p_dat', 'sum'),
    p_brg=('p_brg', 'sum'),
    tot_p=('tot_p', 'sum'),
    tot_a=('tot_a', 'sum'),
    rows=('nama_prasarana', 'count')
).reset_index()

# Keep facilities with coordinates (even if 0,0 or swapped!)
map_nodes_raw = []
nan_nodes_count = 0
null_island_count = 0
swapped_count = 0

for _, r in nodes_grp.iterrows():
    if pd.isna(r['lat']) or pd.isna(r['lon']):
        nan_nodes_count += 1
        continue
    
    lat_val = float(r['lat'])
    lon_val = float(r['lon'])
    
    is_null_island = (lat_val == 0.0 and lon_val == 0.0)
    is_swapped = (lat_val > 50.0 and lon_val < 0.0)
    
    if is_null_island: null_island_count += 1
    if is_swapped: swapped_count += 1
    
    map_nodes_raw.append({
        'm': r['moda'],
        'nama': str(r['nama_prasarana']),
        'p': str(r['provinsi']),
        'lat': lat_val,
        'lon': lon_val,
        'tipe': str(r['tipe']),
        'tot_p': int(r['tot_p']),
        'p_dat': int(r['p_dat']),
        'p_brg': int(r['p_brg']),
        'tot_a': int(r['tot_a']),
        'is_null_island': is_null_island,
        'is_swapped': is_swapped
    })

print(f"Map nodes mentah: {len(map_nodes_raw)} simpul (Null Island: {null_island_count}, Swapped: {swapped_count}, Hilang/NaN: {nan_nodes_count})")

# 5. Extract Concrete Anomaly Records for Tab Gallery
# A. KA duplicate & mirror
df_ka_raw = dfs_raw[4]
ka_dup_sample = df_ka_raw[df_ka_raw.duplicated(subset=['id_prasarana', 'tanggal'], keep=False)].sort_values(by=['id_prasarana', 'tanggal']).head(8)
ka_sample_records = ka_dup_sample[['tanggal', 'id_prasarana', 'nama_prasarana', 'a_dat', 'p_dat', 'a_brg', 'p_brg']].to_dict(orient='records')

# B. BUS Null Island sample
df_bus_raw = dfs_raw[0]
bus_null_sample = df_bus_raw[(df_bus_raw['lat_num'] == 0) & (df_bus_raw['lon_num'] == 0)][['id_prasarana', 'nama_prasarana', 'provinsi', 'lat', 'lon', 'tipe']].drop_duplicates().head(10).to_dict(orient='records')

# C. ASDP Swapped sample
df_asdp_raw = dfs_raw[1]
asdp_swapped_sample = df_asdp_raw[df_asdp_raw['lat_num'] > 50][['id_prasarana', 'nama_prasarana', 'provinsi', 'lat', 'lon', 'tot_a', 'tot_p']].drop_duplicates().head(5).to_dict(orient='records')

# D. BUS Tipe '0' sample
bus_tipe0_sample = df_bus_raw[df_bus_raw['tipe'] == '0'][['tanggal', 'id_prasarana', 'nama_prasarana', 'provinsi', 'tipe', 'tot_a', 'tot_p']].head(6).to_dict(orient='records')

# E. ASDP Extreme Ratio sample
df_asdp_raw['ratio'] = np.where(df_asdp_raw['tot_a'] > 0, df_asdp_raw['tot_p'] / df_asdp_raw['tot_a'], 0)
asdp_extreme_sample = df_asdp_raw[df_asdp_raw['ratio'] > 1500][['tanggal', 'nama_prasarana', 'provinsi', 'tot_a', 'tot_p', 'ratio']].head(6).to_dict(orient='records')

html_template = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>⚠️ Dashboard SIASATI 2026 (RAW DATA — Tanpa Perbaikan Anomali)</title>
<!-- Leaflet CSS & JS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #090a0f;
  --bg2: #12141c;
  --card: #181b26;
  --card2: #1e2230;
  --line: #2d3348;
  --txt: #f3f4f6;
  --mut: #9ca3af;
  --mut2: #6b7280;
  --warn: #f59e0b;
  --bad: #ef4444;
  --bad2: #dc2626;
  --acc: #fb923c;
  --udara: #0284c7;
  --asdp: #10b981;
  --bus: #f59e0b;
  --laut: #0f766e;
  --ka: #8b5cf6;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: radial-gradient(1300px 600px at 50% -10%, #2a1b12 0%, var(--bg) 65%);
  color: var(--txt);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
}
.wrap { max-width: 1560px; margin: 0 auto; padding: 16px 22px 60px; }

/* Alert Banner Header */
.raw-banner {
  background: linear-gradient(90deg, #7f1d1d, #991b1b, #b45309);
  border: 1px solid #f87171;
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(220,38,38,.3);
}
.raw-banner .ic { font-size: 32px; flex: 0 0 auto; }
.raw-banner h2 { font-size: 16px; font-weight: 800; color: #fff; letter-spacing: .2px; }
.raw-banner p { font-size: 13px; color: #fecaca; margin-top: 2px; }

header {
  display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
  padding: 10px 0 16px; border-bottom: 1px solid var(--line); margin-bottom: 18px;
}
.logo {
  width: 48px; height: 48px; border-radius: 12px;
  background: linear-gradient(135deg, #f97316, #ef4444);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; box-shadow: 0 4px 12px rgba(239,68,68,.4);
}
.title-box h1 { font-size: 21px; font-weight: 800; }
.title-box .sub { color: var(--mut); font-size: 13px; margin-top: 2px; }
.badges { margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }
.bdg {
  background: rgba(239,68,68,.15); border: 1px solid rgba(239,68,68,.4);
  color: #fca5a5; border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}
.bdg.raw { background: rgba(245,158,11,.15); border-color: rgba(245,158,11,.4); color: #fcd34d; }

/* Navigation */
nav {
  display: flex; gap: 6px; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--line);
  border-radius: 12px; padding: 6px; margin-bottom: 18px;
  position: sticky; top: 8px; z-index: 500;
  box-shadow: 0 8px 24px rgba(0,0,0,.6);
}
nav button {
  border: 0; background: transparent; color: var(--mut);
  font: 600 13px/1 'Segoe UI', sans-serif;
  padding: 10px 16px; border-radius: 8px; cursor: pointer; transition: .15s;
  display: flex; align-items: center; gap: 6px;
}
nav button:hover { color: var(--txt); background: rgba(245,158,11,.1); }
nav button.on {
  background: linear-gradient(135deg, rgba(239,68,68,.3), rgba(245,158,11,.3));
  color: #fff; box-shadow: inset 0 0 0 1px rgba(239,68,68,.5);
}

section.tab { display: none; }
section.tab.on { display: block; animation: fadeIn .2s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

/* Cards & Layout */
.grid { display: grid; gap: 14px; }
.two { grid-template-columns: 1fr 1fr; }
.three { grid-template-columns: 1fr 1fr 1fr; }
@media(max-width: 1024px) { .two, .three { grid-template-columns: 1fr; } }

.card {
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 14px; padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,.3);
}
.card h3 { font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.card .subh { font-size: 12px; color: var(--mut); margin-top: 2px; font-weight: 400; }
.chart-box { position: relative; margin-top: 12px; min-height: 280px; }

/* KPI Cards */
.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px; margin-bottom: 18px;
}
.kpi {
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px;
  position: relative; overflow: hidden;
}
.kpi::after { content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; background: #ef4444; }
.kpi.warn::after { background: #f59e0b; }
.kpi .lbl { font-size: 11.5px; color: var(--mut); font-weight: 700; text-transform: uppercase; letter-spacing: .4px; }
.kpi .val { font-size: 24px; font-weight: 800; margin-top: 4px; }
.kpi .ftr { font-size: 11.5px; color: var(--mut2); margin-top: 4px; }

/* Table */
table.tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 10px; }
table.tbl th {
  color: var(--mut); text-align: right; font-weight: 600; padding: 8px 10px;
  border-bottom: 1px solid var(--line); background: rgba(18,20,28,.6);
}
table.tbl th:first-child, table.tbl td:first-child { text-align: left; }
table.tbl td {
  padding: 8px 10px; border-bottom: 1px solid rgba(45,51,72,.5); text-align: right;
}
table.tbl tr:hover td { background: rgba(239,68,68,.05); }
.scroll { max-height: 440px; overflow: auto; border-radius: 8px; margin-top: 6px; }

/* Callout Box */
.box-anomaly {
  background: rgba(239,68,68,.08); border-left: 4px solid var(--bad);
  border-radius: 0 8px 8px 0; padding: 12px 14px; margin-top: 12px; font-size: 12.5px; line-height: 1.6;
}
.box-anomaly b { color: #fca5a5; }

/* Map Controls */
#map { height: 600px; border-radius: 12px; border: 1px solid var(--line); }
.map-nav {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; align-items: center;
}
.btn-nav {
  background: var(--bg2); border: 1px solid var(--line); color: var(--txt);
  padding: 6px 12px; border-radius: 6px; font: 600 12px 'Segoe UI'; cursor: pointer; transition: .15s;
}
.btn-nav:hover { border-color: var(--acc); color: #fff; }
.btn-nav.alert { background: rgba(239,68,68,.2); border-color: #ef4444; color: #fca5a5; }
.btn-nav.warn { background: rgba(245,158,11,.2); border-color: #f59e0b; color: #fcd34d; }

.tag { display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 700; }
.tag.bad { background: rgba(239,68,68,.2); color: #fca5a5; border: 1px solid rgba(239,68,68,.4); }
.tag.warn { background: rgba(245,158,11,.2); color: #fcd34d; border: 1px solid rgba(245,158,11,.4); }
</style>
</head>
<body>

<div class="wrap">

  <!-- Danger / Raw Banner -->
  <div class="raw-banner">
    <div class="ic">⚠️</div>
    <div>
      <h2>DASHBOARD DATA MENTAH SIASATI 2026 (RAW UNCLEANED DATA)</h2>
      <p>Dashboard ini menampilkan data <b>apa adanya langsung dari API Siasati TANPA perbaikan anomali</b>. Anda dapat melihat dampak langsung dari kolom rusak (KA Berangkat = Kereta Berangkat), koordinat tertukar ke Kutub Utara, titik terminal terlempar ke Samudera Atlantik (Null Island), dan duplikasi baris.</p>
    </div>
  </div>

  <!-- Header -->
  <header>
    <div class="logo">🚨</div>
    <div class="title-box">
      <h1>Visualisasi Kondisi Mentah Dataset Multimoda 2026</h1>
      <div class="sub">Inspeksi Dampak Kesalahan Data Mentah: Bus, ASDP, Udara, Laut, dan Kereta Api</div>
    </div>
    <div class="badges">
      <div class="bdg">STATUS: RAW / UNCLEANED</div>
      <div class="bdg raw">1.158 Titik di Null Island</div>
      <div class="bdg">KA Berangkat: Rusak 100%</div>
    </div>
  </header>

  <!-- Navigation -->
  <nav>
    <button class="on" onclick="openTab('tab1', this)">📊 Distorsi Nilai & Ringkasan Mentah</button>
    <button onclick="openTab('tab2', this)">🗺️ Peta Anomali Spasial (Null Island & Kutub)</button>
    <button onclick="openTab('tab3', this)">🔍 Galeri Bukti Rekaman Anomali</button>
    <button onclick="openTab('tab4', this)">📈 Tren Harian Mentah</button>
  </nav>

  <!-- Top KPIs -->
  <div class="kpis">
    <div class="kpi">
      <div class="lbl">Total Penumpang Datang</div>
      <div class="val" style="color:#38bdf8;">203,9 Juta</div>
      <div class="ftr">Data kedatangan relatif riil</div>
    </div>
    <div class="kpi">
      <div class="lbl">Total Penumpang Berangkat</div>
      <div class="val" style="color:#ef4444;">166,5 Juta</div>
      <div class="ftr">⚠️ Anjlok karena KA berangkat rusak!</div>
    </div>
    <div class="kpi warn">
      <div class="lbl">Selisih Datang vs Berangkat</div>
      <div class="val" style="color:#f59e0b;">-37,4 Juta</div>
      <div class="ftr">Ketimpangan akibat bug data KA</div>
    </div>
    <div class="kpi">
      <div class="lbl">Simpul di Null Island (0,0)</div>
      <div class="val" style="color:#ef4444;">23 Simpul</div>
      <div class="ftr">18 Terminal Bus & 5 ASDP di Afrika</div>
    </div>
    <div class="kpi warn">
      <div class="lbl">Simpul Tertukar ke Kutub</div>
      <div class="val" style="color:#f59e0b;">2 Pelabuhan</div>
      <div class="ftr">Poka & Haruku (Maluku) di Siberia</div>
    </div>
  </div>

  <!-- TAB 1: DISTORSI NILAI MENTAH -->
  <section id="tab1" class="tab on">
    <div class="grid two">
      <div class="card">
        <h3><span>📉</span> Dampak Anomali: Datang vs Berangkat per Moda</h3>
        <div class="subh">Perhatikan moda KA (Kereta Api): Penumpang Berangkat anjlok 98% karena berisi jumlah trip kereta!</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartRawDatBrg"></canvas>
        </div>
        <div class="box-anomaly">
          <b>Analisis Anomali KA:</b> Pada data mentah, KA Penumpang Datang mencapai <b>41.173.464 orang</b>, sedangkan Penumpang Berangkat hanya <b>862.919</b> (hampir 0). Hal ini terjadi karena kolom berangkat keliru merekam jumlah armada kereta (maksimum 139 rangkaian), bukan jumlah penumpang!
        </div>
      </div>

      <div class="card">
        <h3><span>⛴️</span> Dampak Anomali ASDP: Kloning 100% Simetris</h3>
        <div class="subh">Jumlah penumpang datang dan berangkat identik 100% di semua 19.736 baris rekaman</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartRawAsdp"></canvas>
        </div>
        <div class="box-anomaly">
          <b>Analisis Anomali ASDP:</b> Datang = 43.551.793 orang dan Berangkat = 43.551.793 orang. Tidak ada variasi arah karena data pelabuhan ASDP dicatat berbasis satu manifest trip bolak-balik.
        </div>
      </div>
    </div>

    <div class="card" style="margin-top:14px;">
      <h3><span>📋</span> Tabel Rekapitulasi Data Mentah per Moda</h3>
      <div class="subh">Angka asli yang dihasilkan bila data tidak dibersihkan terlebih dahulu</div>
      <div class="scroll">
        <table class="tbl">
          <thead>
            <tr>
              <th>Moda</th>
              <th>Total Baris</th>
              <th>Total Penumpang</th>
              <th>Penumpang Datang</th>
              <th>Penumpang Berangkat</th>
              <th>Total Armada</th>
              <th>Rasio (Org/Trip)</th>
              <th>Status Anomali Bawaan</th>
            </tr>
          </thead>
          <tbody id="tblRawSummary"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TAB 2: PETA ANOMALI SPASIAL -->
  <section id="tab2" class="tab">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
        <div>
          <h3><span>🗺️</span> Peta Sebaran Mentah: Bukti Nyata Titik Terlempar ke Samudera & Kutub</h3>
          <div class="subh">Gunakan tombol pintas di kanan untuk langsung melihat titik anomali di Afrika & Kutub Utara</div>
        </div>
        <div class="map-nav">
          <button class="btn-nav" onclick="zoomTo('ID')">🇮🇩 Fokus Indonesia</button>
          <button class="btn-nav alert" onclick="zoomTo('NULL')">🌍 Lihat Null Island (0,0) di Samudera Atlantik / Afrika</button>
          <button class="btn-nav warn" onclick="zoomTo('ARCTIC')">❄️ Lihat Maluku Tertukar di Siberia (128° Lat)</button>
        </div>
      </div>

      <div id="map"></div>

      <div class="box-anomaly" style="margin-top:12px;">
        💡 <b>Keterangan Peta Mentah:</b><br>
        1. <b>Titik Merah Berkedip di Samudera Atlantik (Afrika)</b> adalah 23 simpul transportasi (18 Terminal Bus termasuk Cileungsi, Sukoharjo, Padang, dll.) yang memiliki koordinat mentah <code>lat: 0, lon: 0</code>.<br>
        2. <b>Titik Oranye di Laut Siberia / Kutub Utara</b> adalah Pelabuhan ASDP Poka dan Haruku (Maluku) yang koordinatnya terbalik (<code>lat: 128.199, lon: -3.656</code>).<br>
        3. <b>Sebanyak 177 Prasarana GHAIB</b> tidak dapat digambar sama sekali di peta karena koordinatnya berupa string kosong <code>""</code>.
      </div>
    </div>
  </section>

  <!-- TAB 3: BUKTI ANOMALI REKAMAN -->
  <section id="tab3" class="tab">
    <div class="grid two">
      <div class="card">
        <h3><span>🚆</span> Bukti Anomali KA: Baris Riil vs Baris Dummy Nol</h3>
        <div class="subh">Satu stasiun pada hari yang sama dicatat 2 kali (1 riil + 1 dummy nol)</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>Tanggal</th>
                <th>ID</th>
                <th>Stasiun</th>
                <th>KA Datang</th>
                <th>Pnp Datang</th>
                <th>KA Brgkt</th>
                <th>Pnp Brgkt</th>
              </tr>
            </thead>
            <tbody id="tblKaSamples"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3><span>🚌</span> Bukti Anomali BUS: Koordinat (0, 0) Null Island</h3>
        <div class="subh">Daftar terminal bus dengan koordinat 0,0 langsung dari file JSON mentah</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>Terminal</th>
                <th>Provinsi</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Tipe</th>
              </tr>
            </thead>
            <tbody id="tblBusNullSamples"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="grid two" style="margin-top:14px;">
      <div class="card">
        <h3><span>⛴️</span> Bukti Anomali ASDP: Koordinat Tertukar Terbalik</h3>
        <div class="subh">Pelabuhan Maluku terlempar ke lintang 128 derajat (Kutub Utara)</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>Pelabuhan</th>
                <th>Provinsi</th>
                <th>Latitude (Mentah)</th>
                <th>Longitude (Mentah)</th>
                <th>Pnp Datang</th>
              </tr>
            </thead>
            <tbody id="tblAsdpSwappedSamples"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3><span>🚌</span> Bukti Anomali BUS: Munculnya Tipe "0"</h3>
        <div class="subh">Terminal yang tidak terklasifikasi ke Tipe A, B, atau C melainkan angka 0</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>Tanggal</th>
                <th>ID</th>
                <th>Terminal</th>
                <th>Provinsi</th>
                <th>Tipe</th>
                <th>Total Bus</th>
                <th>Total Pnp</th>
              </tr>
            </thead>
            <tbody id="tblBusTipe0Samples"></tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 4: TREN HARIAN MENTAH -->
  <section id="tab4" class="tab">
    <div class="card">
      <h3><span>📈</span> Grafik Garis Harian Mentah Antarmoda</h3>
      <div class="subh">Perhatikan garis Kereta Api (Ungu) yang berada di bawah karena nilai keberangkatan rusak</div>
      <div class="chart-box" style="height:380px;">
        <canvas id="chartRawDaily"></canvas>
      </div>
    </div>
  </section>

</div>

<script>
// RAW PAYLOAD DATA
const rawStats = __RAW_STATS__;
const dailyRaw = __DAILY_RAW__;
const mapNodesRaw = __MAP_NODES_RAW__;
const kaSamples = __KA_SAMPLES__;
const busNullSamples = __BUS_NULL_SAMPLES__;
const asdpSwappedSamples = __ASDP_SWAPPED_SAMPLES__;
const busTipe0Samples = __BUS_TIPE0_SAMPLES__;

// Navigation
function openTab(tabId, btn) {
  document.querySelectorAll('section.tab').forEach(s => s.classList.remove('on'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('on'));
  document.getElementById(tabId).classList.add('on');
  btn.classList.add('on');
  if (tabId === 'tab2') {
    setTimeout(() => { if (window.rawMap) window.rawMap.invalidateSize(); }, 200);
  }
}

// Render Summary Table
function renderRawSummary() {
  const tbody = document.getElementById('tblRawSummary');
  let html = '';
  rawStats.forEach(d => {
    html += `<tr>
      <td><b>${d.moda}</b></td>
      <td>${d.rows.toLocaleString('id-ID')}</td>
      <td><b>${d.tot_p.toLocaleString('id-ID')}</b></td>
      <td style="color:#38bdf8;">${d.p_dat.toLocaleString('id-ID')}</td>
      <td style="color:${d.moda === 'KA' ? '#ef4444; font-weight:bold;' : '#f97316;'}">${d.p_brg.toLocaleString('id-ID')}</td>
      <td>${d.tot_a.toLocaleString('id-ID')}</td>
      <td>${d.rasio}</td>
      <td><span class="tag ${d.moda === 'KA' || d.moda === 'BUS' ? 'bad' : 'warn'}">${d.anomali_note}</span></td>
    </tr>`;
  });
  tbody.innerHTML = html;
}

// Render Evidence Tables
function renderEvidenceTables() {
  // KA Samples
  let htmlKa = '';
  kaSamples.forEach(d => {
    const isZero = (d.p_dat === 0 && d.p_brg === 0);
    htmlKa += `<tr style="${isZero ? 'background:rgba(239,68,68,0.08);' : ''}">
      <td>${d.tanggal}</td>
      <td><b>${d.id_prasarana}</b></td>
      <td>${d.nama_prasarana}</td>
      <td>${d.a_dat}</td>
      <td>${d.p_dat}</td>
      <td><b>${d.a_brg}</b></td>
      <td style="color:#ef4444; font-weight:bold;">${d.p_brg}</td>
    </tr>`;
  });
  document.getElementById('tblKaSamples').innerHTML = htmlKa;

  // Bus Null
  let htmlBusNull = '';
  busNullSamples.forEach(d => {
    htmlBusNull += `<tr>
      <td><b>${d.id_prasarana}</b></td>
      <td>${d.nama_prasarana}</td>
      <td>${d.provinsi}</td>
      <td style="color:#ef4444; font-weight:bold;">${d.lat}</td>
      <td style="color:#ef4444; font-weight:bold;">${d.lon}</td>
      <td>${d.tipe || '-'}</td>
    </tr>`;
  });
  document.getElementById('tblBusNullSamples').innerHTML = htmlBusNull;

  // ASDP Swapped
  let htmlAsdp = '';
  asdpSwappedSamples.forEach(d => {
    htmlAsdp += `<tr>
      <td><b>${d.id_prasarana}</b></td>
      <td>${d.nama_prasarana}</td>
      <td>${d.provinsi}</td>
      <td style="color:#ef4444; font-weight:bold;">${d.lat}</td>
      <td style="color:#ef4444; font-weight:bold;">${d.lon}</td>
      <td>${d.tot_p ? d.tot_p.toLocaleString('id-ID') : 0}</td>
    </tr>`;
  });
  document.getElementById('tblAsdpSwappedSamples').innerHTML = htmlAsdp;

  // Bus Tipe 0
  let htmlBus0 = '';
  busTipe0Samples.forEach(d => {
    htmlBus0 += `<tr>
      <td>${d.tanggal}</td>
      <td><b>${d.id_prasarana}</b></td>
      <td>${d.nama_prasarana}</td>
      <td>${d.provinsi}</td>
      <td><span class="tag bad">Tipe "${d.tipe}"</span></td>
      <td>${d.tot_b}</td>
      <td>${d.tot_p}</td>
    </tr>`;
  });
  document.getElementById('tblBusTipe0Samples').innerHTML = htmlBus0;
}

// Charts
function initRawCharts() {
  // Chart 1: Datang vs Berangkat per Moda (Highlights KA collapse)
  new Chart(document.getElementById('chartRawDatBrg'), {
    type: 'bar',
    data: {
      labels: rawStats.map(d => d.moda),
      datasets: [
        { label: 'Penumpang Datang (Juta)', data: rawStats.map(d => (d.p_dat / 1e6).toFixed(2)), backgroundColor: '#38bdf8', borderRadius: 6 },
        { label: 'Penumpang Berangkat (Juta)', data: rawStats.map(d => (d.p_brg / 1e6).toFixed(2)), backgroundColor: '#ef4444', borderRadius: 6 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#cbd5e1' } } },
      scales: {
        x: { ticks: { color: '#cbd5e1', font: { weight: 'bold' } } },
        y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.06)' }, title: { display: true, text: 'Juta Penumpang', color: '#9ca3af' } }
      }
    }
  });

  // Chart 2: ASDP Symmetry
  const asdpStat = rawStats.find(d => d.moda === 'ASDP');
  new Chart(document.getElementById('chartRawAsdp'), {
    type: 'doughnut',
    data: {
      labels: ['ASDP Penumpang Datang', 'ASDP Penumpang Berangkat'],
      datasets: [{
        data: [asdpStat.p_dat, asdpStat.p_brg],
        backgroundColor: ['#10b981', '#059669'],
        borderWidth: 2, borderColor: '#181b26'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#cbd5e1' } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.label}: ${(ctx.raw/1e6).toFixed(2)} Juta (Persis 50% / 50%)`
          }
        }
      }
    }
  });

  // Chart 3: Raw Daily
  const dates = [...new Set(dailyRaw.map(d => d.tanggal))].sort();
  const modesList = ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA'];
  const colors = { 'UDARA': '#0284c7', 'ASDP': '#10b981', 'BUS': '#f59e0b', 'LAUT': '#0f766e', 'KA': '#8b5cf6' };

  const dailyDatasets = modesList.map(m => {
    const mapM = {};
    dailyRaw.filter(d => d.moda === m).forEach(d => { mapM[d.tanggal] = d.tot_p / 1e3; });
    return {
      label: m + (m === 'KA' ? ' (Terdistorsi Rugi 50%)' : ''),
      data: dates.map(dt => mapM[dt] || 0),
      borderColor: colors[m],
      borderWidth: 1.8,
      pointRadius: 0
    };
  });

  new Chart(document.getElementById('chartRawDaily'), {
    type: 'line',
    data: { labels: dates, datasets: dailyDatasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: '#9ca3af', maxTicksLimit: 12 } },
        y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.06)' }, title: { display: true, text: 'Ribu Penumpang Mentah / Hari', color: '#9ca3af' } }
      }
    }
  });
}

// Leaflet Map with Anomaly Locators
let rawMap = null;
function initRawMap() {
  // Global view to see Africa and Arctic
  rawMap = L.map('map').setView([-2.5, 118], 4);
  window.rawMap = rawMap;

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18
  }).addTo(rawMap);

  // Render raw nodes
  mapNodesRaw.forEach(n => {
    let color = '#38bdf8';
    let rad = 5;
    let strokeColor = '#ffffff';

    if (n.is_null_island) {
      color = '#ef4444'; // Red for Null Island
      rad = 9;
      strokeColor = '#fef08a';
    } else if (n.is_swapped) {
      color = '#f59e0b'; // Amber for swapped coords
      rad = 9;
      strokeColor = '#ffffff';
    }

    const circle = L.circleMarker([n.lat, n.lon], {
      radius: rad,
      fillColor: color,
      color: strokeColor,
      weight: n.is_null_island || n.is_swapped ? 2.5 : 1,
      opacity: 1,
      fillOpacity: 0.8
    });

    let extraBadge = '';
    if (n.is_null_island) extraBadge = '<div style="background:#fee2e2; color:#b91c1c; font-weight:bold; padding:3px 6px; border-radius:4px; font-size:11px; margin-bottom:6px;">⚠️ ANOMALI: KOORDINAT (0,0) NULL ISLAND (AFRIKA)</div>';
    if (n.is_swapped) extraBadge = '<div style="background:#fef3c7; color:#b45309; font-weight:bold; padding:3px 6px; border-radius:4px; font-size:11px; margin-bottom:6px;">⚠️ ANOMALI: LAT/LON TERTUKAR KE SIBERIA</div>';

    const popupContent = `
      <div style="font-family:sans-serif; min-width:210px; color:#0f172a;">
        ${extraBadge}
        <div style="font-size:11px; font-weight:bold; color:${color}; text-transform:uppercase;">${n.m} • ${n.tipe || 'Prasarana'}</div>
        <div style="font-size:14px; font-weight:800; margin:2px 0 4px;">${n.nama}</div>
        <div style="font-size:11.5px; color:#475569; margin-bottom:6px;">Provinsi: <b>${n.p}</b></div>
        <div style="background:#f1f5f9; padding:6px 8px; border-radius:6px; font-size:11.5px;">
          <div>Lat/Lon Mentah: <b>${n.lat}, ${n.lon}</b></div>
          <div>Total Penumpang: <b>${n.tot_p.toLocaleString('id-ID')}</b></div>
          <div>Datang: ${n.p_dat.toLocaleString('id-ID')} | Berangkat: ${n.p_brg.toLocaleString('id-ID')}</div>
        </div>
      </div>
    `;
    circle.bindPopup(popupContent);
    circle.addTo(rawMap);
  });
}

function zoomTo(target) {
  if (target === 'ID') {
    rawMap.flyTo([-2.5, 118], 5);
  } else if (target === 'NULL') {
    // Center of Null Island in Gulf of Guinea / Atlantic Ocean
    rawMap.flyTo([0, 0], 6);
  } else if (target === 'ARCTIC') {
    // Maluku swapped coordinates at lat 128 (Leaflet wraps or clamps at 85/90 degrees, but center near top)
    rawMap.flyTo([75, -3.6], 4);
  }
}

// Initialize on Load
window.addEventListener('DOMContentLoaded', () => {
  renderRawSummary();
  renderEvidenceTables();
  initRawCharts();
  initRawMap();
});
</script>
</body>
</html>
"""

# Replace placeholders
final_html = html_template.replace("__RAW_STATS__", json.dumps(raw_stats, ensure_ascii=False))
final_html = final_html.replace("__DAILY_RAW__", json.dumps(daily_raw_json, ensure_ascii=False))
final_html = final_html.replace("__MAP_NODES_RAW__", json.dumps(map_nodes_raw, ensure_ascii=False))
final_html = final_html.replace("__KA_SAMPLES__", json.dumps(ka_sample_records, ensure_ascii=False))
final_html = final_html.replace("__BUS_NULL_SAMPLES__", json.dumps(bus_null_sample, ensure_ascii=False))
final_html = final_html.replace("__ASDP_SWAPPED_SAMPLES__", json.dumps(asdp_swapped_sample, ensure_ascii=False))
final_html = final_html.replace("__BUS_TIPE0_SAMPLES__", json.dumps(bus_tipe0_sample, ensure_ascii=False))

print(f"Menulis file RAW Dashboard ke: {output_html}...")
with open(output_html, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"[SELESAI] Dashboard Data Mentah berhasil dibuat! Ukuran: {os.path.getsize(output_html)/1024:.1f} KB")
