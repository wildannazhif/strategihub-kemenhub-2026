import os
import json
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
output_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Siasati_2026_Updated_Audit.html"

print("Memuat dataset multimoda terbaru...")
df = pd.read_csv(raw_csv, low_memory=False)

# 1. Summary Per Moda
stats_modes = []
for m in ['BUS', 'ASDP', 'UDARA', 'LAUT', 'KA']:
    sub = df[df['moda'] == m]
    p_dat = int(sub['penumpang_datang'].sum())
    p_brg = int(sub['penumpang_berangkat'].sum())
    tot_p = int(sub['total_penumpang'].sum())
    tot_a = int(sub['total_armada'].sum())
    
    anom_status = ""
    if m == 'KA':
        anom_status = "Diperbaiki: Berangkat disinkronkan ke Datang (1:1)"
    elif m == 'ASDP':
        anom_status = "Anomali Baru: Datang di-0-kan, Berangkat dipusatkan"
    elif m == 'BUS':
        anom_status = "Tipe 0 diubah ke C, Null Island (0,0) masih ada"
    else:
        anom_status = "Normal (Kargo tanpa penumpang minor)"
        
    stats_modes.append({
        'moda': m,
        'rows': len(sub),
        'tot_p': tot_p,
        'p_dat': p_dat,
        'p_brg': p_brg,
        'tot_a': tot_a,
        'rasio': round(tot_p / tot_a, 2) if tot_a > 0 else 0,
        'status_anomali': anom_status
    })

# 2. Daily Summary
daily_df = df.groupby(['tanggal', 'moda']).agg(
    p_dat=('penumpang_datang', 'sum'),
    p_brg=('penumpang_berangkat', 'sum'),
    tot_p=('total_penumpang', 'sum'),
    tot_a=('total_armada', 'sum')
).reset_index()
daily_json = daily_df.to_dict(orient='records')

# 3. Map Nodes (Include valid and anomalies)
nodes_df = df.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
    lat=('lat', 'first'),
    lon=('lon', 'first'),
    tipe=('tipe', 'first'),
    tot_p=('total_penumpang', 'sum'),
    tot_a=('total_armada', 'sum'),
    p_dat=('penumpang_datang', 'sum'),
    p_brg=('penumpang_berangkat', 'sum')
).reset_index()

map_nodes = []
null_island_count = 0
swapped_count = 0
missing_count = 0

for _, r in nodes_df.iterrows():
    lat_val = pd.to_numeric(r['lat'], errors='coerce')
    lon_val = pd.to_numeric(r['lon'], errors='coerce')
    
    if pd.isna(lat_val) or pd.isna(lon_val):
        missing_count += 1
        continue
    
    is_null_island = (lat_val == 0 and lon_val == 0)
    is_swapped = (lat_val > 50 and lon_val < 0)
    
    if is_null_island: null_island_count += 1
    if is_swapped: swapped_count += 1
    
    map_nodes.append({
        'm': r['moda'],
        'nama': str(r['nama_prasarana']),
        'p': str(r['provinsi']),
        'lat': float(lat_val),
        'lon': float(lon_val),
        'tipe': str(r['tipe']) if pd.notna(r['tipe']) else '-',
        'tot_p': int(r['tot_p']),
        'tot_a': int(r['tot_a']),
        'p_dat': int(r['p_dat']),
        'p_brg': int(r['p_brg']),
        'is_null_island': is_null_island,
        'is_swapped': is_swapped
    })

# 4. Anomaly Inspection Lists
# A. Null island terminals
bus_null = df[(df['moda'] == 'BUS') & (pd.to_numeric(df['lat'], errors='coerce') == 0)][['id_prasarana', 'nama_prasarana', 'provinsi', 'lat', 'lon', 'tipe']].drop_duplicates().to_dict(orient='records')
# B. Swapped Maluku ports
asdp_swapped = df[(df['moda'] == 'ASDP') & (pd.to_numeric(df['lat'], errors='coerce') > 50)][['id_prasarana', 'nama_prasarana', 'provinsi', 'lat', 'lon', 'total_penumpang']].drop_duplicates().to_dict(orient='records')
# C. ASDP zero arrival sample
asdp_zero_arrival = df[(df['moda'] == 'ASDP') & (df['armada_berangkat'] > 10)][['tanggal', 'nama_prasarana', 'armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat']].head(6).to_dict(orient='records')
# D. KA Sync Sample
ka_sync_sample = df[(df['moda'] == 'KA') & (df['penumpang_datang'] > 100)][['tanggal', 'id_prasarana', 'nama_prasarana', 'armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat']].head(6).to_dict(orient='records')
# E. Former Tipe 0 now C
former_tipe0 = df[df['id_prasarana'].isin(['B1787', 'B1460', 'B280', 'B348', 'B1496', 'B1618'])][['tanggal', 'id_prasarana', 'nama_prasarana', 'provinsi', 'tipe', 'total_armada', 'total_penumpang']].drop_duplicates(subset=['id_prasarana']).to_dict(orient='records')

html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Audit & Analitik SIASATI 2026 (Update 28 Sep 2026)</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #090d16;
  --bg2: #0f172a;
  --card: #141f36;
  --card2: #1b2a4a;
  --line: #263859;
  --txt: #f1f5f9;
  --mut: #94a3b8;
  --mut2: #64748b;
  --acc: #38bdf8;
  --ok: #22c55e;
  --warn: #f59e0b;
  --bad: #ef4444;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: radial-gradient(1300px 600px at 70% -10%, #162a4d 0%, var(--bg) 65%);
  color: var(--txt);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
}}
.wrap {{ max-width: 1560px; margin: 0 auto; padding: 18px 24px 60px; }}

header {{
  display: flex; flex-wrap: wrap; align-items: center; gap: 16px;
  padding: 12px 0 18px; border-bottom: 1px solid var(--line); margin-bottom: 16px;
}}
.logo {{
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; box-shadow: 0 4px 16px rgba(14,165,233,.4);
}}
.title-box h1 {{ font-size: 22px; font-weight: 800; }}
.title-box .sub {{ color: var(--mut); font-size: 13px; margin-top: 3px; }}
.badges {{ margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }}
.bdg {{
  background: rgba(56,189,248,.12); border: 1px solid rgba(56,189,248,.35);
  color: var(--acc); border-radius: 999px; padding: 5px 14px; font-size: 12px; font-weight: 700;
}}
.bdg.ok {{ background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.35); color: var(--ok); }}
.bdg.warn {{ background: rgba(245,158,11,.15); border-color: rgba(245,158,11,.4); color: var(--warn); }}

/* Changelog Alert Cards */
.changelog-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px; margin-bottom: 20px;
}}
.ch-card {{
  border-radius: 12px; padding: 14px 16px; font-size: 12.5px; line-height: 1.55;
  border-left: 4px solid;
}}
.ch-card.ok {{ background: rgba(34,197,94,.08); border-left-color: var(--ok); }}
.ch-card.warn {{ background: rgba(245,158,11,.08); border-left-color: var(--warn); }}
.ch-card.bad {{ background: rgba(239,68,68,.08); border-left-color: var(--bad); }}
.ch-card h4 {{ font-size: 13.5px; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
.ch-card.ok h4 {{ color: #4ade80; }}
.ch-card.warn h4 {{ color: #fbbf24; }}
.ch-card.bad h4 {{ color: #f87171; }}

/* Nav */
nav {{
  display: flex; gap: 8px; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 6px; margin-bottom: 20px;
  position: sticky; top: 10px; z-index: 500;
  box-shadow: 0 10px 30px rgba(0,0,0,.6);
}}
nav button {{
  border: 0; background: transparent; color: var(--mut);
  font: 600 13px 'Segoe UI', sans-serif;
  padding: 10px 16px; border-radius: 10px; cursor: pointer; transition: .15s;
  display: flex; align-items: center; gap: 6px;
}}
nav button:hover {{ color: var(--txt); background: rgba(56,189,248,.1); }}
nav button.on {{
  background: linear-gradient(135deg, rgba(14,165,233,.25), rgba(99,102,241,.25));
  color: #fff; box-shadow: inset 0 0 0 1px rgba(56,189,248,.5);
}}

section.tab {{ display: none; }}
section.tab.on {{ display: block; animation: fadeIn .2s ease; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}

/* KPIs */
.kpis {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin-bottom: 20px;
}}
.kpi {{
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 16px; padding: 18px 20px;
  position: relative; overflow: hidden;
}}
.kpi::after {{ content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; background: var(--acc); }}
.kpi .lbl {{ font-size: 11.5px; color: var(--mut); font-weight: 700; text-transform: uppercase; letter-spacing: .5px; }}
.kpi .val {{ font-size: 26px; font-weight: 800; margin-top: 5px; }}
.kpi .ftr {{ font-size: 11.5px; color: var(--mut2); margin-top: 4px; }}

/* Grid & Cards */
.grid {{ display: grid; gap: 16px; }}
.two {{ grid-template-columns: 1fr 1fr; }}
@media(max-width: 1080px) {{ .two {{ grid-template-columns: 1fr; }} }}

.card {{
  background: linear-gradient(160deg, var(--card), var(--card2));
  border: 1px solid var(--line); border-radius: 16px; padding: 20px;
  box-shadow: 0 6px 24px rgba(0,0,0,.25);
}}
.card h3 {{ font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }}
.card .subh {{ font-size: 12.5px; color: var(--mut); margin-top: 3px; font-weight: 400; }}
.chart-box {{ position: relative; margin-top: 14px; min-height: 280px; }}

/* Tables */
table.tbl {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 12px; }}
table.tbl th {{
  color: var(--mut); text-align: right; font-weight: 600; padding: 10px 12px;
  border-bottom: 1px solid var(--line); background: rgba(15,23,42,.6);
}}
table.tbl th:first-child, table.tbl td:first-child {{ text-align: left; }}
table.tbl td {{ padding: 9px 12px; border-bottom: 1px solid rgba(38,56,89,.4); text-align: right; }}
table.tbl tr:hover td {{ background: rgba(56,189,248,.06); }}
.scroll {{ max-height: 480px; overflow: auto; border-radius: 10px; margin-top: 8px; }}

/* Map */
#map {{ height: 600px; border-radius: 14px; border: 1px solid var(--line); }}
.map-nav {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; align-items: center; }}
.btn-nav {{
  background: var(--bg2); border: 1px solid var(--line); color: var(--txt);
  padding: 6px 14px; border-radius: 8px; font: 600 12px 'Segoe UI'; cursor: pointer; transition: .15s;
}}
.btn-nav:hover {{ border-color: var(--acc); color: #fff; }}
.btn-nav.alert {{ background: rgba(239,68,68,.2); border-color: #ef4444; color: #fca5a5; }}
.btn-nav.warn {{ background: rgba(245,158,11,.2); border-color: #f59e0b; color: #fcd34d; }}

/* Tags */
.tag {{ display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }}
.tag.ok {{ background: rgba(34,197,94,.2); color: #4ade80; border: 1px solid rgba(34,197,94,.4); }}
.tag.warn {{ background: rgba(245,158,11,.2); color: #fcd34d; border: 1px solid rgba(245,158,11,.4); }}
.tag.bad {{ background: rgba(239,68,68,.2); color: #f87171; border: 1px solid rgba(239,68,68,.4); }}
</style>
</head>
<body>

<div class="wrap">
  <!-- Header -->
  <header>
    <div class="logo">🔄</div>
    <div class="title-box">
      <h1>Dashboard Audit & Analitik SIASATI 2026 (Update 28 September 2026)</h1>
      <div class="sub">Pelacakan Status Anomali Pasca-Pembaruan API: Bus, ASDP, Udara, Laut, dan Kereta Api</div>
    </div>
    <div class="badges">
      <div class="bdg ok">● Terupdate: 28 Sep 2026</div>
      <div class="bdg">302.089 Baris Data</div>
      <div class="bdg warn">Audit Anomali Terkini</div>
    </div>
  </header>

  <!-- Changelog Alert Grid -->
  <div class="changelog-grid">
    <div class="ch-card ok">
      <h4>✅ 1. Anomali KA Diperbaiki Sistem</h4>
      Kolom <code>penumpang_berangkat</code> KA yang sebelumnya rusak (berisi trip kereta max 139) telah disinkronkan menjadi identik 100% dengan <code>penumpang_datang</code>. Total penumpang KA terkoreksi menjadi <b>83,55 Juta</b>.
    </div>
    <div class="ch-card ok">
      <h4>✅ 2. Bus Tipe '0' Telah Dihapus</h4>
      Seluruh 11 baris terminal yang sebelumnya ber-tipe "0" (BSD, Depok, Pinrang, Wonosobo, Wonosari, Kasipute) telah <b>direklasifikasi menjadi Tipe 'C'</b>. Tipe "0" kini 0 baris.
    </div>
    <div class="ch-card warn">
      <h4>⚠️ 3. Anomali Baru pada ASDP</h4>
      Server Siasati mengosongkan kolom <code>penumpang_datang</code> dan <code>kapal_datang</code> (menjadi 0 semua), dan memusatkan 100% pergerakan ferry ke kolom <code>berangkat</code> (43,79 Juta pnp).
    </div>
    <div class="ch-card bad">
      <h4>❌ 4. Anomali Spasial Masih Tersisa</h4>
      Sebanyak <b>1.198 baris di Null Island (0,0)</b> di Samudera Atlantik dan <b>14 baris koordinat tertukar di Maluku</b> belum diperbaiki oleh tim database Kemenhub.
    </div>
  </div>

  <!-- Nav -->
  <nav>
    <button class="on" onclick="openTab('tab1', this)">📊 Status Anomali & Rekapitulasi</button>
    <button onclick="openTab('tab2', this)">🗺️ Peta Spasial Terupdate (Null Island & Kutub)</button>
    <button onclick="openTab('tab3', this)">📈 Dinamika Deret Waktu (s.d. 28 Sep 2026)</button>
    <button onclick="openTab('tab4', this)">🔍 Galeri Bukti Rekaman Terkini</button>
  </nav>

  <!-- Top KPIs -->
  <div class="kpis">
    <div class="kpi">
      <div class="lbl">Total Penumpang Nasional</div>
      <div class="val" style="color:var(--acc);">371,3 Juta</div>
      <div class="ftr">Data terupdate s.d. 28 Sep 2026</div>
    </div>
    <div class="kpi">
      <div class="lbl">Total Pergerakan Armada</div>
      <div class="val" style="color:var(--ok);">10,01 Juta</div>
      <div class="ftr">Trip bus, kapal, pesawat, KA</div>
    </div>
    <div class="kpi">
      <div class="lbl">Status Kolom KA Berangkat</div>
      <div class="val" style="color:var(--ok);">Sinkron 100%</div>
      <div class="ftr">Disamakan dengan kedatangan</div>
    </div>
    <div class="kpi">
      <div class="lbl">Status Terminal Tipe 0</div>
      <div class="val" style="color:var(--ok);">0 Baris</div>
      <div class="ftr">Telah direvisi menjadi Tipe C</div>
    </div>
    <div class="kpi">
      <div class="lbl">Simpul di Null Island (0,0)</div>
      <div class="val" style="color:var(--bad);">23 Simpul</div>
      <div class="ftr">Masih mengambang di Afrika</div>
    </div>
  </div>

  <!-- TAB 1: REKAPITULASI & STATUS -->
  <section id="tab1" class="tab on">
    <div class="grid two">
      <div class="card">
        <h3><span>🥧</span> Pangsa Pasar Penumpang Terupdate (Modal Split)</h3>
        <div class="subh">Komposisi 5 moda setelah perbaikan kolom Kereta Api (Jan–28 Sep 2026)</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartModalSplit"></canvas>
        </div>
      </div>
      <div class="card">
        <h3><span>📊</span> Perbandingan Volume Penumpang Datang vs Berangkat</h3>
        <div class="subh">Perhatikan ASDP: Kedatangan 0 karena seluruh data dipindahkan ke keberangkatan</div>
        <div class="chart-box" style="height:320px;">
          <canvas id="chartDatBrg"></canvas>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h3><span>📋</span> Tabel Status Komparasi Anomali Sebelum vs Sesudah Pembaruan Data</h3>
      <div class="subh">Matriks pelacakan kualitas data per moda transportasi</div>
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
              <th>Status Anomali di Data Terbaru</th>
            </tr>
          </thead>
          <tbody id="tblStatusBody"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TAB 2: PETA SPASIAL -->
  <section id="tab2" class="tab">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
        <div>
          <h3><span>🗺️</span> Peta Sebaran Prasarana Terupdate (1.300+ Simpul)</h3>
          <div class="subh">Dilengkapi penanda khusus untuk memeriksa anomali geocoding yang masih tersisa</div>
        </div>
        <div class="map-nav">
          <button class="btn-nav" onclick="zoomTo('ID')">🇮🇩 Fokus Indonesia</button>
          <button class="btn-nav alert" onclick="zoomTo('NULL')">🌍 Lihat Null Island (0,0) di Samudera Atlantik / Afrika</button>
          <button class="btn-nav warn" onclick="zoomTo('ARCTIC')">❄️ Lihat Maluku Tertukar di Siberia (128° Lat)</button>
        </div>
      </div>

      <div id="map"></div>
    </div>
  </section>

  <!-- TAB 3: TREN HARIAN TERBARU -->
  <section id="tab3" class="tab">
    <div class="card">
      <h3><span>📈</span> Tren Deret Waktu Harian Antarmoda (1 Januari s/d 28 September 2026)</h3>
      <div class="subh">Perhatikan garis KA (Ungu) yang kini telah normal mengikuti garis kedatangan</div>
      <div class="chart-box" style="height:380px;">
        <canvas id="chartDailyTrend"></canvas>
      </div>
    </div>
  </section>

  <!-- TAB 4: BUKTI REKAMAN TERKINI -->
  <section id="tab4" class="tab">
    <div class="grid two">
      <div class="card">
        <h3><span>🚆</span> Bukti Data KA yang Telah Disinkronkan</h3>
        <div class="subh">Nilai penumpang berangkat kini disamakan persis dengan penumpang datang</div>
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
            <tbody id="tblKaSync"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3><span>⛴️</span> Bukti Anomali Baru ASDP: Kedatangan di-0-kan</h3>
        <div class="subh">Seluruh arus kedatangan kapal dan penumpang diisi 0 oleh server</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>Tanggal</th>
                <th>Pelabuhan</th>
                <th>Kapal Datang</th>
                <th>Pnp Datang</th>
                <th>Kapal Brgkt</th>
                <th>Pnp Brgkt</th>
              </tr>
            </thead>
            <tbody id="tblAsdpZero"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="grid two" style="margin-top:16px;">
      <div class="card">
        <h3><span>🚌</span> Bukti Mantan Terminal Tipe '0' yang Direklasifikasi ke 'C'</h3>
        <div class="subh">Status BSD, Depok, Pinrang, dll. kini telah resmi menjadi Tipe C</div>
        <div class="scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>Terminal</th>
                <th>Provinsi</th>
                <th>Tipe Baru</th>
                <th>Total Armada</th>
                <th>Total Penumpang</th>
              </tr>
            </thead>
            <tbody id="tblFormerTipe0"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3><span>📍</span> Bukti Terminal yang Masih Terjebak di Null Island (0, 0)</h3>
        <div class="subh">Terminal yang koordinatnya belum diperbaiki oleh tim Kemenhub</div>
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
            <tbody id="tblBusNull"></tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

</div>

<script>
const statsModes = {json.dumps(stats_modes, ensure_ascii=False)};
const dailyData = {json.dumps(daily_json, ensure_ascii=False)};
const mapNodes = {json.dumps(map_nodes, ensure_ascii=False)};
const kaSync = {json.dumps(ka_sync_sample, ensure_ascii=False)};
const asdpZero = {json.dumps(asdp_zero_arrival, ensure_ascii=False)};
const formerTipe0 = {json.dumps(former_tipe0, ensure_ascii=False)};
const busNull = {json.dumps(bus_null, ensure_ascii=False)};

const colors = {{
  'UDARA': '#0284c7',
  'ASDP': '#10b981',
  'BUS': '#f59e0b',
  'LAUT': '#0f766e',
  'KA': '#8b5cf6'
}};

function openTab(tabId, btn) {{
  document.querySelectorAll('section.tab').forEach(s => s.classList.remove('on'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('on'));
  document.getElementById(tabId).classList.add('on');
  btn.classList.add('on');
  if (tabId === 'tab2') {{
    setTimeout(() => {{ if (window.myMap) window.myMap.invalidateSize(); }}, 200);
  }}
}}

function renderStatusTable() {{
  const tbody = document.getElementById('tblStatusBody');
  let html = '';
  statsModes.forEach(d => {{
    let tagClass = 'ok';
    if (d.status_anomali.includes('Baru')) tagClass = 'warn';
    if (d.status_anomali.includes('Null Island')) tagClass = 'bad';
    html += `<tr>
      <td><b>${{d.moda}}</b></td>
      <td>${{d.rows.toLocaleString('id-ID')}}</td>
      <td><b>${{d.tot_p.toLocaleString('id-ID')}}</b></td>
      <td>${{d.p_dat.toLocaleString('id-ID')}}</td>
      <td>${{d.p_brg.toLocaleString('id-ID')}}</td>
      <td>${{d.tot_a.toLocaleString('id-ID')}}</td>
      <td><span class="tag ${{tagClass}}">${{d.status_anomali}}</span></td>
    </tr>`;
  }});
  tbody.innerHTML = html;
}}

function renderEvidence() {{
  // KA Sync
  let htmlKa = '';
  kaSync.forEach(d => {{
    htmlKa += `<tr>
      <td>${{d.tanggal}}</td>
      <td><b>${{d.id_prasarana}}</b></td>
      <td>${{d.nama_prasarana}}</td>
      <td>${{d.armada_datang}}</td>
      <td style="color:#38bdf8; font-weight:bold;">${{d.penumpang_datang}}</td>
      <td>${{d.armada_berangkat}}</td>
      <td style="color:#4ade80; font-weight:bold;">${{d.penumpang_berangkat}}</td>
    </tr>`;
  }});
  document.getElementById('tblKaSync').innerHTML = htmlKa;

  // ASDP Zero
  let htmlAsdp = '';
  asdpZero.forEach(d => {{
    htmlAsdp += `<tr>
      <td>${{d.tanggal}}</td>
      <td><b>${{d.nama_prasarana}}</b></td>
      <td style="color:#f87171;">${{d.armada_datang}}</td>
      <td style="color:#f87171; font-weight:bold;">${{d.penumpang_datang}}</td>
      <td>${{d.armada_berangkat}}</td>
      <td style="color:#38bdf8; font-weight:bold;">${{d.penumpang_berangkat.toLocaleString('id-ID')}}</td>
    </tr>`;
  }});
  document.getElementById('tblAsdpZero').innerHTML = htmlAsdp;

  // Former Tipe 0
  let htmlTipe = '';
  formerTipe0.forEach(d => {{
    htmlTipe += `<tr>
      <td><b>${{d.id_prasarana}}</b></td>
      <td>${{d.nama_prasarana}}</td>
      <td>${{d.provinsi}}</td>
      <td><span class="tag ok">Tipe "${{d.tipe}}" (Baru)</span></td>
      <td>${{d.total_armada}}</td>
      <td>${{d.total_penumpang}}</td>
    </tr>`;
  }});
  document.getElementById('tblFormerTipe0').innerHTML = htmlTipe;

  // Bus Null
  let htmlNull = '';
  busNull.forEach(d => {{
    htmlNull += `<tr>
      <td><b>${{d.id_prasarana}}</b></td>
      <td>${{d.nama_prasarana}}</td>
      <td>${{d.provinsi}}</td>
      <td style="color:#ef4444; font-weight:bold;">${{d.lat}}</td>
      <td style="color:#ef4444; font-weight:bold;">${{d.lon}}</td>
      <td>${{d.tipe}}</td>
    </tr>`;
  }});
  document.getElementById('tblBusNull').innerHTML = htmlNull;
}}

function initCharts() {{
  // Donut Modal Split
  new Chart(document.getElementById('chartModalSplit'), {{
    type: 'doughnut',
    data: {{
      labels: statsModes.map(d => d.moda),
      datasets: [{{
        data: statsModes.map(d => d.tot_p),
        backgroundColor: statsModes.map(d => colors[d.moda]),
        borderWidth: 2, borderColor: '#141f36'
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#cbd5e1' }} }} }}
    }}
  }});

  // Datang vs Berangkat Bar
  new Chart(document.getElementById('chartDatBrg'), {{
    type: 'bar',
    data: {{
      labels: statsModes.map(d => d.moda),
      datasets: [
        {{ label: 'Penumpang Datang (Juta)', data: statsModes.map(d => (d.p_dat / 1e6).toFixed(2)), backgroundColor: '#38bdf8', borderRadius: 6 }},
        {{ label: 'Penumpang Berangkat (Juta)', data: statsModes.map(d => (d.p_brg / 1e6).toFixed(2)), backgroundColor: '#f97316', borderRadius: 6 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      scales: {{
        x: {{ ticks: {{ color: '#cbd5e1', font: {{ weight: 'bold' }} }} }},
        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.06)' }}, title: {{ display: true, text: 'Juta Penumpang', color: '#94a3b8' }} }}
      }}
    }}
  }});

  // Daily Trend Line
  const dates = [...new Set(dailyData.map(d => d.tanggal))].sort();
  const modesList = ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA'];
  const dailyDatasets = modesList.map(m => {{
    const mapM = {{}};
    dailyData.filter(d => d.moda === m).forEach(d => {{ mapM[d.tanggal] = d.tot_p / 1e3; }});
    return {{
      label: m,
      data: dates.map(dt => mapM[dt] || 0),
      borderColor: colors[m],
      borderWidth: 1.8,
      pointRadius: 0
    }};
  }});

  new Chart(document.getElementById('chartDailyTrend'), {{
    type: 'line',
    data: {{ labels: dates, datasets: dailyDatasets }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      scales: {{
        x: {{ ticks: {{ color: '#94a3b8', maxTicksLimit: 14 }} }},
        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.06)' }}, title: {{ display: true, text: 'Ribu Penumpang / Hari', color: '#94a3b8' }} }}
      }}
    }}
  }});
}}

// Leaflet Map
let myMap = null;
function initMap() {{
  myMap = L.map('map').setView([-2.5, 118], 5);
  window.myMap = myMap;

  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18
  }}).addTo(myMap);

  mapNodes.forEach(n => {{
    let col = colors[n.m] || '#38bdf8';
    let rad = 5;
    let stroke = '#ffffff';

    if (n.is_null_island) {{
      col = '#ef4444';
      rad = 9;
      stroke = '#fef08a';
    }} else if (n.is_swapped) {{
      col = '#f59e0b';
      rad = 9;
    }}

    const circle = L.circleMarker([n.lat, n.lon], {{
      radius: rad,
      fillColor: col,
      color: stroke,
      weight: n.is_null_island || n.is_swapped ? 2.5 : 1,
      opacity: 1,
      fillOpacity: 0.8
    }});

    circle.bindPopup(`
      <div style="font-family:sans-serif; min-width:200px; color:#0f172a;">
        <div style="font-size:11px; font-weight:bold; color:${{col}};">${{n.m}} • Tipe ${{n.tipe}}</div>
        <div style="font-size:14px; font-weight:800; margin:2px 0;">${{n.nama}}</div>
        <div style="font-size:11.5px; color:#475569; margin-bottom:6px;">Provinsi: <b>${{n.p}}</b></div>
        <div style="background:#f1f5f9; padding:6px 8px; border-radius:6px; font-size:11.5px;">
          <div>Total Penumpang: <b>${{n.tot_p.toLocaleString('id-ID')}}</b></div>
          <div>Total Armada: <b>${{n.tot_a.toLocaleString('id-ID')}}</b></div>
          <div>Lat/Lon: ${{n.lat}}, ${{n.lon}}</div>
        </div>
      </div>
    `);
    circle.addTo(myMap);
  }});
}}

function zoomTo(target) {{
  if (target === 'ID') myMap.flyTo([-2.5, 118], 5);
  else if (target === 'NULL') myMap.flyTo([0, 0], 6);
  else if (target === 'ARCTIC') myMap.flyTo([75, -3.6], 4);
}}

window.addEventListener('DOMContentLoaded', () => {{
  renderStatusTable();
  renderEvidence();
  initCharts();
  initMap();
}});
</script>
</body>
</html>
"""

print(f"Menulis file Dashboard Audit Terupdate ke: {output_html}...")
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SELESAI] Dashboard Audit Terupdate berhasil dibuat! Ukuran: {os.path.getsize(output_html)/1024:.1f} KB")
