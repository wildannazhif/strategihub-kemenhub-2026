"""
build_production_dashboard_sidebar.py
Integrates the complete production-grade UI design with:
1. Collapsible left sidebar navigation.
2. Updated dataset from StrategiHub (209,885 clean rows, 371,840,258 passengers, 10,030,995 armada, 272 days).
3. Exact deduplication (drop identical duplicates) and sum aggregation of differing duplicates.
4. Empty coordinates kept empty per user instruction.
5. Dedicated Leaflet GIS Spasial Map Tab in the sidebar with interactive controls, node inspector, and responsive auto-resize.
"""

import json
import os

BUNDLE_PATH = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
OUTPUT_HTML = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html"

def generate_dashboard():
    with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    json_data_str = json.dumps(data)

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StrategiHub Multimoda 2026 • Pusat Data dan Informasi Kemenhub</title>

<!-- Standard Institutional Typography -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Tailwind CSS Play CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Leaflet GIS CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />

<script>
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        fontFamily: {{
          sans: ["'Plus Jakarta Sans'", "system-ui", "-apple-system", "sans-serif"],
          mono: ["'JetBrains Mono'", "monospace"],
        }},
        colors: {{
          kemenhub: {{
            50: "#f0f5fa",
            100: "#e0ebf5",
            200: "#c7dcee",
            600: "#1a5287",
            700: "#15426d",
            800: "#113557",
            900: "#0c243c",
          }},
        }}
      }}
    }}
  }};
</script>

<style>
  body {{
    font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  }}
  .num-mono {{
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
  }}
  ::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
  }}
  ::-webkit-scrollbar-track {{
    background: transparent;
  }}
  ::-webkit-scrollbar-thumb {{
    background: #cbd5e1;
    border-radius: 3px;
  }}
  .dark ::-webkit-scrollbar-thumb {{
    background: #334155;
  }}
  /* Custom Leaflet Styling */
  .leaflet-popup-content-wrapper {{
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
    padding: 0;
    overflow: hidden;
  }}
  .dark .leaflet-popup-content-wrapper {{
    background-color: #0f172a;
    color: #f8fafc;
    border-color: #334155;
  }}
  .leaflet-popup-content {{
    margin: 0;
    line-height: 1.4;
  }}
  .leaflet-popup-tip {{
    background: white;
  }}
  .dark .leaflet-popup-tip {{
    background: #0f172a;
  }}
  #spatial-map-card:fullscreen {{
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    background: #0f172a !important;
  }}
  #spatial-map-card:fullscreen #spatialMapCanvas {{
    height: 100vh !important;
    min-height: 100vh !important;
    border-radius: 0 !important;
  }}
</style>
</head>

<body class="bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100 min-h-screen flex flex-col font-sans transition-colors duration-200">

  <!-- ============================================================= -->
  <!-- COLLAPSIBLE SIDEBAR NAVIGATION (w-64)                         -->
  <!-- ============================================================= -->
  <aside id="sidebar" class="fixed top-0 bottom-0 left-0 z-50 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-transform duration-250 ease-in-out shadow-sm">
    
    <!-- Sidebar Header -->
    <div class="h-16 px-4 flex items-center justify-between border-b border-slate-200 dark:border-slate-800">
      <div class="flex items-center gap-2.5 min-w-0">
        <div class="w-8 h-8 rounded bg-kemenhub-800 dark:bg-blue-600 flex items-center justify-center font-bold text-white text-xs tracking-wider shrink-0">
          ST
        </div>
        <div class="truncate">
          <div class="text-xs font-bold uppercase tracking-tight text-slate-900 dark:text-white truncate">StrategiHub Analytics</div>
          <div class="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">PUSDATIN KEMENHUB</div>
        </div>
      </div>

      <button onclick="toggleSidebar()" class="p-1 rounded-md text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Sembunyikan Sidebar">
        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
    </div>

    <!-- Navigation Modules List -->
    <div class="p-3 space-y-5 overflow-y-auto flex-1">
      
      <div>
        <p class="px-2.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Modul Operasional</p>
        <nav class="space-y-1">
          <button onclick="switchTab('tab-timeline', '1. Kronologi Harian (272 Hari)', this)" class="nav-btn active w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-semibold text-kemenhub-800 dark:text-blue-400 bg-kemenhub-50 dark:bg-blue-950/40 border border-slate-200 dark:border-blue-900/50 transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-sky-600 shrink-0"></span>
            <span class="truncate">1. Kronologi Harian (272H)</span>
          </button>

          <button onclick="switchTab('tab-lebaran', '2. Puncak Lebaran 2026 (Mudik & Balik)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0"></span>
            <span class="truncate">2. Puncak Lebaran 2026</span>
          </button>

          <button onclick="switchTab('tab-modal-share', '3. Pangsa Pasar Antar-Moda', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0"></span>
            <span class="truncate">3. Pangsa Pasar Antar-Moda</span>
          </button>

          <button onclick="switchTab('tab-load-factor', '4. Rasio Beban Armada (Load Factor)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>
            <span class="truncate">4. Beban Armada (Rasio)</span>
          </button>

          <button onclick="switchTab('tab-top-hubs', '5. Registri Simpul Transportasi (Top 30)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-purple-600 shrink-0"></span>
            <span class="truncate">5. Registri Simpul (Top 30)</span>
          </button>

          <button onclick="switchTab('tab-matrix', '6. Matriks Rekapitulasi 13 Indikator', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan-600 shrink-0"></span>
            <span class="truncate">6. Matriks 13 Indikator</span>
          </button>

          <!-- TAB 7: LEAFLET SPATIAL MAP -->
          <button onclick="switchTab('tab-spatial-map', '7. Peta Spasial Simpul (Leaflet GIS)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
            <span class="truncate font-semibold text-emerald-700 dark:text-emerald-400">7. Peta Spasial (Leaflet)</span>
          </button>

          <!-- TAB 8: FORECASTING NATARU 2026/2027 -->
          <button onclick="switchTab('tab-forecasting', '8. Proyeksi & Prediksi Nataru 2026/2027', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
            <span class="truncate font-semibold text-indigo-700 dark:text-indigo-400">8. Proyeksi Nataru 2026</span>
          </button>

          <!-- BUTTON BUKA SIDEBAR METODOLOGI KEPADATAN -->
          <button onclick="toggleExplanationSidebar(true)" class="w-full mt-2.5 flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/80 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-all text-left group shadow-xs">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-indigo-600 animate-pulse shrink-0"></span>
              <span class="truncate">📘 Metodologi Kepadatan</span>
            </div>
            <span class="text-[9px] px-1.5 py-0.2 rounded bg-indigo-600 text-white font-mono uppercase">Info</span>
          </button>
        </nav>
      </div>

      <!-- Rentang Waktu Quick Filter -->
      <div>
        <p class="px-2.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Rentang Waktu</p>
        <div class="space-y-1 bg-slate-50 dark:bg-slate-800/60 p-1.5 rounded-md border border-slate-200 dark:border-slate-800">
          <button onclick="setTimelineFilter('all', this)" class="btn-range active w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-semibold text-slate-900 dark:text-white bg-white dark:bg-slate-900 shadow-xs transition-all">
            <span>Sepanjang 2026</span>
            <span class="num-mono text-[10px] text-slate-500">272H</span>
          </button>
          <button onclick="setTimelineFilter('lebaran', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Puncak Lebaran</span>
            <span class="num-mono text-[10px] text-slate-500">27H</span>
          </button>
          <button onclick="setTimelineFilter('libur_sekolah', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Libur Sekolah</span>
            <span class="num-mono text-[10px] text-slate-500">31H</span>
          </button>
          <button onclick="setTimelineFilter('tahun_baru', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Tahun Baru</span>
            <span class="num-mono text-[10px] text-slate-500">15H</span>
          </button>
        </div>
      </div>

    </div>

    <!-- Sidebar Bottom Footer -->
    <div class="p-3 border-t border-slate-200 dark:border-slate-800 space-y-2">
      <button onclick="exportActiveCSV()" class="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-md text-xs font-semibold border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 shadow-xs transition-all">
        <svg class="w-3.5 h-3.5 text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
        <span>Unduh Data CSV</span>
      </button>

      <div class="px-2.5 py-1.5 rounded bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
        <span class="flex items-center gap-1.5 font-semibold text-emerald-700 dark:text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> TERVERIFIKASI
        </span>
        <span class="num-mono font-bold">209.885 ROW</span>
      </div>
    </div>

  </aside>

  <!-- ============================================================= -->
  <!-- SIDEBAR METODOLOGI & STANDAR KEPADATAN SIMPUL (DRAWER)        -->
  <!-- ============================================================= -->
  <div id="backdrop-penjelasan" onclick="toggleExplanationSidebar(false)" class="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 z-50 backdrop-blur-xs opacity-0 pointer-events-none transition-opacity duration-300"></div>

  <aside id="sidebar-penjelasan-kepadatan" class="fixed top-0 bottom-0 right-0 z-50 w-full sm:w-[500px] lg:w-[540px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col transform translate-x-full transition-transform duration-300 ease-in-out">
    
    <!-- Sidebar Header -->
    <div class="h-16 px-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 shrink-0 bg-slate-50/70 dark:bg-slate-800/40">
      <div class="flex items-center gap-2.5 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white text-sm shrink-0 shadow-xs">
          📘
        </div>
        <div class="truncate">
          <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight truncate">
            Metodologi & Kamus Kepadatan Simpul
          </h3>
          <p class="text-[10px] text-slate-500 font-sans truncate">
            Standar Pengukuran Beban, Rasio Armada, & Tolok Ukur Padat Simpul Kemenhub
          </p>
        </div>
      </div>

      <button onclick="toggleExplanationSidebar(false)" class="p-1.5 rounded-md text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors" title="Tutup Sidebar">
        <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>
    </div>

    <!-- Scrollable Body with Clean Typography -->
    <div class="p-5 space-y-5 overflow-y-auto flex-1 text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
      
      <!-- Box 1: Sumber Data Riil StrategiHub -->
      <div class="bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 rounded-lg p-3.5 space-y-2">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
          <h4 class="text-xs font-bold text-indigo-900 dark:text-indigo-200 uppercase tracking-tight">
            1. Dari Mana Sumber Datanya?
          </h4>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Data baseline dihitung langsung dari data mentah StrategiHub Kemenhub 2026: <code class="px-1 py-0.5 rounded bg-white dark:bg-slate-800 text-[10px] font-mono text-indigo-600 dark:text-indigo-300 border border-slate-200 dark:border-slate-700">strategihub_multimoda_2026.csv</code> (18,3 MB, mencakup transaksi harian 1.088 simpul prasarana).
        </p>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Angka baseline penumpang harian (<code class="font-mono">pnpDay</code>) dan armada (<code class="font-mono">armDay</code>) diambil dari <strong>periode Posko Puncak Nasional (17 Hari Arus Mudik & Balik Lebaran 2026: 13–29 Maret 2026, dengan Hari H pada 21 Maret 2026)</strong>, kemudian <strong>dibagi 17 hari</strong> untuk memperoleh rata-rata beban harian puncak riil:
        </p>
        <div class="text-[10px] font-mono bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800 space-y-1">
          <div>• <strong>Pelabuhan Merak:</strong> 1.412.249 pnp / 16 = <strong>88.266 pnp/h</strong> (188 trip kapal/h)</div>
          <div>• <strong>Pelabuhan Bakauheni:</strong> 1.561.165 pnp / 16 = <strong>97.573 pnp/h</strong> (195 trip kapal/h)</div>
          <div>• <strong>Stasiun Pasar Senen:</strong> 889.656 pnp / 16 = <strong>55.604 pnp/h</strong> (149 trip KA/h)</div>
          <div>• <strong>Bandara Ngurah Rai:</strong> 1.656.062 pnp / 16 = <strong>103.504 pnp/h</strong> (641 flight/h)</div>
        </div>
      </div>

      <!-- Box 2: Tahu Padat atau Engga Dari Mana? (3 Tolok Ukur) -->
      <div class="space-y-3.5">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            2. Tahu Simpul Padat atau Tidak Dari Mana? (3 Tolok Ukur)
          </h4>
          <p class="text-[11px] text-slate-500 mt-0.5">Penentuan status beban simpul prasarana menggunakan 3 parameter terintegrasi:</p>
        </div>

        <!-- Tolok Ukur A -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>A. Rasio Beban per Armada (Density / Load Factor)</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">P/A Ratio</span>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-300">
            Rumus: <code class="font-mono font-bold text-slate-900 dark:text-white bg-slate-200 dark:bg-slate-700 px-1 rounded">Rasio Kepadatan = Penumpang Harian / Trip Armada Harian</code>.
            Membandingkan rasio hari normal vs hari puncak:
          </p>
          <ul class="text-[11px] space-y-1.5 list-disc list-inside text-slate-600 dark:text-slate-300">
            <li><strong>Pelabuhan Bakauheni (ASDP):</strong> Hari normal 206 pnp/kapal &rarr; saat puncak melonjak jadi <strong class="text-rose-600 dark:text-rose-400 font-mono">614 pnp/kapal</strong> (naik hampir 3x lipat). Kapal beroperasi desak-desakan dan kantong parkir pelabuhan meluber.</li>
            <li><strong>Stasiun Pasar Senen (KA):</strong> Hari normal 247 pnp/KA &rarr; saat puncak melonjak jadi <strong class="text-rose-600 dark:text-rose-400 font-mono">357 pnp/KA</strong>. Okupansi gerbong mencapai 100% penuh.</li>
            <li><strong>Bandara Ngurah Rai Bali (Udara):</strong> Hari normal 156 pnp/flight &rarr; saat puncak naik jadi <strong class="text-sky-600 dark:text-sky-400 font-mono">165+ pnp/flight</strong>. Dari kapasitas 180 kursi pesawat A320/B737, kursi terisi >92–95%.</li>
          </ul>
        </div>

        <!-- Tolok Ukur B -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2.5">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>B. Persentase Lonjakan Beban vs Hari Normal (Surge %)</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300">Surge %</span>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-300">
            Rumus: <code class="font-mono font-bold text-slate-900 dark:text-white bg-slate-200 dark:bg-slate-700 px-1 rounded">Lonjakan (%) = [(Volume Puncak - Volume Normal) / Volume Normal] &times; 100%</code>.
          </p>
          <div class="overflow-x-auto rounded border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-[11px] font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-600 dark:text-slate-400">
                <tr>
                  <th class="p-1.5">Klasifikasi Beban</th>
                  <th class="p-1.5">Kriteria Lonjakan</th>
                  <th class="p-1.5">Contoh Simpul Riil</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
                <tr>
                  <td class="p-1.5 font-bold text-rose-600 dark:text-rose-400">🔴 Sangat Kritis (95–99%)</td>
                  <td class="p-1.5 font-mono">> +80% s/d +200%</td>
                  <td class="p-1.5">Merak (+92%), Bakauheni (+195%), Senen (+88%)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-amber-600 dark:text-amber-400">🟠 Padat Tinggi (85–94%)</td>
                  <td class="p-1.5 font-mono">+50% s/d +80%</td>
                  <td class="p-1.5">Gambir (+56%), Yogyakarta (+61%), Ngurah Rai</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-yellow-600 dark:text-yellow-400">🟡 Sibuk Terkendali (65–84%)</td>
                  <td class="p-1.5 font-mono">+25% s/d +50%</td>
                  <td class="p-1.5">Purabaya (+49%), Batam Center (+59%)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-emerald-600 dark:text-emerald-400">🟢 Stabil / Normal (<65%)</td>
                  <td class="p-1.5 font-mono">< +25%</td>
                  <td class="p-1.5">Simpul non-wisata / Pelni rute timur</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tolok Ukur C -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
          <div class="font-bold text-slate-900 dark:text-white text-xs">
            C. Batas Kapasitas Fisik Prasarana (Physical Bottlenecks)
          </div>
          <div class="space-y-1.5 text-[11px] text-slate-600 dark:text-slate-300">
            <div>
              • <strong>Pelabuhan ASDP (Merak & Bakauheni):</strong> Batasnya adalah kapasitas kantong parkir buffer zone dermaga dan waktu bongkar muat (port time). Kedatangan kendaraan > kapasitas sandar kapal memicu antrean 4–6 jam meluber ke jalan tol.
            </div>
            <div>
              • <strong>Stasiun Kereta Api (Pasar Senen):</strong> Batasnya adalah kapasitas tempat duduk gerbong KA. Okupansi 100% berarti tiket ludes terjual; penumpang tidak bisa terangkut tanpa pengerahan KLB KA tambahan.
            </div>
            <div>
              • <strong>Bandara Udara (Ngurah Rai DPS):</strong> Batasnya adalah utilisasi slot penerbangan di runway (mencapai 98% kapasitas maksimal) dan ketersediaan parking stand pesawat. Memicu kenaikan harga tiket ke batas TBA.
            </div>
            <div>
              • <strong>Terminal Bus (Purabaya Surabaya):</strong> Batasnya adalah waktu tunggu penumpang di ruang tunggu keberangkatan yang meningkat dari 15 menit ke ~45 menit.
            </div>
          </div>
        </div>
      </div>

      <!-- Box 3: Tabel Komparasi Data Riil Normal vs Puncak -->
      <div class="space-y-2">
        <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
          3. Tabel Komparasi Data Riil StrategiHub (Normal vs Puncak)
        </h4>
        <div class="overflow-x-auto rounded border border-slate-200 dark:border-slate-700">
          <table class="w-full text-left text-[10px] font-mono">
            <thead class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold">
              <tr>
                <th class="p-1.5 font-sans">Simpul Prasarana</th>
                <th class="p-1.5 text-right">Normal (Pnp)</th>
                <th class="p-1.5 text-right">Puncak (Pnp)</th>
                <th class="p-1.5 text-right">Rasio Normal</th>
                <th class="p-1.5 text-right">Rasio Puncak</th>
                <th class="p-1.5 text-center font-sans">Lonjakan</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              <tr>
                <td class="p-1.5 font-sans font-semibold">Pelabuhan Merak</td>
                <td class="p-1.5 text-right">25.218</td>
                <td class="p-1.5 text-right font-bold text-rose-600">48.460</td>
                <td class="p-1.5 text-right">69,0</td>
                <td class="p-1.5 text-right font-bold text-rose-600">106,4</td>
                <td class="p-1.5 text-center font-bold text-rose-600">+92,2%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Pelabuhan Bakauheni</td>
                <td class="p-1.5 text-right">22.988</td>
                <td class="p-1.5 text-right font-bold text-rose-600">67.958</td>
                <td class="p-1.5 text-right">206,0</td>
                <td class="p-1.5 text-right font-bold text-rose-600">614,5</td>
                <td class="p-1.5 text-center font-bold text-rose-600">+195,6%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Stasiun Pasar Senen</td>
                <td class="p-1.5 text-right">16.744</td>
                <td class="p-1.5 text-right font-bold text-rose-600">31.466</td>
                <td class="p-1.5 text-right">247,1</td>
                <td class="p-1.5 text-right font-bold text-rose-600">357,1</td>
                <td class="p-1.5 text-center font-bold text-rose-600">+87,9%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Stasiun Gambir</td>
                <td class="p-1.5 text-right">15.650</td>
                <td class="p-1.5 text-right">24.449</td>
                <td class="p-1.5 text-right">130,6</td>
                <td class="p-1.5 text-right">165,9</td>
                <td class="p-1.5 text-center text-amber-600 font-semibold">+56,2%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Stasiun Yogyakarta</td>
                <td class="p-1.5 text-right">18.959</td>
                <td class="p-1.5 text-right">30.626</td>
                <td class="p-1.5 text-right">92,2</td>
                <td class="p-1.5 text-right">122,3</td>
                <td class="p-1.5 text-center text-amber-600 font-semibold">+61,5%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Bandara Ngurah Rai</td>
                <td class="p-1.5 text-right">58.152</td>
                <td class="p-1.5 text-right">66.151</td>
                <td class="p-1.5 text-right">156,2</td>
                <td class="p-1.5 text-right font-bold text-sky-600">164,3</td>
                <td class="p-1.5 text-center font-semibold text-sky-600">Slot 98%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Bandara Soekarno Hatta</td>
                <td class="p-1.5 text-right">141.847</td>
                <td class="p-1.5 text-right">172.431</td>
                <td class="p-1.5 text-right">143,7</td>
                <td class="p-1.5 text-right">154,9</td>
                <td class="p-1.5 text-center text-sky-600 font-semibold">+21,6%</td>
              </tr>
              <tr>
                <td class="p-1.5 font-sans font-semibold">Terminal Purabaya</td>
                <td class="p-1.5 text-right">21.845</td>
                <td class="p-1.5 text-right">32.595</td>
                <td class="p-1.5 text-right">16,4</td>
                <td class="p-1.5 text-right">20,2</td>
                <td class="p-1.5 text-center text-yellow-600 font-semibold">+49,2%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Box 4: Formula Matematis Simulasi Tambahan Armada -->
      <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
        <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          4. Formula Matematis Simulasi Tambahan Armada
        </h4>
        <div class="space-y-1.5 text-[11px] font-mono text-slate-700 dark:text-slate-300">
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Tambahan Armada (Trip/h)</strong> = Armada_Baseline &times; (Persentase / 100)
          </div>
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Kapasitas Terbuka (Pnp)</strong> = Penumpang_Baseline &times; (Persentase / 100)
          </div>
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Beban Kesibukan Baru (%)</strong> = Beban_Awal / (1 + Persentase / 100)
          </div>
        </div>
      </div>

    </div>

    <!-- Sidebar Footer Actions -->
    <div class="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between gap-3 shrink-0">
      <button onclick="toggleExplanationSidebar(false)" class="px-3 py-1.5 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 transition-colors">
        Tutup
      </button>
      <button onclick="toggleExplanationSidebar(false); switchTab('tab-forecasting', '8. Proyeksi & Prediksi Nataru 2026/2027', document.querySelectorAll('.nav-btn')[7]);" class="px-3.5 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5">
        <span>Buka Simulator Simpul</span>
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
      </button>
    </div>

  </aside>

  <!-- Floating Action Button for Metodologi Sidebar -->
  <button onclick="toggleExplanationSidebar(true)" class="fixed bottom-6 right-6 z-40 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2.5 px-3.5 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2 border border-indigo-400 group">
    <svg class="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
    <span class="hidden sm:inline">📘 Metodologi Kepadatan</span>
    <span class="sm:hidden">📘 Metode</span>
  </button>

  <!-- ============================================================= -->
  <!-- MAIN WORKSPACE CONTAINER                                      -->
  <!-- ============================================================= -->
  <div id="main-area" class="flex-1 ml-64 min-w-0 flex flex-col min-h-screen transition-all duration-250 ease-in-out">

    <!-- Top Sticky Bar -->
    <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40 h-16 px-4 sm:px-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3 min-w-0">
        <button onclick="toggleSidebar()" class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 shadow-xs transition-all">
          <svg class="w-4 h-4 text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9-3 3 3 3"/></svg>
          <span id="txt-sidebar-toggle">Sembunyikan Menu</span>
        </button>

        <div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 truncate">
          <span>StrategiHub</span>
          <span class="text-slate-300 dark:text-slate-700">/</span>
          <span>Multimoda 2026</span>
          <span class="text-slate-300 dark:text-slate-700">/</span>
          <span id="active-breadcrumb" class="font-semibold text-slate-900 dark:text-white truncate">1. Kronologi Harian (272 Hari)</span>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        <!-- Button Buka Sidebar Metodologi Kepadatan -->
        <button onclick="toggleExplanationSidebar(true)" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all" title="Buka Sidebar Metodologi Kepadatan">
          <svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
          <span class="hidden sm:inline">Metodologi Kepadatan</span>
          <span class="sm:hidden">Metode</span>
        </button>

        <!-- Dark/Light Theme Toggle -->
        <button onclick="toggleTheme()" class="p-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all" title="Ganti Mode Tampilan (Terang/Gelap)">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </div>
    </header>

    <!-- Integrated Executive Operational Strip -->
    <section class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      <div class="px-6 py-3.5">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-slate-800">
          
          <!-- Metric 1: Total Volume YTD -->
          <div class="pt-2 md:pt-0 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5">
              Total Mobilitas Penumpang YTD
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-pnp">371.840.258</span>
              <span class="text-xs text-slate-500 font-medium">penumpang</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono">
              Rata-rata: <span class="font-semibold text-slate-700 dark:text-slate-300">1.367.060</span> pnp/hari (272 hari)
            </div>
          </div>

          <!-- Metric 2: All-Time Peak -->
          <div class="pt-3 md:pt-0 md:pl-4 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5 flex items-center justify-between">
              <span>Puncak Tertinggi 2026</span>
              <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">ALL-TIME PEAK</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-rose-600 dark:text-rose-400 num-mono tracking-tight">2.415.296</span>
              <span class="text-xs text-slate-500 font-medium">penumpang</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono">
              24 Mar 2026 (H+3 Balik) • <span class="font-semibold text-rose-600 dark:text-rose-400">+103,2%</span> vs normal
            </div>
          </div>

          <!-- Metric 3: Mudik Peak -->
          <div class="pt-3 md:pt-0 md:pl-4 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5 flex items-center justify-between">
              <span>Puncak Arus Mudik</span>
              <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">MUDIK PEAK</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-purple-700 dark:text-purple-400 num-mono tracking-tight">2.258.514</span>
              <span class="text-xs text-slate-500 font-medium">penumpang</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono">
              18 Mar 2026 (H-2 Mudik) • <span class="font-semibold text-purple-700 dark:text-purple-400">+90,0%</span> vs normal
            </div>
          </div>

          <!-- Metric 4: Armada Beroperasi -->
          <div class="pt-3 md:pt-0 md:pl-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5">
              Total Armada Beroperasi YTD
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-arm">10.030.995</span>
              <span class="text-xs text-slate-500 font-medium">armada</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono">
              Pesawat, Kereta, Bus, Feri, Kapal Laut
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- Main Dynamic Content Workspace -->
    <main class="flex-1 p-6 space-y-6">

      <!-- ========================================================= -->
      <!-- TAB 1: KRONOLOGI MOBILITAS HARIAN (272 HARI)              -->
      <!-- ========================================================= -->
      <div id="tab-timeline" class="tab-content space-y-6">
        
        <!-- Timeline Control Bar & Chart -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2.5 flex-wrap">
                <h2 id="timeline-chart-heading" class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Kronologi Mobilitas Multimoda Nasional 2026
                </h2>
                <span id="timeline-metric-badge" class="text-[11px] font-semibold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/60 px-2 py-0.5 rounded border border-sky-200 dark:border-sky-800">
                  Volume Penumpang
                </span>
              </div>
              <p id="timeline-chart-desc" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Volume harian agregat penumpang: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut (01 Jan s.d. 29 Sep 2026)
              </p>
            </div>

            <!-- Controls: Metrik Switcher (Pindah ke tempat yang berubah) & Active Range Label -->
            <div class="flex items-center gap-3">
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="metric-btn-pnp" onclick="setTimelineMetric('pnp')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Penumpang</button>
                <button id="metric-btn-arm" onclick="setTimelineMetric('arm')" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Armada</button>
              </div>

              <span id="timeline-badge-info" class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded border border-slate-200 dark:border-slate-700">
                1 Jan 2026 - 29 Sep 2026 (272 Hari)
              </span>
            </div>
          </div>

          <!-- Full-Width Chart Canvas -->
          <div class="relative w-full h-[430px] pt-2">
            <canvas id="chartTimelineCanvas"></canvas>
          </div>

          <!-- Chart Footnote with Interactive Guidance -->
          <div class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-500">
            <div class="flex items-center gap-1.5">
              <span class="text-blue-600 dark:text-blue-400 font-semibold">ℹ Petunjuk:</span>
              <span>Klik nama moda pada legenda di kanan atas grafik untuk menyembunyikan atau menampilkan garis moda.</span>
            </div>
            <div class="num-mono text-[11px] text-slate-400">
              Sumber: Raw Log StrategiHub Pusdatin Kemenhub (209.885 baris bersih)
            </div>
          </div>
        </div>

        <!-- Split Panel: Monthly Accumulation Table vs Day-of-Week Distribution -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- Left (7 Cols): Dense Monthly Data Table -->
          <div class="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Akumulasi Bulanan per Moda Transportasi</h3>
                <p class="text-[11px] text-slate-500">Volume pergerakan dari Januari sampai dengan September 2026</p>
              </div>
              <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">9 Bulan</span>
            </div>

            <div class="overflow-x-auto mt-3">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Bulan</th>
                    <th class="py-2.5 px-3 text-sky-700 dark:text-sky-400">Udara</th>
                    <th class="py-2.5 px-3 text-amber-700 dark:text-amber-400">Kereta Api</th>
                    <th class="py-2.5 px-3 text-green-700 dark:text-green-400">Bus AKAP</th>
                    <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">ASDP</th>
                    <th class="py-2.5 px-3 text-cyan-700 dark:text-cyan-400">Laut</th>
                    <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total</th>
                  </tr>
                </thead>
                <tbody id="tbody-monthly" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                </tbody>
              </table>
            </div>
          </div>

          <!-- Right (5 Cols): Day of Week Profile -->
          <div class="lg:col-span-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Profil Hari dalam Seminggu</h3>
                  <p class="text-[11px] text-slate-500">Rata-rata volume penumpang harian (Senin s.d. Minggu)</p>
                </div>
                <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Senin - Minggu</span>
              </div>

              <div class="relative w-full h-[220px] mt-3">
                <canvas id="chartDOWCanvas"></canvas>
              </div>
            </div>

            <div class="overflow-x-auto mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th class="py-2 px-2.5">Hari</th>
                    <th class="py-2 px-2.5">Udara</th>
                    <th class="py-2 px-2.5">KA</th>
                    <th class="py-2 px-2.5">Bus</th>
                    <th class="py-2 px-2.5">ASDP</th>
                    <th class="py-2 px-2.5">Laut</th>
                    <th class="py-2 px-2.5 text-right font-bold">Total</th>
                  </tr>
                </thead>
                <tbody id="tbody-dow" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                </tbody>
              </table>
            </div>
          </div>

        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 2: PUNCAK LEBARAN 2026                               -->
      <!-- ========================================================= -->
      <div id="tab-lebaran" class="tab-content hidden space-y-6">
        
        <!-- Phase Scrubber (Chronological Strip) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Pilih Tanggal Spesifik Angkutan Lebaran 2026 (H-8 s.d. H+8 • 13 - 29 Maret 2026)
              </h3>
              <p class="text-[11px] text-slate-500">Klik salah satu tanggal untuk menginspeksi rincian volume 5 moda operasional (Hari H: 21 Maret 2026)</p>
            </div>
            <div class="flex items-center gap-3 text-xs">
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span> Hari H (21 Mar)</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-rose-600"></span> Puncak Balik</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-purple-600"></span> Puncak Mudik</span>
            </div>
          </div>

          <!-- Scrubber Buttons Strip -->
          <div class="flex gap-2 overflow-x-auto pb-2" id="lebaran-scrubber">
          </div>
        </div>

        <!-- Active Day Contextual Inspector -->
        <div class="bg-white dark:bg-slate-900 border-l-4 border-l-kemenhub-800 dark:border-l-blue-500 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2">
                <span id="insp-tag" class="px-2 py-0.5 rounded font-bold text-xs bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800">
                  H+3 BALIK 1
                </span>
                <span id="insp-phase" class="text-xs font-semibold text-slate-600 dark:text-slate-400">
                  Puncak Arus Balik Terbesar 2026
                </span>
              </div>
              <div class="text-xl font-bold text-slate-900 dark:text-white num-mono mt-1" id="insp-date">
                24 Maret 2026
              </div>
              <p id="insp-summary" class="text-xs text-slate-500 num-mono mt-0.5">
                Total Penumpang: 2.415.296 • Total Armada: 45.835 Trip/Flight
              </p>
            </div>

            <!-- Breakdown per Moda -->
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-center" id="insp-breakdown">
            </div>
          </div>
        </div>

        <!-- Dynamic Curves vs Surge Comparison -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div class="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-100 dark:border-slate-800">
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Dinamika Harian 5 Moda Angkutan Lebaran 2026
              </h3>
              <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">17 Hari Pengamatan (H-8 s.d. H+8)</span>
            </div>

            <div class="relative w-full h-[320px] mt-3">
              <canvas id="chartLebaranLineCanvas"></canvas>
            </div>
          </div>

          <div class="lg:col-span-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
              Persentase Lonjakan (%) terhadap Rata-rata Normal Februari
            </h3>
            <div class="relative w-full h-[320px] mt-3">
              <canvas id="chartSurgeBarCanvas"></canvas>
            </div>
          </div>
        </div>

        <!-- Dense Surge Data Table -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Tabel Komparasi Angka Lonjakan Puncak Lebaran</h3>
              <p class="text-[11px] text-slate-500">Perbandingan baseline harian Februari dengan volume puncak arus mudik dan arus balik</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Unit: Penumpang</span>
          </div>

          <div class="overflow-x-auto mt-3">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3">Moda Transportasi</th>
                  <th class="py-2.5 px-3">Baseline Normal (Feb)</th>
                  <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">Puncak Mudik (18 Mar / H-3)</th>
                  <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">Lonjakan (%)</th>
                  <th class="py-2.5 px-3 text-rose-700 dark:text-rose-400">Puncak Balik 1 (24 Mar / H+3)</th>
                  <th class="py-2.5 px-3 text-rose-700 dark:text-rose-400">Lonjakan (%)</th>
                  <th class="py-2.5 px-3">Puncak Balik 2 (29 Mar / H+8)</th>
                  <th class="py-2.5 px-3">Lonjakan (%)</th>
                </tr>
              </thead>
              <tbody id="tbody-surge" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 3: PANGSA PASAR ANTAR-MODA (MODAL SHARE %)           -->
      <!-- ========================================================= -->
      <div id="tab-modal-share" class="tab-content hidden space-y-6">
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- 100% Stacked Area Chart -->
          <div class="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Dinamika Pangsa Pasar Penumpang Bulanan (100% Stacked)</h3>
                <p class="text-[11px] text-slate-500">Pergeseran proporsi mobilitas 5 moda dari Januari sampai dengan September 2026</p>
              </div>
              <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Satuan: % Total</span>
            </div>

            <div class="relative w-full h-[320px] mt-3">
              <canvas id="chartModalShareAreaCanvas"></canvas>
            </div>
          </div>

          <!-- Normal vs Peak Comparison Doughnuts -->
          <div class="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
                Komparasi Struktur Moda: Normal vs Puncak
              </h3>

              <div class="grid grid-cols-2 gap-4 mt-4">
                <div class="text-center">
                  <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">Februari (Normal)</div>
                  <div class="relative w-full h-[140px]">
                    <canvas id="donutNormalCanvas"></canvas>
                  </div>
                  <div class="text-[10px] text-slate-400 mt-1 font-mono">Total: 33,3M</div>
                </div>

                <div class="text-center">
                  <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">Maret (Lebaran)</div>
                  <div class="relative w-full h-[140px]">
                    <canvas id="donutPeakCanvas"></canvas>
                  </div>
                  <div class="text-[10px] text-slate-400 mt-1 font-mono">Total: 49,8M</div>
                </div>
              </div>
            </div>

            <div class="p-3 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs mt-4">
              <div class="font-bold text-slate-800 dark:text-slate-200 mb-1">Dinamika Pangsa:</div>
              <p class="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                Pada periode Lebaran (Maret), pangsa ASDP melonjak dari 11,8% menjadi 17,9%, membuktikan pergeseran mobilitas ke penyeberangan kendaraan darat.
              </p>
            </div>
          </div>

        </div>

        <!-- Monthly Share Breakdown Table -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
            Tabel Persentase Pangsa Pasar Bulanan (%)
          </h3>

          <div class="overflow-x-auto mt-3">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3">Bulan</th>
                  <th class="py-2.5 px-3 text-sky-700 dark:text-sky-400">Udara (%)</th>
                  <th class="py-2.5 px-3 text-amber-700 dark:text-amber-400">Kereta Api (%)</th>
                  <th class="py-2.5 px-3 text-green-700 dark:text-green-400">Bus AKAP (%)</th>
                  <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">ASDP (%)</th>
                  <th class="py-2.5 px-3 text-cyan-700 dark:text-cyan-400">Laut (%)</th>
                  <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total Volume</th>
                </tr>
              </thead>
              <tbody id="tbody-share" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 4: RASIO BEBAN ARMADA (LOAD FACTOR PROXY)            -->
      <!-- ========================================================= -->
      <div id="tab-load-factor" class="tab-content hidden space-y-6">
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div class="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Rasio Kepadatan Penumpang per Armada</h3>
                <p class="text-[11px] text-slate-500">Penumpang per trip armada pada kondisi Normal vs Puncak Arus Mudik vs Puncak Arus Balik</p>
              </div>
              <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Satuan: Pnp / Armada</span>
            </div>

            <div class="relative w-full h-[320px] mt-3">
              <canvas id="chartLoadFactorCanvas"></canvas>
            </div>
          </div>

          <div class="lg:col-span-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
                Tabel Evaluasi Utilisasi Armada
              </h3>

              <div class="overflow-x-auto mt-3">
                <table class="w-full text-left text-xs">
                  <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                    <tr>
                      <th class="py-2 px-2.5">Moda</th>
                      <th class="py-2 px-2.5">Normal</th>
                      <th class="py-2 px-2.5 text-purple-700 dark:text-purple-400">Mudik</th>
                      <th class="py-2 px-2.5 text-rose-700 dark:text-rose-400">Balik</th>
                      <th class="py-2 px-2.5 text-right font-bold">Lonjakan Beban</th>
                    </tr>
                  </thead>
                  <tbody id="tbody-load-factor" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                  </tbody>
                </table>
              </div>
            </div>

            <div class="p-3 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs mt-4">
              <div class="font-bold text-slate-800 dark:text-slate-200 mb-1">Temuan Utilisasi:</div>
              <p class="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                Lonjakan beban tertinggi terjadi pada <strong>Penyeberangan ASDP (+121,9%)</strong> di mana rata-rata penumpang per trip melonjak dari 110 menjadi 245 penumpang/trip pada arus balik.
              </p>
            </div>
          </div>

        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 5: REGISTRI SIMPUL TRANSPORTASI (TOP 30 NASIONAL)    -->
      <!-- ========================================================= -->
      <div id="tab-top-hubs" class="tab-content hidden space-y-4">
        
        <!-- Filter & Search Toolbar -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4">
          
          <!-- Mode Tabs -->
          <div class="flex items-center gap-1.5 flex-wrap text-xs">
            <button onclick="filterHubModa('ALL', this)" class="hub-tab-btn active px-3 py-1.5 rounded-md font-semibold bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 shadow-xs transition-all">
              Semua Moda
            </button>
            <button onclick="filterHubModa('UDARA', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Bandara Udara
            </button>
            <button onclick="filterHubModa('KA', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Stasiun Kereta Api
            </button>
            <button onclick="filterHubModa('BUS', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Terminal Bus AKAP
            </button>
            <button onclick="filterHubModa('ASDP', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Pelabuhan ASDP
            </button>
            <button onclick="filterHubModa('LAUT', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Pelabuhan Laut
            </button>
          </div>

          <!-- Search & Period Options -->
          <div class="flex items-center gap-3">
            <div class="relative">
              <input type="text" id="input-hub-search" onkeyup="handleHubSearch(this.value)" placeholder="Cari simpul, kota, provinsi..." class="w-60 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-xs rounded-md px-3 py-1.5 focus:bg-white dark:focus:bg-slate-900">
            </div>

            <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-50 dark:bg-slate-800 text-xs font-medium">
              <button id="hub-period-peak" onclick="setHubPeriod('peak')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-semibold shadow-xs">
                Puncak Lebaran
              </button>
              <button id="hub-period-ytd" onclick="setHubPeriod('ytd')" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                Sepanjang 2026
              </button>
            </div>
          </div>

        </div>

        <!-- Results Count Status -->
        <div class="flex items-center justify-between text-xs text-slate-500 px-1">
          <span id="hub-result-count">Menampilkan 30 prasarana transportasi</span>
          <span class="num-mono">Diurutkan berdasarkan total volume penumpang</span>
        </div>

        <!-- Registry Table -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3 w-12 text-center">Rank</th>
                  <th class="py-2.5 px-3">Nama Prasarana / Simpul</th>
                  <th class="py-2.5 px-3 w-28">Moda</th>
                  <th class="py-2.5 px-3">Provinsi</th>
                  <th class="py-2.5 px-3">Volume Penumpang</th>
                  <th class="py-2.5 px-3">Armada Beroperasi</th>
                  <th class="py-2.5 px-3 w-56">Skala Volume Relatif</th>
                </tr>
              </thead>
              <tbody id="tbody-hubs" class="divide-y divide-slate-100 dark:divide-slate-800 text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 6: MATRIKS REKAPITULASI 13 INDIKATOR MULTIMODA       -->
      <!-- ========================================================= -->
      <div id="tab-matrix" class="tab-content hidden space-y-4">
        
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Matriks Rekapitulasi Komparasi 13 Indikator Multimoda Nasional 2026</h3>
              <p class="text-[11px] text-slate-500">Perbandingan kuantitatif menyeluruh untuk evaluasi perencanaan dan alokasi sumber daya operasional</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">13 Indikator Resmi</span>
          </div>

          <div class="overflow-x-auto mt-2">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-3 px-3.5 w-72">Indikator Kuantitatif</th>
                  <th class="py-3 px-3 text-sky-700 dark:text-sky-400">UDARA</th>
                  <th class="py-3 px-3 text-amber-700 dark:text-amber-400">KERETA API</th>
                  <th class="py-3 px-3 text-green-700 dark:text-green-400">BUS AKAP</th>
                  <th class="py-3 px-3 text-purple-700 dark:text-purple-400">ASDP</th>
                  <th class="py-3 px-3 text-cyan-700 dark:text-cyan-400">LAUT</th>
                  <th class="py-3 px-3 text-right font-bold text-slate-900 dark:text-white">TOTAL NASIONAL</th>
                </tr>
              </thead>
              <tbody id="tbody-matrix" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 7: PETA SPASIAL SEBARAN SIMPUL MULTIMODA (LEAFLET GIS)-->
      <!-- ========================================================= -->
      <div id="tab-spatial-map" class="tab-content hidden space-y-3">
        
        <!-- GIS Header Bar -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-2.5 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2.5 flex-wrap">
                <h2 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Peta Spasial Sebaran Simpul Multimoda Nasional 2026
                </h2>
                <span class="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                  GIS Leaflet Fullscreen
                </span>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Sebaran geografis 1.014 simpul transportasi nasional terpetakan di seluruh wilayah Indonesia (194 prasarana tanpa koordinat dikosongkan)
              </p>
            </div>

            <!-- Metric & Basemap & Fullscreen Controls -->
            <div class="flex items-center gap-2.5 flex-wrap">
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="map-metric-pnp" onclick="setSpatialMapMetric('pnp', this)" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Ukuran: Penumpang</button>
                <button id="map-metric-arm" onclick="setSpatialMapMetric('arm', this)" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Ukuran: Armada</button>
              </div>

              <!-- Basemap Selector (100% Bebas API Key) -->
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-medium">
                <button id="btn-basemap-canvas" onclick="setBasemap('canvas', this)" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-semibold shadow-xs transition-all" title="Kanvas Minimalis Bebas API Key">Peta: Minimalis</button>
                <button id="btn-basemap-osm" onclick="setBasemap('osm', this)" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all" title="OpenStreetMap Standar Bebas API Key">Peta: Terbuka (OSM)</button>
                <button id="btn-basemap-sat" onclick="setBasemap('sat', this)" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all" title="Citra Satelit ESRI Bebas API Key">Peta: Satelit</button>
              </div>

              <button onclick="resetSpatialMap()" class="inline-flex items-center gap-1.5 px-3 py-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all" title="Reset Tampilan Peta ke Indonesia">
                <svg class="w-3.5 h-3.5 text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                <span>Fokus Indonesia</span>
              </button>

              <button onclick="toggleMapFullscreen()" id="btn-map-fs" class="inline-flex items-center gap-1.5 px-3 py-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all" title="Perbesar Layar Penuh">
                <svg class="w-3.5 h-3.5 text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                <span id="txt-map-fs">Layar Penuh</span>
              </button>
            </div>
          </div>

          <!-- Mode Filter Bar & Stats -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div class="flex items-center gap-1.5 flex-wrap text-xs">
              <span class="text-slate-400 font-semibold text-[11px] mr-1">Filter Moda:</span>
              <button onclick="filterSpatialModa('ALL', this)" class="map-moda-btn active px-2.5 py-1 rounded text-xs font-semibold bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 shadow-xs transition-all">
                Semua Moda (1.014)
              </button>
              <button onclick="filterSpatialModa('UDARA', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-sky-800 dark:text-sky-300 hover:bg-sky-50 dark:hover:bg-sky-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                ✈ Udara (257)
              </button>
              <button onclick="filterSpatialModa('KA', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-amber-800 dark:text-amber-300 hover:bg-amber-50 dark:hover:bg-amber-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                🚆 Kereta Api (193)
              </button>
              <button onclick="filterSpatialModa('BUS', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-green-800 dark:text-green-300 hover:bg-green-50 dark:hover:bg-green-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                🚌 Bus AKAP (139)
              </button>
              <button onclick="filterSpatialModa('ASDP', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-purple-800 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                ⛴ ASDP (158)
              </button>
              <button onclick="filterSpatialModa('LAUT', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-cyan-800 dark:text-cyan-300 hover:bg-cyan-50 dark:hover:bg-cyan-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                🚢 Laut (267)
              </button>
            </div>

            <!-- Spatial Summary Badges -->
            <div class="flex items-center gap-2 text-xs flex-wrap">
              <span class="px-2 py-0.5 rounded font-mono text-[11px] bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                ● 1.014 Terpetakan
              </span>
              <span class="px-2 py-0.5 rounded font-mono text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                ◌ 194 Koordinat Dikosongkan
              </span>
            </div>
          </div>
        </div>

        <!-- Fullscreen Leaflet Map Container -->
        <div id="spatial-map-card" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 flex flex-col transition-all">
          <div id="spatialMapCanvas" class="w-full h-[calc(100vh-250px)] min-h-[660px] rounded-md relative z-10"></div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- TAB 8: PROYEKSI & FORECASTING NATARU 2026/2027            -->
      <!-- ========================================================= -->
      <div id="tab-forecasting" class="tab-content hidden space-y-5">
        
        <!-- Header & Simulation Control Bar with Dropdowns -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-4">
          <!-- Top Row: Title, Badge, Description -->
          <div class="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2.5 flex-wrap">
                <h2 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Proyeksi Mobilitas Multimoda Q4 & Libur Nataru 2026/2027
                </h2>
                <span class="text-[11px] font-semibold text-indigo-700 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                  Model Prediktif Time Series + Event Shocks
                </span>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Simulasi horizon 100 hari (28 Sep 2026 – 5 Jan 2027) mengantisipasi lonjakan kapasitas angkutan Natal 2026 dan Tahun Baru 2027
              </p>
            </div>

            <!-- Horizon Badges -->
            <div class="flex items-center gap-2 text-xs flex-wrap">
              <span class="px-2.5 py-1 rounded font-mono text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                Data Historis: 1 Jan - 27 Sep 2026 (270H)
              </span>
              <span class="px-2.5 py-1 rounded font-mono text-[11px] bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Horizon Prediksi: 28 Sep 2026 - 5 Jan 2027 (100H)
              </span>
            </div>
          </div>

          <!-- Bottom Row: Sleek Dropdowns Toolbar -->
          <div class="flex flex-wrap items-center gap-4 text-xs">
            <!-- 1. Dropdown Skenario -->
            <div class="flex items-center gap-2">
              <label for="select-forecast-scen" class="text-slate-500 dark:text-slate-400 font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1">
                <span>🎯 Skenario:</span>
              </label>
              <div class="relative">
                <select id="select-forecast-scen" onchange="setForecastScenario(this.value)" class="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold rounded-md pl-3 pr-8 py-1.5 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none appearance-none cursor-pointer shadow-xs">
                  <option value="moderat" selected>Moderat (Baseline Tren Normal)</option>
                  <option value="optimis">Optimis (+12% Animo Masyarakat)</option>
                  <option value="konservatif">Konservatif (Dampak Cuaca Ekstrem)</option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>
            </div>

            <!-- 2. Dropdown Metrik -->
            <div class="flex items-center gap-2">
              <label for="select-forecast-metric" class="text-slate-500 dark:text-slate-400 font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1">
                <span>📊 Metrik:</span>
              </label>
              <div class="relative">
                <select id="select-forecast-metric" onchange="setForecastMetric(this.value)" class="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold rounded-md pl-3 pr-8 py-1.5 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none appearance-none cursor-pointer shadow-xs">
                  <option value="pnp" selected>Volume Penumpang (Orang)</option>
                  <option value="arm">Kebutuhan Armada (Trip)</option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>
            </div>

            <!-- 3. Dropdown Filter Garis Proyeksi (Moda) -->
            <div class="flex items-center gap-2">
              <label for="select-forecast-moda" class="text-slate-500 dark:text-slate-400 font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1">
                <span>📈 Garis Grafik:</span>
              </label>
              <div class="relative">
                <select id="select-forecast-moda" onchange="setForecastModa(this.value)" class="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold rounded-md pl-3 pr-8 py-1.5 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none appearance-none cursor-pointer shadow-xs">
                  <option value="TOTAL" selected>Total Multimoda (Semua Moda)</option>
                  <option value="UDARA">✈ Udara (Penerbangan Domestik)</option>
                  <option value="KA">🚆 Perkeretaapian (KAI)</option>
                  <option value="BUS">🚌 Bus AKAP (Antar Kota)</option>
                  <option value="ASDP">⛴ ASDP (Penyeberangan Feri)</option>
                  <option value="LAUT">🚢 Transportasi Laut (Kapal Pelni)</option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Executive Projections Strip (4 Cards) -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Card 1: Total Volume Nataru -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Proyeksi Nataru (18 Hari)</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">18 Des - 4 Jan</span>
            </div>
            <div id="card-fc-total-pnp" class="num-mono text-2xl font-extrabold text-slate-900 dark:text-white">24.754.162</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span>Rata-rata: <strong id="card-fc-avg-pnp" class="text-slate-800 dark:text-slate-200">1.375.231</strong> /hari</span>
              <span class="text-emerald-600 font-semibold">+15,7% vs Normal</span>
            </div>
          </div>

          <!-- Card 2: Puncak Arus Mudik Natal -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Puncak Mudik Natal (H-1)</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">Kamis, 24 Des</span>
            </div>
            <div id="card-fc-xmas-pnp" class="num-mono text-2xl font-extrabold text-amber-700 dark:text-amber-400">1.596.000</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span>Lonjakan: <strong id="card-fc-xmas-surge" class="text-amber-600 dark:text-amber-400">+34,2%</strong></span>
              <span class="text-slate-400">vs Normal</span>
            </div>
          </div>

          <!-- Card 3: Puncak Arus Balik Tahun Baru -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Puncak Balik Tahun Baru</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300">Minggu, 3 Jan</span>
            </div>
            <div id="card-fc-ny-pnp" class="num-mono text-2xl font-extrabold text-rose-700 dark:text-rose-400">1.678.553</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span>Lonjakan: <strong id="card-fc-ny-surge" class="text-rose-600 dark:text-rose-400">+41,2%</strong></span>
              <span class="text-slate-400">Puncak Tertinggi Q4</span>
            </div>
          </div>

          <!-- Card 4: Kebutuhan Armada Peak -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Kebutuhan Armada Puncak</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">Siaga Operasi</span>
            </div>
            <div id="card-fc-arm-peak" class="num-mono text-2xl font-extrabold text-slate-900 dark:text-white">42.850</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span>Trip Tambahan: <strong class="text-emerald-600">+4.100</strong> /hari</span>
              <span class="text-slate-400">ASDP & Bus Utama</span>
            </div>
          </div>
        </div>

        <!-- Main Horizon Line Chart Card -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Tren Berkelanjutan: Data Historis 2026 Tersambung ke Garis Proyeksi Nataru 2026/2027
              </h3>
              <p class="text-[11px] text-slate-500">
                Garis solid mewakili realisasi riil (Jan - Sep). Garis putus-putus ungu mewakili proyeksi model (Okt - Jan 2027) beserta pita keyakinan 95%.
              </p>
            </div>
            <div class="flex items-center gap-3 text-[11px] font-mono">
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-0.5 bg-sky-600"></span> Realisasi 2026</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-0.5 border-t border-dashed border-indigo-500"></span> Proyeksi Model</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-indigo-500/20 border border-indigo-400"></span> Rentang 95% CI</span>
            </div>
          </div>

          <div class="h-[380px] w-full relative">
            <canvas id="chartForecastCanvas"></canvas>
          </div>
        </div>

        <!-- Card: Model Specification & Accuracy Validation (RMSE & MAPE) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Spesifikasi Model & Evaluasi Akurasi Pengujian (Backtest Holdout)
                </h3>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                Pengujian empiris out-of-sample: 242 hari data latih (1 Jan – 30 Agt 2026) vs 28 hari data uji (31 Agt – 27 Sep 2026)
              </p>
            </div>
            <span class="text-[11px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
              Metode: Holt-Winters Damped Trend (&phi; = 0.98) + Weekly Seasonality (s=7) + Shocks
            </span>
          </div>

          <!-- Metric Badges & Mathematical Definitions -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <!-- MAPE -->
            <div class="p-3.5 rounded-md bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-emerald-800 dark:text-emerald-300">MAPE (Mean Absolute % Error)</span>
                <span class="text-[10px] font-bold bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 px-1.5 py-0.5 rounded">Akurasi Tinggi (&lt;10%)</span>
              </div>
              <div class="text-2xl font-black font-mono text-emerald-700 dark:text-emerald-400">6,53%</div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Rata-rata persentase deviasi prediksi terhadap data aktual lapangan. Nilai 6,53% membuktikan model sangat akurat (&lt;10% standar internasional).
              </p>
            </div>

            <!-- RMSE -->
            <div class="p-3.5 rounded-md bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-indigo-800 dark:text-indigo-300">RMSE (Root Mean Squared Error)</span>
                <span class="text-[10px] font-bold bg-indigo-200 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-1.5 py-0.5 rounded">Satuan Riil Pnp</span>
              </div>
              <div class="text-2xl font-black font-mono text-indigo-700 dark:text-indigo-400">94.259 <span class="text-xs font-normal text-slate-500">pnp/hari</span></div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Standar deviasi kesalahan dalam satuan penumpang riil. Mengkuadratkan selisih agar penalti lonjakan ekstrem terdeteksi untuk keamanan logistik armada.
              </p>
            </div>

            <!-- MAE & Relative Ratio -->
            <div class="p-3.5 rounded-md bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-800 dark:text-slate-200">MAE & Rasio Error Absolut</span>
                <span class="text-[10px] font-mono text-slate-500">Rerata: 1,228M pnp</span>
              </div>
              <div class="text-2xl font-black font-mono text-slate-800 dark:text-slate-100">77.117 <span class="text-xs font-normal text-slate-500">pnp (7,67%)</span></div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Rata-rata selisih volume absolut harian. Deviasi 77k pnp ini hanya mewakili 7,67% dari rata-rata pergerakan harian nasional.
              </p>
            </div>

            <!-- Mode Breakdown Summary -->
            <div class="p-3.5 rounded-md bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
              <span class="text-[11px] font-bold text-slate-800 dark:text-slate-200 block">Akurasi Per Moda (Uji 28H)</span>
              <div class="space-y-1 text-[11px] font-mono pt-0.5">
                <div class="flex justify-between items-center"><span>🚢 Laut:</span> <span class="font-bold text-emerald-600">5,27%</span></div>
                <div class="flex justify-between items-center"><span>🚌 Bus AKAP:</span> <span class="font-bold text-emerald-600">5,43%</span></div>
                <div class="flex justify-between items-center"><span>🚆 Kereta Api:</span> <span class="font-bold text-emerald-600">8,13%</span></div>
                <div class="flex justify-between items-center"><span>⛴ ASDP:</span> <span class="font-bold text-emerald-600">8,82%</span></div>
                <div class="flex justify-between items-center"><span>✈ Udara:</span> <span class="font-bold text-amber-600">28,64%</span> <span class="text-[10px] text-slate-400 font-sans">(tiket dinamis)</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section: Interactive Per-Prasarana / Simpul Simulation Panel -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-5">
          <!-- Header & Preset Policy Buttons -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Simulasi Kebutuhan Armada Berdasarkan Prasarana / Simpul Transportasi
                </h3>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                Identifikasi simpul prasarana tersibuk (pelabuhan penyeberangan, stasiun KA, bandara, terminal) dan simulasi penambahan sarana (kapal, pesawat, KA, bus)
              </p>
            </div>
            
            <!-- Smart Allocation Presets -->
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-semibold text-slate-400">Preset Kebijakan Simpul:</span>
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button onclick="applySimpulPreset('rekomendasi_kritis', this)" class="simpul-preset-btn active px-2.5 py-1 rounded bg-indigo-600 text-white shadow-xs transition-all">⚡ Rekomendasi Simpul Kritis</button>
                <button onclick="applySimpulPreset('status_quo', this)" class="simpul-preset-btn px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Status Quo (0%)</button>
                <button onclick="applySimpulPreset('rata_10', this)" class="simpul-preset-btn px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Merata (+10%)</button>
                <button onclick="applySimpulPreset('siaga_penuh', this)" class="simpul-preset-btn px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Siaga Penuh (+20%)</button>
              </div>
              <button onclick="toggleExplanationSidebar(true)" class="px-2.5 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all flex items-center gap-1.5" title="Buka Sidebar Metodologi Kepadatan">
                <svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                <span>📘 Metodologi Kepadatan</span>
              </button>
            </div>
          </div>

          <!-- Highlight Summary Strip: 5 Primary Bottlenecks -->
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 text-xs">
            <div onclick="selectSimpul('merak')" class="cursor-pointer bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 rounded-lg p-2.5 hover:ring-2 hover:ring-rose-400 transition-all">
              <div class="flex items-center justify-between text-[10px] text-rose-600 dark:text-rose-400 font-bold uppercase">
                <span>Pelabuhan Merak</span>
                <span>⛴ ASDP</span>
              </div>
              <div class="font-mono font-black text-rose-700 dark:text-rose-300 text-base mt-0.5">88.266 pnp/h</div>
              <div class="text-[10px] text-slate-600 dark:text-slate-300 mt-0.5">Kapal Feri: <strong>188 trip/h</strong></div>
              <div class="text-[10px] text-rose-600 dark:text-rose-400 font-semibold mt-1">⚠️ Butuh: +38 Kapal (+20%)</div>
            </div>

            <div onclick="selectSimpul('bakauheni')" class="cursor-pointer bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 rounded-lg p-2.5 hover:ring-2 hover:ring-rose-400 transition-all">
              <div class="flex items-center justify-between text-[10px] text-rose-600 dark:text-rose-400 font-bold uppercase">
                <span>Pelabuhan Bakauheni</span>
                <span>⛴ ASDP</span>
              </div>
              <div class="font-mono font-black text-rose-700 dark:text-rose-300 text-base mt-0.5">97.573 pnp/h</div>
              <div class="text-[10px] text-slate-600 dark:text-slate-300 mt-0.5">Kapal Feri: <strong>195 trip/h</strong></div>
              <div class="text-[10px] text-rose-600 dark:text-rose-400 font-semibold mt-1">⚠️ Butuh: +39 Kapal (+20%)</div>
            </div>

            <div onclick="selectSimpul('pasarsenen')" class="cursor-pointer bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 rounded-lg p-2.5 hover:ring-2 hover:ring-amber-400 transition-all">
              <div class="flex items-center justify-between text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase">
                <span>Stasiun Pasar Senen</span>
                <span>🚆 KA</span>
              </div>
              <div class="font-mono font-black text-amber-700 dark:text-amber-300 text-base mt-0.5">55.604 pnp/h</div>
              <div class="text-[10px] text-slate-600 dark:text-slate-300 mt-0.5">KA Jarak Jauh: <strong>149 trip/h</strong></div>
              <div class="text-[10px] text-amber-600 dark:text-amber-400 font-semibold mt-1">⚠️ Butuh: +22 KA (+15%)</div>
            </div>

            <div onclick="selectSimpul('ngurahrai')" class="cursor-pointer bg-sky-50/70 dark:bg-sky-950/30 border border-sky-200 dark:border-sky-900/60 rounded-lg p-2.5 hover:ring-2 hover:ring-sky-400 transition-all">
              <div class="flex items-center justify-between text-[10px] text-sky-600 dark:text-sky-400 font-bold uppercase">
                <span>Bandara Ngurah Rai</span>
                <span>✈ UDARA</span>
              </div>
              <div class="font-mono font-black text-sky-700 dark:text-sky-300 text-base mt-0.5">103.504 pnp/h</div>
              <div class="text-[10px] text-slate-600 dark:text-slate-300 mt-0.5">Pesawat Jet: <strong>641 flight/h</strong></div>
              <div class="text-[10px] text-sky-600 dark:text-sky-400 font-semibold mt-1">⚠️ Butuh: +64 Flight (+10%)</div>
            </div>

            <div onclick="selectSimpul('purabaya')" class="cursor-pointer bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/60 rounded-lg p-2.5 hover:ring-2 hover:ring-emerald-400 transition-all">
              <div class="flex items-center justify-between text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase">
                <span>Terminal Purabaya</span>
                <span>🚌 BUS</span>
              </div>
              <div class="font-mono font-black text-emerald-700 dark:text-emerald-300 text-base mt-0.5">53.640 pnp/h</div>
              <div class="text-[10px] text-slate-600 dark:text-slate-300 mt-0.5">Bus AKAP: <strong>2.745 trip/h</strong></div>
              <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">✅ Butuh: +137 Bus (+5%)</div>
            </div>
          </div>

          <!-- Interactive Single-Hub Inspector & Fleet Slider -->
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-4 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <label for="select-simpul" class="text-xs font-bold text-slate-700 dark:text-slate-300">Pilih Simpul Prasarana yang Diuji:</label>
                <select id="select-simpul" onchange="selectSimpul(this.value)" class="text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-900 dark:text-white shadow-xs">
                  <!-- Options rendered dynamically -->
                </select>
              </div>
              <div id="simpul-badge-header" class="flex items-center gap-2 text-xs">
                <!-- Status Badge -->
              </div>
            </div>

            <!-- Dynamic Active Simpul Container -->
            <div id="active-simpul-card" class="space-y-4">
              <!-- Rendered by JS -->
            </div>
          </div>

          <!-- Top 10 Hub Matrix Table -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                Matriks Kebutuhan Penambahan Sarana di 10 Simpul Prasarana Nasional (Hari Puncak Nataru)
              </div>
              <button onclick="resetAllSimpulSliders()" class="text-[11px] font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white underline">
                Reset Semua Simpul ke 0%
              </button>
            </div>

            <div class="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg">
              <table class="w-full text-left border-collapse text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Simpul Prasarana & Wilayah</th>
                    <th class="py-2.5 px-3">Sarana Transportasi</th>
                    <th class="py-2.5 px-3 text-center">Beban Kesibukan</th>
                    <th class="py-2.5 px-3 text-right">Armada Baseline</th>
                    <th class="py-2.5 px-3 text-center" style="min-width: 150px;">Simulasi Tambahan</th>
                    <th class="py-2.5 px-3 text-right">Total Armada Baru</th>
                    <th class="py-2.5 px-3 text-right">Kapasitas Terbuka</th>
                    <th class="py-2.5 px-3 text-center">Estimasi Dampak Lapangan & Antrean</th>
                  </tr>
                </thead>
                <tbody id="tbody-simpul-matrix" class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-200">
                  <!-- Rendered dynamically by JS -->
                </tbody>
              </table>
            </div>

            <!-- Clear Operational Diagnosis Box -->
            <div id="simpulOperationalSummary" class="p-4 rounded-md bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 text-xs text-slate-600 dark:text-slate-300">
              <!-- Rendered dynamically by JS -->
            </div>
          </div>
        </div>

        <!-- Table: Daily Forecast Detail (100 Days) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Tabel Rincian Harian Prediksi Mobilitas Multimoda (Horizon 100 Hari)
              </h4>
              <p class="text-[11px] text-slate-500">Estimasi volume harian, batas rentang interval 95% CI, persentase lonjakan, dan alokasi armada</p>
            </div>

            <!-- Table Range Filter -->
            <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-[11px] font-medium">
              <button onclick="setForecastTableRange('nataru', this)" class="btn-fc-tbl active px-2 py-0.5 rounded bg-white dark:bg-slate-900 text-indigo-700 dark:text-indigo-400 font-semibold shadow-xs transition-all">Posko Nataru (18H)</button>
              <button onclick="setForecastTableRange('des', this)" class="btn-fc-tbl px-2 py-0.5 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Desember</button>
              <button onclick="setForecastTableRange('nov', this)" class="btn-fc-tbl px-2 py-0.5 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">November</button>
              <button onclick="setForecastTableRange('okt', this)" class="btn-fc-tbl px-2 py-0.5 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Oktober</button>
              <button onclick="setForecastTableRange('all', this)" class="btn-fc-tbl px-2 py-0.5 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Semua (100H)</button>
            </div>
          </div>

          <!-- Table Container -->
          <div class="overflow-x-auto max-h-[420px] overflow-y-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 bg-slate-50 dark:bg-slate-800/90 backdrop-blur-xs text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3">Tanggal</th>
                  <th class="py-2.5 px-3">Hari</th>
                  <th class="py-2.5 px-3 text-right">Estimasi Penumpang</th>
                  <th class="py-2.5 px-3 text-right">Rentang 95% CI</th>
                  <th class="py-2.5 px-3 text-center">Lonjakan vs Normal</th>
                  <th class="py-2.5 px-3 text-center">Status Operasional</th>
                  <th class="py-2.5 px-3 text-right">Kebutuhan Armada (Trip)</th>
                </tr>
              </thead>
              <tbody id="tbody-forecast" class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-200">
                <!-- Populated by JS -->
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </main>

    <!-- Institutional Footer -->
    <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-4 mt-auto">
      <div class="px-6 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
        <div class="flex items-center gap-3">
          <span class="font-semibold text-slate-700 dark:text-slate-300">Pusat Data dan Informasi (PUSDATIN) Kemenhub</span>
          <span>•</span>
          <span>Sistem Analitik Mobilitas StrategiHub 2026</span>
        </div>
        <div class="num-mono text-[11px]">
          Terverifikasi Bersih: 209.885 baris • 1 Jan - 29 Sep 2026
        </div>
      </div>
    </footer>

  </div>

<!-- Chart.js CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Leaflet GIS JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<!-- APPLICATION DATA & CONTROLLER -->
<script>
const DATA = {json_data_str};

const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// State Variables
let isSidebarOpen = true;
let currentMetric = 'pnp'; // 'pnp' or 'arm'
let currentTimelineRange = 'all';
let currentHubModa = 'ALL';
let currentHubPeriod = 'peak'; // 'peak' or 'ytd'
let currentHubSearchTerm = '';

// Chart Instances
let chartTimeline = null;
let chartDOW = null;
let chartLebaranLine = null;
let chartSurgeBar = null;
let chartModalShareArea = null;
let chartDonutNormal = null;
let chartDonutPeak = null;
let chartLoadFactor = null;

// Track active dataset visibilities
let timelineVisibility = [true, true, true, true, true, true];
let lebaranVisibility = [true, true, true, true, true, true];

// Spatial Map Variables
let spatialMap = null;
let spatialMarkerGroup = null;
let currentSpatialModa = 'ALL';
let currentSpatialMetric = 'pnp';
let currentSpatialSearch = '';
let selectedSpatialNode = null;
let mapTileLayer = null;

// Standard Functional Colors
const COLOR = {{
  UDARA: '#0284c7', // Sky 600
  KA: '#d97706',    // Amber 600
  BUS: '#16a34a',   // Green 600
  ASDP: '#9333ea',  // Purple 600
  LAUT: '#0891b2',  // Cyan 600
  TOTAL: '#0f172a'  // Dark/White
}};

// ---------------------------------------------------------------
// SIDEBAR COLLAPSIBLE CONTROLLER
// ---------------------------------------------------------------
function toggleSidebar() {{
  const sb = document.getElementById('sidebar');
  const main = document.getElementById('main-area');
  const txt = document.getElementById('txt-sidebar-toggle');

  isSidebarOpen = !isSidebarOpen;
  if (isSidebarOpen) {{
    sb.classList.remove('-translate-x-full');
    main.classList.add('ml-64');
    txt.innerText = 'Sembunyikan Menu';
  }} else {{
    sb.classList.add('-translate-x-full');
    main.classList.remove('ml-64');
    txt.innerText = 'Buka Menu Fitur';
  }}

  setTimeout(() => {{
    if (chartTimeline) chartTimeline.resize();
    if (chartDOW) chartDOW.resize();
    if (chartLebaranLine) chartLebaranLine.resize();
    if (chartSurgeBar) chartSurgeBar.resize();
    if (chartModalShareArea) chartModalShareArea.resize();
    if (chartDonutNormal) chartDonutNormal.resize();
    if (chartDonutPeak) chartDonutPeak.resize();
    if (chartLoadFactor) chartLoadFactor.resize();
    if (spatialMap) spatialMap.invalidateSize();
    if (chartForecast) chartForecast.resize();
  }}, 260);
}}

// ---------------------------------------------------------------
// TAB SWITCHING LOGIC (FROM SIDEBAR)
// ---------------------------------------------------------------
function switchTab(targetId, title, btn) {{
  document.querySelectorAll('.nav-btn').forEach(b => {{
    b.classList.remove('active', 'font-semibold', 'text-kemenhub-800', 'dark:text-blue-400', 'bg-kemenhub-50', 'dark:bg-blue-950/40', 'border-slate-200', 'dark:border-blue-900/50');
    b.classList.add('border-transparent', 'font-medium', 'text-slate-600', 'dark:text-slate-400');
  }});
  document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

  btn.classList.add('active', 'font-semibold', 'text-kemenhub-800', 'dark:text-blue-400', 'bg-kemenhub-50', 'dark:bg-blue-950/40', 'border-slate-200', 'dark:border-blue-900/50');
  btn.classList.remove('border-transparent', 'font-medium', 'text-slate-600', 'dark:text-slate-400');

  const content = document.getElementById(targetId);
  if (content) content.classList.remove('hidden');

  document.getElementById('active-breadcrumb').innerText = title;

  setTimeout(() => {{
    if (targetId === 'tab-timeline' && chartTimeline) chartTimeline.resize();
    if (targetId === 'tab-lebaran') renderLebaranWorkspace();
    if (targetId === 'tab-modal-share') renderModalShareWorkspace();
    if (targetId === 'tab-load-factor') renderLoadFactorWorkspace();
    if (targetId === 'tab-top-hubs') renderHubsTable();
    if (targetId === 'tab-matrix') renderMatrixTable();
    if (targetId === 'tab-spatial-map') {{
      initSpatialMap();
      setTimeout(() => {{ if (spatialMap) spatialMap.invalidateSize(); }}, 200);
    }}
    if (targetId === 'tab-forecasting') {{
      renderForecastWorkspace();
    }}
  }}, 50);
}}

function toggleTheme() {{
  document.documentElement.classList.toggle('dark');
  setTimeout(() => {{
    if (chartTimeline) chartTimeline.update();
    if (chartDOW) chartDOW.update();
    if (chartLebaranLine) chartLebaranLine.update();
    if (chartSurgeBar) chartSurgeBar.update();
    if (chartModalShareArea) chartModalShareArea.update();
    if (chartLoadFactor) chartLoadFactor.update();
    if (chartForecast) chartForecast.update();
    updateMapTheme();
  }}, 100);
}}

function setTimelineMetric(metric) {{
  currentMetric = metric;
  const isPnp = metric === 'pnp';

  const btnPnp = document.getElementById('metric-btn-pnp');
  const btnArm = document.getElementById('metric-btn-arm');
  const badge = document.getElementById('timeline-metric-badge');
  const desc = document.getElementById('timeline-chart-desc');

  if (btnPnp && btnArm) {{
    btnPnp.classList.toggle('bg-white', isPnp);
    btnPnp.classList.toggle('dark:bg-slate-900', isPnp);
    btnPnp.classList.toggle('text-slate-900', isPnp);
    btnPnp.classList.toggle('dark:text-white', isPnp);
    btnPnp.classList.toggle('shadow-xs', isPnp);
    btnPnp.classList.toggle('text-slate-600', !isPnp);

    btnArm.classList.toggle('bg-white', !isPnp);
    btnArm.classList.toggle('dark:bg-slate-900', !isPnp);
    btnArm.classList.toggle('text-slate-900', !isPnp);
    btnArm.classList.toggle('dark:text-white', !isPnp);
    btnArm.classList.toggle('shadow-xs', !isPnp);
    btnArm.classList.toggle('text-slate-600', isPnp);
  }}

  if (badge) {{
    badge.innerText = isPnp ? 'Volume Penumpang' : 'Armada Beroperasi';
    badge.className = isPnp 
      ? 'text-[11px] font-semibold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/60 px-2 py-0.5 rounded border border-sky-200 dark:border-sky-800'
      : 'text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800';
  }}

  if (desc) {{
    desc.innerText = isPnp
      ? 'Volume harian agregat penumpang: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut (01 Jan s.d. 29 Sep 2026)'
      : 'Jumlah harian armada beroperasi (Flight/Trip/Armada): Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut';
  }}

  document.getElementById('timeline-chart-heading').innerText = isPnp 
    ? 'Kronologi Mobilitas Multimoda Nasional 2026'
    : 'Kronologi Armada Beroperasi Multimoda 2026';

  renderTimelineChart();
}}
const setGlobalMetric = setTimelineMetric;

// ---------------------------------------------------------------
// TAB 1: KRONOLOGI MOBILITAS CONTROLLER
// ---------------------------------------------------------------
function getFilteredTimelineData() {{
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') return all.filter(d => d.date >= '2026-03-13' && d.date <= '2026-03-29');
  if (currentTimelineRange === 'libur_sekolah') return all.filter(d => d.date >= '2026-06-15' && d.date <= '2026-07-15');
  if (currentTimelineRange === 'tahun_baru') return all.filter(d => d.date >= '2026-01-01' && d.date <= '2026-01-15');
  return all;
}}

function renderTimelineChart() {{
  const raw = getFilteredTimelineData();
  const ctx = document.getElementById('chartTimelineCanvas').getContext('2d');
  const labels = raw.map(d => d.date);
  const p = currentMetric === 'pnp' ? '' : 'arm_';
  const isDark = document.documentElement.classList.contains('dark');

  const totalColor = isDark ? '#f8fafc' : '#0f172a';

  const datasets = [
    {{ label: 'Total Multimoda', data: raw.map(d => d[p + 'TOTAL']), borderColor: totalColor, borderWidth: 2, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Udara', data: raw.map(d => d[p + 'UDARA']), borderColor: COLOR.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Kereta Api', data: raw.map(d => d[p + 'KA']), borderColor: COLOR.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Bus AKAP', data: raw.map(d => d[p + 'BUS']), borderColor: COLOR.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'ASDP', data: raw.map(d => d[p + 'ASDP']), borderColor: COLOR.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Laut', data: raw.map(d => d[p + 'LAUT']), borderColor: COLOR.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
  ];

  if (chartTimeline) chartTimeline.destroy();
  chartTimeline = new Chart(ctx, {{
    type: 'line',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{
          display: true,
          position: 'top',
          align: 'end',
          labels: {{
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: 'circle',
            font: {{ family: 'Plus Jakarta Sans', size: 11, weight: '500' }},
            color: isDark ? '#94a3b8' : '#475569',
            padding: 12
          }},
          onClick: (e, legendItem, legend) => {{
            const index = legendItem.datasetIndex;
            const ci = legend.chart;
            if (ci.isDatasetVisible(index)) {{
              ci.hide(index);
              legendItem.hidden = true;
              timelineVisibility[index] = false;
            }} else {{
              ci.show(index);
              legendItem.hidden = false;
              timelineVisibility[index] = true;
            }}
          }}
        }},
        tooltip: {{
          backgroundColor: isDark ? '#0f172a' : '#ffffff',
          titleColor: isDark ? '#ffffff' : '#0f172a',
          bodyColor: isDark ? '#cbd5e1' : '#334155',
          borderColor: isDark ? '#334155' : '#cbd5e1',
          borderWidth: 1,
          padding: 8,
          bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
          titleFont: {{ family: 'Plus Jakarta Sans', size: 11, weight: 'bold' }},
          callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{currentMetric === 'pnp' ? 'pnp' : 'armada'}}` }}
        }}
      }},
      scales: {{
        x: {{ 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }},
          ticks: {{ color: isDark ? '#64748b' : '#94a3b8', maxTicksLimit: 14, font: {{ family: 'JetBrains Mono', size: 10 }} }}
        }},
        y: {{ 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }},
          ticks: {{ 
            color: isDark ? '#64748b' : '#94a3b8', 
            font: {{ family: 'JetBrains Mono', size: 10 }}, 
            callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v/1e3).toFixed(0) + 'k') 
          }} 
        }}
      }}
    }}
  }});

  // Apply preserved visibility states
  for (let i = 0; i <= 5; i++) {{
    chartTimeline.setDatasetVisibility(i, timelineVisibility[i]);
  }}
  chartTimeline.update();
}}

function setTimelineFilter(rangeKey, btn) {{
  currentTimelineRange = rangeKey;
  document.querySelectorAll('.btn-range').forEach(b => {{
    b.classList.remove('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
  btn.classList.remove('text-slate-600', 'dark:text-slate-400');

  const labelMap = {{
    'all': '1 Jan 2026 - 29 Sep 2026 (272 Hari)',
    'lebaran': '13 Mar 2026 - 29 Mar 2026 (17 Hari)',
    'libur_sekolah': '15 Jun 2026 - 15 Jul 2026 (31 Hari)',
    'tahun_baru': '1 Jan 2026 - 15 Jan 2026 (15 Hari)'
  }};
  document.getElementById('timeline-badge-info').innerText = labelMap[rangeKey] || '';
  renderTimelineChart();
}}

function renderMonthlyTable() {{
  const ms = DATA.monthly_summary;
  const tbody = document.getElementById('tbody-monthly');
  tbody.innerHTML = '';
  
  ms.forEach((m, idx) => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-200">${{m.label}}</td>
      <td class="py-2.5 px-3">${{numFmt(m.UDARA)}}</td>
      <td class="py-2.5 px-3">${{numFmt(m.KA)}}</td>
      <td class="py-2.5 px-3">${{numFmt(m.BUS)}}</td>
      <td class="py-2.5 px-3">${{numFmt(m.ASDP)}}</td>
      <td class="py-2.5 px-3">${{numFmt(m.LAUT)}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{numFmt(m.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderDOWWorkspace() {{
  const dow = DATA.dow_summary;
  const ctx = document.getElementById('chartDOWCanvas').getContext('2d');
  const isDark = document.documentElement.classList.contains('dark');

  if (chartDOW) chartDOW.destroy();
  chartDOW = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: dow.map(d => d.dow),
      datasets: [{{
        label: 'Rata-rata Penumpang Harian',
        data: dow.map(d => d.TOTAL),
        backgroundColor: '#0284c7',
        borderRadius: 4
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b' }} }},
        y: {{ 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}, 
          ticks: {{ 
            color: isDark ? '#94a3b8' : '#64748b', 
            font: {{ family: 'JetBrains Mono' }}, 
            callback: v => (v/1e6).toFixed(1) + 'M' 
          }} 
        }}
      }}
    }}
  }});

  const tbody = document.getElementById('tbody-dow');
  tbody.innerHTML = '';
  dow.forEach(d => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-sans font-medium text-slate-900 dark:text-slate-200">${{d.dow}}</td>
      <td class="py-2 px-2.5">${{numFmt(d.UDARA)}}</td>
      <td class="py-2 px-2.5">${{numFmt(d.KA)}}</td>
      <td class="py-2 px-2.5">${{numFmt(d.BUS)}}</td>
      <td class="py-2 px-2.5">${{numFmt(d.ASDP)}}</td>
      <td class="py-2 px-2.5">${{numFmt(d.LAUT)}}</td>
      <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${{numFmt(d.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 2: PUNCAK LEBARAN CONTROLLER
// ---------------------------------------------------------------
function selectLebaranDate(dateStr) {{
  const day = DATA.lebaran_daily.find(d => d.date === dateStr);
  if (!day) return;

  const tagEl = document.getElementById('insp-tag');
  tagEl.innerText = day.tag;
  if (day.is_h_day) {{
    tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800';
  }} else if (day.is_peak_balik1 || day.is_peak_mudik || day.is_peak_balik2) {{
    tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800';
  }} else {{
    tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-700';
  }}

  document.getElementById('insp-phase').innerText = day.desc;
  document.getElementById('insp-date').innerText = day.date;
  document.getElementById('insp-summary').innerText = `Total Penumpang: ${{numFmt(day.TOTAL)}} • Total Armada: ${{numFmt(day.arm_TOTAL)}} Trip/Flight`;

  const container = document.getElementById('insp-breakdown');
  container.innerHTML = `
    <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <div class="text-[10px] font-bold text-sky-700 dark:text-sky-400">UDARA</div>
      <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day.UDARA)}}</div>
    </div>
    <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <div class="text-[10px] font-bold text-amber-700 dark:text-amber-400">KERETA API</div>
      <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day.KA)}}</div>
    </div>
    <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <div class="text-[10px] font-bold text-green-700 dark:text-green-400">BUS AKAP</div>
      <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day.BUS)}}</div>
    </div>
    <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <div class="text-[10px] font-bold text-purple-700 dark:text-purple-400">ASDP</div>
      <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day.ASDP)}}</div>
    </div>
    <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <div class="text-[10px] font-bold text-cyan-700 dark:text-cyan-400">LAUT</div>
      <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day.LAUT)}}</div>
    </div>
  `;
}}

function renderLebaranWorkspace() {{
  if (chartLebaranLine) return;

  const strip = document.getElementById('lebaran-scrubber');
  strip.innerHTML = '';
  DATA.lebaran_daily.forEach((d, idx) => {{
    const btn = document.createElement('button');
    const isPeak = d.is_peak_balik1 || d.is_peak_mudik || d.is_peak_balik2;
    const isHDay = d.is_h_day;
    let tagShort = d.tag.startsWith('Hari H') ? 'HARI H' : d.tag.split(' ')[0];

    let btnClass = 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-400';
    let tagColor = 'text-slate-500';

    if (isHDay) {{
      btnClass = 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-400 dark:border-emerald-700 text-emerald-900 dark:text-emerald-200 font-bold';
      tagColor = 'text-emerald-700 dark:text-emerald-300 font-bold';
    }} else if (isPeak) {{
      btnClass = 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200 font-semibold';
      tagColor = 'text-rose-700 dark:text-rose-400';
    }}

    btn.className = `shrink-0 text-left px-2.5 py-1.5 rounded border text-xs transition-all ${{btnClass}}`;
    btn.innerHTML = `
      <div class="text-[9px] uppercase tracking-wider ${{tagColor}}">${{tagShort}}</div>
      <div class="text-xs font-bold num-mono">${{(d.TOTAL/1e6).toFixed(2)}}M</div>
      <div class="text-[9px] text-slate-400 num-mono">${{d.date.substring(5)}}</div>
    `;
    btn.onclick = () => {{
      document.querySelectorAll('#lebaran-scrubber button').forEach(b => b.classList.remove('ring-2', 'ring-kemenhub-800', 'dark:ring-blue-500'));
      btn.classList.add('ring-2', 'ring-kemenhub-800', 'dark:ring-blue-500');
      selectLebaranDate(d.date);
    }};
    strip.appendChild(btn);
  }});
  selectLebaranDate('2026-03-21');
  const hBtn = strip.children[8]; // 2026-03-21 is index 8
  if (hBtn) hBtn.classList.add('ring-2', 'ring-kemenhub-800', 'dark:ring-blue-500');

  const isDark = document.documentElement.classList.contains('dark');
  const ctxLine = document.getElementById('chartLebaranLineCanvas').getContext('2d');
  const ld = DATA.lebaran_daily;
  chartLebaranLine = new Chart(ctxLine, {{
    type: 'line',
    data: {{
      labels: ld.map(d => d.date.substring(5) + ' (' + (d.tag.startsWith('Hari H') ? 'Hari H' : d.tag.split(' ')[0]) + ')'),
      datasets: [
        {{ label: 'Total', data: ld.map(d => d.TOTAL), borderColor: isDark ? '#ffffff' : '#0f172a', borderWidth: 2, pointRadius: 2, tension: 0.15 }},
        {{ label: 'Udara', data: ld.map(d => d.UDARA), borderColor: COLOR.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Kereta Api', data: ld.map(d => d.KA), borderColor: COLOR.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Bus', data: ld.map(d => d.BUS), borderColor: COLOR.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'ASDP', data: ld.map(d => d.ASDP), borderColor: COLOR.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Laut', data: ld.map(d => d.LAUT), borderColor: COLOR.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          display: true,
          position: 'top',
          align: 'end',
          labels: {{
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: 'circle',
            font: {{ family: 'Plus Jakarta Sans', size: 10, weight: '500' }},
            color: isDark ? '#cbd5e1' : '#475569'
          }},
          onClick: (e, legendItem, legend) => {{
            const index = legendItem.datasetIndex;
            const ci = legend.chart;
            if (ci.isDatasetVisible(index)) {{
              ci.hide(index);
              legendItem.hidden = true;
              lebaranVisibility[index] = false;
            }} else {{
              ci.show(index);
              legendItem.hidden = false;
              lebaranVisibility[index] = true;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', maxRotation: 45, font: {{ size: 9, family: 'JetBrains Mono' }} }} }},
        y: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e3).toFixed(0) + 'k' }} }}
      }}
    }}
  }});

  const ctxSurge = document.getElementById('chartSurgeBarCanvas').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
  const labelsSurge = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Laut', 'Udara', 'TOTAL'];
  chartSurgeBar = new Chart(ctxSurge, {{
    type: 'bar',
    data: {{
      labels: labelsSurge,
      datasets: [
        {{ label: 'Mudik 18 Mar / H-3 (%)', data: modas.map(m => DATA.surge_summary[m].surge_mudik_pct), backgroundColor: '#9333ea', borderRadius: 3 }},
        {{ label: 'Balik 24 Mar / H+3 (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik1_pct), backgroundColor: '#0284c7', borderRadius: 3 }},
        {{ label: 'Balik 29 Mar / H+8 (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik2_pct), backgroundColor: '#f43f5e', borderRadius: 3 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: isDark ? '#cbd5e1' : '#475569' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b' }} }},
        y: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'JetBrains Mono' }}, callback: v => '+' + v + '%' }} }}
      }}
    }}
  }});

  const tbody = document.getElementById('tbody-surge');
  tbody.innerHTML = '';
  modas.forEach((m, idx) => {{
    const s = DATA.surge_summary[m];
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{labelsSurge[idx]}}</td>
      <td class="py-2.5 px-3">${{numFmt(s.baseline)}}</td>
      <td class="py-2.5 px-3 font-bold text-purple-700 dark:text-purple-400">${{numFmt(s.peak_mudik)}}</td>
      <td class="py-2.5 px-3 text-purple-700 dark:text-purple-400 font-semibold">+${{s.surge_mudik_pct}}%</td>
      <td class="py-2.5 px-3 font-bold text-rose-700 dark:text-rose-400">${{numFmt(s.peak_balik1)}}</td>
      <td class="py-2.5 px-3 text-rose-700 dark:text-rose-400 font-semibold">+${{s.surge_balik1_pct}}%</td>
      <td class="py-2.5 px-3">${{numFmt(s.peak_balik2)}}</td>
      <td class="py-2.5 px-3">+${{s.surge_balik2_pct}}%</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 3: MODAL SHARE CONTROLLER
// ---------------------------------------------------------------
function renderModalShareWorkspace() {{
  if (chartModalShareArea) return;

  const isDark = document.documentElement.classList.contains('dark');
  const ms = DATA.monthly_summary;
  const ctx = document.getElementById('chartModalShareAreaCanvas').getContext('2d');

  chartModalShareArea = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: ms.map(m => m.label.split(' ')[0]),
      datasets: [
        {{ label: 'Udara', data: ms.map(m => m.share_UDARA), borderColor: COLOR.UDARA, backgroundColor: 'rgba(2, 132, 199, 0.4)', fill: true, tension: 0.15 }},
        {{ label: 'Kereta Api', data: ms.map(m => m.share_KA), borderColor: COLOR.KA, backgroundColor: 'rgba(217, 119, 6, 0.4)', fill: true, tension: 0.15 }},
        {{ label: 'Bus AKAP', data: ms.map(m => m.share_BUS), borderColor: COLOR.BUS, backgroundColor: 'rgba(22, 163, 74, 0.4)', fill: true, tension: 0.15 }},
        {{ label: 'ASDP', data: ms.map(m => m.share_ASDP), borderColor: COLOR.ASDP, backgroundColor: 'rgba(147, 51, 234, 0.4)', fill: true, tension: 0.15 }},
        {{ label: 'Laut', data: ms.map(m => m.share_LAUT), borderColor: COLOR.LAUT, backgroundColor: 'rgba(8, 145, 178, 0.4)', fill: true, tension: 0.15 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: isDark ? '#cbd5e1' : '#475569' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b' }} }},
        y: {{ stacked: true, max: 100, grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'JetBrains Mono' }}, callback: v => v + '%' }} }}
      }}
    }}
  }});

  const feb = ms.find(m => m.bulan === '2026-02');
  const mar = ms.find(m => m.bulan === '2026-03');
  const labels = ['Udara', 'KA', 'Bus', 'ASDP', 'Laut'];
  const colors = [COLOR.UDARA, COLOR.KA, COLOR.BUS, COLOR.ASDP, COLOR.LAUT];

  const ctxNorm = document.getElementById('donutNormalCanvas').getContext('2d');
  chartDonutNormal = new Chart(ctxNorm, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [feb.share_UDARA, feb.share_KA, feb.share_BUS, feb.share_ASDP, feb.share_LAUT],
        backgroundColor: colors,
        borderWidth: 1
      }}]
    }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
  }});

  const ctxPeak = document.getElementById('donutPeakCanvas').getContext('2d');
  chartDonutPeak = new Chart(ctxPeak, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [mar.share_UDARA, mar.share_KA, mar.share_BUS, mar.share_ASDP, mar.share_LAUT],
        backgroundColor: colors,
        borderWidth: 1
      }}]
    }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
  }});

  const tbody = document.getElementById('tbody-share');
  tbody.innerHTML = '';
  ms.forEach(m => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-100">${{m.label}}</td>
      <td class="py-2.5 px-3">${{m.share_UDARA}}%</td>
      <td class="py-2.5 px-3">${{m.share_KA}}%</td>
      <td class="py-2.5 px-3">${{m.share_BUS}}%</td>
      <td class="py-2.5 px-3 font-semibold text-purple-700 dark:text-purple-400">${{m.share_ASDP}}%</td>
      <td class="py-2.5 px-3">${{m.share_LAUT}}%</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{numFmt(m.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 4: LOAD FACTOR PROXY CONTROLLER
// ---------------------------------------------------------------
function renderLoadFactorWorkspace() {{
  if (chartLoadFactor) return;

  const isDark = document.documentElement.classList.contains('dark');
  const ctx = document.getElementById('chartLoadFactorCanvas').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labelsLF = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Laut', 'Udara'];
  const lf = DATA.load_factor_stats;

  chartLoadFactor = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: labelsLF,
      datasets: [
        {{ label: 'Baseline Normal', data: modas.map(m => lf[m].baseline_lf), backgroundColor: '#64748b', borderRadius: 3 }},
        {{ label: 'Puncak Mudik', data: modas.map(m => lf[m].mudik_lf), backgroundColor: '#9333ea', borderRadius: 3 }},
        {{ label: 'Puncak Balik', data: modas.map(m => lf[m].balik_lf), backgroundColor: '#0284c7', borderRadius: 3 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: isDark ? '#cbd5e1' : '#475569' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b' }} }},
        y: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'JetBrains Mono' }} }} }}
      }}
    }}
  }});

  const tbody = document.getElementById('tbody-load-factor');
  tbody.innerHTML = '';
  modas.forEach((m, idx) => {{
    const s = lf[m];
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{labelsLF[idx]}}</td>
      <td class="py-2.5 px-3">${{s.baseline_lf}} pnp/arm</td>
      <td class="py-2.5 px-3 text-purple-700 dark:text-purple-400 font-semibold">${{s.mudik_lf}}</td>
      <td class="py-2.5 px-3 text-rose-700 dark:text-rose-400 font-semibold">${{s.balik_lf}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">+${{s.surge_lf_pct}}%</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 5: TOP HUBS CONTROLLER
// ---------------------------------------------------------------
function filterHubModa(moda, btn) {{
  currentHubModa = moda;
  document.querySelectorAll('.hub-tab-btn').forEach(b => {{
    b.classList.remove('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
    b.classList.add('font-medium', 'text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
  btn.classList.remove('font-medium', 'text-slate-600', 'dark:text-slate-400');
  renderHubsTable();
}}

function setHubPeriod(period) {{
  currentHubPeriod = period;
  const isPeak = period === 'peak';
  
  document.getElementById('hub-period-peak').classList.toggle('bg-white', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('dark:bg-slate-900', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('text-slate-900', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('dark:text-white', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('font-semibold', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('shadow-xs', isPeak);
  document.getElementById('hub-period-peak').classList.toggle('text-slate-600', !isPeak);

  document.getElementById('hub-period-ytd').classList.toggle('bg-white', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('dark:bg-slate-900', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('text-slate-900', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('dark:text-white', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('font-semibold', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('shadow-xs', !isPeak);
  document.getElementById('hub-period-ytd').classList.toggle('text-slate-600', isPeak);

  renderHubsTable();
}}

function handleHubSearch(term) {{
  currentHubSearchTerm = term.toLowerCase().trim();
  renderHubsTable();
}}

function renderHubsTable() {{
  const source = currentHubPeriod === 'peak' ? DATA.top_hubs_peak : DATA.top_hubs_ytd;
  let list = [];

  if (currentHubModa === 'ALL') {{
    Object.keys(source).forEach(m => {{
      source[m].forEach(h => list.push({{ ...h, moda: m }}));
    }});
    list.sort((a, b) => b.pnp - a.pnp);
    list = list.slice(0, 30);
  }} else {{
    list = (source[currentHubModa] || []).map(h => ({{ ...h, moda: currentHubModa }}));
  }}

  if (currentHubSearchTerm) {{
    list = list.filter(h => 
      h.nama_prasarana.toLowerCase().includes(currentHubSearchTerm) || 
      h.provinsi.toLowerCase().includes(currentHubSearchTerm)
    );
  }}

  document.getElementById('hub-result-count').innerText = `Menampilkan ${{list.length}} prasarana transportasi`;

  const tbody = document.getElementById('tbody-hubs');
  tbody.innerHTML = '';
  
  if (list.length === 0) {{
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-400">Tidak ada simpul yang sesuai dengan filter pencarian</td></tr>`;
    return;
  }}

  const maxPnp = list[0].pnp;

  list.forEach((h, idx) => {{
    const pct = Math.round((h.pnp / maxPnp) * 100);
    const color = COLOR[h.moda] || '#64748b';
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 text-center font-mono font-bold text-slate-400">${{idx + 1}}</td>
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{h.nama_prasarana}}</td>
      <td class="py-2.5 px-3">
        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold text-white" style="background-color: ${{color}}">
          ${{h.moda}}
        </span>
      </td>
      <td class="py-2.5 px-3 font-sans text-slate-600 dark:text-slate-300">${{h.provinsi}}</td>
      <td class="py-2.5 px-3 font-mono font-bold text-slate-900 dark:text-white">${{numFmt(h.pnp)}}</td>
      <td class="py-2.5 px-3 font-mono text-slate-600 dark:text-slate-400">${{numFmt(h.arm)}}</td>
      <td class="py-2.5 px-3">
        <div class="flex items-center gap-2">
          <div class="flex-1 h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
            <div class="h-full rounded-full transition-all duration-300" style="width: ${{pct}}%; background-color: ${{color}}"></div>
          </div>
          <span class="text-[10px] font-mono text-slate-400 w-8 text-right">${{pct}}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 6: 13 INDIKATOR MATRIX CONTROLLER
// ---------------------------------------------------------------
function renderMatrixTable() {{
  const tbody = document.getElementById('tbody-matrix');
  tbody.innerHTML = '';

  const meta = DATA.meta;
  const lf = DATA.load_factor_stats;
  const surge = DATA.surge_summary;
  const ms = DATA.monthly_summary;
  const mar = ms.find(m => m.bulan === '2026-03') || {{}};
  const feb = ms.find(m => m.bulan === '2026-02') || {{}};

  const rows = [
    {{ label: '1. Total Penumpang YTD (Org)', u: numFmt(DATA.top_hubs_ytd.UDARA.reduce((a,b)=>a+b.pnp,0)), ka: '83.748.346', bus: '75.683.884', asdp: '43.795.040', laut: '49.638.662', tot: numFmt(meta.total_passengers_ytd) }},
    {{ label: '2. Total Armada Operasi YTD (Trip)', u: '1.151.589', ka: '1.781.924', bus: '5.949.853', asdp: '317.788', laut: '829.841', tot: numFmt(meta.total_armada_ytd) }},
    {{ label: '3. Rata-rata Penumpang Harian', u: '437.406', ka: '307.898', bus: '278.250', asdp: '161.011', laut: '182.495', tot: '1.367.060' }},
    {{ label: '4. Volume Puncak Mudik (18 Mar)', u: numFmt(surge.UDARA.peak_mudik), ka: numFmt(surge.KA.peak_mudik), bus: numFmt(surge.BUS.peak_mudik), asdp: numFmt(surge.ASDP.peak_mudik), laut: numFmt(surge.LAUT.peak_mudik), tot: numFmt(surge.TOTAL.peak_mudik) }},
    {{ label: '5. Lonjakan Arus Mudik (%)', u: '+' + surge.UDARA.surge_mudik_pct + '%', ka: '+' + surge.KA.surge_mudik_pct + '%', bus: '+' + surge.BUS.surge_mudik_pct + '%', asdp: '+' + surge.ASDP.surge_mudik_pct + '%', laut: '+' + surge.LAUT.surge_mudik_pct + '%', tot: '+' + surge.TOTAL.surge_mudik_pct + '%' }},
    {{ label: '6. Volume Puncak Balik 1 (24 Mar)', u: numFmt(surge.UDARA.peak_balik1), ka: numFmt(surge.KA.peak_balik1), bus: numFmt(surge.BUS.peak_balik1), asdp: numFmt(surge.ASDP.peak_balik1), laut: numFmt(surge.LAUT.peak_balik1), tot: numFmt(surge.TOTAL.peak_balik1) }},
    {{ label: '7. Lonjakan Arus Balik 1 (%)', u: '+' + surge.UDARA.surge_balik1_pct + '%', ka: '+' + surge.KA.surge_balik1_pct + '%', bus: '+' + surge.BUS.surge_balik1_pct + '%', asdp: '+' + surge.ASDP.surge_balik1_pct + '%', laut: '+' + surge.LAUT.surge_balik1_pct + '%', tot: '+' + surge.TOTAL.surge_balik1_pct + '%' }},
    {{ label: '8. Load Factor Normal (Pnp/Arm)', u: lf.UDARA.baseline_lf, ka: lf.KA.baseline_lf, bus: lf.BUS.baseline_lf, asdp: lf.ASDP.baseline_lf, laut: lf.LAUT.baseline_lf, tot: '37,1' }},
    {{ label: '9. Load Factor Puncak Lebaran', u: lf.UDARA.peak_lf, ka: lf.KA.peak_lf, bus: lf.BUS.peak_lf, asdp: lf.ASDP.peak_lf, laut: lf.LAUT.peak_lf, tot: '52,7' }},
    {{ label: '10. Pangsa Pasar Normal Feb (%)', u: feb.share_UDARA + '%', ka: feb.share_KA + '%', bus: feb.share_BUS + '%', asdp: feb.share_ASDP + '%', laut: feb.share_LAUT + '%', tot: '100,0%' }},
    {{ label: '11. Pangsa Pasar Puncak Mar (%)', u: mar.share_UDARA + '%', ka: mar.share_KA + '%', bus: mar.share_BUS + '%', asdp: mar.share_ASDP + '%', laut: mar.share_LAUT + '%', tot: '100,0%' }},
    {{ label: '12. Jumlah Simpul Terverifikasi', u: '257 Bandara', ka: '193 Stasiun', bus: '215 Terminal', asdp: '276 Pelabuhan', laut: '267 Pelabuhan', tot: '1.208 Simpul' }},
    {{ label: '13. Simpul Terpadat Nasional', u: 'Soekarno-Hatta (CGK)', ka: 'Yogyakarta (YK)', bus: 'Purboyo Madiun', asdp: 'Bakauheni Lampung', laut: 'Tanjung Perak', tot: 'Multimoda' }},
  ];

  rows.forEach(r => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-900 dark:text-slate-100">${{r.label}}</td>
      <td class="py-2.5 px-3">${{r.u}}</td>
      <td class="py-2.5 px-3">${{r.ka}}</td>
      <td class="py-2.5 px-3">${{r.bus}}</td>
      <td class="py-2.5 px-3 font-bold text-purple-700 dark:text-purple-400">${{r.asdp}}</td>
      <td class="py-2.5 px-3">${{r.laut}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{r.tot}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 7: LEAFLET SPATIAL MAP CONTROLLER
// ---------------------------------------------------------------
let currentBasemap = 'canvas'; // 'canvas', 'osm', 'sat'

function getBasemapConfig(type, isDark) {{
  if (type === 'osm') {{
    return {{
      url: 'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18
    }};
  }} else if (type === 'sat') {{
    return {{
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
      attr: 'Tiles &copy; Esri, Maxar, Earthstar Geographics',
      maxZoom: 17
    }};
  }} else {{
    // ESRI Gray Canvas (Zero API Key, Zero Watermark, Super Clean)
    return {{
      url: isDark 
        ? 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}'
        : 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',
      attr: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      maxZoom: 16
    }};
  }}
}}

function setBasemap(type, btn) {{
  currentBasemap = type;
  const isDark = document.documentElement.classList.contains('dark');
  const cfg = getBasemapConfig(type, isDark);
  if (mapTileLayer) {{
    mapTileLayer.setUrl(cfg.url);
  }}

  ['btn-basemap-canvas', 'btn-basemap-osm', 'btn-basemap-sat'].forEach(id => {{
    const b = document.getElementById(id);
    if (!b) return;
    const isAct = b === btn;
    b.classList.toggle('bg-white', isAct);
    b.classList.toggle('dark:bg-slate-900', isAct);
    b.classList.toggle('text-slate-900', isAct);
    b.classList.toggle('dark:text-white', isAct);
    b.classList.toggle('font-semibold', isAct);
    b.classList.toggle('shadow-xs', isAct);
    b.classList.toggle('text-slate-600', !isAct);
    b.classList.toggle('dark:text-slate-400', !isAct);
  }});
}}

function initSpatialMap() {{
  if (spatialMap) return;

  const isDark = document.documentElement.classList.contains('dark');
  const cfg = getBasemapConfig(currentBasemap, isDark);

  spatialMap = L.map('spatialMapCanvas', {{
    center: [-2.2, 117.5],
    zoom: 5,
    minZoom: 3,
    maxZoom: 16
  }});

  mapTileLayer = L.tileLayer(cfg.url, {{
    attribution: cfg.attr,
    maxZoom: cfg.maxZoom
  }}).addTo(spatialMap);

  spatialMarkerGroup = L.layerGroup().addTo(spatialMap);

  // Add custom map legend
  const legend = L.control({{ position: 'bottomleft' }});
  legend.onAdd = function() {{
    const div = L.DomUtil.create('div', 'p-2.5 rounded-md bg-white/95 dark:bg-slate-900/95 border border-slate-200 dark:border-slate-800 text-[11px] shadow-sm space-y-1');
    div.innerHTML = `
      <div class="font-bold text-slate-800 dark:text-slate-200 text-[10px] uppercase tracking-wider mb-1">Legenda Moda</div>
      <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-600"></span><span class="text-slate-600 dark:text-slate-300">Udara (257)</span></div>
      <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-600"></span><span class="text-slate-600 dark:text-slate-300">Kereta Api (193)</span></div>
      <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-green-600"></span><span class="text-slate-600 dark:text-slate-300">Bus AKAP (139)</span></div>
      <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-purple-600"></span><span class="text-slate-600 dark:text-slate-300">ASDP (158)</span></div>
      <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-600"></span><span class="text-slate-600 dark:text-slate-300">Laut (267)</span></div>
    `;
    return div;
  }};
  legend.addTo(spatialMap);

  renderSpatialMapNodes();
}}

function updateMapTheme() {{
  if (!spatialMap || !mapTileLayer) return;
  const isDark = document.documentElement.classList.contains('dark');
  if (currentBasemap === 'canvas') {{
    const cfg = getBasemapConfig('canvas', isDark);
    mapTileLayer.setUrl(cfg.url);
  }}
}}

function renderSpatialMapNodes() {{
  if (!spatialMarkerGroup) return;
  spatialMarkerGroup.clearLayers();

  const nodes = DATA.spatial_nodes.filter(n => {{
    if (!n.has_coords) return false;
    if (currentSpatialModa !== 'ALL' && n.m !== currentSpatialModa) return false;
    return true;
  }});

  nodes.forEach(n => {{
    const val = currentSpatialMetric === 'pnp' ? n.pnp : n.arm;
    const radius = val > 0 ? Math.max(4.5, Math.min(24, 4.5 + Math.log10(val + 1) * 2.4)) : 4;
    const color = COLOR[n.m] || '#64748b';

    const marker = L.circleMarker([n.lat, n.lon], {{
      radius: radius,
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.75
    }});

    const pnpTot = n.pnp || 1;
    const datPct = Math.round((n.p_dat / pnpTot) * 100);
    const brgPct = 100 - datPct;

    const popupHtml = `
      <div class="p-3 text-xs font-sans min-w-[240px]">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
          <span class="px-1.5 py-0.5 rounded font-bold text-[10px] text-white" style="background-color: ${{color}}">${{n.m}}</span>
          <span class="text-[10px] text-slate-400 font-mono">${{n.tipe}}</span>
        </div>
        <div class="font-bold text-sm text-slate-900 dark:text-white mt-1.5">${{n.nama}}</div>
        <div class="text-[11px] text-slate-500">${{n.p}} • ID: ${{n.id}}</div>
        
        <div class="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800 space-y-1.5">
          <div class="flex justify-between font-mono">
            <span class="text-slate-500">Total Penumpang:</span>
            <span class="font-bold text-slate-900 dark:text-white">${{numFmt(n.pnp)}}</span>
          </div>
          <div class="space-y-0.5">
            <div class="flex justify-between font-mono text-[10px] text-slate-500">
              <span>Datang: ${{numFmt(n.p_dat)}} (${{datPct}}%)</span>
              <span>Berangkat: ${{numFmt(n.p_brg)}} (${{brgPct}}%)</span>
            </div>
            <div class="w-full h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex">
              <div class="h-full bg-sky-500" style="width: ${{datPct}}%"></div>
              <div class="h-full bg-amber-500" style="width: ${{brgPct}}%"></div>
            </div>
          </div>
          <div class="flex justify-between font-mono pt-1">
            <span class="text-slate-500">Total Armada:</span>
            <span class="font-bold text-slate-900 dark:text-white">${{numFmt(n.arm)}}</span>
          </div>
          <div class="flex justify-between font-mono text-[10px] text-slate-400">
            <span>Aktifitas Lapor:</span>
            <span>${{n.days}} Hari</span>
          </div>
        </div>

        <div class="mt-2 pt-1.5 border-t border-slate-100 dark:border-slate-800 text-[10px] font-mono text-slate-400">
          Lat: ${{n.lat}}, Lon: ${{n.lon}}
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    marker.bindTooltip(`<b>${{n.nama}}</b> (${{n.m}}): ${{numFmt(n.pnp)}} pnp`, {{ direction: 'top' }});

    spatialMarkerGroup.addLayer(marker);
  }});
}}

function filterSpatialModa(moda, btn) {{
  currentSpatialModa = moda;
  document.querySelectorAll('.map-moda-btn').forEach(b => {{
    b.classList.remove('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
    b.classList.add('font-medium', 'text-slate-600', 'dark:text-slate-400', 'bg-slate-100', 'dark:bg-slate-800');
  }});
  btn.classList.add('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
  btn.classList.remove('font-medium', 'text-slate-600', 'dark:text-slate-400', 'bg-slate-100', 'dark:bg-slate-800');
  renderSpatialMapNodes();
}}

function setSpatialMapMetric(metric, btn) {{
  currentSpatialMetric = metric;
  const isPnp = metric === 'pnp';

  const btnPnp = document.getElementById('map-metric-pnp');
  const btnArm = document.getElementById('map-metric-arm');

  if (btnPnp && btnArm) {{
    btnPnp.classList.toggle('bg-white', isPnp);
    btnPnp.classList.toggle('dark:bg-slate-900', isPnp);
    btnPnp.classList.toggle('text-slate-900', isPnp);
    btnPnp.classList.toggle('dark:text-white', isPnp);
    btnPnp.classList.toggle('shadow-xs', isPnp);
    btnPnp.classList.toggle('text-slate-600', !isPnp);

    btnArm.classList.toggle('bg-white', !isPnp);
    btnArm.classList.toggle('dark:bg-slate-900', !isPnp);
    btnArm.classList.toggle('text-slate-900', !isPnp);
    btnArm.classList.toggle('dark:text-white', !isPnp);
    btnArm.classList.toggle('shadow-xs', !isPnp);
    btnArm.classList.toggle('text-slate-600', isPnp);
  }}

  renderSpatialMapNodes();
}}

function resetSpatialMap() {{
  if (spatialMap) {{
    spatialMap.flyTo([-2.2, 117.5], 5, {{ duration: 0.8 }});
  }}
}}

function toggleMapFullscreen() {{
  const card = document.getElementById('spatial-map-card');
  if (!card) return;
  if (!document.fullscreenElement) {{
    if (card.requestFullscreen) {{
      card.requestFullscreen();
    }} else if (card.webkitRequestFullscreen) {{
      card.webkitRequestFullscreen();
    }}
  }} else {{
    if (document.exitFullscreen) {{
      document.exitFullscreen();
    }}
  }}
}}

document.addEventListener('fullscreenchange', () => {{
  const isFs = !!document.fullscreenElement;
  const txtFs = document.getElementById('txt-map-fs');
  if (txtFs) {{
    txtFs.innerText = isFs ? 'Kecilkan' : 'Layar Penuh';
  }}
  setTimeout(() => {{
    if (spatialMap) spatialMap.invalidateSize();
  }}, 150);
}});

// ---------------------------------------------------------------
// TAB 8: FORECASTING NATARU 2026/2027 CONTROLLER
// ---------------------------------------------------------------
let currentForecastScenario = 'moderat';
let currentForecastMetric = 'pnp'; // 'pnp' or 'arm'
let currentForecastModa = 'TOTAL';
let currentForecastRange = 'nataru'; // 'nataru', 'des', 'nov', 'okt', 'all'
let currentSimArmadaPct = 10;
let chartForecast = null;

function setForecastScenario(scen) {{
  currentForecastScenario = scen;
  const select = document.getElementById('select-forecast-scen');
  if (select && select.value !== scen) select.value = scen;

  renderForecastSummaryCards();
  renderForecastChart();
  renderForecastTable();
  renderArmadaSimulation();
}}

function setForecastMetric(metric) {{
  currentForecastMetric = metric;
  const select = document.getElementById('select-forecast-metric');
  if (select && select.value !== metric) select.value = metric;

  renderForecastChart();
  renderForecastTable();
}}

function setForecastModa(moda) {{
  currentForecastModa = moda;
  const select = document.getElementById('select-forecast-moda');
  if (select && select.value !== moda) select.value = moda;

  renderForecastChart();
}}

function setForecastTableRange(rangeKey, btn) {{
  currentForecastRange = rangeKey;
  document.querySelectorAll('.btn-fc-tbl').forEach(b => {{
    b.classList.remove('active', 'bg-white', 'dark:bg-slate-900', 'text-indigo-700', 'dark:text-indigo-400', 'font-semibold', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-indigo-700', 'dark:text-indigo-400', 'font-semibold', 'shadow-xs');
  btn.classList.remove('text-slate-600', 'dark:text-slate-400');

  renderForecastTable();
}}

function renderForecastSummaryCards() {{
  if (!DATA.forecast_nataru) return;
  const sum = DATA.forecast_nataru.summaries[currentForecastScenario];
  if (!sum) return;

  document.getElementById('card-fc-total-pnp').innerText = numFmt(sum.total_passengers);
  document.getElementById('card-fc-avg-pnp').innerText = numFmt(sum.avg_daily_passengers);
  document.getElementById('card-fc-xmas-pnp').innerText = numFmt(sum.xmas_peak_val);
  document.getElementById('card-fc-xmas-surge').innerText = `+${{sum.xmas_peak_surge}}%`;
  document.getElementById('card-fc-ny-pnp').innerText = numFmt(sum.ny_peak_val);
  document.getElementById('card-fc-ny-surge').innerText = `+${{sum.ny_peak_surge}}%`;
  
  // Peak armada
  const scenData = DATA.forecast_nataru.scenarios[currentForecastScenario];
  const maxArmDay = scenData.reduce((max, d) => d.arm_TOTAL > max.arm_TOTAL ? d : max, scenData[0]);
  document.getElementById('card-fc-arm-peak').innerText = numFmt(maxArmDay.arm_TOTAL);
}}

function renderForecastChart() {{
  if (!DATA.forecast_nataru) return;
  const ctx = document.getElementById('chartForecastCanvas');
  if (!ctx) return;

  const isDark = document.documentElement.classList.contains('dark');
  const isPnp = currentForecastMetric === 'pnp';
  const moda = currentForecastModa;

  // Filter historical data (up to 2026-09-27)
  const hist = DATA.daily_timeline.filter(d => d.date <= '2026-09-27');
  const fc = DATA.forecast_nataru.scenarios[currentForecastScenario];

  // Combined timeline
  const allLabels = [...hist.map(d => d.date), ...fc.map(d => d.date)];

  // Historical data values
  const histKey = isPnp ? moda : (moda === 'TOTAL' ? 'arm_TOTAL' : `arm_${{moda}}`);
  const histData = [...hist.map(d => d[histKey]), ...fc.map(() => null)];

  // Forecast data values (start connecting from last historical point)
  const lastHistVal = hist[hist.length - 1][histKey];
  const fcData = [
    ...hist.slice(0, -1).map(() => null),
    lastHistVal,
    ...fc.map(d => isPnp ? d[moda] : d[`arm_${{moda}}`])
  ];

  // Colors
  const modaColor = moda === 'TOTAL' ? (isDark ? '#38bdf8' : '#0284c7') : (COLOR[moda] || '#6366f1');
  const forecastColor = '#6366f1'; // Indigo

  const datasets = [
    {{
      label: `Realisasi Historis (${{isPnp ? 'Penumpang' : 'Armada'}})`,
      data: histData,
      borderColor: modaColor,
      backgroundColor: 'transparent',
      borderWidth: 1.8,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.15,
      spanGaps: false
    }},
    {{
      label: `Proyeksi Model (${{isPnp ? 'Penumpang' : 'Armada'}})`,
      data: fcData,
      borderColor: forecastColor,
      backgroundColor: 'transparent',
      borderWidth: 2.2,
      borderDash: [5, 4],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.2,
      spanGaps: false
    }}
  ];

  // Add 95% Confidence Interval band when viewing total passenger volume
  if (isPnp && moda === 'TOTAL') {{
    const ciUpper = [
      ...hist.slice(0, -1).map(() => null),
      lastHistVal,
      ...fc.map(d => d.ci_upper)
    ];
    const ciLower = [
      ...hist.slice(0, -1).map(() => null),
      lastHistVal,
      ...fc.map(d => d.ci_lower)
    ];

    datasets.push({{
      label: 'Batas Atas 95% CI',
      data: ciUpper,
      borderColor: 'transparent',
      backgroundColor: isDark ? 'rgba(99, 102, 241, 0.12)' : 'rgba(99, 102, 241, 0.15)',
      fill: '+1',
      pointRadius: 0,
      tension: 0.2
    }});
    datasets.push({{
      label: 'Batas Bawah 95% CI',
      data: ciLower,
      borderColor: 'transparent',
      backgroundColor: 'transparent',
      fill: false,
      pointRadius: 0,
      tension: 0.2
    }});
  }}

  if (chartForecast) chartForecast.destroy();
  chartForecast = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: allLabels,
      datasets: datasets
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{
        mode: 'index',
        intersect: false
      }},
      plugins: {{
        legend: {{
          display: true,
          position: 'top',
          align: 'end',
          labels: {{
            boxWidth: 12,
            boxHeight: 4,
            color: isDark ? '#94a3b8' : '#475569',
            font: {{ family: 'JetBrains Mono', size: 10 }},
            filter: (item) => !item.text.includes('Batas')
          }}
        }},
        tooltip: {{
          backgroundColor: isDark ? '#0f172a' : '#ffffff',
          titleColor: isDark ? '#ffffff' : '#0f172a',
          bodyColor: isDark ? '#cbd5e1' : '#334155',
          borderColor: isDark ? '#334155' : '#e2e8f0',
          borderWidth: 1,
          padding: 10,
          callbacks: {{
            title: function(items) {{
              const dStr = items[0].label;
              const d = new Date(dStr);
              const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
              return `${{days[d.getDay()]}}, ${{dStr}}`;
            }},
            label: function(ctx) {{
              if (ctx.raw === null || ctx.raw === undefined) return null;
              if (ctx.dataset.label.includes('Batas')) return null;
              return `${{ctx.dataset.label}}: ${{Number(ctx.raw).toLocaleString('id-ID')}}`;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{
          grid: {{ display: false }},
          ticks: {{
            color: isDark ? '#64748b' : '#94a3b8',
            font: {{ family: 'JetBrains Mono', size: 10 }},
            maxTicksLimit: 14,
            callback: function(val, index) {{
              const label = allLabels[index];
              return label ? label.slice(5) : '';
            }}
          }}
        }},
        y: {{
          grid: {{ color: isDark ? '#1e293b' : '#f1f5f9' }},
          ticks: {{
            color: isDark ? '#64748b' : '#94a3b8',
            font: {{ family: 'JetBrains Mono', size: 10 }},
            callback: (v) => v >= 1000000 ? `${{(v/1000000).toFixed(1)}}M` : (v >= 1000 ? `${{(v/1000).toFixed(0)}}k` : v)
          }}
        }}
      }}
    }}
  }});
}}

function renderForecastTable() {{
  if (!DATA.forecast_nataru) return;
  const tbody = document.getElementById('tbody-forecast');
  if (!tbody) return;
  tbody.innerHTML = '';

  const fc = DATA.forecast_nataru.scenarios[currentForecastScenario];
  const rKey = currentForecastRange;

  const filtered = fc.filter(d => {{
    if (rKey === 'nataru') return d.date >= '2026-12-18' && d.date <= '2027-01-04';
    if (rKey === 'okt') return d.date.startsWith('2026-10');
    if (rKey === 'nov') return d.date.startsWith('2026-11');
    if (rKey === 'des') return d.date.startsWith('2026-12');
    return true; // 'all'
  }});

  const dayNames = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];

  filtered.forEach(row => {{
    const d = new Date(row.date);
    const dayName = dayNames[d.getDay()];

    let badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">Normal</span>`;
    if (row.date === '2026-12-24') {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300">Puncak Natal</span>`;
    }} else if (row.date === '2027-01-03') {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-300">Puncak Balik</span>`;
    }} else if (row.surge_pct >= 40) {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300">Sangat Tinggi</span>`;
    }} else if (row.surge_pct >= 20) {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">Tinggi</span>`;
    }}

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-medium text-slate-900 dark:text-white">${{row.date}}</td>
      <td class="py-2 px-2.5 font-sans ${{['Min', 'Sab'].includes(dayName) ? 'text-rose-600 font-semibold' : 'text-slate-500'}}">${{dayName}}</td>
      <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${{numFmt(row.TOTAL)}}</td>
      <td class="py-2 px-2.5 text-right text-slate-500 text-[10px]">${{numFmt(row.ci_lower)}} - ${{numFmt(row.ci_upper)}}</td>
      <td class="py-2 px-2.5 text-center ${{row.surge_pct >= 30 ? 'text-amber-600 font-bold' : (row.surge_pct >= 15 ? 'text-blue-600' : 'text-slate-500')}}">+${{row.surge_pct}}%</td>
      <td class="py-2 px-2.5 text-center">${{badgeStatus}}</td>
      <td class="py-2 px-2.5 text-right text-slate-700 dark:text-slate-300 font-semibold">${{numFmt(row.arm_TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 8: SIMULASI KEBUTUHAN ARMADA BERDASARKAN PRASARANA / SIMPUL
// ---------------------------------------------------------------
const SIMPUL_DATA = [
  {{
    id: 'merak',
    name: 'Pelabuhan Merak',
    prov: 'Banten',
    moda: 'ASDP',
    modaLabel: '⛴ ASDP Feri',
    saranaType: 'Kapal Ro-Ro Feri Penyeberangan',
    saranaUnit: 'trip kapal',
    pnpDay: 88266,
    armDay: 188,
    baseStress: 98,
    recAddPct: 20,
    baseQueue: 'Antrean kendaraan 4 – 6 Jam di dermaga & kantong parkir Cikuasa Atas',
    mitigatedQueue: 'Antrean terpangkas menjadi 1 – 1,5 Jam (mengalir lancar)',
    fieldAction: 'Percepatan waktu bongkar muat (port time < 45 menit) & pengerahan kapal feri kapasitas besar (>5.000 GT)',
    color: 'rose'
  }},
  {{
    id: 'bakauheni',
    name: 'Pelabuhan Bakauheni',
    prov: 'Lampung',
    moda: 'ASDP',
    modaLabel: '⛴ ASDP Feri',
    saranaType: 'Kapal Ro-Ro Feri Penyeberangan',
    saranaUnit: 'trip kapal',
    pnpDay: 97573,
    armDay: 195,
    baseStress: 97,
    recAddPct: 20,
    baseQueue: 'Antrean kendaraan 4 – 5 Jam saat arus balik Sumatera ke Jawa',
    mitigatedQueue: 'Antrean terpangkas menjadi 1 – 1,5 Jam',
    fieldAction: 'Optimalisasi pola operasi TBB (Tiba Bongkar Berangkat) tanpa memuat untuk menyedot antrean pelabuhan seberang',
    color: 'rose'
  }},
  {{
    id: 'pasarsenen',
    name: 'Stasiun Pasar Senen',
    prov: 'DKI Jakarta',
    moda: 'KA',
    modaLabel: '🚆 Kereta Api',
    saranaType: 'Rangkaian KA Jarak Jauh (KAI)',
    saranaUnit: 'perjalanan KA',
    pnpDay: 55604,
    armDay: 149,
    baseStress: 99,
    recAddPct: 15,
    baseQueue: 'Tiket KA ekonomi habis terjual 100%, antrean boarding hall padat',
    mitigatedQueue: 'Okupansi turun ke 86%, ketersediaan tiket tambahan terbuka',
    fieldAction: 'Penambahan perjalanan KLB KA Tambahan Nataru relasi Pasar Senen – Yogyakarta / Solo / Surabaya',
    color: 'amber'
  }},
  {{
    id: 'gambir',
    name: 'Stasiun Gambir',
    prov: 'DKI Jakarta',
    moda: 'KA',
    modaLabel: '🚆 Kereta Api',
    saranaType: 'Rangkaian KA Eksekutif & Kompartemen',
    saranaUnit: 'perjalanan KA',
    pnpDay: 42106,
    armDay: 248,
    baseStress: 92,
    recAddPct: 10,
    baseQueue: 'Tiket eksekutif Trans-Jawa 95% terjual, ruang tunggu peron padat',
    mitigatedQueue: 'Kapasitas eksekutif terbuka, waktu tunggu boarding nyaman',
    fieldAction: 'Penambahan stamformasi panjang rangkaian kereta & penambahan jadwal keberangkatan pagi/malam',
    color: 'amber'
  }},
  {{
    id: 'ngurahrai',
    name: 'Bandara I Gusti Ngurah Rai (DPS)',
    prov: 'Bali',
    moda: 'UDARA',
    modaLabel: '✈ Udara',
    saranaType: 'Pesawat Jet Komersial (A320 / B737)',
    saranaUnit: 'penerbangan (flight)',
    pnpDay: 103504,
    armDay: 641,
    baseStress: 96,
    recAddPct: 10,
    baseQueue: 'Slot penerbangan padat 98%, tarif tiket mencapai Tarif Batas Atas (TBA)',
    mitigatedQueue: 'Slot extra flight malam terakomodasi, keterjangkauan tarif tiket terjaga',
    fieldAction: 'Perpanjangan jam operasional bandara menjadi 24 jam & pemberian slot terbang malam bagi maskapai',
    color: 'sky'
  }},
  {{
    id: 'soetta',
    name: 'Bandara Soekarno-Hatta (CGK)',
    prov: 'Banten',
    moda: 'UDARA',
    modaLabel: '✈ Udara',
    saranaType: 'Pesawat Komersial & Widebody',
    saranaUnit: 'penerbangan (flight)',
    pnpDay: 283048,
    armDay: 1875,
    baseStress: 90,
    recAddPct: 10,
    baseQueue: 'Kepadatan di check-in counter & delay rotasi pesawat rute hub',
    mitigatedQueue: 'Kelancaran transit multimoda antar-pulau terjaga optimal',
    fieldAction: 'Optimalisasi pergerakan runway capacity (aircraft movement per hour) di Runway 1, 2, dan 3',
    color: 'sky'
  }},
  {{
    id: 'yogyakarta',
    name: 'Stasiun Yogyakarta (Tugu)',
    prov: 'D.I. Yogyakarta',
    moda: 'KA',
    modaLabel: '🚆 Kereta Api',
    saranaType: 'Rangkaian KA Jarak Jauh & Aglomerasi',
    saranaUnit: 'perjalanan KA',
    pnpDay: 38595,
    armDay: 379,
    baseStress: 91,
    recAddPct: 10,
    baseQueue: 'Peron padat wisatawan, frekuensi komuter aglomerasi penuh sesak',
    mitigatedQueue: 'Penumpukan peron terurai, flow keluar masuk penumpang lancar',
    fieldAction: 'Penambahan frekuensi KRL Commuter Line Solo-Yogya dan KA Bandara YIA',
    color: 'amber'
  }},
  {{
    id: 'ketapang',
    name: 'Pelabuhan Ketapang & Gilimanuk',
    prov: 'Jatim – Bali',
    moda: 'ASDP',
    modaLabel: '⛴ ASDP Feri',
    saranaType: 'Kapal Penyeberangan Selat Bali',
    saranaUnit: 'trip kapal',
    pnpDay: 56310,
    armDay: 324,
    baseStress: 88,
    recAddPct: 15,
    baseQueue: 'Antrean kendaraan liburan Jawa-Bali 2 – 3 Jam di kantong buffer zone',
    mitigatedQueue: 'Waktu antrean terpangkas menjadi < 45 menit',
    fieldAction: 'Pengoperasian dermaga ponton bergerak & kapal perbantuan kapasitas besar',
    color: 'rose'
  }},
  {{
    id: 'purabaya',
    name: 'Terminal Purabaya (Bungurasih)',
    prov: 'Jawa Timur',
    moda: 'BUS',
    modaLabel: '🚌 Bus AKAP',
    saranaType: 'Armada Bus AKAP Antar Kota',
    saranaUnit: 'trip bus',
    pnpDay: 53640,
    armDay: 2745,
    baseStress: 76,
    recAddPct: 5,
    baseQueue: 'Waktu tunggu penumpang di jalur keberangkatan ~45 menit saat malam puncak',
    mitigatedQueue: 'Waktu tunggu terpangkas menjadi ~15 menit',
    fieldAction: 'Penyiagaan armada bus pariwisata cadangan sebagai bus bantuan rute Trans-Jawa',
    color: 'emerald'
  }},
  {{
    id: 'batam',
    name: 'Pelabuhan Batam Center',
    prov: 'Kepulauan Riau',
    moda: 'LAUT',
    modaLabel: '🚢 Laut',
    saranaType: 'Kapal Ferry Penumpang & Cepat',
    saranaUnit: 'trip kapal',
    pnpDay: 59518,
    armDay: 816,
    baseStress: 70,
    recAddPct: 5,
    baseQueue: 'Antrean ruang tunggu ponton pada jam favorit pagi & sore',
    mitigatedQueue: 'Sirkulasi embarkasi penumpang cepat & tertib',
    fieldAction: 'Penjadwalan extra trip kapal ferry rute Batam-Bintan dan antisipasi cuaca gelombang tinggi',
    color: 'cyan'
  }}
];

let selectedSimpulId = 'merak';
let simpulCustomPcts = {{
  merak: 20,
  bakauheni: 20,
  pasarsenen: 15,
  gambir: 10,
  ngurahrai: 10,
  soetta: 10,
  yogyakarta: 10,
  ketapang: 15,
  purabaya: 5,
  batam: 5
}};

function selectSimpul(simpulId) {{
  selectedSimpulId = simpulId;
  const sel = document.getElementById('select-simpul');
  if (sel && sel.value !== simpulId) sel.value = simpulId;
  renderSimpulSimulation();
}}

function onSimpulSliderChange(simId, val) {{
  simpulCustomPcts[simId] = Number(val);
  document.querySelectorAll('.simpul-preset-btn').forEach(b => {{
    b.classList.remove('active', 'bg-indigo-600', 'text-white', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  renderSimpulSimulation();
}}

function applySimpulPreset(presetKey, btn) {{
  if (presetKey === 'rekomendasi_kritis') {{
    simpulCustomPcts = {{
      merak: 20,
      bakauheni: 20,
      pasarsenen: 15,
      gambir: 10,
      ngurahrai: 10,
      soetta: 10,
      yogyakarta: 10,
      ketapang: 15,
      purabaya: 5,
      batam: 5
    }};
  }} else if (presetKey === 'status_quo') {{
    SIMPUL_DATA.forEach(s => {{ simpulCustomPcts[s.id] = 0; }});
  }} else if (presetKey === 'rata_10') {{
    SIMPUL_DATA.forEach(s => {{ simpulCustomPcts[s.id] = 10; }});
  }} else if (presetKey === 'siaga_penuh') {{
    simpulCustomPcts = {{
      merak: 25,
      bakauheni: 25,
      pasarsenen: 20,
      gambir: 15,
      ngurahrai: 15,
      soetta: 15,
      yogyakarta: 15,
      ketapang: 20,
      purabaya: 10,
      batam: 10
    }};
  }}

  document.querySelectorAll('.simpul-preset-btn').forEach(b => {{
    b.classList.remove('active', 'bg-indigo-600', 'text-white', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  if (btn) {{
    btn.classList.add('active', 'bg-indigo-600', 'text-white', 'shadow-xs');
    btn.classList.remove('text-slate-600', 'dark:text-slate-400');
  }}

  renderSimpulSimulation();
}}

function resetAllSimpulSliders() {{
  SIMPUL_DATA.forEach(s => {{ simpulCustomPcts[s.id] = 0; }});
  document.querySelectorAll('.simpul-preset-btn').forEach(b => {{
    b.classList.remove('active', 'bg-indigo-600', 'text-white', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  renderSimpulSimulation();
}}

function renderSimpulSimulation() {{
  const selDropdown = document.getElementById('select-simpul');
  if (selDropdown && selDropdown.options.length === 0) {{
    selDropdown.innerHTML = '';
    SIMPUL_DATA.forEach(s => {{
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.innerText = `${{s.name}} (${{s.moda}} - ${{s.prov}})`;
      if (s.id === selectedSimpulId) opt.selected = true;
      selDropdown.appendChild(opt);
    }});
  }}

  const active = SIMPUL_DATA.find(s => s.id === selectedSimpulId) || SIMPUL_DATA[0];
  const activePct = simpulCustomPcts[active.id] || 0;
  const activeAddArm = Math.round(active.armDay * (activePct / 100));
  const activeNewArm = active.armDay + activeAddArm;
  const activeAddCap = Math.round(active.pnpDay * (activePct / 100));
  const activeNewStress = Math.max(30, Math.round(active.baseStress / (1 + activePct / 100)));

  let activeImpactText = '';
  if (activePct === 0) {{
    activeImpactText = active.baseQueue;
  }} else if (activePct < active.recAddPct) {{
    activeImpactText = `Kepadatan berkurang ~${{activePct * 3}}%, namun masih berpotensi antrean pada jam-jam sibuk`;
  }} else {{
    activeImpactText = active.mitigatedQueue;
  }}

  let stressBadge = '';
  let stressBg = 'bg-rose-500';
  if (activeNewStress >= 90) {{
    stressBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300">Sangat Kritis (${{activeNewStress}}%)</span>`;
    stressBg = 'bg-rose-500';
  }} else if (activeNewStress >= 75) {{
    stressBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300">Siaga (${{activeNewStress}}%)</span>`;
    stressBg = 'bg-amber-500';
  }} else {{
    stressBadge = `<span class="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">Terkendali (${{activeNewStress}}%)</span>`;
    stressBg = 'bg-emerald-500';
  }}

  const badgeHeader = document.getElementById('simpul-badge-header');
  if (badgeHeader) {{
    badgeHeader.innerHTML = `
      <span class="px-2 py-0.5 rounded text-xs font-bold bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200">${{active.modaLabel}}</span>
      ${{stressBadge}}
    `;
  }}

  const activeCard = document.getElementById('active-simpul-card');
  if (activeCard) {{
    activeCard.innerHTML = `
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 items-center">
        <!-- Col 1: Prasarana Info & Stress Meter -->
        <div class="space-y-2">
          <div>
            <div class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Simpul Prasarana</div>
            <div class="font-bold text-slate-900 dark:text-white text-base">${{active.name}}</div>
            <div class="text-xs text-slate-500">Provinsi: ${{active.prov}} | Sarana: <strong class="text-slate-700 dark:text-slate-300">${{active.saranaType}}</strong></div>
          </div>
          <div>
            <div class="flex justify-between text-xs text-slate-500 mb-1">
              <span>Beban Kesibukan Hari Puncak:</span>
              <span class="font-mono font-bold text-slate-800 dark:text-slate-200">${{activeNewStress}}%</span>
            </div>
            <div class="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
              <div class="${{stressBg}} h-2 rounded-full transition-all duration-300" style="width: ${{activeNewStress}}%"></div>
            </div>
            <div class="text-[10px] text-slate-400 mt-1">Baseline Puncak: ${{numFmt(active.pnpDay)}} pnp/hari (${{numFmt(active.armDay)}} ${{active.saranaUnit}}/hari)</div>
          </div>
        </div>

        <!-- Col 2: Interactive Slider -->
        <div class="bg-white dark:bg-slate-900 p-3.5 rounded-lg border border-slate-200 dark:border-slate-700 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Tambah Sarana (${{active.saranaType}}):</span>
            <span class="font-mono font-black text-indigo-600 dark:text-indigo-400 text-sm">+${{activePct}}%</span>
          </div>
          <input type="range" min="0" max="40" step="5" value="${{activePct}}" oninput="onSimpulSliderChange('${{active.id}}', this.value)" class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600">
          <div class="flex justify-between text-[10px] font-mono text-slate-400">
            <span>0% (Status Quo)</span>
            <span class="text-indigo-500 font-bold">Rekomendasi: +${{active.recAddPct}}%</span>
            <span>+40% (Max)</span>
          </div>
          <div class="pt-1 flex gap-2">
            <button onclick="onSimpulSliderChange('${{active.id}}', ${{active.recAddPct}})" class="text-[10px] px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-semibold hover:bg-indigo-100 transition-colors">
              Gunakan Rekomendasi (+${{active.recAddPct}}%)
            </button>
            <button onclick="onSimpulSliderChange('${{active.id}}', 0)" class="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
              Reset 0%
            </button>
          </div>
        </div>

        <!-- Col 3: Reactive Impact Results -->
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Tambahan Sarana</div>
            <div class="font-mono font-bold text-indigo-600 dark:text-indigo-400 text-base mt-0.5">+${{numFmt(activeAddArm)}} ${{active.saranaUnit}}</div>
            <div class="text-[10px] text-slate-500 font-mono mt-0.5">Total: ${{numFmt(activeNewArm)}} trip/hari</div>
          </div>
          <div class="bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Kapasitas Terbuka</div>
            <div class="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-base mt-0.5">+${{numFmt(activeAddCap)}} pnp</div>
            <div class="text-[10px] text-emerald-600 font-semibold mt-0.5">Daya serap puncak</div>
          </div>
          <div class="col-span-2 bg-indigo-50/70 dark:bg-indigo-950/40 p-2.5 rounded-lg border border-indigo-200 dark:border-indigo-800/60">
            <div class="text-[10px] text-indigo-800 dark:text-indigo-300 font-bold uppercase">Dampak Penguraian di Lapangan:</div>
            <div class="text-xs text-slate-800 dark:text-slate-200 mt-0.5 font-medium">${{activeImpactText}}</div>
            <div class="text-[10px] text-slate-500 dark:text-slate-400 mt-1 italic">SOP Lapangan: ${{active.fieldAction}}</div>
            <div class="mt-2 pt-1.5 border-t border-indigo-200 dark:border-indigo-800/60 flex items-center justify-between">
              <span class="text-[10px] text-indigo-800 dark:text-indigo-300 font-semibold">Tahu padat atau tidaknya dari mana?</span>
              <button onclick="toggleExplanationSidebar(true)" class="text-[10px] text-indigo-600 dark:text-indigo-400 font-bold hover:underline flex items-center gap-1">
                <span>Buka Sidebar Metodologi</span>
                <svg class="w-3 h-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }}

  const tbody = document.getElementById('tbody-simpul-matrix');
  if (tbody) {{
    tbody.innerHTML = '';
    SIMPUL_DATA.forEach(s => {{
      const pct = simpulCustomPcts[s.id] || 0;
      const addArm = Math.round(s.armDay * (pct / 100));
      const newArm = s.armDay + addArm;
      const addCap = Math.round(s.pnpDay * (pct / 100));
      const newStress = Math.max(30, Math.round(s.baseStress / (1 + pct / 100)));

      let badge = '';
      if (newStress >= 90) {{
        badge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300">Kritis (${{newStress}}%)</span>`;
      }} else if (newStress >= 75) {{
        badge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300">Siaga (${{newStress}}%)</span>`;
      }} else {{
        badge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">Terkendali (${{newStress}}%)</span>`;
      }}

      let rowImpact = '';
      if (pct === 0) rowImpact = s.baseQueue;
      else if (pct < s.recAddPct) rowImpact = `Kepadatan turun ~${{pct * 3}}%, antrean moderat`;
      else rowImpact = s.mitigatedQueue;

      const isCurrentSelected = s.id === selectedSimpulId;
      const tr = document.createElement('tr');
      tr.className = `hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer ${{isCurrentSelected ? 'bg-indigo-50/50 dark:bg-indigo-950/20' : ''}}`;
      tr.onclick = (e) => {{
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {{
          selectSimpul(s.id);
        }}
      }};

      tr.innerHTML = `
        <td class="py-2.5 px-3 font-sans">
          <div class="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
            ${{s.name}}
            ${{isCurrentSelected ? '<span class="text-[9px] px-1 py-0.2 rounded bg-indigo-600 text-white font-mono">Aktif</span>' : ''}}
          </div>
          <div class="text-[10px] text-slate-500">${{s.prov}} • ${{s.modaLabel}}</div>
        </td>
        <td class="py-2.5 px-3 font-sans text-slate-700 dark:text-slate-300">
          <div class="font-medium">${{s.saranaType}}</div>
          <div class="text-[10px] text-slate-400 font-mono">${{numFmt(s.pnpDay)}} pnp/hari</div>
        </td>
        <td class="py-2.5 px-3 text-center">${{badge}}</td>
        <td class="py-2.5 px-3 text-right font-mono text-slate-600 dark:text-slate-400">${{numFmt(s.armDay)}} ${{s.saranaUnit}}</td>
        <td class="py-2.5 px-3 text-center">
          <div class="flex items-center gap-1.5 justify-center">
            <input type="range" min="0" max="40" step="5" value="${{pct}}" oninput="onSimpulSliderChange('${{s.id}}', this.value)" class="w-20 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600">
            <span class="font-mono font-bold text-indigo-600 dark:text-indigo-400 text-xs w-9 text-right">+${{pct}}%</span>
          </div>
        </td>
        <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-900 dark:text-white">
          ${{numFmt(newArm)}}
          <span class="text-[10px] font-normal text-indigo-600 dark:text-indigo-400 block">+${{numFmt(addArm)}} trip</span>
        </td>
        <td class="py-2.5 px-3 text-right font-mono font-semibold text-emerald-600 dark:text-emerald-400">
          +${{numFmt(addCap)}}
          <span class="text-[10px] text-slate-400 font-normal block">kursi/hari</span>
        </td>
        <td class="py-2.5 px-3 text-center font-sans text-xs text-slate-700 dark:text-slate-300 max-w-[220px]">
          ${{rowImpact}}
        </td>
      `;
      tbody.appendChild(tr);
    }});
  }}

  const elSum = document.getElementById('simpulOperationalSummary');
  if (elSum) {{
    const merak = SIMPUL_DATA.find(s => s.id === 'merak');
    const bakauheni = SIMPUL_DATA.find(s => s.id === 'bakauheni');
    const pasarsenen = SIMPUL_DATA.find(s => s.id === 'pasarsenen');
    const gambir = SIMPUL_DATA.find(s => s.id === 'gambir');
    const ngurahrai = SIMPUL_DATA.find(s => s.id === 'ngurahrai');
    const soetta = SIMPUL_DATA.find(s => s.id === 'soetta');
    const ketapang = SIMPUL_DATA.find(s => s.id === 'ketapang');
    const purabaya = SIMPUL_DATA.find(s => s.id === 'purabaya');

    const merakAdd = Math.round(merak.armDay * (simpulCustomPcts.merak / 100));
    const bakauAdd = Math.round(bakauheni.armDay * (simpulCustomPcts.bakauheni / 100));
    const senenAdd = Math.round(pasarsenen.armDay * (simpulCustomPcts.pasarsenen / 100));
    const gambirAdd = Math.round(gambir.armDay * (simpulCustomPcts.gambir / 100));
    const dpsAdd = Math.round(ngurahrai.armDay * (simpulCustomPcts.ngurahrai / 100));
    const soettaAdd = Math.round(soetta.armDay * (simpulCustomPcts.soetta / 100));
    const ketaAdd = Math.round(ketapang.armDay * (simpulCustomPcts.ketapang / 100));
    const puraAdd = Math.round(purabaya.armDay * (simpulCustomPcts.purabaya / 100));

    elSum.innerHTML = `
      <div class="flex items-start gap-2.5">
        <span class="w-2.5 h-2.5 rounded-full bg-indigo-600 mt-1 shrink-0"></span>
        <div class="space-y-1.5">
          <div class="font-bold text-slate-900 dark:text-white text-xs">
            Instruksi & Alokasi Penambahan Armada per Simpul Prasarana (Hasil Simulasi Posko Kemenhub):
          </div>
          <div class="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed space-y-1">
            <div>
              ⛴ <strong>Kapal Penyeberangan yang Harus Ditambah:</strong>
              <strong>Pelabuhan Merak</strong> butuh tambahan <strong>+${{merakAdd}} trip kapal Ro-Ro/hari (+${{simpulCustomPcts.merak}}%)</strong> dan <strong>Pelabuhan Bakauheni</strong> butuh <strong>+${{bakauAdd}} trip kapal/hari (+${{simpulCustomPcts.bakauheni}}%)</strong> untuk memangkas antrean 5 jam menjadi 1-1,5 jam. Lintas Selat Bali (<strong>Pelabuhan Ketapang-Gilimanuk</strong>) butuh <strong>+${{ketaAdd}} trip kapal/hari (+${{simpulCustomPcts.ketapang}}%)</strong> guna mengurai buffer zone wisatawan darat.
            </div>
            <div>
              🚆 <strong>Kereta Api yang Harus Ditambah:</strong>
              <strong>Stasiun Pasar Senen</strong> wajib ditambah <strong>+${{senenAdd}} perjalanan KA jarak jauh/hari (+${{simpulCustomPcts.pasarsenen}}%)</strong> untuk membuka tiket KA ekonomi rute Jawa Tengah/Timur yang ludes 100%. <strong>Stasiun Gambir</strong> butuh tambahan <strong>+${{gambirAdd}} perjalanan KA/hari (+${{simpulCustomPcts.gambir}}%)</strong> untuk rute eksekutif Trans-Jawa.
            </div>
            <div>
              ✈ <strong>Pesawat yang Harus Ditambah:</strong>
              <strong>Bandara I Gusti Ngurah Rai (DPS Bali)</strong> butuh tambahan <strong>+${{dpsAdd}} extra flight/hari (+${{simpulCustomPcts.ngurahrai}}%)</strong> via izin slot malam (red-eye flight) demi meredam lonjakan tarif batas atas. <strong>Bandara Soekarno-Hatta (CGK)</strong> butuh penambahan <strong>+${{soettaAdd}} extra flight/hari (+${{simpulCustomPcts.soetta}}%)</strong> untuk mengamankan konektivitas transit antar-pulau.
            </div>
            <div>
              🚌 <strong>Bus yang Harus Ditambah:</strong>
              <strong>Terminal Purabaya (Surabaya)</strong> butuh penyiagaan <strong>+${{puraAdd}} armada bus cadangan/hari (+${{simpulCustomPcts.purabaya}}%)</strong> untuk mengantisipasi lonjakan arus balik penumpang malam hari.
            </div>
          </div>
        </div>
      </div>
    `;
  }}
}}

// Backward compatibility alias
const renderArmadaSimulation = renderSimpulSimulation;

function renderForecastWorkspace() {{
  renderForecastSummaryCards();
  renderForecastChart();
  renderForecastTable();
  renderArmadaSimulation();
}}

// ---------------------------------------------------------------
// CSV EXPORT LOGIC
// ---------------------------------------------------------------
function exportActiveCSV() {{
  const raw = getFilteredTimelineData();
  let csv = 'tanggal,udara_pnp,ka_pnp,bus_pnp,asdp_pnp,laut_pnp,total_pnp,udara_arm,ka_arm,bus_arm,asdp_arm,laut_arm,total_arm\\n';
  raw.forEach(d => {{
    csv += `${{d.date}},${{d.UDARA}},${{d.KA}},${{d.BUS}},${{d.ASDP}},${{d.LAUT}},${{d.TOTAL}},${{d.arm_UDARA}},${{d.arm_KA}},${{d.arm_BUS}},${{d.arm_ASDP}},${{d.arm_LAUT}},${{d.arm_TOTAL}}\\n`;
  }});
  const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', `strategihub_kemenhub_multimoda_${{currentTimelineRange}}_${{currentMetric}}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

// ---------------------------------------------------------------
// SIDEBAR METODOLOGI KEPADATAN CONTROLLER
// ---------------------------------------------------------------
function toggleExplanationSidebar(open) {{
  const sb = document.getElementById('sidebar-penjelasan-kepadatan');
  const backdrop = document.getElementById('backdrop-penjelasan');
  if (!sb) return;
  const isCurrentlyOpen = sb.classList.contains('translate-x-0');
  const shouldOpen = open !== undefined ? open : !isCurrentlyOpen;
  
  if (shouldOpen) {{
    sb.classList.remove('translate-x-full');
    sb.classList.add('translate-x-0');
    if (backdrop) {{
      backdrop.classList.remove('opacity-0', 'pointer-events-none');
      backdrop.classList.add('opacity-100', 'pointer-events-auto');
    }}
  }} else {{
    sb.classList.add('translate-x-full');
    sb.classList.remove('translate-x-0');
    if (backdrop) {{
      backdrop.classList.add('opacity-0', 'pointer-events-none');
      backdrop.classList.remove('opacity-100', 'pointer-events-auto');
    }}
  }}
}}

document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') {{
    toggleExplanationSidebar(false);
  }}
}});

// ---------------------------------------------------------------
// INITIALIZATION ON LOAD
// ---------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {{
  renderTimelineChart();
  renderMonthlyTable();
  renderDOWWorkspace();
}});
</script>
</body>
</html>
"""
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Production dashboard with interactive Leaflet GIS successfully generated: {OUTPUT_HTML}")
    print(f"File size: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")

if __name__ == '__main__':
    generate_dashboard()
