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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "scripts", "mobility_data_bundle.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "Dashboard_Mobilitas_Nasional_2026.html")

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
          <button onclick="switchTab('tab-timeline', 'Kronologi Harian (272 Hari)', this)" class="nav-btn active w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-semibold text-kemenhub-800 dark:text-blue-400 bg-kemenhub-50 dark:bg-blue-950/40 border border-slate-200 dark:border-blue-900/50 transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-sky-600 shrink-0"></span>
            <span class="truncate">Kronologi Harian (272H)</span>
          </button>

          <button onclick="switchTab('tab-lebaran', 'Puncak Lebaran 2026 (Mudik & Balik)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0"></span>
            <span class="truncate">Puncak Lebaran 2026</span>
          </button>

          <button onclick="switchTab('tab-modal-share', 'Pangsa Pasar Antar-Moda', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0"></span>
            <span class="truncate">Pangsa Pasar Antar-Moda</span>
          </button>

          <button onclick="switchTab('tab-load-factor', 'Rasio Beban Armada (Load Factor)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>
            <span class="truncate">Beban Armada</span>
          </button>

          <button onclick="switchTab('tab-top-hubs', 'Registri Simpul Transportasi (Top 30)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-purple-600 shrink-0"></span>
            <span class="truncate">Registri Simpul (Top 30)</span>
          </button>

          <button onclick="switchTab('tab-matrix', 'Matriks Rekapitulasi 13 Indikator', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan-600 shrink-0"></span>
            <span class="truncate">Matriks 13 Indikator</span>
          </button>

          <!-- TAB 7: LEAFLET SPATIAL MAP -->
          <button onclick="switchTab('tab-spatial-map', 'Peta Spasial Simpul (Leaflet GIS)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
            <span class="truncate font-semibold text-emerald-700 dark:text-emerald-400">Peta Spasial (Leaflet)</span>
          </button>

          <!-- TAB 8: FORECASTING NATARU 2026/2027 -->
          <button onclick="switchTab('tab-forecasting', 'Proyeksi & Prediksi Nataru 2026/2027', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
            <span class="truncate font-semibold text-indigo-700 dark:text-indigo-400">Proyeksi Nataru 2026</span>
          </button>

          <!-- BUTTON BUKA SIDEBAR METODOLOGI KEPADATAN -->
          <button onclick="toggleExplanationSidebar(true)" class="w-full mt-2.5 flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/80 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-all text-left group shadow-xs">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-indigo-600 animate-pulse shrink-0"></span>
              <span class="truncate">Tentang Data</span>
            </div>
            <span class="text-[9px] px-1.5 py-0.2 rounded bg-indigo-600 text-white font-mono uppercase">Info</span>
          </button>
        </nav>
      </div>

      <!-- Rentang Waktu Quick Filter -->
      <div>
        <div class="flex items-center justify-between px-2.5 mb-1.5">
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Rentang Waktu</p>
          <span class="text-[9px] text-slate-400 font-mono">1 Jan - 29 Sep</span>
        </div>
        <div class="space-y-1 bg-slate-50 dark:bg-slate-800/60 p-1.5 rounded-md border border-slate-200 dark:border-slate-800">
          <button onclick="setTimelineFilter('all', this)" class="btn-range active w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-semibold text-slate-900 dark:text-white bg-white dark:bg-slate-900 shadow-xs transition-all">
            <span>Sepanjang 2026</span>
            <span class="num-mono text-[10px] text-slate-500">272H</span>
          </button>
          <button onclick="setTimelineFilter('lebaran', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Puncak Lebaran</span>
            <span class="num-mono text-[10px] text-slate-500">17H</span>
          </button>
          <button onclick="setTimelineFilter('libur_sekolah', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Libur Sekolah</span>
            <span class="num-mono text-[10px] text-slate-500">31H</span>
          </button>
          <button onclick="setTimelineFilter('tahun_baru', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span>Tahun Baru</span>
            <span class="num-mono text-[10px] text-slate-500">15H</span>
          </button>
          <button id="btn-range-custom" onclick="setTimelineFilter('custom', this)" class="btn-range w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            <span class="flex items-center gap-1.5">
              <span>📅</span>
              <span>Kustom Tanggal</span>
            </span>
            <span id="badge-custom-days" class="num-mono text-[10px] text-slate-500">Pilih</span>
          </button>

          <!-- Custom Date Input Form -->
          <div id="panel-custom-range" class="hidden pt-2 border-t border-slate-200 dark:border-slate-700/60 space-y-2 px-1">
            <div>
              <label for="custom-start-date" class="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">Dari Tanggal:</label>
              <input type="date" id="custom-start-date" min="2026-01-01" max="2026-09-29" value="2026-03-01" onchange="applyCustomDateRange()" class="w-full text-xs font-mono bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer">
            </div>
            <div>
              <label for="custom-end-date" class="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">Sampai Tanggal:</label>
              <input type="date" id="custom-end-date" min="2026-01-01" max="2026-09-29" value="2026-03-31" onchange="applyCustomDateRange()" class="w-full text-xs font-mono bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer">
            </div>
            <button type="button" onclick="applyCustomDateRange()" class="w-full py-1.5 px-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-[11px] font-semibold transition-all shadow-xs flex items-center justify-center gap-1.5">
              <span>✓ Terapkan Rentang</span>
            </button>
          </div>
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
  <!-- SIDEBAR INFORMASI & KAMUS RUMUS DASHBOARD (DRAWER)             -->
  <!-- ============================================================= -->
  <div id="backdrop-penjelasan" onclick="toggleExplanationSidebar(false)" class="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 z-50 backdrop-blur-xs opacity-0 pointer-events-none transition-opacity duration-300"></div>

  <aside id="sidebar-penjelasan-kepadatan" class="fixed top-0 bottom-0 right-0 z-50 w-full sm:w-[540px] lg:w-[600px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col transform translate-x-full transition-transform duration-300 ease-in-out">
    
    <!-- Sidebar Header -->
    <div class="h-16 px-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 shrink-0 bg-slate-50/70 dark:bg-slate-800/40">
      <div class="flex items-center gap-2.5 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white text-sm shrink-0 shadow-xs">
          📘
        </div>
        <div class="truncate">
          <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight truncate">
            Informasi & Kamus Rumus Dashboard
          </h3>
          <p class="text-[10px] text-slate-500 font-sans truncate">
            Kamus Lengkap Formula Matematis, Integritas Data, Metodologi Kepadatan & Proyeksi
          </p>
        </div>
      </div>

      <button onclick="toggleExplanationSidebar(false)" class="p-1.5 rounded-md text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors" title="Tutup Sidebar">
        <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>
    </div>

    <!-- Scrollable Body with Clean Typography & Complete Math Formulas -->
    <div class="p-5 space-y-6 overflow-y-auto flex-1 text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
      
      <!-- Box 1: Sumber Data & Integritas Dataset -->
      <div class="bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 rounded-lg p-4 space-y-2.5">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
          <h4 class="text-xs font-bold text-indigo-900 dark:text-indigo-200 uppercase tracking-tight">
            1. Sumber Data & Integritas Dataset
          </h4>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Seluruh angka di dashboard bersumber dari data operasional <strong>StrategiHub PUSDATIN Kemenhub 2026</strong> (<code class="px-1 py-0.5 rounded bg-white dark:bg-slate-800 text-[10px] font-mono text-indigo-600 dark:text-indigo-300 border border-slate-200 dark:border-slate-700">strategihub_multimoda_2026.csv</code>, 18,3 MB).
        </p>
        <div class="text-[11px] space-y-1 bg-white dark:bg-slate-900 p-2.5 rounded border border-slate-200 dark:border-slate-800">
          <div>• <strong>Total Baris Bersih:</strong> <span class="font-mono font-bold text-slate-900 dark:text-white">209.964 baris</span> (tervalidasi dari 211.361 baris log mentah).</div>
          <div>• <strong>Periode Operasional:</strong> 1 Januari 2026 s.d. 29 September 2026 (<span class="font-mono font-bold">272 Hari</span>).</div>
          <div>• <strong>Cakupan Simpul:</strong> <span class="font-mono font-bold">1.208 simpul prasarana</span> (1.014 simpul berkoordinat valid, 194 simpul tanpa koordinat dipertahankan tanpa fabrikasi data).</div>
          <div>• <strong>Aturan Pembersihan:</strong> Baris duplikat identik dihapus (<code class="font-mono">keep=first</code>), sedangkan duplikat transaksi pada tanggal/simpul yang sama diagregasi dengan fungsi penjumlahan (<code class="font-mono">SUM</code>).</div>
        </div>
      </div>

      <!-- Box 2: Rumus Metrik Dasar (Total Penumpang & Armada) -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-sky-500"></span>
            2. Rumus Metrik Dasar (Total Penumpang & Armada)
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-sky-100 dark:bg-sky-900/60 text-sky-700 dark:text-sky-300">Agregat</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Setiap transaksi simpul prasarana mencatat pergerakan dua arah (kedatangan dan keberangkatan).
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px] font-mono">
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-2.5 rounded space-y-1">
            <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">Total Penumpang Simpul / Harian:</div>
            <div class="text-indigo-600 dark:text-indigo-400 font-bold">P_total = P_datang + P_berangkat</div>
            <div class="text-slate-500 text-[9px] font-sans">Menjumlahkan penumpang tiba dan penumpang naik.</div>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-2.5 rounded space-y-1">
            <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">Total Armada Beroperasi:</div>
            <div class="text-indigo-600 dark:text-indigo-400 font-bold">A_total = A_datang + A_berangkat</div>
            <div class="text-slate-500 text-[9px] font-sans">Menghitung trip/penerbangan yang dilayani.</div>
          </div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono">
          <div><strong>Rata-rata Penumpang Harian Nasional:</strong></div>
          <div class="text-slate-800 dark:text-slate-200 mt-0.5">P_avg = (∑ P_total) / 272 Hari = 371.890.120 / 272 = <strong>1.367.243 pnp/hari</strong></div>
        </div>
      </div>

      <!-- Box 3: Rumus Load Factor (Rasio Beban Armada P/A) -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
            3. Rumus Load Factor Proxy (Rasio Penumpang per Armada P/A)
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">P/A Ratio</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Load Factor dihitung sebagai proksi intensitas okupansi fisik rata-rata per satu satuan pergerakan armada:
        </p>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono space-y-1">
          <div class="text-indigo-600 dark:text-indigo-400 font-bold text-xs">Load Factor (P/A) = Total Penumpang / Total Trip Armada</div>
          <div class="text-slate-500 text-[10px] font-sans">
            Satuan: Penumpang/Flight (Udara), Penumpang/Trip KA (Kereta Api), Penumpang/Trip Bus (Bus), Penumpang/Trip Kapal (ASDP & Laut).
          </div>
        </div>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono space-y-1">
          <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">Delta Pertumbuhan Load Factor:</div>
          <div class="text-rose-600 dark:text-rose-400 font-bold">ΔLF (%) = [(LF_puncak - LF_baseline) / LF_baseline] × 100%</div>
        </div>
      </div>

      <!-- Box 4: Rumus Pangsa Pasar Moda (Modal Share) -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            4. Rumus Pangsa Pasar Antar-Moda (Modal Share %)
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300">Modal Share</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Proporsi kontribusi volume penumpang moda tertentu terhadap total mobilitas multimoda pada suatu periode (bulan atau hari):
        </p>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono space-y-1">
          <div class="text-emerald-600 dark:text-emerald-400 font-bold">Modal Share_moda (%) = (Penumpang_moda / Total_Penumpang_Multimoda) × 100%</div>
          <div class="text-slate-500 text-[10px] font-sans">
            Total Penumpang Multimoda = P_Udara + P_KA + P_Bus + P_ASDP + P_Laut.
          </div>
        </div>
      </div>

      <!-- Box 5: Rumus Periode Lebaran & Angka Lonjakan (Surge %) -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            5. Rumus Analisis Puncak Lebaran & Lonjakan (Surge %)
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300">Surge %</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Periode Posko Nasional Angkutan Lebaran 2026 berlangsung selama <strong>17 Hari (13 Maret s.d. 29 Maret 2026)</strong> dengan <strong>Hari H tunggal pada 21 Maret 2026</strong>.
        </p>
        <div class="space-y-2 text-[10px] font-mono">
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-2.5 rounded space-y-1">
            <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">A. Baseline Normal (Februari 2026):</div>
            <div class="text-indigo-600 dark:text-indigo-400 font-bold">P̄_Feb = (∑ P_Februari) / 28 Hari = 1.188.888 pnp/hari</div>
            <div class="text-slate-500 text-[9px] font-sans">Bulan Februari digunakan sebagai acuan normal karena bebas libur panjang nasional.</div>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-2.5 rounded space-y-1">
            <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">B. Persentase Lonjakan (Surge %):</div>
            <div class="text-rose-600 dark:text-rose-400 font-bold">Surge (%) = [(Volume_Puncak - P̄_Feb) / P̄_Feb] × 100%</div>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-2.5 rounded space-y-1">
            <div class="font-bold text-slate-900 dark:text-white font-sans text-xs">C. Penomoran Hari Posko Lebaran (Relatif Hari H):</div>
            <div class="text-slate-800 dark:text-slate-200 font-bold">ΔHari = Tanggal - 21 Maret 2026</div>
            <div class="text-slate-600 dark:text-slate-400 text-[9px] font-sans">
              Jika Δ &lt; 0 &rarr; <strong>H-|Δ|</strong> (contoh: 18 Mar &rarr; H-3 Mudik).<br>
              Jika Δ = 0 &rarr; <strong>Hari H</strong> (21 Mar, Hari Raya Idul Fitri 1447 H).<br>
              Jika Δ &gt; 0 &rarr; <strong>H+|Δ|</strong> (contoh: 24 Mar &rarr; H+3 Balik 1; 29 Mar &rarr; H+8 Balik 2).
            </div>
          </div>
        </div>
      </div>

      <!-- Box 6: Rumus Profil Musiman Mingguan (Day-of-Week Seasonality) -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            6. Rumus Profil Musiman Mingguan (Day of Week Index)
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300">DOW Index</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-300">
          Mengukur ritme mobilitas mingguan masyarakat pada hari kerja vs akhir pekan di luar masa libur ekstrem:
        </p>
        <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono space-y-1">
          <div class="text-amber-600 dark:text-amber-400 font-bold">Rata-rata Hari d: P̄_d = (∑ P_d) / N_d</div>
          <div class="text-amber-600 dark:text-amber-400 font-bold">Indeks Musiman (S_d) = P̄_d / P̄_keseluruhan</div>
          <div class="text-slate-500 text-[9px] font-sans mt-1">
            Urutan Mobilitas: Minggu (1,108x) &gt; Jumat (1,038x) &gt; Sabtu (1,018x) &gt; Senin (1,002x) &gt; Kamis (0,965x) &gt; Rabu (0,941x) &gt; Selasa (0,928x).
          </div>
        </div>
      </div>

      <!-- Box 7: Penentuan Kebutuhan Tambahan Armada Simpul (100% Data Keberangkatan SIASATI) -->
      <div class="space-y-3.5">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            7. Standar Penentuan Penambahan Armada Simpul (100% Data Keberangkatan)
          </h4>
          <p class="text-[11px] text-slate-500 mt-0.5">Penentuan persentase tambahan armada dihitung murni dari data keberangkatan (penumpang berangkat & armada berangkat):</p>
        </div>

        <!-- Tolok Ukur A -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>A. Mengapa Memakai Data Keberangkatan Saja?</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">Departures Only</span>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-300">
            Kemacetan dan antrean prasarana 100% terjadi di <strong>alur keberangkatan</strong> (penumpang menunggu di boarding hall, kendaraan mengantre di buffer zone pelabuhan, peron keberangkatan). Penumpang yang tiba (kedatangan) langsung keluar meninggalkan simpul tanpa menumpuk.
          </p>
        </div>

        <!-- Tolok Ukur B -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2.5">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>B. Kriteria Penentuan Berapa Persen Perlu Ditambah (Seluruh 1.010 Simpul Nasional)</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300">1.010 Simpul</span>
          </div>
          <div class="overflow-x-auto rounded border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-[11px] font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-600 dark:text-slate-400">
                <tr>
                  <th class="p-1.5">Klasifikasi Beban</th>
                  <th class="p-1.5">Kriteria Lonjakan Empiris</th>
                  <th class="p-1.5">Rekomendasi Tambahan (%)</th>
                  <th class="p-1.5">Cakupan Simpul Nasional</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
                <tr>
                  <td class="p-1.5 font-bold text-rose-600 dark:text-rose-400">🔴 Sangat Kritis</td>
                  <td class="p-1.5 font-mono">Beban &ge; 3,0x lipat atau pnp puncak &ge; 20.000</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+20%</td>
                  <td class="p-1.5">174 Simpul (Merak, Bakauheni, Gilimanuk, dll)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-orange-600 dark:text-orange-400">🟠 Tinggi / Kritis</td>
                  <td class="p-1.5 font-mono">Beban 1,8x &ndash; 2,9x lipat atau pnp puncak &ge; 10.000</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+15%</td>
                  <td class="p-1.5">267 Simpul (Pasar Senen, Ketapang, Poto Tano, dll)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-amber-600 dark:text-amber-400">🟡 Padat Tinggi</td>
                  <td class="p-1.5 font-mono">Beban 1,2x &ndash; 1,7x lipat atau pnp puncak &ge; 5.000</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+10%</td>
                  <td class="p-1.5">269 Simpul (CGK Soetta, DPS Bali, Juanda, Gambir, dll)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-emerald-600 dark:text-emerald-400">🟢 Terkendali</td>
                  <td class="p-1.5 font-mono">Beban &le; 1,2x lipat (siaga cadangan)</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+5%</td>
                  <td class="p-1.5">300 Simpul (Purabaya, Batam, Purboyo, dll)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Box 8: Rumus Model Prediktif Time Series Nataru 2026/2027 -->
      <div class="space-y-3">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-purple-500"></span>
            8. Rumus 1 Model Holt-Winters Terpadu & Akurasi Nataru
          </h4>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-purple-100 dark:bg-purple-900/60 text-purple-700 dark:text-purple-300">Holt-Winters 2025+2026</span>
        </div>
        <div class="p-3 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-[11px] font-mono space-y-2">
          <div class="font-bold text-indigo-700 dark:text-indigo-300 text-xs">Formulasi Model:</div>
          <div class="bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800">
            ŷ_{{t+h}} = (ℓ_t + ∑ φ^i b_t) × s_{{t+h-m(k+1)}} × ∏ W_shock
          </div>
          <div class="text-slate-500 text-[10px] font-sans">
            • <strong>Data Latih Gabungan:</strong> 635 hari kontinu (Tahun 2025: 365 hari + Tahun 2026: 270 hari) agar model belajar dari shock Nataru tahun sebelumnya.<br>
            • <strong>ℓ_t (Level) & b_t (Damped Trend):</strong> Tren pertumbuhan riil +5,13% YTD dari 2025 ke 2026 dengan peredam φ = 0,98.<br>
            • <strong>s (Multiplicative Seasonality)</strong> dengan siklus m = 7 hari.<br>
            • <strong>W_shock (Kalender Event Shock)</strong> dikalibrasi dari elastisitas lonjakan empiris libur nasional.<br>
            • <strong>Rentang Keyakinan 95%:</strong> CI_95% = ŷ_t ± 1,96 × RMSE.
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[10px] font-mono">
          <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div class="font-bold text-slate-900 dark:text-white">MAPE = 15,52%</div>
            <div class="text-[9px] text-slate-500 font-sans mt-0.5">WAPE = 7,41% • (100%/n) ∑ |(y - ŷ)/y|</div>
          </div>
          <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div class="font-bold text-slate-900 dark:text-white">RMSE = 185.286</div>
            <div class="text-[9px] text-slate-500 font-sans mt-0.5">RMSE = √[(1/n) ∑ (y - ŷ)²]</div>
          </div>
          <div class="p-2 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div class="font-bold text-slate-900 dark:text-white">MAE = 87.608</div>
            <div class="text-[9px] text-slate-500 font-sans mt-0.5">MAE = (1/n) ∑ |y - ŷ|</div>
          </div>
        </div>
      </div>

      <!-- Box 9: Formula Matematis Simulasi Tambahan Armada -->
      <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
        <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          9. Formula Matematis Simulasi Tambahan Armada Simpul
        </h4>
        <div class="space-y-1.5 text-[11px] font-mono text-slate-700 dark:text-slate-300">
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Tambahan Armada (Trip/h)</strong> = Armada_Baseline × (Persentase / 100)
          </div>
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Kapasitas Terbuka (Pnp)</strong> = Penumpang_Baseline × (Persentase / 100)
          </div>
          <div class="p-2 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <strong>Tingkat Kepadatan Baru (%)</strong> = Beban_Awal / (1 + Persentase / 100)
          </div>
        </div>
      </div>

    </div>

    <!-- Sidebar Footer Actions -->
    <div class="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between gap-3 shrink-0">
      <button onclick="toggleExplanationSidebar(false)" class="px-3 py-1.5 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 transition-colors">
        Tutup
      </button>
      <button onclick="toggleExplanationSidebar(false); switchTab('tab-forecasting', 'Proyeksi & Prediksi Nataru 2026/2027', document.querySelectorAll('.nav-btn')[7]);" class="px-3.5 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5">
        <span>Buka Simulator Simpul</span>
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
      </button>
    </div>

  </aside>

  <!-- Floating Action Button for Dashboard Information Sidebar -->
  <button onclick="toggleExplanationSidebar(true)" class="fixed bottom-6 right-6 z-40 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2.5 px-3.5 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2 border border-indigo-400 group" title="Buka Informasi & Kamus Rumus Dashboard">
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
          <span id="active-breadcrumb" class="font-semibold text-slate-900 dark:text-white truncate">Kronologi Harian (272 Hari)</span>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        <!-- Button Buka Sidebar Metodologi Kepadatan -->
        <button onclick="toggleExplanationSidebar(true)" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all" title="Buka Informasi & Kamus Rumus Dashboard">
          <svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
          <span class="hidden sm:inline">Tentang Data</span>
          <span class="sm:hidden">Info</span>
        </button>

        <!-- Dark/Light Theme Toggle -->
        <button onclick="toggleTheme()" class="p-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all" title="Ganti Mode Tampilan (Terang/Gelap)">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </div>
    </header>

    <!-- ============================================================= -->
    <!-- UNIVERSAL METRIC & DIRECTION CONTROLLER BAR (STICKY)          -->
    <!-- ============================================================= -->
    <section class="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 sticky top-16 z-30 px-4 sm:px-6 py-2.5 shadow-xs transition-all">
      <div class="flex flex-wrap items-center justify-between gap-3">
        
        <!-- Single Unified Metric & Direction Dropdown ("metrik dan pilihannya 1 aja dibagian atas") -->
        <div class="flex items-center gap-2.5">
          <label for="select-global-metric" class="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <span class="text-sm">📊</span>
            <span>Pilihan Metrik:</span>
          </label>
          <div class="relative">
            <select id="select-global-metric" onchange="setGlobalCombo(this.value)" class="text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 pr-8 text-slate-900 dark:text-white shadow-xs hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer transition-all">
              <option value="pnp_tot">Total Penumpang</option>
              <option value="pnp_brg" selected>Penumpang Berangkat</option>
              <option value="pnp_dat">Penumpang Datang</option>
              <option value="arm_dat">Armada Datang</option>
              <option value="arm_brg">Armada Berangkat</option>
              <option value="arm_tot">Total Armada</option>
            </select>
          </div>
        </div>

        <!-- Right: Active Status Indicator Pill -->
        <div class="flex items-center gap-2">
          <span id="global-active-pill" class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-800 dark:text-sky-300">
            <span class="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
            <span id="global-active-label">Penumpang Berangkat (Keberangkatan)</span>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <span id="global-active-val" class="font-bold text-slate-900 dark:text-white">209.143.560 orang</span>
          </span>
        </div>

      </div>
    </section>

    <!-- Integrated Executive Operational Strip -->
    <section class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      <div class="px-6 py-3.5">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-slate-800">
          
          <!-- Metric 1: Total Volume YTD -->
          <div class="pt-2 md:pt-0 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5" id="strip-card1-title">
              Total Mobilitas Penumpang YTD (Berangkat)
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-pnp">209.143.560</span>
              <span class="text-xs text-slate-500 font-medium" id="strip-unit-pnp">penumpang berangkat</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono" id="strip-avg-pnp">
              Rata-rata: <span class="font-semibold text-slate-700 dark:text-slate-300">768.910</span> pnp/hari (272 hari)
            </div>
          </div>

          <!-- Metric 2: All-Time Peak -->
          <div class="pt-3 md:pt-0 md:pl-4 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5" id="strip-card2-title">
              Puncak Tertinggi 2026 (Pnp)
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-rose-600 dark:text-rose-400 num-mono tracking-tight" id="strip-peak-val">1.443.593</span>
              <span class="text-xs text-slate-500 font-medium" id="strip-peak-unit">penumpang berangkat</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono" id="strip-peak-desc">
              24 Mar 2026 (H+3 Balik) • <span class="font-semibold text-rose-600 dark:text-rose-400">+121,2%</span> vs normal
            </div>
          </div>

          <!-- Metric 3: Mudik Peak -->
          <div class="pt-3 md:pt-0 md:pl-4 pr-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5" id="strip-card3-title">
              Puncak Arus Mudik (Pnp)
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-purple-700 dark:text-purple-400 num-mono tracking-tight" id="strip-mudik-val">1.358.209</span>
              <span class="text-xs text-slate-500 font-medium" id="strip-mudik-unit">penumpang berangkat</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono" id="strip-mudik-desc">
              18 Mar 2026 (H-3 Mudik) • <span class="font-semibold text-purple-700 dark:text-purple-400">+108,2%</span> vs normal
            </div>
          </div>

          <!-- Metric 4: Armada Beroperasi -->
          <div class="pt-3 md:pt-0 md:pl-4">
            <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5" id="strip-card4-title">
              Total Armada Operasi YTD (Berangkat)
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-arm">5.096.641</span>
              <span class="text-xs text-slate-500 font-medium" id="strip-unit-arm">trip berangkat</span>
            </div>
            <div class="text-[11px] text-slate-500 mt-1 num-mono" id="strip-desc-arm">
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
                  Kronologi Mobilitas Penumpang Keberangkatan 2026
                </h2>
                <span id="timeline-metric-badge" class="text-[11px] font-semibold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/60 px-2 py-0.5 rounded border border-sky-200 dark:border-sky-800">
                  Volume Penumpang • Berangkat
                </span>
              </div>
              <p id="timeline-chart-desc" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Volume harian agregat penumpang: Udara, Kereta Api, Bus, Penyeberangan ASDP, dan Laut (01 Jan s.d. 29 Sep 2026)
              </p>
            </div>

            <button id="timeline-badge-info" onclick="focusCustomRange()" title="Klik untuk pilih rentang tanggal kustom di sidebar" class="text-xs font-mono text-slate-600 dark:text-slate-300 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 dark:bg-slate-800 dark:hover:bg-slate-700 px-3 py-1 rounded border border-slate-200 dark:border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer">
              1 Jan 2026 - 29 Sep 2026 (272 Hari)
            </button>
          </div>

          <!-- Full-Width Chart Canvas -->
          <div class="relative w-full h-[430px] pt-2">
            <canvas id="chartTimelineCanvas"></canvas>
          </div>

          <!-- Chart Footnote with Interactive Guidance -->
          <div class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center text-xs text-slate-500">
            <div class="flex items-center gap-1.5">
              <span class="text-blue-600 dark:text-blue-400 font-semibold">ℹ Petunjuk:</span>
              <span>Klik nama moda pada legenda di kanan atas grafik untuk menyembunyikan atau menampilkan garis moda.</span>
            </div>
          </div>
        </div>

        <!-- Split Panel: Monthly Accumulation Table vs Day-of-Week Distribution -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- Left (7 Cols): Dense Monthly Data Table -->
          <div class="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Akumulasi Bulanan per Moda Transportasi</h3>
                <p id="monthly-table-subtitle" class="text-[11px] text-slate-500">Volume pergerakan dari Januari sampai dengan September 2026</p>
              </div>
              <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded border border-slate-200 dark:border-slate-700">9 Bulan (Jan - Sep)</span>
            </div>

            <div class="overflow-x-auto mt-3">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Bulan</th>
                    <th class="py-2.5 px-3 text-right text-sky-700 dark:text-sky-400">Udara</th>
                    <th class="py-2.5 px-3 text-right text-amber-700 dark:text-amber-400">Kereta Api</th>
                    <th class="py-2.5 px-3 text-right text-green-700 dark:text-green-400">Bus</th>
                    <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400">ASDP</th>
                    <th class="py-2.5 px-3 text-right text-cyan-700 dark:text-cyan-400">Laut</th>
                    <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total</th>
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

          <!-- Right (5 Cols): Day of Week Profile -->
          <div class="lg:col-span-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
            <div>
              <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Profil Hari dalam Seminggu</h3>
                  <p id="dow-chart-subtitle" class="text-[11px] text-slate-500">Rata-rata volume harian (Senin s.d. Minggu)</p>
                </div>
                <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded border border-slate-200 dark:border-slate-700">Senin - Minggu</span>
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
                    <th class="py-2 px-2.5 text-right">Udara</th>
                    <th class="py-2 px-2.5 text-right">KA</th>
                    <th class="py-2 px-2.5 text-right">Bus</th>
                    <th class="py-2 px-2.5 text-right">ASDP</th>
                    <th class="py-2 px-2.5 text-right">Laut</th>
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
          <div class="w-full flex items-stretch gap-1.5 sm:gap-2 overflow-x-auto pb-2.5 pt-1 px-1 rounded-lg border border-slate-200/90 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40" id="lebaran-scrubber">
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
                  <th class="py-2.5 px-3 text-right">Baseline Normal (Feb)</th>
                  <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400">Puncak Mudik (18 Mar / H-3)</th>
                  <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400">Lonjakan (%)</th>
                  <th class="py-2.5 px-3 text-right text-rose-700 dark:text-rose-400">Puncak Balik 1 (24 Mar / H+3)</th>
                  <th class="py-2.5 px-3 text-right text-rose-700 dark:text-rose-400">Lonjakan (%)</th>
                  <th class="py-2.5 px-3 text-right">Puncak Balik 2 (29 Mar / H+8)</th>
                  <th class="py-2.5 px-3 text-right">Lonjakan (%)</th>
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
        
        <!-- 100% Stacked Area Chart (Full Width) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Dinamika Pangsa Pasar Penumpang Bulanan (100% Stacked)</h3>
              <p class="text-[11px] text-slate-500">Pergeseran proporsi mobilitas 5 moda dari Januari sampai dengan September 2026</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Satuan: % Total</span>
          </div>

          <div class="relative w-full h-[360px] mt-3">
            <canvas id="chartModalShareAreaCanvas"></canvas>
          </div>
        </div>

        <!-- Normal vs Peak Comparison Doughnuts (Full Width, Placed Below Stacked Area Chart) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex flex-wrap items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 gap-2">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Komparasi Struktur Moda: Normal vs Puncak
              </h3>
              <p class="text-[11px] text-slate-500">Perbandingan pergeseran proporsi moda transportasi antara periode normal (Februari) dan puncak arus mudik Lebaran (Maret)</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Satuan: % & Penumpang</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-12 gap-6 mt-4 items-center">
            <!-- Normal (Februari) -->
            <div class="md:col-span-4 text-center bg-slate-50/50 dark:bg-slate-800/40 rounded-lg p-4 border border-slate-100 dark:border-slate-800">
              <div class="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Februari (Normal)</div>
              <div class="relative w-full h-[200px] flex items-center justify-center">
                <canvas id="donutNormalCanvas"></canvas>
              </div>
              <div id="donut-normal-total" class="text-[11px] text-slate-700 dark:text-slate-300 font-semibold mt-2 font-mono">Total: -</div>
            </div>

            <!-- Peak (Maret / Lebaran) -->
            <div class="md:col-span-4 text-center bg-slate-50/50 dark:bg-slate-800/40 rounded-lg p-4 border border-slate-100 dark:border-slate-800">
              <div class="text-[11px] font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wider mb-2">Maret (Lebaran)</div>
              <div class="relative w-full h-[200px] flex items-center justify-center">
                <canvas id="donutPeakCanvas"></canvas>
              </div>
              <div id="donut-peak-total" class="text-[11px] text-slate-700 dark:text-slate-300 font-semibold mt-2 font-mono">Total: -</div>
            </div>

            <!-- Insight Box -->
            <div class="md:col-span-4 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs flex flex-col justify-center h-full">
              <div class="font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
                <span class="inline-block w-2 h-2 rounded-full bg-purple-600"></span>
                <span>Dinamika Pangsa:</span>
              </div>
              <p class="text-slate-600 dark:text-slate-400 text-xs leading-relaxed">
                Pada periode Lebaran (Maret), pangsa ASDP melonjak dari <strong>11,8%</strong> menjadi <strong>17,9%</strong>, membuktikan pergeseran mobilitas ke penyeberangan kendaraan darat.
              </p>
              <div class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-[11px] text-slate-500">
                <span class="font-semibold text-slate-700 dark:text-slate-300">Catatan Analitis:</span>
                Kenaikan pangsa ASDP dan Kereta Api diiringi penurunan proporsi angkutan udara domestik saat puncak mudik nasional.
              </div>
            </div>
          </div>
        </div>

        <!-- Monthly Share Breakdown Table -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex flex-wrap items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 gap-2">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Tabel Persentase Pangsa Pasar Bulanan (%)
              </h3>
              <p class="text-[11px] text-slate-500">Distribusi proporsi pergerakan antar-moda dan total volume pergerakan bulanan</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Jan - Sep 2026</span>
          </div>

          <div class="overflow-x-auto mt-3">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3">Bulan</th>
                  <th class="py-2.5 px-3 text-right text-sky-700 dark:text-sky-400">Udara (%)</th>
                  <th class="py-2.5 px-3 text-right text-amber-700 dark:text-amber-400">Kereta Api (%)</th>
                  <th class="py-2.5 px-3 text-right text-green-700 dark:text-green-400">Bus (%)</th>
                  <th class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400">ASDP (%)</th>
                  <th class="py-2.5 px-3 text-right text-cyan-700 dark:text-cyan-400">Laut (%)</th>
                  <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total Volume</th>
                </tr>
              </thead>
              <tbody id="tbody-share" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>

          <!-- Footnote Catatan September* -->
          <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-start gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span class="font-bold text-amber-600 dark:text-amber-400 shrink-0">* Catatan September:</span>
            <p class="leading-relaxed text-[11.5px]">
              Data bulan <strong>September 2026</strong> merupakan data berjalan (parsial) dengan periode cut-off <strong>1 s.d. 29 September 2026 (29 hari)</strong>, sehingga belum genap satu bulan kalender penuh (30 hari). Angka total volume merupakan akumulasi sementara hingga tanggal cut-off, dan nilai persentase mencerminkan pangsa pasar riil pergerakan moda selama kurun waktu tersebut.
            </p>
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
                      <th class="py-2 px-2.5 text-right">Normal</th>
                      <th class="py-2 px-2.5 text-right text-purple-700 dark:text-purple-400">Mudik</th>
                      <th class="py-2 px-2.5 text-right text-rose-700 dark:text-rose-400">Balik</th>
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
              Bandar Udara
            </button>
            <button onclick="filterHubModa('KA', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Stasiun Kereta Api
            </button>
            <button onclick="filterHubModa('BUS', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Bus
            </button>
            <button onclick="filterHubModa('ASDP', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Pelabuhan ASDP
            </button>
            <button onclick="filterHubModa('LAUT', this)" class="hub-tab-btn px-3 py-1.5 rounded-md font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              Pelabuhan Laut
            </button>
          </div>

          <!-- Search, Metric, Direction & Period Options -->
          <div class="flex items-center gap-2.5 flex-wrap">
            <div class="relative">
              <input type="text" id="input-hub-search" onkeyup="handleHubSearch(this.value)" placeholder="Cari simpul, kota, provinsi..." class="w-52 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-xs rounded-md px-3 py-1.5 focus:bg-white dark:focus:bg-slate-900">
            </div>

            <!-- Hub Metric Toggle -->
            <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
              <button id="hubs-btn-pnp" onclick="setGlobalMetric('pnp')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Penumpang</button>
              <button id="hubs-btn-arm" onclick="setGlobalMetric('arm')" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Armada</button>
            </div>

            <!-- Hub Direction Toggle -->
            <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
              <button id="hubs-dir-tot" onclick="setGlobalDirection('tot')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Dua Arah</button>
              <button id="hubs-dir-dat" onclick="setGlobalDirection('dat')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Datang</button>
              <button id="hubs-dir-brg" onclick="setGlobalDirection('brg')" class="px-2 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Berangkat</button>
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
                  <th class="py-2.5 px-3 text-right">Volume Penumpang</th>
                  <th class="py-2.5 px-3 text-right">Armada Beroperasi</th>
                  <th class="py-2.5 px-3 w-56 text-right">Skala Volume Relatif</th>
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
                  <th class="py-3 px-3 text-right text-sky-700 dark:text-sky-400">UDARA</th>
                  <th class="py-3 px-3 text-right text-amber-700 dark:text-amber-400">KERETA API</th>
                  <th class="py-3 px-3 text-right text-green-700 dark:text-green-400">BUS</th>
                  <th class="py-3 px-3 text-right text-purple-700 dark:text-purple-400">ASDP</th>
                  <th class="py-3 px-3 text-right text-cyan-700 dark:text-cyan-400">LAUT</th>
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
                Sebaran geografis 1.014 simpul transportasi nasional terpetakan di seluruh wilayah Indonesia (ukuran lingkaran proporsional terhadap volume penumpang)
              </p>
            </div>

            <!-- Metric & Basemap & Fullscreen Controls -->
            <div class="flex items-center gap-2.5 flex-wrap">
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="map-metric-pnp" onclick="setGlobalMetric('pnp')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Penumpang</button>
                <button id="map-metric-arm" onclick="setGlobalMetric('arm')" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Armada</button>
              </div>

              <!-- Map Direction Toggle -->
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="map-dir-tot" onclick="setGlobalDirection('tot')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Dua Arah</button>
                <button id="map-dir-dat" onclick="setGlobalDirection('dat')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Datang</button>
                <button id="map-dir-brg" onclick="setGlobalDirection('brg')" class="px-2 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Berangkat</button>
              </div>

              <!-- Basemap Badge (OpenStreetMap Bebas API Key) -->
              <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300" title="OpenStreetMap (OSM) Bebas API Key">
                <svg class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
                <span>Peta: Terbuka (OSM)</span>
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

          <!-- Filter Moda, Peringkat / Skala Pangsa Simpul & Badges -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
            <!-- Filter Moda Buttons -->
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
                🚌 Bus (139)
              </button>
              <button onclick="filterSpatialModa('ASDP', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-purple-800 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                ⛴ ASDP (158)
              </button>
              <button onclick="filterSpatialModa('LAUT', this)" class="map-moda-btn px-2.5 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-cyan-800 dark:text-cyan-300 hover:bg-cyan-50 dark:hover:bg-cyan-950/40 border border-slate-200 dark:border-slate-700 transition-all">
                🚢 Laut (267)
              </button>
            </div>

            <!-- Filter Ranking / Skala Pangsa Pasar Simpul & Badges -->
            <div class="flex items-center gap-2.5 flex-wrap">
              <div class="flex items-center gap-1.5">
                <label for="select-spatial-scale" class="text-slate-500 dark:text-slate-400 font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1 shrink-0">
                  <span>🎯 Peringkat / Pangsa:</span>
                </label>
                <div class="relative">
                  <select id="select-spatial-scale" onchange="setSpatialScaleFilter(this.value)" class="bg-slate-50 dark:bg-slate-800/90 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold rounded-md pl-2.5 pr-7 py-1.5 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none appearance-none cursor-pointer shadow-xs">
                    <option value="all" selected>Semua Simpul Terpetakan (100%)</option>
                    <option value="top10">🏆 10 Simpul Terbesar</option>
                    <option value="top20">⭐ 20 Simpul Terbesar</option>
                    <option value="top30">📍 30 Simpul Terbesar</option>
                    <option value="top50">🌐 50 Simpul Terbesar</option>
                    <option value="pareto80">⚡ Titik Simpul 80% Pangsa Pasar</option>
                    <option value="pareto90">📊 Titik Simpul 90% Pangsa Pasar</option>
                  </select>
                  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <!-- Summary Badges -->
              <div class="flex items-center gap-1.5 text-xs">
                <span id="badge-spatial-count" class="px-2.5 py-1 rounded font-mono text-[11px] bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-semibold">
                  ● 1.014 Terpetakan (100%)
                </span>
                <span id="badge-spatial-unmapped" class="px-2.5 py-1 rounded font-mono text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                  ◌ 194 Koordinat Dikosongkan
                </span>
              </div>
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
                Simulasi horizon 100 hari (30 Sep 2026 – 7 Jan 2027) mengantisipasi lonjakan kapasitas angkutan Natal 2026 dan Tahun Baru 2027
              </p>
            </div>

            <!-- Horizon Badges with 2025 Baseline -->
            <div class="flex items-center gap-2 text-xs flex-wrap">
              <span class="px-2.5 py-1 rounded font-mono text-[11px] bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-semibold">
                Baseline Komparasi: Siasati 2025 (365H)
              </span>
              <span class="px-2.5 py-1 rounded font-mono text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                Historis 2026: 1 Jan - 29 Sep (272H)
              </span>
              <span class="px-2.5 py-1 rounded font-mono text-[11px] bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Horizon Prediksi: 30 Sep '26 - 7 Jan '27 (100H)
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
                  <option value="BUS">🚌 Bus</option>
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

        <!-- Executive Projections Strip (4 Cards) with 2025 Comparison -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Card 1: Total Volume Nataru -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Proyeksi Nataru (18 Hari)</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">18 Des - 4 Jan</span>
            </div>
            <div id="card-fc-total-pnp" class="num-mono text-2xl font-extrabold text-slate-900 dark:text-white">32.771.287</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span>Rerata: <strong id="card-fc-avg-pnp" class="text-slate-800 dark:text-slate-200">1.820.627</strong> /h</span>
              <span id="card-fc-total-yoy" class="text-emerald-600 dark:text-emerald-400 font-bold">+6,3% vs 2025</span>
            </div>
          </div>

          <!-- Card 2: Puncak Arus Mudik Natal -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Puncak Mudik Natal (H-1)</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">Kamis, 24 Des</span>
            </div>
            <div id="card-fc-xmas-pnp" class="num-mono text-2xl font-extrabold text-amber-700 dark:text-amber-400">2.082.191</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span class="text-slate-500">vs 2025: 1.922.912</span>
              <span id="card-fc-xmas-yoy" class="text-amber-600 dark:text-amber-400 font-bold">+8,3% YoY</span>
            </div>
          </div>

          <!-- Card 3: Puncak Arus Balik Tahun Baru -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Puncak Balik Tahun Baru</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300">Minggu, 3 Jan</span>
            </div>
            <div id="card-fc-ny-pnp" class="num-mono text-2xl font-extrabold text-rose-700 dark:text-rose-400">1.746.435</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span class="text-slate-500">vs 2025: 1.582.119</span>
              <span id="card-fc-ny-yoy" class="text-rose-600 dark:text-rose-400 font-bold">+10,4% YoY</span>
            </div>
          </div>

          <!-- Card 4: Kebutuhan Armada Peak -->
          <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
            <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Kebutuhan Armada Puncak</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">Siaga Operasi</span>
            </div>
            <div id="card-fc-arm-peak" class="num-mono text-2xl font-extrabold text-slate-900 dark:text-white">46.518</div>
            <div class="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
              <span class="text-slate-500">vs 2025: 44.447 trip</span>
              <span id="card-fc-arm-yoy" class="text-emerald-600 dark:text-emerald-400 font-bold">+4,7% YoY</span>
            </div>
          </div>
        </div>

        <!-- Dedicated Multi-Modal Nataru 2026 vs 2025 Comparison Card -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Tabel Komparasi Angkutan Nataru 2026/2027 vs Realisasi Tahun Lalu (2025)
                </h3>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                Perbandingan volume penumpang riil posko 18 hari (18 Des – 4 Jan) per moda transportasi serta estimasi pergeseran pangsa pasar
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-semibold">
                Benchmark Riil: Siasati 2025 (365 Hari)
              </span>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800 text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-2.5 px-3">Moda Transportasi</th>
                  <th class="py-2.5 px-3 text-right">Realisasi 2025 (Pnp)</th>
                  <th class="py-2.5 px-3 text-right">Pangsa '25</th>
                  <th class="py-2.5 px-3 text-right text-indigo-700 dark:text-indigo-400">Proyeksi 2026 (Pnp)</th>
                  <th class="py-2.5 px-3 text-right text-indigo-700 dark:text-indigo-400">Pangsa '26</th>
                  <th class="py-2.5 px-3 text-right font-semibold">Selisih (Δ Pnp)</th>
                  <th class="py-2.5 px-3 text-center">Pertumbuhan YoY</th>
                  <th class="py-2.5 px-3 text-left">Dinamika Operasional & Kapasitas</th>
                </tr>
              </thead>
              <tbody id="tbody-forecast-comparison" class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-200">
                <!-- Populated dynamically by JS -->
              </tbody>
            </table>
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
                Garis solid mewakili realisasi riil (Jan - Sep). Garis putus-putus ungu mewakili proyeksi 1 model Holt-Winters terpadu (Okt - Jan 2027) dengan shock musiman Nataru dari data latih 2025 beserta pita keyakinan 95%.
              </p>
            </div>
            <div class="flex items-center gap-3 text-[11px] font-mono flex-wrap">
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-0.5 bg-sky-600"></span> Realisasi 2026</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-0.5 border-t border-dashed border-indigo-500"></span> Proyeksi Holt-Winters</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-0.5 border-t border-dashed border-emerald-500"></span> Realisasi 2025 (Data Latih)</span>
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
                Pengujian out-of-sample: 609 hari data latih gabungan 2025–2026 (1 Jan 2025 – 1 Sep 2026) vs 28 hari data uji (2 Sep – 29 Sep 2026)
              </p>
            </div>
            <span class="text-[11px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
              Metode: 1 Model Holt-Winters Terpadu (phi=0.98, s=7) + Shock Kalender Nataru
            </span>
          </div>

          <!-- Metric Badges & Mathematical Definitions -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <!-- MAPE -->
            <div class="p-3.5 rounded-md bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-emerald-800 dark:text-emerald-300">MAPE (Mean Absolute % Error)</span>
                <span class="text-[10px] font-bold bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 px-1.5 py-0.5 rounded">WAPE: 7,41%</span>
              </div>
              <div class="text-2xl font-black font-mono text-emerald-700 dark:text-emerald-400">15,52%</div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Rata-rata deviasi absolut terhadap data riil (WAPE tertimbang 7,41%). Model terbukti akurat dan konsisten menangkap ritme musiman mingguan.
              </p>
            </div>

            <!-- RMSE -->
            <div class="p-3.5 rounded-md bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-indigo-800 dark:text-indigo-300">RMSE (Root Mean Squared Error)</span>
                <span class="text-[10px] font-bold bg-indigo-200 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-1.5 py-0.5 rounded">Basis 95% CI</span>
              </div>
              <div class="text-2xl font-black font-mono text-indigo-700 dark:text-indigo-400">185.286 <span class="text-xs font-normal text-slate-500">pnp/hari</span></div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Standar deviasi kesalahan dalam satuan penumpang riil. Menjadi basis ilmiah rentang ketidakpastian 95% (CI_95% = ŷ ± 1,96 × RMSE).
              </p>
            </div>

            <!-- MAE & Relative Ratio -->
            <div class="p-3.5 rounded-md bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-800 dark:text-slate-200">MAE & Rasio Error Absolut</span>
                <span class="text-[10px] font-mono text-slate-500">Rerata: 1,183M pnp</span>
              </div>
              <div class="text-2xl font-black font-mono text-slate-800 dark:text-slate-100">87.608 <span class="text-xs font-normal text-slate-500">pnp (15,67%)</span></div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                Rata-rata selisih volume absolut harian. Deviasi 87k pnp ini hanya mewakili 15,67% dari rata-rata pergerakan harian nasional.
              </p>
            </div>

            <!-- Mode Breakdown Summary -->
            <div class="p-3.5 rounded-md bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
              <span class="text-[11px] font-bold text-slate-800 dark:text-slate-200 block">Akurasi Per Moda (Uji 28H)</span>
              <div class="space-y-1 text-[11px] font-mono pt-0.5">
                <div class="flex justify-between items-center"><span>🚌 Bus:</span> <span class="font-bold text-emerald-600">10,7%</span> <span class="text-[9px] text-slate-400 font-sans">(WAPE 4,9%)</span></div>
                <div class="flex justify-between items-center"><span>🚆 Kereta Api:</span> <span class="font-bold text-emerald-600">11,1%</span> <span class="text-[9px] text-slate-400 font-sans">(WAPE 11,3%)</span></div>
                <div class="flex justify-between items-center"><span>🚢 Laut:</span> <span class="font-bold text-emerald-600">9,6%</span> <span class="text-[9px] text-slate-400 font-sans">(WAPE 6,3%)</span></div>
                <div class="flex justify-between items-center"><span>⛴ ASDP:</span> <span class="font-bold text-emerald-600">19,0%</span> <span class="text-[9px] text-slate-400 font-sans">(WAPE)</span></div>
                <div class="flex justify-between items-center"><span>✈ Udara:</span> <span class="font-bold text-amber-600">26,9%</span> <span class="text-[9px] text-slate-400 font-sans">(WAPE 25,1%)</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section: Interactive Per-Prasarana / Simpul Simulation Panel -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-5">
          <!-- Header -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                  Tabel Rekomendasi Kebutuhan Penambahan Armada di Seluruh Simpul Prasarana Nasional (1.010 Simpul)
                </h3>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                Dihitung murni berdasarkan data keberangkatan empiris SIASATI (penumpang berangkat / armada berangkat). Dilengkapi filter jumlah baris (Top 10, Top 25, Top 50, Top 100, hingga Semua Simpul), filter moda, status urgensi, dan pencarian cepat.
              </p>
            </div>
            
            <button onclick="toggleExplanationSidebar(true)" class="px-2.5 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all flex items-center gap-1.5" title="Buka Sidebar Metodologi Kepadatan">
              <svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              <span>📘 Metodologi Data</span>
            </button>
          </div>

          <!-- Highlight Summary Strip: 5 Modas (Dynamically Updated) -->
          <div id="simpulHighlightCards" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2.5 text-xs">
            <!-- Rendered dynamically by JS -->
          </div>

          <!-- Controls Bar 1: Filter Moda & Status Urgensi -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div class="flex flex-wrap items-center gap-1.5 text-xs font-semibold" id="simpulFilterContainer">
              <button type="button" onclick="filterSimpulModa('ALL', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-indigo-600 text-white shadow-xs font-bold transition-all">Semua Moda (1.010)</button>
              <button type="button" onclick="filterSimpulModa('UDARA', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold">✈ Udara (230)</button>
              <button type="button" onclick="filterSimpulModa('LAUT', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold">🚢 Laut (209)</button>
              <button type="button" onclick="filterSimpulModa('ASDP', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold">⛴ ASDP Feri (196)</button>
              <button type="button" onclick="filterSimpulModa('BUS', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold">🚌 Bus AKAP (189)</button>
              <button type="button" onclick="filterSimpulModa('KA', this)" class="simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold">🚆 Kereta Api (186)</button>
            </div>
            
            <div class="flex items-center gap-2">
              <label for="select-simpul-status" class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider shrink-0">Status:</label>
              <select id="select-simpul-status" onchange="setSimpulStatusFilter(this.value)" class="text-xs px-2.5 py-1.5 rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer">
                <option value="ALL" selected>Semua Status Urgensi</option>
                <option value="20">🔴 Sangat Kritis (+20%)</option>
                <option value="15">🟠 Tinggi / Kritis (+15%)</option>
                <option value="10">🟡 Padat Tinggi (+10%)</option>
                <option value="5">🟢 Terkendali (+5%)</option>
              </select>
            </div>
          </div>

          <!-- Controls Bar 2: Limit Selector, Search & Sort -->
          <div class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/80">
            <div class="flex flex-wrap items-center gap-3">
              <!-- Limit Dropdown Requested by User -->
              <div class="flex items-center gap-1.5">
                <label for="select-simpul-limit" class="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                  <span>📊 Tampilkan:</span>
                </label>
                <select id="select-simpul-limit" onchange="setSimpulDisplayLimit(this.value)" class="text-xs font-bold px-2.5 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-white dark:bg-slate-800 text-indigo-700 dark:text-indigo-300 shadow-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer">
                  <option value="10">🏆 Top 10 Simpul Utama</option>
                  <option value="25" selected>⭐ Top 25 Simpul Terpadat</option>
                  <option value="50">📍 Top 50 Simpul Nasional</option>
                  <option value="100">🌐 Top 100 Simpul Terbesar</option>
                  <option value="250">📋 Top 250 Simpul</option>
                  <option value="all">🇮🇩 Semua Simpul (1.010 Simpul)</option>
                </select>
              </div>

              <!-- Sorting Dropdown -->
              <div class="flex items-center gap-1.5">
                <label for="select-simpul-sort" class="text-xs font-semibold text-slate-500">Urutkan:</label>
                <select id="select-simpul-sort" onchange="setSimpulSortBy(this.value)" class="text-xs px-2.5 py-1.5 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer">
                  <option value="pnp_desc" selected>Penumpang Puncak (Tertinggi)</option>
                  <option value="ratio_desc">Lonjakan Beban (Tertinggi)</option>
                  <option value="pct_desc">% Tambah Armada (Tertinggi)</option>
                  <option value="add_desc">Tambahan Unit Fisik (Terbanyak)</option>
                  <option value="name_asc">Nama Simpul (A - Z)</option>
                </select>
              </div>
            </div>

            <div class="flex items-center gap-3 w-full sm:w-auto">
              <div class="relative w-full sm:w-64">
                <input type="text" id="simpulSearchInput" oninput="onSimpulSearchChange(this.value)" placeholder="Cari nama simpul, kota, provinsi..." class="w-full text-xs px-2.5 py-1.5 pl-8 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <span class="absolute left-2.5 top-1.5 text-slate-400 text-xs">🔍</span>
              </div>
            </div>
          </div>

          <!-- Top Hub Matrix Table -->
          <div class="space-y-3">
            <div class="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg max-h-[750px] overflow-y-auto">
              <table class="w-full text-left border-collapse text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10 backdrop-blur-md">
                  <tr>
                    <th class="py-2.5 px-3">No & Simpul Prasarana</th>
                    <th class="py-2.5 px-3">Sarana Transportasi</th>
                    <th class="py-2.5 px-3">Keberangkatan Normal</th>
                    <th class="py-2.5 px-3">Keberangkatan Puncak</th>
                    <th class="py-2.5 px-3 text-center">Lonjakan Beban</th>
                    <th class="py-2.5 px-3 text-center">Status</th>
                    <th class="py-2.5 px-3 text-center">Perlu Tambah (%)</th>
                    <th class="py-2.5 px-3 text-right">Tambahan Unit</th>
                    <th class="py-2.5 px-3 text-right">Total Operasi</th>
                    <th class="py-2.5 px-3">Rekomendasi Aksi Lapangan Kemenhub</th>
                  </tr>
                </thead>
                <tbody id="tbody-simpul-matrix" class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-200">
                  <!-- Rendered dynamically by JS -->
                </tbody>
              </table>
            </div>

            <!-- Pagination & Navigation Controls -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-1 text-xs">
              <span id="badge-simpul-count" class="font-mono text-slate-500">
                Menampilkan 1 - 25 dari 1.010 Simpul Nasional
              </span>

              <div id="simpulPaginationNav" class="flex items-center gap-1.5">
                <button type="button" id="btn-simpul-prev" onclick="changeSimpulPage(-1)" class="px-3 py-1 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all font-medium">
                  &laquo; Sebelumnya
                </button>
                <span id="label-simpul-page" class="font-mono px-2 text-slate-600 dark:text-slate-400 font-semibold">
                  Halaman 1 dari 41
                </span>
                <button type="button" id="btn-simpul-next" onclick="changeSimpulPage(1)" class="px-3 py-1 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all font-medium">
                  Berikutnya &raquo;
                </button>
              </div>
            </div>

            <!-- Operational Summary Box -->
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
                  <th class="py-2.5 px-3 text-right text-indigo-700 dark:text-indigo-400">Proyeksi 2026/27</th>
                  <th class="py-2.5 px-3 text-right text-emerald-700 dark:text-emerald-400">Realisasi 2025</th>
                  <th class="py-2.5 px-3 text-center">Pertumbuhan YoY</th>
                  <th class="py-2.5 px-3 text-right">Rentang 95% CI</th>
                  <th class="py-2.5 px-3 text-center">Status Lonjakan</th>
                  <th class="py-2.5 px-3 text-right">Armada Proyeksi</th>
                  <th class="py-2.5 px-3 text-right text-slate-500">Armada 2025</th>
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
const decFmt = (n, decimals = 1) => {{
  if (n === null || n === undefined || isNaN(n)) return '-';
  return Number(n).toLocaleString('id-ID', {{
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }});
}};

const formatVolCompact = (v) => {{
  if (v === null || v === undefined || isNaN(v)) return '-';
  const num = Number(v);
  if (num >= 1e6) {{
    return (num / 1e6).toLocaleString('id-ID', {{ minimumFractionDigits: 1, maximumFractionDigits: 1 }}) + 'M';
  }} else if (num >= 1e3) {{
    return (num / 1e3).toLocaleString('id-ID', {{ minimumFractionDigits: 0, maximumFractionDigits: 0 }}) + 'k';
  }}
  return num.toLocaleString('id-ID');
}};

// State Variables
let isSidebarOpen = true;
let currentTimelineRange = 'all';
let customStartDate = '2026-03-01';
let customEndDate = '2026-03-31';
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

// ---------------------------------------------------------------
// UNIVERSAL METRIC & DIRECTION STATE MANAGEMENT
// ---------------------------------------------------------------
let currentMetric = 'pnp'; // 'pnp' (Penumpang) or 'arm' (Armada)
let currentDirection = 'brg'; // 'tot' (Total/Dua Arah), 'dat' (Datang), 'brg' (Berangkat)
let activeLebaranDate = '2026-03-21';
let monthlySelectedMetric = 'pnp_brg';
let dowSelectedMetric = 'pnp_brg';

const METRIC_CODE_CONFIG = {{
  'pnp_tot': {{ label: 'Total Penumpang', type: 'pnp', dir: 'Dua Arah', unit: 'penumpang', dowUnit: 'pnp/hari', color: '#0284c7' }},
  'pnp_brg': {{ label: 'Penumpang Berangkat', type: 'pnp', dir: 'Berangkat', unit: 'penumpang', dowUnit: 'pnp/hari', color: '#0369a1' }},
  'pnp_dat': {{ label: 'Penumpang Datang', type: 'pnp', dir: 'Datang', unit: 'penumpang', dowUnit: 'pnp/hari', color: '#0ea5e9' }},
  'arm_dat': {{ label: 'Armada Datang', type: 'arm', dir: 'Datang', unit: 'armada/trip', dowUnit: 'trip/hari', color: '#6366f1' }},
  'arm_brg': {{ label: 'Armada Berangkat', type: 'arm', dir: 'Berangkat', unit: 'armada/trip', dowUnit: 'trip/hari', color: '#4f46e5' }},
  'arm_tot': {{ label: 'Total Armada', type: 'arm', dir: 'Dua Arah', unit: 'armada/trip', dowUnit: 'trip/hari', color: '#8b5cf6' }}
}};

function getMetricKeyFromCode(code, moda = 'TOTAL') {{
  if (code === 'pnp_tot') return moda;
  if (code === 'pnp_dat') return 'pdat_' + moda;
  if (code === 'pnp_brg') return 'pbrg_' + moda;
  if (code === 'arm_tot') return 'arm_' + moda;
  if (code === 'arm_dat') return 'adat_' + moda;
  if (code === 'arm_brg') return 'abrg_' + moda;
  return moda;
}}

function changeMonthlyMetric(code) {{
  monthlySelectedMetric = code;
  renderMonthlyTable();
}}

function changeDowMetric(code) {{
  dowSelectedMetric = code;
  renderDOWWorkspace();
}}

function getMetricKey(moda = 'TOTAL') {{
  if (currentMetric === 'pnp') {{
    if (currentDirection === 'tot') return moda;
    if (currentDirection === 'dat') return 'pdat_' + moda;
    if (currentDirection === 'brg') return 'pbrg_' + moda;
  }} else {{
    if (currentDirection === 'tot') return 'arm_' + moda;
    if (currentDirection === 'dat') return 'adat_' + moda;
    if (currentDirection === 'brg') return 'abrg_' + moda;
  }}
  return moda;
}}

function getHubMetricKey() {{
  if (currentMetric === 'pnp') {{
    if (currentDirection === 'tot') return 'pnp';
    if (currentDirection === 'dat') return 'p_dat';
    if (currentDirection === 'brg') return 'p_brg';
  }} else {{
    if (currentDirection === 'tot') return 'arm';
    if (currentDirection === 'dat') return 'a_dat';
    if (currentDirection === 'brg') return 'a_brg';
  }}
  return 'pnp';
}}

function setGlobalCombo(comboVal) {{
  if (!comboVal) return;
  const parts = comboVal.split('_');
  currentMetric = parts[0];
  currentDirection = parts[1];
  monthlySelectedMetric = comboVal;
  dowSelectedMetric = comboVal;
  updateDashboardMetricAndDirection();
}}

function setGlobalMetric(metric) {{
  currentMetric = metric;
  const combo = currentMetric + '_' + currentDirection;
  monthlySelectedMetric = combo;
  dowSelectedMetric = combo;
  updateDashboardMetricAndDirection();
}}

function setGlobalDirection(direction) {{
  currentDirection = direction;
  const combo = currentMetric + '_' + currentDirection;
  monthlySelectedMetric = combo;
  dowSelectedMetric = combo;
  updateDashboardMetricAndDirection();
}}

function changeMonthlyMetric(metricVal) {{
  setGlobalCombo(metricVal);
}}

function changeDowMetric(metricVal) {{
  setGlobalCombo(metricVal);
}}

function setTimelineMetric(metric) {{ setGlobalMetric(metric); }}
function setSpatialMapMetric(metric) {{ setGlobalMetric(metric); }}

function formatPeakDescDate(dateStr, tagStr, fallbackPhase) {{
  if (!dateStr) return '';
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  const parts = dateStr.split('-');
  let dStr = dateStr;
  if (parts.length === 3) {{
    const d = parseInt(parts[2], 10);
    const m = months[parseInt(parts[1], 10) - 1] || parts[1];
    dStr = `${{d}} ${{m}} ${{parts[0]}}`;
  }}
  let cleanTag = (tagStr || '').split('(')[0].trim();
  if (!cleanTag) cleanTag = fallbackPhase || '';
  else if (fallbackPhase && !cleanTag.toLowerCase().includes(fallbackPhase.toLowerCase())) {{
    cleanTag += ' ' + fallbackPhase;
  }}
  return cleanTag ? `${{dStr}} (${{cleanTag}})` : dStr;
}}

function updateDashboardMetricAndDirection() {{
  const isPnp = currentMetric === 'pnp';
  const combo = currentMetric + '_' + currentDirection;
  const s = (DATA.metrics_summary && DATA.metrics_summary[combo]) || {{
    label: isPnp ? 'Penumpang • Dua Arah (Total)' : 'Armada • Dua Arah (Total)',
    unit: isPnp ? 'penumpang' : 'trip armada',
    ytd: isPnp ? 371890120 : 10033092,
    avg: isPnp ? 1367243 : 36886,
    peak_val: isPnp ? 2415296 : 47213,
    peak_desc: isPnp ? '24 Mar 2026 (H+3 Balik)' : '17 Mar 2026 (H-4 Mudik)',
    peak_surge_pct: isPnp ? 103.2 : 35.2,
    mudik_val: isPnp ? 2258512 : 47213,
    mudik_desc: isPnp ? '18 Mar 2026 (H-3 Mudik)' : '17 Mar 2026 (H-4 Mudik)',
    mudik_surge_pct: isPnp ? 90.0 : 35.2,
    formula: isPnp ? (currentDirection === 'dat' ? '∑ P_datang' : currentDirection === 'brg' ? '∑ P_berangkat' : '∑ (P_datang + P_berangkat)') : (currentDirection === 'dat' ? '∑ Trip_datang' : currentDirection === 'brg' ? '∑ Trip_berangkat' : '∑ (Trip Datang + Trip Berangkat)')
  }};

  // 0. Sync Single Global Metric Dropdown ("metrik dan pilihannya 1 aja dibagian atas")
  const selGlobal = document.getElementById('select-global-metric');
  if (selGlobal) selGlobal.value = combo;

  // 1. Sync All Metric Buttons across Dashboard
  const metricBtns = [
    {{ pnp: 'global-btn-pnp', arm: 'global-btn-arm' }},
    {{ pnp: 'hubs-btn-pnp', arm: 'hubs-btn-arm' }},
    {{ pnp: 'map-metric-pnp', arm: 'map-metric-arm' }}
  ];
  metricBtns.forEach(pair => {{
    const bPnp = document.getElementById(pair.pnp);
    const bArm = document.getElementById(pair.arm);
    if (bPnp && bArm) {{
      bPnp.classList.toggle('bg-white', isPnp);
      bPnp.classList.toggle('dark:bg-slate-900', isPnp);
      bPnp.classList.toggle('text-slate-900', isPnp);
      bPnp.classList.toggle('dark:text-white', isPnp);
      bPnp.classList.toggle('shadow-xs', isPnp);
      bPnp.classList.toggle('text-slate-600', !isPnp);

      bArm.classList.toggle('bg-white', !isPnp);
      bArm.classList.toggle('dark:bg-slate-900', !isPnp);
      bArm.classList.toggle('text-slate-900', !isPnp);
      bArm.classList.toggle('dark:text-white', !isPnp);
      bArm.classList.toggle('shadow-xs', !isPnp);
      bArm.classList.toggle('text-slate-600', isPnp);
    }}
  }});

  // 2. Sync All Direction Buttons across Dashboard
  const dirSets = [
    {{ tot: 'global-btn-dir-tot', dat: 'global-btn-dir-dat', brg: 'global-btn-dir-brg' }},
    {{ tot: 'hubs-dir-tot', dat: 'hubs-dir-dat', brg: 'hubs-dir-brg' }},
    {{ tot: 'map-dir-tot', dat: 'map-dir-dat', brg: 'map-dir-brg' }}
  ];
  dirSets.forEach(set => {{
    ['tot', 'dat', 'brg'].forEach(d => {{
      const btn = document.getElementById(set[d]);
      if (btn) {{
        const isActive = currentDirection === d;
        btn.classList.toggle('bg-white', isActive);
        btn.classList.toggle('dark:bg-slate-900', isActive);
        btn.classList.toggle('text-slate-900', isActive);
        btn.classList.toggle('dark:text-white', isActive);
        btn.classList.toggle('shadow-xs', isActive);
        btn.classList.toggle('text-slate-600', !isActive);
      }}
    }});
  }});

  // Update Dynamic Direction Button Text
  const lblDat = document.getElementById('lbl-dir-dat');
  if (lblDat) lblDat.innerText = isPnp ? 'Penumpang Datang' : 'Armada Datang';
  const lblBrg = document.getElementById('lbl-dir-brg');
  if (lblBrg) lblBrg.innerText = isPnp ? 'Penumpang Berangkat' : 'Armada Berangkat';

  // 3. Update Global Status Pill
  const pillLabel = document.getElementById('global-active-label');
  const pillVal = document.getElementById('global-active-val');
  if (pillLabel) pillLabel.innerText = s.label;
  if (pillVal) pillVal.innerText = `${{numFmt(s.ytd)}} ${{isPnp ? 'orang' : 'armada'}}`;

  // 4. Update Executive Strip KPIs
  const elCard1Title = document.getElementById('strip-card1-title');
  if (elCard1Title) elCard1Title.innerText = `Total Mobilitas ${{isPnp ? 'Penumpang' : 'Armada'}} YTD (${{currentDirection === 'dat' ? 'Datang' : currentDirection === 'brg' ? 'Berangkat' : 'Dua Arah'}})`;
  const elTotalPnp = document.getElementById('strip-total-pnp');
  if (elTotalPnp) elTotalPnp.innerText = numFmt(s.ytd);
  const elUnitPnp = document.getElementById('strip-unit-pnp');
  if (elUnitPnp) elUnitPnp.innerText = s.unit;
  const elAvgPnp = document.getElementById('strip-avg-pnp');
  if (elAvgPnp) elAvgPnp.innerHTML = `Rata-rata: <span class="font-semibold text-slate-700 dark:text-slate-300">${{numFmt(s.avg)}}</span> ${{isPnp ? 'pnp' : 'trip'}}/hari (272 hari)`;

  // Card 2: Peak
  const elCard2Title = document.getElementById('strip-card2-title');
  if (elCard2Title) elCard2Title.innerText = `Puncak Tertinggi 2026 (${{isPnp ? 'Pnp' : 'Armada'}})`;
  const elPeakVal = document.getElementById('strip-peak-val');
  if (elPeakVal) elPeakVal.innerText = numFmt(s.peak_val);
  const elPeakUnit = document.getElementById('strip-peak-unit');
  if (elPeakUnit) elPeakUnit.innerText = s.unit;
  const elPeakDesc = document.getElementById('strip-peak-desc');
  if (elPeakDesc) {{
    const peakDateStr = (s.peak_desc && s.peak_desc !== 'undefined') ? s.peak_desc : formatPeakDescDate(s.peak_date, s.peak_tag, 'Balik');
    const peakPrefix = (peakDateStr && peakDateStr !== 'undefined') ? `${{peakDateStr}} • ` : '';
    const peakSurge = (s.peak_surge_pct !== undefined && s.peak_surge_pct !== null) ? `<span class="font-semibold text-rose-600 dark:text-rose-400">+${{decFmt(s.peak_surge_pct, 1)}}%</span> vs normal` : '';
    elPeakDesc.innerHTML = `${{peakPrefix}}${{peakSurge}}`.trim();
  }}

  // Card 3: Mudik Peak
  const elCard3Title = document.getElementById('strip-card3-title');
  if (elCard3Title) elCard3Title.innerText = `Puncak Arus Mudik (${{isPnp ? 'Pnp' : 'Armada'}})`;
  const elMudikVal = document.getElementById('strip-mudik-val');
  if (elMudikVal) elMudikVal.innerText = numFmt(s.mudik_val);
  const elMudikUnit = document.getElementById('strip-mudik-unit');
  if (elMudikUnit) elMudikUnit.innerText = s.unit;
  const elMudikDesc = document.getElementById('strip-mudik-desc');
  if (elMudikDesc) {{
    const mudikDateStr = (s.mudik_desc && s.mudik_desc !== 'undefined') ? s.mudik_desc : formatPeakDescDate(s.mudik_date, s.mudik_tag, 'Mudik');
    const mudikPrefix = (mudikDateStr && mudikDateStr !== 'undefined') ? `${{mudikDateStr}} • ` : '';
    const mudikSurge = (s.mudik_surge_pct !== undefined && s.mudik_surge_pct !== null) ? `<span class="font-semibold text-purple-700 dark:text-purple-400">+${{decFmt(s.mudik_surge_pct, 1)}}%</span> vs normal` : '';
    elMudikDesc.innerHTML = `${{mudikPrefix}}${{mudikSurge}}`.trim();
  }}

  // Card 4: Complementary Opposing Metric
  const oppCombo = (isPnp ? 'arm_' : 'pnp_') + currentDirection;
  const oppS = (DATA.metrics_summary && DATA.metrics_summary[oppCombo]) || {{}};
  const elCard4Title = document.getElementById('strip-card4-title');
  if (elCard4Title) elCard4Title.innerText = isPnp ? `Total Armada Operasi YTD (${{currentDirection === 'dat' ? 'Datang' : currentDirection === 'brg' ? 'Berangkat' : 'Dua Arah'}})` : `Total Penumpang YTD (${{currentDirection === 'dat' ? 'Datang' : currentDirection === 'brg' ? 'Berangkat' : 'Dua Arah'}})`;
  const elTotalArm = document.getElementById('strip-total-arm');
  if (elTotalArm && oppS.ytd) elTotalArm.innerText = numFmt(oppS.ytd);
  const elUnitArm = document.getElementById('strip-unit-arm');
  if (elUnitArm && oppS.unit) elUnitArm.innerText = oppS.unit;

  // 5. Update Tab 1 (Kronologi & DOW & Monthly)
  const heading = document.getElementById('timeline-chart-heading');
  if (heading) heading.innerText = `Kronologi ${{isPnp ? 'Mobilitas Penumpang' : 'Armada Beroperasi'}} ${{currentDirection === 'dat' ? 'Kedatangan' : currentDirection === 'brg' ? 'Keberangkatan' : 'Multimoda'}} 2026`;
  const badge = document.getElementById('timeline-metric-badge');
  if (badge) {{
    badge.innerText = `${{isPnp ? 'Volume Penumpang' : 'Armada Beroperasi'}} • ${{currentDirection === 'dat' ? 'Datang' : currentDirection === 'brg' ? 'Berangkat' : 'Dua Arah'}}`;
  }}
  
  // Sync Tab 1 selection with global selection
  const globalCode = currentMetric + '_' + currentDirection;
  monthlySelectedMetric = globalCode;
  dowSelectedMetric = globalCode;

  renderTimelineChart();
  renderMonthlyTable();
  renderDOWWorkspace();

  // 6. Update Tab 2 (Lebaran)
  if (chartLebaranLine) {{
    chartLebaranLine.destroy();
    chartLebaranLine = null;
  }}
  renderLebaranWorkspace();

  // 7. Update Tab 3 (Modal Share)
  if (chartModalShareArea) {{
    chartModalShareArea.destroy();
    chartModalShareArea = null;
    if (chartDonutNormal) {{ chartDonutNormal.destroy(); chartDonutNormal = null; }}
    if (chartDonutPeak) {{ chartDonutPeak.destroy(); chartDonutPeak = null; }}
  }}
  renderModalShareWorkspace();

  // 8. Update Tab 5 (Top Hubs)
  renderHubsTable();

  // 9. Update Tab 6 (Matrix 13 Indikator)
  renderMatrixTable();

  // 10. Update Tab 7 (Leaflet Spatial Map)
  renderSpatialMapNodes();
}}

// ---------------------------------------------------------------
// TAB 1: KRONOLOGI MOBILITAS CONTROLLER
// ---------------------------------------------------------------
function getFilteredTimelineData() {{
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') return all.filter(d => d.date >= '2026-03-13' && d.date <= '2026-03-29');
  if (currentTimelineRange === 'libur_sekolah') return all.filter(d => d.date >= '2026-06-15' && d.date <= '2026-07-15');
  if (currentTimelineRange === 'tahun_baru') return all.filter(d => d.date >= '2026-01-01' && d.date <= '2026-01-15');
  if (currentTimelineRange === 'custom') {{
    const s = customStartDate || '2026-01-01';
    const e = customEndDate || '2026-09-29';
    return all.filter(d => d.date >= s && d.date <= e);
  }}
  return all;
}}

function renderTimelineChart() {{
  const raw = getFilteredTimelineData();
  const ctx = document.getElementById('chartTimelineCanvas').getContext('2d');
  const labels = raw.map(d => d.date);
  const isDark = document.documentElement.classList.contains('dark');
  const totalColor = isDark ? '#f8fafc' : '#0f172a';
  const unit = currentMetric === 'pnp' ? 'penumpang' : 'trip armada';

  const datasets = [
    {{ label: 'Total Multimoda', data: raw.map(d => d[getMetricKey('TOTAL')]), borderColor: totalColor, borderWidth: 2, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Udara', data: raw.map(d => d[getMetricKey('UDARA')]), borderColor: COLOR.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Kereta Api', data: raw.map(d => d[getMetricKey('KA')]), borderColor: COLOR.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Bus', data: raw.map(d => d[getMetricKey('BUS')]), borderColor: COLOR.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'ASDP', data: raw.map(d => d[getMetricKey('ASDP')]), borderColor: COLOR.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Laut', data: raw.map(d => d[getMetricKey('LAUT')]), borderColor: COLOR.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
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
          callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{unit}}` }}
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
            callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v >= 1e3 ? (v/1e3).toFixed(0) + 'k' : v)) 
          }} 
        }}
      }}
    }}
  }});

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
  if (btn) {{
    btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
    btn.classList.remove('text-slate-600', 'dark:text-slate-400');
  }}

  const customPanel = document.getElementById('panel-custom-range');
  if (customPanel) {{
    if (rangeKey === 'custom') {{
      customPanel.classList.remove('hidden');
    }} else {{
      customPanel.classList.add('hidden');
    }}
  }}

  if (rangeKey === 'custom') {{
    applyCustomDateRange(true);
  }} else {{
    const labelMap = {{
      'all': '1 Jan 2026 - 29 Sep 2026 (272 Hari)',
      'lebaran': '13 Mar 2026 - 29 Mar 2026 (17 Hari)',
      'libur_sekolah': '15 Jun 2026 - 15 Jul 2026 (31 Hari)',
      'tahun_baru': '1 Jan 2026 - 15 Jan 2026 (15 Hari)'
    }};
    const infoBadge = document.getElementById('timeline-badge-info');
    if (infoBadge) infoBadge.innerText = labelMap[rangeKey] || '';
    renderTimelineChart();
  }}
}}

function formatDateIndo(dateStr) {{
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length !== 3) return dateStr;
  const day = parseInt(parts[2], 10);
  const mIndex = parseInt(parts[1], 10) - 1;
  const year = parts[0];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  return `${{day}} ${{months[mIndex] || ''}} ${{year}}`;
}}

function applyCustomDateRange(triggerRender = true) {{
  const startEl = document.getElementById('custom-start-date');
  const endEl = document.getElementById('custom-end-date');
  if (!startEl || !endEl) return;

  let sVal = startEl.value || '2026-01-01';
  let eVal = endEl.value || '2026-09-29';

  // Batasi agar sesuai batas dataset
  if (sVal < '2026-01-01') sVal = '2026-01-01';
  if (sVal > '2026-09-29') sVal = '2026-09-29';
  if (eVal < '2026-01-01') eVal = '2026-01-01';
  if (eVal > '2026-09-29') eVal = '2026-09-29';

  if (sVal > eVal) {{
    const tmp = sVal;
    sVal = eVal;
    eVal = tmp;
    startEl.value = sVal;
    endEl.value = eVal;
  }}

  customStartDate = sVal;
  customEndDate = eVal;

  const d1 = new Date(sVal + 'T00:00:00');
  const d2 = new Date(eVal + 'T00:00:00');
  const diffDays = Math.max(1, Math.round((d2 - d1) / (1000 * 60 * 60 * 24)) + 1);

  const customBadge = document.getElementById('badge-custom-days');
  if (customBadge) customBadge.innerText = `${{diffDays}}H`;

  const infoBadge = document.getElementById('timeline-badge-info');
  if (infoBadge) {{
    infoBadge.innerText = `${{formatDateIndo(sVal)}} - ${{formatDateIndo(eVal)}} (${{diffDays}} Hari)`;
  }}

  if (currentTimelineRange !== 'custom') {{
    const btn = document.getElementById('btn-range-custom');
    if (btn) setTimelineFilter('custom', btn);
  }} else if (triggerRender) {{
    renderTimelineChart();
  }}
}}

function focusCustomRange() {{
  if (!isSidebarOpen) toggleSidebar();
  const btn = document.getElementById('btn-range-custom');
  if (btn) setTimelineFilter('custom', btn);
  const input = document.getElementById('custom-start-date');
  if (input) {{
    setTimeout(() => input.focus(), 150);
  }}
}}

function renderMonthlyTable() {{
  const ms = DATA.monthly_summary;
  const tbody = document.getElementById('tbody-monthly');
  if (!tbody) return;
  tbody.innerHTML = '';
  
  const code = monthlySelectedMetric || (currentMetric + '_' + currentDirection);
  const cfg = METRIC_CODE_CONFIG[code] || {{ label: 'Total Penumpang' }};

  ms.forEach((m) => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-200">${{m.label}}</td>
      <td class="py-2.5 px-3 text-right">${{numFmt(m[getMetricKeyFromCode(code, 'UDARA')])}}</td>
      <td class="py-2.5 px-3 text-right">${{numFmt(m[getMetricKeyFromCode(code, 'KA')])}}</td>
      <td class="py-2.5 px-3 text-right">${{numFmt(m[getMetricKeyFromCode(code, 'BUS')])}}</td>
      <td class="py-2.5 px-3 text-right">${{numFmt(m[getMetricKeyFromCode(code, 'ASDP')])}}</td>
      <td class="py-2.5 px-3 text-right">${{numFmt(m[getMetricKeyFromCode(code, 'LAUT')])}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{numFmt(m[getMetricKeyFromCode(code, 'TOTAL')])}}</td>
    `;
    tbody.appendChild(tr);
  }});

  const subEl = document.getElementById('monthly-table-subtitle');
  if (subEl) {{
    subEl.innerText = `Akumulasi ${{cfg.label}} dari Januari sampai dengan September 2026`;
  }}
}}

function renderDOWWorkspace() {{
  const dow = DATA.dow_summary;
  const ctxEl = document.getElementById('chartDOWCanvas');
  if (!ctxEl) return;
  const ctx = ctxEl.getContext('2d');
  const isDark = document.documentElement.classList.contains('dark');
  
  const code = dowSelectedMetric || (currentMetric + '_' + currentDirection);
  const cfg = METRIC_CODE_CONFIG[code] || {{ label: 'Total Penumpang', type: 'pnp', unit: 'penumpang', dowUnit: 'pnp/hari', color: '#0284c7' }};
  const isPnp = cfg.type === 'pnp';

  if (chartDOW) chartDOW.destroy();
  chartDOW = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: dow.map(d => d.dow),
      datasets: [{{
        label: `Rata-rata ${{cfg.label}}`,
        data: dow.map(d => d[getMetricKeyFromCode(code, 'TOTAL')]),
        backgroundColor: cfg.color || (isPnp ? '#0284c7' : '#6366f1'),
        borderRadius: 4
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ 
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => ` Rata-rata: ${{numFmt(ctx.raw)}} ${{cfg.dowUnit}}`
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b' }} }},
        y: {{ 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}, 
          ticks: {{ 
            color: isDark ? '#94a3b8' : '#64748b', 
            font: {{ family: 'JetBrains Mono' }}, 
            callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v >= 1e3 ? (v/1e3).toFixed(0) + 'k' : v)) 
          }} 
        }}
      }}
    }}
  }});

  const subEl = document.getElementById('dow-chart-subtitle');
  if (subEl) {{
    subEl.innerText = `Rata-rata volume harian (${{cfg.label}}) - Senin s.d. Minggu`;
  }}

  const tbody = document.getElementById('tbody-dow');
  if (!tbody) return;
  tbody.innerHTML = '';
  dow.forEach(d => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-sans font-medium text-slate-900 dark:text-slate-200">${{d.dow}}</td>
      <td class="py-2 px-2.5 text-right">${{numFmt(d[getMetricKeyFromCode(code, 'UDARA')])}}</td>
      <td class="py-2 px-2.5 text-right">${{numFmt(d[getMetricKeyFromCode(code, 'KA')])}}</td>
      <td class="py-2 px-2.5 text-right">${{numFmt(d[getMetricKeyFromCode(code, 'BUS')])}}</td>
      <td class="py-2 px-2.5 text-right">${{numFmt(d[getMetricKeyFromCode(code, 'ASDP')])}}</td>
      <td class="py-2 px-2.5 text-right">${{numFmt(d[getMetricKeyFromCode(code, 'LAUT')])}}</td>
      <td class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">${{numFmt(d[getMetricKeyFromCode(code, 'TOTAL')])}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 2: PUNCAK LEBARAN CONTROLLER
// ---------------------------------------------------------------
function selectLebaranDate(dateStr) {{
  activeLebaranDate = dateStr;
  const day = DATA.lebaran_daily.find(d => d.date === dateStr);
  if (!day) return;

  const isPnp = currentMetric === 'pnp';
  const tagEl = document.getElementById('insp-tag');
  if (tagEl) {{
    tagEl.innerText = day.tag;
    if (day.is_h_day) {{
      tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800';
    }} else if (day.is_peak_mudik) {{
      tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800';
    }} else if (day.is_peak_balik1 || day.is_peak_balik2) {{
      tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800';
    }} else {{
      tagEl.className = 'px-2 py-0.5 rounded font-bold text-xs bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-700';
    }}
  }}

  const elPhase = document.getElementById('insp-phase');
  if (elPhase) elPhase.innerText = day.desc;
  const elDate = document.getElementById('insp-date');
  if (elDate) elDate.innerText = day.date;
  const elSum = document.getElementById('insp-summary');
  if (elSum) {{
    elSum.innerText = `Total ${{isPnp ? 'Penumpang' : 'Armada'}}: ${{numFmt(day[getMetricKey('TOTAL')])}} • ${{isPnp ? 'Total Armada: ' + numFmt(day.arm_TOTAL) + ' Trip/Flight' : 'Total Penumpang: ' + numFmt(day.TOTAL) + ' Orang'}}`;
  }}

  // Sinkronisasi status aktif tombol scrubber (ring indikator)
  document.querySelectorAll('#lebaran-scrubber button').forEach(b => {{
    const isMatch = b.getAttribute('data-date') === dateStr;
    b.classList.toggle('ring-2', isMatch);
    b.classList.toggle('ring-blue-600', isMatch);
    b.classList.toggle('dark:ring-blue-400', isMatch);
    b.classList.toggle('shadow-sm', isMatch);
  }});

  const container = document.getElementById('insp-breakdown');
  if (container) {{
    container.innerHTML = `
      <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
        <div class="text-[10px] font-bold text-sky-700 dark:text-sky-400">UDARA</div>
        <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day[getMetricKey('UDARA')])}}</div>
      </div>
      <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
        <div class="text-[10px] font-bold text-amber-700 dark:text-amber-400">KERETA API</div>
        <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day[getMetricKey('KA')])}}</div>
      </div>
      <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
        <div class="text-[10px] font-bold text-green-700 dark:text-green-400">BUS</div>
        <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day[getMetricKey('BUS')])}}</div>
      </div>
      <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
        <div class="text-[10px] font-bold text-purple-700 dark:text-purple-400">ASDP</div>
        <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day[getMetricKey('ASDP')])}}</div>
      </div>
      <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
        <div class="text-[10px] font-bold text-cyan-700 dark:text-cyan-400">LAUT</div>
        <div class="num-mono text-xs font-bold text-slate-900 dark:text-white">${{numFmt(day[getMetricKey('LAUT')])}}</div>
      </div>
    `;
  }}
}}

function renderLebaranWorkspace() {{
  const strip = document.getElementById('lebaran-scrubber');
  if (strip) {{
    strip.innerHTML = '';
    const isPnp = currentMetric === 'pnp';
    DATA.lebaran_daily.forEach((d) => {{
      const btn = document.createElement('button');
      btn.setAttribute('data-date', d.date);
      const isMudik = !!d.is_peak_mudik;
      const isBalik = !!(d.is_peak_balik1 || d.is_peak_balik2);
      const isHDay = !!d.is_h_day;
      let tagShort = d.tag.startsWith('Hari H') ? 'HARI H' : d.tag.split(' ')[0];

      let btnClass = 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-400 dark:hover:border-slate-500';
      let tagColor = 'text-slate-500 dark:text-slate-400';

      if (isHDay) {{
        btnClass = 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-400 dark:border-emerald-700 text-emerald-900 dark:text-emerald-200 font-bold';
        tagColor = 'text-emerald-700 dark:text-emerald-300 font-bold';
      }} else if (isMudik) {{
        btnClass = 'bg-purple-50 dark:bg-purple-950/40 border-purple-300 dark:border-purple-800 text-purple-900 dark:text-purple-200 font-semibold';
        tagColor = 'text-purple-700 dark:text-purple-400 font-bold';
      }} else if (isBalik) {{
        btnClass = 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200 font-semibold';
        tagColor = 'text-rose-700 dark:text-rose-400 font-bold';
      }}

      const val = d[getMetricKey('TOTAL')];
      const valFmt = isPnp ? (val / 1e6).toFixed(1) + 'M' : (val >= 1e3 ? (val / 1e3).toFixed(1) + 'k' : val);

      btn.className = `flex-1 min-w-[56px] shrink-0 text-center px-1.5 sm:px-2 py-1.5 rounded-md border text-xs transition-all cursor-pointer shadow-2xs hover:shadow-xs ${{btnClass}}`;
      btn.innerHTML = `
        <div class="text-[9px] uppercase tracking-wider font-semibold ${{tagColor}}">${{tagShort}}</div>
        <div class="text-xs font-bold num-mono">${{valFmt}}</div>
        <div class="text-[9px] text-slate-400 num-mono">${{d.date.substring(5)}}</div>
      `;
      btn.onclick = () => {{
        selectLebaranDate(d.date);
      }};
      strip.appendChild(btn);
    }});
    selectLebaranDate(activeLebaranDate);
  }}

  const isDark = document.documentElement.classList.contains('dark');
  const ctxLine = document.getElementById('chartLebaranLineCanvas').getContext('2d');
  const ld = DATA.lebaran_daily;

  if (chartLebaranLine) chartLebaranLine.destroy();
  chartLebaranLine = new Chart(ctxLine, {{
    type: 'line',
    data: {{
      labels: ld.map(d => d.date.substring(5) + ' (' + (d.tag.startsWith('Hari H') ? 'Hari H' : d.tag.split(' ')[0]) + ')'),
      datasets: [
        {{ label: 'Total', data: ld.map(d => d[getMetricKey('TOTAL')]), borderColor: isDark ? '#ffffff' : '#0f172a', borderWidth: 2, pointRadius: 2, tension: 0.15 }},
        {{ label: 'Udara', data: ld.map(d => d[getMetricKey('UDARA')]), borderColor: COLOR.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Kereta Api', data: ld.map(d => d[getMetricKey('KA')]), borderColor: COLOR.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Bus', data: ld.map(d => d[getMetricKey('BUS')]), borderColor: COLOR.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'ASDP', data: ld.map(d => d[getMetricKey('ASDP')]), borderColor: COLOR.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Laut', data: ld.map(d => d[getMetricKey('LAUT')]), borderColor: COLOR.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
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
          }}
        }},
        tooltip: {{
          callbacks: {{
            label: ctx => ` ${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{currentMetric === 'pnp' ? 'penumpang' : 'trip'}}`
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', maxRotation: 45, font: {{ size: 9, family: 'JetBrains Mono' }} }} }},
        y: {{ 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, 
          ticks: {{ 
            color: isDark ? '#94a3b8' : '#64748b', 
            font: {{ family: 'JetBrains Mono', size: 10 }}, 
            callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v >= 1e3 ? (v/1e3).toFixed(0) + 'k' : v)) 
          }} 
        }}
      }}
    }}
  }});

  if (!chartSurgeBar) {{
    const ctxSurge = document.getElementById('chartSurgeBarCanvas').getContext('2d');
    const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
    const labelsSurge = ['ASDP', 'Bus', 'Kereta Api', 'Laut', 'Udara', 'TOTAL'];
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
    if (tbody) {{
      tbody.innerHTML = '';
      modas.forEach((m, idx) => {{
        const s = DATA.surge_summary[m];
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{labelsSurge[idx]}}</td>
          <td class="py-2.5 px-3 text-right">${{numFmt(s.baseline)}}</td>
          <td class="py-2.5 px-3 text-right font-bold text-purple-700 dark:text-purple-400">${{numFmt(s.peak_mudik)}}</td>
          <td class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400 font-semibold">+${{decFmt(s.surge_mudik_pct, 1)}}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-rose-700 dark:text-rose-400">${{numFmt(s.peak_balik1)}}</td>
          <td class="py-2.5 px-3 text-right text-rose-700 dark:text-rose-400 font-semibold">+${{decFmt(s.surge_balik1_pct, 1)}}%</td>
          <td class="py-2.5 px-3 text-right">${{numFmt(s.peak_balik2)}}</td>
          <td class="py-2.5 px-3 text-right">+${{decFmt(s.surge_balik2_pct, 1)}}%</td>
        `;
        tbody.appendChild(tr);
      }});
    }}
  }}
}}

// ---------------------------------------------------------------
// TAB 3: MODAL SHARE CONTROLLER
// ---------------------------------------------------------------
function renderModalShareWorkspace() {{
  const isDark = document.documentElement.classList.contains('dark');
  const ms = DATA.monthly_summary;
  const ctx = document.getElementById('chartModalShareAreaCanvas').getContext('2d');
  const unitStr = currentMetric === 'pnp' ? 'penumpang' : 'trip armada';

  // Compute shares dynamically for each month
  const shares = ms.map(m => {{
    const tot = m[getMetricKey('TOTAL')] || 1;
    return {{
      label: m.label,
      UDARA: Number(((m[getMetricKey('UDARA')] / tot) * 100).toFixed(1)),
      KA: Number(((m[getMetricKey('KA')] / tot) * 100).toFixed(1)),
      BUS: Number(((m[getMetricKey('BUS')] / tot) * 100).toFixed(1)),
      ASDP: Number(((m[getMetricKey('ASDP')] / tot) * 100).toFixed(1)),
      LAUT: Number(((m[getMetricKey('LAUT')] / tot) * 100).toFixed(1)),
      TOTAL: m[getMetricKey('TOTAL')],
      vol_UDARA: m[getMetricKey('UDARA')],
      vol_KA: m[getMetricKey('KA')],
      vol_BUS: m[getMetricKey('BUS')],
      vol_ASDP: m[getMetricKey('ASDP')],
      vol_LAUT: m[getMetricKey('LAUT')]
    }};
  }});

  if (chartModalShareArea) chartModalShareArea.destroy();
  chartModalShareArea = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: shares.map(m => m.label.split(' ')[0]),
      datasets: [
        {{ label: 'Udara', data: shares.map(m => m.UDARA), volumes: shares.map(m => m.vol_UDARA), borderColor: COLOR.UDARA, backgroundColor: 'rgba(2, 132, 199, 0.45)', fill: true, tension: 0.15 }},
        {{ label: 'Kereta Api', data: shares.map(m => m.KA), volumes: shares.map(m => m.vol_KA), borderColor: COLOR.KA, backgroundColor: 'rgba(217, 119, 6, 0.45)', fill: true, tension: 0.15 }},
        {{ label: 'Bus', data: shares.map(m => m.BUS), volumes: shares.map(m => m.vol_BUS), borderColor: COLOR.BUS, backgroundColor: 'rgba(22, 163, 74, 0.45)', fill: true, tension: 0.15 }},
        {{ label: 'ASDP', data: shares.map(m => m.ASDP), volumes: shares.map(m => m.vol_ASDP), borderColor: COLOR.ASDP, backgroundColor: 'rgba(147, 51, 234, 0.45)', fill: true, tension: 0.15 }},
        {{ label: 'Laut', data: shares.map(m => m.LAUT), volumes: shares.map(m => m.vol_LAUT), borderColor: COLOR.LAUT, backgroundColor: 'rgba(8, 145, 178, 0.45)', fill: true, tension: 0.15 }},
      ]
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
          position: 'top',
          align: 'end',
          labels: {{ 
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: 'circle',
            font: {{ family: 'Plus Jakarta Sans', size: 11, weight: '500' }},
            color: isDark ? '#cbd5e1' : '#475569',
            padding: 12
          }} 
        }},
        tooltip: {{
          backgroundColor: isDark ? '#0f172a' : '#ffffff',
          titleColor: isDark ? '#ffffff' : '#0f172a',
          bodyColor: isDark ? '#cbd5e1' : '#334155',
          borderColor: isDark ? '#334155' : '#cbd5e1',
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          usePointStyle: true,
          bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
          titleFont: {{ family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }},
          callbacks: {{
            title: (items) => {{
              if (!items.length) return '';
              const mIdx = items[0].dataIndex;
              return shares[mIdx] ? shares[mIdx].label : items[0].label;
            }},
            label: (c) => {{
              const idx = c.dataIndex;
              const pct = c.raw;
              const vol = c.dataset.volumes ? c.dataset.volumes[idx] : null;
              const volFmt = vol ? `${{numFmt(vol)}} ${{unitStr}}` : '';
              return ` ${{c.dataset.label}}: ${{decFmt(pct, 1)}}% • ${{volFmt}}`;
            }},
            footer: (items) => {{
              if (!items.length) return '';
              const mIdx = items[0].dataIndex;
              const m = shares[mIdx];
              return m ? `Total Multimoda: ${{numFmt(m.TOTAL)}} ${{unitStr}}` : '';
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ 
          grid: {{ display: false }}, 
          ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'Plus Jakarta Sans', size: 11, weight: '500' }} }} 
        }},
        y: {{ 
          stacked: true, 
          max: 100, 
          grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, 
          ticks: {{ 
            color: isDark ? '#94a3b8' : '#64748b', 
            font: {{ family: 'JetBrains Mono', size: 10 }}, 
            callback: v => v + '%' 
          }} 
        }}
      }}
    }}
  }});

  // Plugin: Hanya tampilkan persentase (%) yang bersih di dalam irisan donat
  const donutLabelsPlugin = {{
    id: 'donutLabelsPlugin',
    afterDatasetsDraw(chart) {{
      const {{ ctx, data }} = chart;
      const meta = chart.getDatasetMeta(0);
      if (!meta || !meta.data || meta.data.length === 0) return;

      ctx.save();
      meta.data.forEach((arc, i) => {{
        const val = data.datasets[0].data[i];
        if (val === undefined || val === null || val === 0) return;

        const angleSpan = arc.endAngle - arc.startAngle;
        if (angleSpan < 0.22) return; // Terlalu sempit untuk teks di dalam irisan

        const pctStr = decFmt(val, 1) + '%';
        const midAngle = (arc.startAngle + arc.endAngle) / 2;
        const midRadius = (arc.innerRadius + arc.outerRadius) / 2;
        const x = arc.x + Math.cos(midAngle) * midRadius;
        const y = arc.y + Math.sin(midAngle) * midRadius;

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = '700 11px "Plus Jakarta Sans", sans-serif';

        // Tampilan bersih: teks persentase putih dengan bayangan halus
        ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
        ctx.shadowBlur = 3;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 1;
        ctx.fillStyle = '#ffffff';

        ctx.fillText(pctStr, x, y);
      }});

      // Tampilkan total volume di tengah lingkaran donat
      if (data.datasets[0].totalVolume) {{
        const isDk = document.documentElement.classList.contains('dark');
        const cx = meta.data[0].x;
        const cy = meta.data[0].y;
        ctx.shadowBlur = 0;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        ctx.fillStyle = isDk ? '#94a3b8' : '#64748b';
        ctx.font = 'bold 8.5px "Plus Jakarta Sans", sans-serif';
        ctx.fillText('TOTAL', cx, cy - 8);

        ctx.fillStyle = isDk ? '#f8fafc' : '#0f172a';
        ctx.font = 'bold 13px "JetBrains Mono", monospace';
        ctx.fillText(formatVolCompact(data.datasets[0].totalVolume), cx, cy + 7);
      }}
      ctx.restore();
    }}
  }};

  const feb = shares[1] || shares[0];
  const mar = shares[2] || shares[0];
  const labels = ['Udara', 'Kereta Api', 'Bus', 'ASDP', 'Laut'];
  const colors = [COLOR.UDARA, COLOR.KA, COLOR.BUS, COLOR.ASDP, COLOR.LAUT];

  const febVolumes = [feb.vol_UDARA, feb.vol_KA, feb.vol_BUS, feb.vol_ASDP, feb.vol_LAUT];
  const marVolumes = [mar.vol_UDARA, mar.vol_KA, mar.vol_BUS, mar.vol_ASDP, mar.vol_LAUT];

  const donutTooltipConfig = {{
    backgroundColor: isDark ? '#0f172a' : '#ffffff',
    titleColor: isDark ? '#ffffff' : '#0f172a',
    bodyColor: isDark ? '#cbd5e1' : '#334155',
    borderColor: isDark ? '#334155' : '#cbd5e1',
    borderWidth: 1,
    padding: 10,
    boxPadding: 4,
    bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
    titleFont: {{ family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }},
    callbacks: {{
      label: (c) => {{
        const pct = c.raw;
        return ` Pangsa: ${{decFmt(pct, 1)}}%`;
      }},
      afterLabel: (c) => {{
        const idx = c.dataIndex;
        const vol = c.dataset.volumes ? c.dataset.volumes[idx] : null;
        return vol ? ` Volume: ${{numFmt(vol)}} ${{unitStr}}` : '';
      }}
    }}
  }};

  const ctxNorm = document.getElementById('donutNormalCanvas').getContext('2d');
  if (chartDonutNormal) chartDonutNormal.destroy();
  chartDonutNormal = new Chart(ctxNorm, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [feb.UDARA, feb.KA, feb.BUS, feb.ASDP, feb.LAUT],
        volumes: febVolumes,
        totalVolume: feb.TOTAL,
        backgroundColor: colors,
        borderWidth: 1.5,
        borderColor: isDark ? '#1e293b' : '#ffffff'
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      cutout: '52%',
      plugins: {{
        legend: {{ display: false }},
        tooltip: donutTooltipConfig
      }}
    }},
    plugins: [donutLabelsPlugin]
  }});

  const ctxPeak = document.getElementById('donutPeakCanvas').getContext('2d');
  if (chartDonutPeak) chartDonutPeak.destroy();
  chartDonutPeak = new Chart(ctxPeak, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [mar.UDARA, mar.KA, mar.BUS, mar.ASDP, mar.LAUT],
        volumes: marVolumes,
        totalVolume: mar.TOTAL,
        backgroundColor: colors,
        borderWidth: 1.5,
        borderColor: isDark ? '#1e293b' : '#ffffff'
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      cutout: '52%',
      plugins: {{
        legend: {{ display: false }},
        tooltip: donutTooltipConfig
      }}
    }},
    plugins: [donutLabelsPlugin]
  }});

  // Update total labels under the doughnut canvases
  const elNormalTotal = document.getElementById('donut-normal-total');
  if (elNormalTotal) {{
    elNormalTotal.innerText = `Total: ${{formatVolCompact(feb.TOTAL)}} (${{numFmt(feb.TOTAL)}} ${{unitStr}})`;
  }}
  const elPeakTotal = document.getElementById('donut-peak-total');
  if (elPeakTotal) {{
    elPeakTotal.innerText = `Total: ${{formatVolCompact(mar.TOTAL)}} (${{numFmt(mar.TOTAL)}} ${{unitStr}})`;
  }}

  const tbody = document.getElementById('tbody-share');
  if (tbody) {{
    tbody.innerHTML = '';
    shares.forEach(m => {{
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-sans font-medium text-slate-900 dark:text-slate-100">${{m.label}}</td>
        <td class="py-2.5 px-3 text-right">${{decFmt(m.UDARA, 1)}}%</td>
        <td class="py-2.5 px-3 text-right">${{decFmt(m.KA, 1)}}%</td>
        <td class="py-2.5 px-3 text-right">${{decFmt(m.BUS, 1)}}%</td>
        <td class="py-2.5 px-3 text-right font-semibold text-purple-700 dark:text-purple-400">${{decFmt(m.ASDP, 1)}}%</td>
        <td class="py-2.5 px-3 text-right">${{decFmt(m.LAUT, 1)}}%</td>
        <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{numFmt(m.TOTAL)}}</td>
      `;
      tbody.appendChild(tr);
    }});
  }}
}}

// ---------------------------------------------------------------
// TAB 4: LOAD FACTOR PROXY CONTROLLER
// ---------------------------------------------------------------
function renderLoadFactorWorkspace() {{
  if (chartLoadFactor) return;

  const isDark = document.documentElement.classList.contains('dark');
  const ctx = document.getElementById('chartLoadFactorCanvas').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labelsLF = ['ASDP', 'Bus', 'Kereta Api', 'Laut', 'Udara'];
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
  if (tbody) {{
    tbody.innerHTML = '';
    modas.forEach((m, idx) => {{
      const s = lf[m];
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{labelsLF[idx]}}</td>
        <td class="py-2.5 px-3 text-right">${{decFmt(s.baseline_lf, 1)}} pnp/arm</td>
        <td class="py-2.5 px-3 text-right text-purple-700 dark:text-purple-400 font-semibold">${{decFmt(s.mudik_lf, 1)}}</td>
        <td class="py-2.5 px-3 text-right text-rose-700 dark:text-rose-400 font-semibold">${{decFmt(s.balik_lf, 1)}}</td>
        <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">+${{decFmt(s.surge_lf_pct, 1)}}%</td>
      `;
      tbody.appendChild(tr);
    }});
  }}
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
  const sortKey = getHubMetricKey();
  const isPnp = currentMetric === 'pnp';

  if (currentHubModa === 'ALL') {{
    Object.keys(source).forEach(m => {{
      source[m].forEach(h => list.push({{ ...h, moda: m }}));
    }});
    list.sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0));
    list = list.slice(0, 30);
  }} else {{
    list = (source[currentHubModa] || []).map(h => ({{ ...h, moda: currentHubModa }}));
    list.sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0));
  }}

  if (currentHubSearchTerm) {{
    list = list.filter(h => 
      h.nama_prasarana.toLowerCase().includes(currentHubSearchTerm) || 
      h.provinsi.toLowerCase().includes(currentHubSearchTerm)
    );
  }}

  const resultCount = document.getElementById('hub-result-count');
  if (resultCount) {{
    resultCount.innerText = `Menampilkan ${{list.length}} prasarana transportasi (Diurutkan: ${{isPnp ? 'Penumpang' : 'Armada'}} • ${{currentDirection === 'dat' ? 'Datang' : currentDirection === 'brg' ? 'Berangkat' : 'Dua Arah'}})`;
  }}

  const tbody = document.getElementById('tbody-hubs');
  if (!tbody) return;
  tbody.innerHTML = '';
  
  if (list.length === 0) {{
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-400">Tidak ada simpul yang sesuai dengan filter pencarian</td></tr>`;
    return;
  }}

  const maxVal = list[0][sortKey] || 1;

  list.forEach((h, idx) => {{
    const activeVal = h[sortKey] || 0;
    const pct = Math.round((activeVal / maxVal) * 100);
    const color = COLOR[h.moda] || '#64748b';
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';

    const pnpDisplay = currentDirection === 'dat' ? h.p_dat : (currentDirection === 'brg' ? h.p_brg : h.pnp);
    const armDisplay = currentDirection === 'dat' ? h.a_dat : (currentDirection === 'brg' ? h.a_brg : h.arm);

    tr.innerHTML = `
      <td class="py-2.5 px-3 text-center font-mono font-bold text-slate-400">${{idx + 1}}</td>
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{h.nama_prasarana}}</td>
      <td class="py-2.5 px-3">
        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold text-white" style="background-color: ${{color}}">
          ${{h.moda}}
        </span>
      </td>
      <td class="py-2.5 px-3 font-sans text-slate-600 dark:text-slate-300">${{h.provinsi}}</td>
      <td class="py-2.5 px-3 text-right font-mono font-bold ${{isPnp ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-900 dark:text-white'}}">${{numFmt(pnpDisplay)}}</td>
      <td class="py-2.5 px-3 text-right font-mono ${{!isPnp ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-600 dark:text-slate-400'}}">${{numFmt(armDisplay)}}</td>
      <td class="py-2.5 px-3 text-right">
        <div class="flex items-center gap-2 justify-end">
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
  if (!tbody) return;
  tbody.innerHTML = '';

  const meta = DATA.meta;
  const lf = DATA.load_factor_stats;
  const surge = DATA.surge_summary;
  const ms = DATA.monthly_summary;
  const mar = ms.find(m => m.bulan === '2026-03') || {{}};
  const feb = ms.find(m => m.bulan === '2026-02') || {{}};
  const isPnp = currentMetric === 'pnp';
  const combo = currentMetric + '_' + currentDirection;
  const s = (DATA.metrics_summary && DATA.metrics_summary[combo]) || {{}};

  const rows = [
    {{ label: `1. Volume ${{s.label || 'Multimoda'}} YTD`, u: numFmt(DATA.top_hubs_ytd.UDARA.reduce((a,b)=>a+(b[getHubMetricKey()]||0),0)), ka: numFmt(DATA.top_hubs_ytd.KA.reduce((a,b)=>a+(b[getHubMetricKey()]||0),0)), bus: numFmt(DATA.top_hubs_ytd.BUS.reduce((a,b)=>a+(b[getHubMetricKey()]||0),0)), asdp: numFmt(DATA.top_hubs_ytd.ASDP.reduce((a,b)=>a+(b[getHubMetricKey()]||0),0)), laut: numFmt(DATA.top_hubs_ytd.LAUT.reduce((a,b)=>a+(b[getHubMetricKey()]||0),0)), tot: numFmt(s.ytd || meta.total_passengers_ytd) }},
    {{ label: `2. Rata-rata Harian (${{s.unit || 'pnp'}})`, u: numFmt(Math.round((s.ytd || meta.total_passengers_ytd) * 0.325 / 272)), ka: numFmt(Math.round((s.ytd || meta.total_passengers_ytd) * 0.224 / 272)), bus: numFmt(Math.round((s.ytd || meta.total_passengers_ytd) * 0.203 / 272)), asdp: numFmt(Math.round((s.ytd || meta.total_passengers_ytd) * 0.113 / 272)), laut: numFmt(Math.round((s.ytd || meta.total_passengers_ytd) * 0.135 / 272)), tot: numFmt(s.avg || 1367243) }},
    {{ label: '3. Volume Puncak Mudik (18 Mar)', u: numFmt(surge.UDARA.peak_mudik), ka: numFmt(surge.KA.peak_mudik), bus: numFmt(surge.BUS.peak_mudik), asdp: numFmt(surge.ASDP.peak_mudik), laut: numFmt(surge.LAUT.peak_mudik), tot: numFmt(s.mudik_val || surge.TOTAL.peak_mudik) }},
    {{ label: '4. Lonjakan Arus Mudik (%)', u: '+' + decFmt(surge.UDARA.surge_mudik_pct, 1) + '%', ka: '+' + decFmt(surge.KA.surge_mudik_pct, 1) + '%', bus: '+' + decFmt(surge.BUS.surge_mudik_pct, 1) + '%', asdp: '+' + decFmt(surge.ASDP.surge_mudik_pct, 1) + '%', laut: '+' + decFmt(surge.LAUT.surge_mudik_pct, 1) + '%', tot: '+' + decFmt(s.mudik_surge_pct || surge.TOTAL.surge_mudik_pct, 1) + '%' }},
    {{ label: '5. Volume Puncak Balik 1 (24 Mar)', u: numFmt(surge.UDARA.peak_balik1), ka: numFmt(surge.KA.peak_balik1), bus: numFmt(surge.BUS.peak_balik1), asdp: numFmt(surge.ASDP.peak_balik1), laut: numFmt(surge.LAUT.peak_balik1), tot: numFmt(s.peak_val || surge.TOTAL.peak_balik1) }},
    {{ label: '6. Lonjakan Arus Balik 1 (%)', u: '+' + decFmt(surge.UDARA.surge_balik1_pct, 1) + '%', ka: '+' + decFmt(surge.KA.surge_balik1_pct, 1) + '%', bus: '+' + decFmt(surge.BUS.surge_balik1_pct, 1) + '%', asdp: '+' + decFmt(surge.ASDP.surge_balik1_pct, 1) + '%', laut: '+' + decFmt(surge.LAUT.surge_balik1_pct, 1) + '%', tot: '+' + decFmt(s.peak_surge_pct || surge.TOTAL.surge_balik1_pct, 1) + '%' }},
    {{ label: '7. Load Factor Normal (Pnp/Arm)', u: decFmt(lf.UDARA.baseline_lf, 1), ka: decFmt(lf.KA.baseline_lf, 1), bus: decFmt(lf.BUS.baseline_lf, 1), asdp: decFmt(lf.ASDP.baseline_lf, 1), laut: decFmt(lf.LAUT.baseline_lf, 1), tot: '37,1' }},
    {{ label: '8. Load Factor Puncak Lebaran', u: decFmt(lf.UDARA.peak_lf, 1), ka: decFmt(lf.KA.peak_lf, 1), bus: decFmt(lf.BUS.peak_lf, 1), asdp: decFmt(lf.ASDP.peak_lf, 1), laut: decFmt(lf.LAUT.peak_lf, 1), tot: '52,7' }},
    {{ label: '9. Pangsa Pasar Normal Feb (%)', u: decFmt(feb.share_UDARA, 1) + '%', ka: decFmt(feb.share_KA, 1) + '%', bus: decFmt(feb.share_BUS, 1) + '%', asdp: decFmt(feb.share_ASDP, 1) + '%', laut: decFmt(feb.share_LAUT, 1) + '%', tot: '100,0%' }},
    {{ label: '10. Pangsa Pasar Puncak Mar (%)', u: decFmt(mar.share_UDARA, 1) + '%', ka: decFmt(mar.share_KA, 1) + '%', bus: decFmt(mar.share_BUS, 1) + '%', asdp: decFmt(mar.share_ASDP, 1) + '%', laut: decFmt(mar.share_LAUT, 1) + '%', tot: '100,0%' }},
    {{ label: '11. Jumlah Simpul Terverifikasi', u: '257 Bandara', ka: '193 Stasiun', bus: '215 Terminal', asdp: '276 Pelabuhan', laut: '267 Pelabuhan', tot: '1.208 Simpul' }},
    {{ label: '12. Simpul Terpadat Nasional', u: 'Soekarno-Hatta (CGK)', ka: 'Yogyakarta (YK)', bus: 'Purboyo Madiun', asdp: 'Bakauheni Lampung', laut: 'Tanjung Perak', tot: 'Multimoda' }},
  ];

  rows.forEach(r => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-900 dark:text-slate-100">${{r.label}}</td>
      <td class="py-2.5 px-3 text-right">${{r.u}}</td>
      <td class="py-2.5 px-3 text-right">${{r.ka}}</td>
      <td class="py-2.5 px-3 text-right">${{r.bus}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-purple-700 dark:text-purple-400">${{r.asdp}}</td>
      <td class="py-2.5 px-3 text-right">${{r.laut}}</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{r.tot}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 7: LEAFLET SPATIAL MAP CONTROLLER
// ---------------------------------------------------------------
let currentBasemap = 'osm'; // Hanya OpenStreetMap (OSM)
let currentSpatialScale = 'all'; // 'all', 'top10', 'top20', 'top30', 'top50', 'pareto80', 'pareto90'

function getBasemapConfig() {{
  return {{
    url: 'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
    attr: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    maxZoom: 18
  }};
}}

function initSpatialMap() {{
  if (spatialMap) return;

  const baseConfig = getBasemapConfig();

  spatialMap = L.map('spatialMapCanvas', {{
    center: [-2.2, 117.5],
    zoom: 5,
    minZoom: 4,
    maxZoom: 18,
    zoomControl: false
  }});

  L.control.zoom({{ position: 'bottomright' }}).addTo(spatialMap);

  mapTileLayer = L.tileLayer(baseConfig.url, {{
    attribution: baseConfig.attr,
    maxZoom: baseConfig.maxZoom
  }}).addTo(spatialMap);

  spatialMarkerGroup = L.layerGroup().addTo(spatialMap);

  const legend = L.control({{ position: 'bottomleft' }});
  legend.onAdd = function() {{
    const div = L.DomUtil.create('div', 'p-2.5 rounded-lg bg-white/90 dark:bg-slate-900/90 backdrop-blur border border-slate-200 dark:border-slate-800 text-[11px] font-sans shadow-md space-y-1.5');
    div.innerHTML = `
      <div class="font-bold text-slate-800 dark:text-slate-200">Moda Transportasi:</div>
      <div class="space-y-0.5">
        <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Udara (257)</span></div>
        <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Kereta Api (193)</span></div>
        <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-green-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Bus (139)</span></div>
        <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-purple-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">ASDP (158)</span></div>
        <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Laut (267)</span></div>
      </div>
      <div class="border-t border-slate-200 dark:border-slate-700 pt-1.5">
        <div class="font-bold text-slate-800 dark:text-slate-200 mb-1">Ukuran Dot (Penumpang):</div>
        <div class="flex items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400">
          <div class="flex items-center gap-1"><span class="inline-block w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0"></span><span>&lt;100rb</span></div>
          <div class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-full bg-slate-400 shrink-0"></span><span>1-5 Jt</span></div>
          <div class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded-full bg-slate-400 shrink-0"></span><span>&gt;10 Jt</span></div>
        </div>
      </div>
    `;
    return div;
  }};
  legend.addTo(spatialMap);

  renderSpatialMapNodes();
}}

function updateMapTheme() {{
  if (!spatialMap || !mapTileLayer) return;
  // Basemap OpenStreetMap (OSM) standar konsisten di tema gelap maupun terang
}}

function setSpatialScaleFilter(scale) {{
  currentSpatialScale = scale;
  const select = document.getElementById('select-spatial-scale');
  if (select && select.value !== scale) select.value = scale;
  renderSpatialMapNodes();
}}

function renderSpatialMapNodes() {{
  if (!spatialMarkerGroup) return;
  spatialMarkerGroup.clearLayers();

  const sortKey = getHubMetricKey();
  const isPnp = currentMetric === 'pnp';

  // 1. Ambil kandidat dengan koordinat dan filter moda aktif
  const pool = DATA.spatial_nodes.filter(n => {{
    if (!n.has_coords) return false;
    if (currentSpatialModa !== 'ALL' && n.m !== currentSpatialModa) return false;
    return true;
  }});

  // Urutkan simpul dari volume tertinggi ke terendah berdasarkan metrik aktif
  pool.sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0));

  const totalPoolVol = pool.reduce((acc, n) => acc + (n[sortKey] || 0), 0);

  // 2. Filter berdasarkan skala / ranking / pangsa pasar
  let nodes = pool;
  if (currentSpatialScale === 'top10') {{
    nodes = pool.slice(0, 10);
  }} else if (currentSpatialScale === 'top20') {{
    nodes = pool.slice(0, 20);
  }} else if (currentSpatialScale === 'top30') {{
    nodes = pool.slice(0, 30);
  }} else if (currentSpatialScale === 'top50') {{
    nodes = pool.slice(0, 50);
  }} else if (currentSpatialScale === 'pareto80') {{
    let cum = 0;
    const threshold = totalPoolVol * 0.8;
    nodes = [];
    for (const n of pool) {{
      nodes.push(n);
      cum += (n[sortKey] || 0);
      if (cum >= threshold) break;
    }}
  }} else if (currentSpatialScale === 'pareto90') {{
    let cum = 0;
    const threshold = totalPoolVol * 0.9;
    nodes = [];
    for (const n of pool) {{
      nodes.push(n);
      cum += (n[sortKey] || 0);
      if (cum >= threshold) break;
    }}
  }}

  const displayedVol = nodes.reduce((acc, n) => acc + (n[sortKey] || 0), 0);
  const sharePct = totalPoolVol > 0 ? (displayedVol / totalPoolVol * 100) : 100;

  // 3. Perbarui teks badge informasi
  const badgeEl = document.getElementById('badge-spatial-count');
  if (badgeEl) {{
    const countStr = numFmt(nodes.length);
    const pctStr = decFmt(sharePct, 1);
    if (currentSpatialScale === 'all') {{
      badgeEl.innerText = `● ${{countStr}} Terpetakan (100%)`;
    }} else {{
      badgeEl.innerText = `● ${{countStr}} Simpul (${{pctStr}}% Pangsa)`;
    }}
  }}

  // 4. Render marker lingkaran Leaflet (ukuran dot proporsional dinamis terhadap volume penumpang)
  const maxMetricVal = DATA.spatial_nodes.reduce((max, node) => Math.max(max, (node[sortKey] || 0)), 1);

  nodes.forEach((n, rankIdx) => {{
    const val = n[sortKey] || 0;
    // Semakin banyak penumpang, semakin besar ukuran dot (proporsional 3px s/d 25px)
    const ratio = Math.min(1, Math.max(0, val / maxMetricVal));
    const minR = 3;
    const maxR = 25;
    const radius = val > 0 ? (minR + Math.pow(ratio, 0.42) * (maxR - minR)) : 2.5;
    const color = COLOR[n.m] || '#64748b';
    const isTop10 = rankIdx < 10;

    const marker = L.circleMarker([n.lat, n.lon], {{
      radius: radius,
      fillColor: color,
      color: isTop10 ? '#f59e0b' : '#ffffff',
      weight: isTop10 ? 1.8 : 0.75,
      opacity: 0.95,
      fillOpacity: 0.72
    }});

    // Efek hover interaktif dan membawa marker ke lapisan depan
    marker.on('mouseover', function() {{
      this.setStyle({{ weight: 2.4, fillOpacity: 0.95, radius: radius + 2.5 }});
      this.bringToFront();
    }});
    marker.on('mouseout', function() {{
      this.setStyle({{ weight: isTop10 ? 1.8 : 0.75, fillOpacity: 0.72, radius: radius }});
    }});

    const rankBadge = rankIdx < 50 
      ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold ${{isTop10 ? 'bg-amber-100 text-amber-900 border border-amber-300 dark:bg-amber-950 dark:text-amber-200' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'}}">Peringkat #${{rankIdx + 1}}</span>` 
      : '';
    const shareOfTotal = totalPoolVol > 0 ? decFmt((val / totalPoolVol * 100), 2) + '%' : '-';

    const popupHtml = `
      <div class="p-3 text-xs font-sans space-y-2 max-w-[280px]">
        <div class="flex items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-700 pb-1.5">
          <span class="font-bold text-slate-900 dark:text-white truncate">${{n.nama}}</span>
          <span class="px-1.5 py-0.2 rounded text-[10px] font-bold text-white shrink-0" style="background-color: ${{color}}">${{n.m}}</span>
        </div>
        <div class="flex items-center justify-between text-[11px] text-slate-500">
          <span>${{n.p}} • Tipe: ${{n.tipe}}</span>
          ${{rankBadge}}
        </div>
        <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 space-y-1 text-[11px] font-mono">
          <div class="flex justify-between ${{sortKey === 'pnp' ? 'font-bold text-indigo-600 dark:text-indigo-400' : ''}}">
            <span>Total Penumpang:</span><span>${{numFmt(n.pnp)}}</span>
          </div>
          <div class="flex justify-between ${{sortKey === 'p_dat' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}}">
            <span>↳ Pnp Datang:</span><span>${{numFmt(n.p_dat)}}</span>
          </div>
          <div class="flex justify-between ${{sortKey === 'p_brg' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}}">
            <span>↳ Pnp Berangkat:</span><span>${{numFmt(n.p_brg)}}</span>
          </div>
          <div class="border-t border-slate-200 dark:border-slate-700 pt-1 flex justify-between ${{sortKey === 'arm' ? 'font-bold text-indigo-600 dark:text-indigo-400' : ''}}">
            <span>Total Armada:</span><span>${{numFmt(n.arm)}}</span>
          </div>
          <div class="flex justify-between ${{sortKey === 'a_dat' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}}">
            <span>↳ Armada Datang:</span><span>${{numFmt(n.a_dat)}}</span>
          </div>
          <div class="flex justify-between ${{sortKey === 'a_brg' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}}">
            <span>↳ Armada Berangkat:</span><span>${{numFmt(n.a_brg)}}</span>
          </div>
          <div class="border-t border-slate-200 dark:border-slate-700 pt-1 flex justify-between font-semibold text-emerald-600 dark:text-emerald-400">
            <span>Pangsa terhadap Total:</span><span>${{shareOfTotal}}</span>
          </div>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    marker.addTo(spatialMarkerGroup);
  }});
}}

function filterSpatialModa(moda, btn) {{
  currentSpatialModa = moda;
  document.querySelectorAll('.map-moda-btn').forEach(b => {{
    b.classList.remove('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
    b.classList.add('font-medium', 'text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
  btn.classList.remove('font-medium', 'text-slate-600', 'dark:text-slate-400');
  renderSpatialMapNodes();
}}

function setBasemap(type, btn) {{
  currentBasemap = 'osm';
  if (mapTileLayer) {{
    const cfg = getBasemapConfig();
    mapTileLayer.setUrl(cfg.url);
  }}
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
  const txt = document.getElementById('txt-map-fs');
  if (txt) txt.innerText = isFs ? 'Kecilkan' : 'Layar Penuh';
  setTimeout(() => {{
    if (spatialMap) spatialMap.invalidateSize();
  }}, 150);
}});


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
  renderForecastComparisonTable();
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

  const totalEl = document.getElementById('card-fc-total-pnp');
  if (totalEl) totalEl.innerText = numFmt(sum.total_passengers);

  const avgEl = document.getElementById('card-fc-avg-pnp');
  if (avgEl) avgEl.innerText = numFmt(sum.avg_daily_passengers);

  const totalYoyEl = document.getElementById('card-fc-total-yoy');
  if (totalYoyEl) {{
    const sign = sum.yoy_total_pct >= 0 ? '+' : '';
    totalYoyEl.innerText = `${{sign}}${{decFmt(sum.yoy_total_pct, 1)}}% vs 2025`;
    totalYoyEl.className = sum.yoy_total_pct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
  }}

  const xmasEl = document.getElementById('card-fc-xmas-pnp');
  if (xmasEl) xmasEl.innerText = numFmt(sum.xmas_peak_val);

  const xmasYoyEl = document.getElementById('card-fc-xmas-yoy');
  if (xmasYoyEl) {{
    const sign = sum.xmas_peak_yoy >= 0 ? '+' : '';
    xmasYoyEl.innerText = `${{sign}}${{decFmt(sum.xmas_peak_yoy, 1)}}% YoY`;
    xmasYoyEl.className = sum.xmas_peak_yoy >= 0 ? 'text-amber-600 dark:text-amber-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
  }}

  const nyEl = document.getElementById('card-fc-ny-pnp');
  if (nyEl) nyEl.innerText = numFmt(sum.ny_peak_val);

  const nyYoyEl = document.getElementById('card-fc-ny-yoy');
  if (nyYoyEl) {{
    const sign = sum.ny_peak_yoy >= 0 ? '+' : '';
    nyYoyEl.innerText = `${{sign}}${{decFmt(sum.ny_peak_yoy, 1)}}% YoY`;
    nyYoyEl.className = sum.ny_peak_yoy >= 0 ? 'text-rose-600 dark:text-rose-400 font-bold' : 'text-slate-500 font-bold';
  }}
  
  // Peak armada
  const scenData = DATA.forecast_nataru.scenarios[currentForecastScenario];
  const maxArmDay = scenData.reduce((max, d) => d.arm_TOTAL > max.arm_TOTAL ? d : max, scenData[0]);
  const armPeakEl = document.getElementById('card-fc-arm-peak');
  if (armPeakEl) armPeakEl.innerText = numFmt(maxArmDay.arm_TOTAL);

  const armYoyEl = document.getElementById('card-fc-arm-yoy');
  if (armYoyEl) {{
    const baseArm25 = maxArmDay.arm_2025 || 44447;
    const armDiffPct = ((maxArmDay.arm_TOTAL / baseArm25) - 1.0) * 100;
    const sign = armDiffPct >= 0 ? '+' : '';
    armYoyEl.innerText = `${{sign}}${{decFmt(armDiffPct, 1)}}% YoY`;
  }}
}}

function renderForecastComparisonTable() {{
  if (!DATA.forecast_nataru) return;
  const tbody = document.getElementById('tbody-forecast-comparison');
  if (!tbody) return;
  tbody.innerHTML = '';

  const sum = DATA.forecast_nataru.summaries[currentForecastScenario];
  if (!sum || !sum.mode_breakdown) return;

  const modesMeta = [
    {{ key: 'UDARA', label: '✈ Udara (Penerbangan Domestik)', color: COLOR.UDARA, note: 'Kapasitas armada jet beroperasi optimal; tiket dinamis memfilter demand jarak jauh' }},
    {{ key: 'KA', label: '🚆 Kereta Api (KAI)', color: COLOR.KA, note: 'Tingkat isian stabil tinggi (load factor 90%+); seluruh kuota KA favorit terjual' }},
    {{ key: 'BUS', label: '🚌 Bus', color: COLOR.BUS, note: 'Rute Trans Jawa & jalan tol primadona; armada reguler & cadangan siaga penuh' }},
    {{ key: 'ASDP', label: '⛴ ASDP (Penyeberangan Feri)', color: COLOR.ASDP, note: 'Lonjakan kendaraan pribadi tinggi di lintasan Merak-Bakauheni & Ketapang-Gilimanuk' }},
    {{ key: 'LAUT', label: '🚢 Laut (Kapal Penumpang Pelni)', color: COLOR.LAUT, note: 'Pertumbuhan tertinggi; pergerakan antarpulau & rute perintis Indonesia Timur' }},
  ];

  modesMeta.forEach(m => {{
    const rowData = sum.mode_breakdown[m.key];
    if (!rowData) return;
    const yoyClass = rowData.yoy_pct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${{m.color}}"></span>
        <span>${{m.label}}</span>
      </td>
      <td class="py-2.5 px-3 text-right font-medium">${{numFmt(rowData.passengers_2025)}}</td>
      <td class="py-2.5 px-3 text-right text-slate-500">${{decFmt(rowData.share_pct_2025, 1)}}%</td>
      <td class="py-2.5 px-3 text-right font-bold text-indigo-700 dark:text-indigo-400">${{numFmt(rowData.passengers_2026)}}</td>
      <td class="py-2.5 px-3 text-right font-semibold text-indigo-600 dark:text-indigo-400">${{decFmt(rowData.share_pct_2026, 1)}}%</td>
      <td class="py-2.5 px-3 text-right font-semibold">${{rowData.diff >= 0 ? '+' : ''}}${{numFmt(rowData.diff)}}</td>
      <td class="py-2.5 px-3 text-center ${{yoyClass}}">${{rowData.yoy_pct >= 0 ? '+' : ''}}${{decFmt(rowData.yoy_pct, 1)}}%</td>
      <td class="py-2.5 px-3 text-left font-sans text-[11px] text-slate-500 dark:text-slate-400">${{m.note}}</td>
    `;
    tbody.appendChild(tr);
  }});

  // Total Multimoda Row
  const totalYoyClass = sum.yoy_total_pct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-extrabold' : 'text-rose-600 dark:text-rose-400 font-extrabold';
  const trTotal = document.createElement('tr');
  trTotal.className = 'bg-slate-100/80 dark:bg-slate-800/80 font-bold border-t-2 border-slate-300 dark:border-slate-600';
  trTotal.innerHTML = `
    <td class="py-3 px-3 uppercase text-slate-900 dark:text-white font-bold">🌟 Total Multimoda Nasional</td>
    <td class="py-3 px-3 text-right font-black text-slate-900 dark:text-white">${{numFmt(sum.total_passengers_2025)}}</td>
    <td class="py-3 px-3 text-right text-slate-600 dark:text-slate-400">100,0%</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300 text-xs">${{numFmt(sum.total_passengers)}}</td>
    <td class="py-3 px-3 text-right font-black text-indigo-700 dark:text-indigo-300">100,0%</td>
    <td class="py-3 px-3 text-right text-slate-900 dark:text-white">${{sum.diff_passengers >= 0 ? '+' : ''}}${{numFmt(sum.diff_passengers)}}</td>
    <td class="py-3 px-3 text-center text-xs ${{totalYoyClass}}">${{sum.yoy_total_pct >= 0 ? '+' : ''}}${{decFmt(sum.yoy_total_pct, 1)}}%</td>
    <td class="py-3 px-3 text-left font-sans text-[11px] text-slate-700 dark:text-slate-300 font-semibold">
      Ekspansi mobilitas nasional; rerata harian naik dari ${{numFmt(sum.avg_daily_passengers_2025)}} ke ${{numFmt(sum.avg_daily_passengers)}} pnp/hari
    </td>
  `;
  tbody.appendChild(trTotal);
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

  // Combined timeline labels
  const allLabels = [...hist.map(d => d.date), ...fc.map(d => d.date)];

  // Historical data values (2026)
  const histKey = isPnp ? moda : (moda === 'TOTAL' ? 'arm_TOTAL' : `arm_${{moda}}`);
  const histData = [...hist.map(d => d[histKey]), ...fc.map(() => null)];

  // Forecast data values (start connecting from last historical point)
  const lastHistVal = hist[hist.length - 1][histKey];
  const fcData = [
    ...hist.slice(0, -1).map(() => null),
    lastHistVal,
    ...fc.map(d => isPnp ? d[moda] : d[`arm_${{moda}}`])
  ];

  // Realisasi Tahun Lalu 2025 mapping
  const map2025 = {{}};
  if (DATA.timeline_2025) {{
    DATA.timeline_2025.forEach(r => {{
      const md = r.date.slice(5);
      map2025[md] = r;
    }});
  }}
  const hist25Data = allLabels.map(d => {{
    const md = d.slice(5);
    const r25 = map2025[md];
    if (!r25) return null;
    return isPnp ? r25[moda] : (moda === 'TOTAL' ? r25.arm_TOTAL : r25[`arm_${{moda}}`]);
  }});

  // Colors
  const modaColor = moda === 'TOTAL' ? (isDark ? '#38bdf8' : '#0284c7') : (COLOR[moda] || '#6366f1');
  const forecastColor = '#6366f1'; // Indigo
  const prevYearColor = isDark ? '#34d399' : '#059669'; // Emerald

  const datasets = [
    {{
      label: `Realisasi Historis 2026 (${{isPnp ? 'Penumpang' : 'Armada'}})`,
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
      label: `Proyeksi Holt-Winters 2026/2027 (${{isPnp ? 'Penumpang' : 'Armada'}})`,
      data: fcData,
      borderColor: forecastColor,
      backgroundColor: 'transparent',
      borderWidth: 2.2,
      borderDash: [5, 4],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.2,
      spanGaps: false
    }},
    {{
      label: `Realisasi 2025 (Data Latih) (${{isPnp ? 'Penumpang' : 'Armada'}})`,
      data: hist25Data,
      borderColor: prevYearColor,
      backgroundColor: 'transparent',
      borderWidth: 1.8,
      borderDash: [3, 3],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.15,
      spanGaps: true
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
    }} else if (row.status === 'PEAK_SURGE') {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300">Puncak Lonjakan</span>`;
    }} else if (row.status === 'HIGH') {{
      badgeStatus = `<span class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">Tinggi</span>`;
    }}

    const yoyClass = row.yoy_pct >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-rose-600 dark:text-rose-400 font-bold';

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-2.5 font-medium text-slate-900 dark:text-white">${{row.date}}</td>
      <td class="py-2 px-2.5 font-sans ${{['Min', 'Sab'].includes(dayName) ? 'text-rose-600 font-semibold' : 'text-slate-500'}}">${{dayName}}</td>
      <td class="py-2 px-2.5 text-right font-bold text-indigo-700 dark:text-indigo-400">${{numFmt(row.TOTAL)}}</td>
      <td class="py-2 px-2.5 text-right font-semibold text-slate-800 dark:text-slate-200">${{numFmt(row.pnp_2025)}}</td>
      <td class="py-2 px-2.5 text-center ${{yoyClass}}">${{row.yoy_pct >= 0 ? '+' : ''}}${{decFmt(row.yoy_pct, 1)}}%</td>
      <td class="py-2 px-2.5 text-right text-slate-500 text-[10px]">${{numFmt(row.ci_lower)}} - ${{numFmt(row.ci_upper)}}</td>
      <td class="py-2 px-2.5 text-center">${{badgeStatus}}</td>
      <td class="py-2 px-2.5 text-right text-slate-700 dark:text-slate-300 font-semibold">${{numFmt(row.arm_TOTAL)}}</td>
      <td class="py-2 px-2.5 text-right text-slate-500">${{numFmt(row.arm_2025)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 8: SIMULASI KEBUTUHAN ARMADA BERDASARKAN PRASARANA / SIMPUL
// ---------------------------------------------------------------
// ---------------------------------------------------------------
// ---------------------------------------------------------------
// TAB 8: MATRIKS KEBUTUHAN PENAMBAHAN ARMADA SIMPUL NASIONAL
// ---------------------------------------------------------------
let simpulDisplayLimit = 25; // default 25 baris
let simpulCurrentPage = 1;
let simpulModaFilter = 'ALL';
let simpulStatusFilter = 'ALL';
let simpulSearchQuery = '';
let simpulSortBy = 'pnp_desc';

function setSimpulDisplayLimit(limit) {{
  simpulDisplayLimit = (limit === 'all') ? 'all' : parseInt(limit, 10);
  simpulCurrentPage = 1;
  renderSimpulSimulation();
}}

function filterSimpulModa(moda, btn) {{
  simpulModaFilter = moda;
  simpulCurrentPage = 1;
  document.querySelectorAll('.simpul-filter-btn').forEach(b => {{
    b.className = 'simpul-filter-btn px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all font-semibold';
  }});
  if (btn) {{
    btn.className = 'simpul-filter-btn px-2.5 py-1 rounded-md bg-indigo-600 text-white shadow-xs font-bold transition-all';
  }}
  renderSimpulSimulation();
}}

function setSimpulStatusFilter(status) {{
  simpulStatusFilter = status;
  simpulCurrentPage = 1;
  renderSimpulSimulation();
}}

function onSimpulSearchChange(val) {{
  simpulSearchQuery = (val || '').toLowerCase().trim();
  simpulCurrentPage = 1;
  renderSimpulSimulation();
}}

function setSimpulSortBy(val) {{
  simpulSortBy = val;
  simpulCurrentPage = 1;
  renderSimpulSimulation();
}}

function changeSimpulPage(delta) {{
  simpulCurrentPage += delta;
  renderSimpulSimulation();
}}

function renderDynamicSimpulHighlights(filteredData) {{
  const container = document.getElementById('simpulHighlightCards');
  if (!container) return;

  const modas = [
    {{ key: 'ASDP', label: '⛴ ASDP Feri', color: 'rose' }},
    {{ key: 'KA', label: '🚆 Kereta Api', color: 'amber' }},
    {{ key: 'UDARA', label: '✈ Penerbangan', color: 'sky' }},
    {{ key: 'BUS', label: '🚌 Bus AKAP', color: 'emerald' }},
    {{ key: 'LAUT', label: '🚢 Kapal Laut', color: 'cyan' }},
  ];

  let html = '';
  modas.forEach(m => {{
    const sub = filteredData.filter(d => d.moda === m.key);
    const count = sub.length;
    const totalPuncakArm = sub.reduce((acc, c) => acc + (c.armPuncak || 0), 0);
    const totalAddArm = sub.reduce((acc, c) => acc + (c.addArm || 0), 0);
    const avgPct = totalPuncakArm > 0 ? (totalAddArm / totalPuncakArm * 100).toFixed(1) : '0';

    html += `
      <div class="bg-${{m.color}}-50/70 dark:bg-${{m.color}}-950/30 border border-${{m.color}}-200 dark:border-${{m.color}}-900/60 rounded-lg p-3">
        <div class="flex items-center justify-between text-[10px] text-${{m.color}}-600 dark:text-${{m.color}}-400 font-bold uppercase">
          <span>${{m.label}}</span>
          <span>${{count}} Simpul</span>
        </div>
        <div class="font-mono font-black text-${{m.color}}-700 dark:text-${{m.color}}-300 text-lg mt-1">+${{avgPct}}% Armada</div>
        <div class="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5">
          Butuh <strong>+${{numFmt(totalAddArm)}} unit/hari</strong>
        </div>
      </div>
    `;
  }});

  container.innerHTML = html;
}}

function renderDynamicSimpulSummary(filteredData) {{
  const elSum = document.getElementById('simpulOperationalSummary');
  if (!elSum) return;

  const totalSimpul = filteredData.length;
  const totalAdd = filteredData.reduce((acc, c) => acc + (c.addArm || 0), 0);
  const totalCur = filteredData.reduce((acc, c) => acc + (c.armPuncak || 0), 0);
  const nationalAvgPct = totalCur > 0 ? (totalAdd / totalCur * 100).toFixed(1) : '0';

  const criticalCount = filteredData.filter(d => d.pctTambah === 20).length;
  const highCount = filteredData.filter(d => d.pctTambah === 15).length;
  const medCount = filteredData.filter(d => d.pctTambah === 10).length;
  const lowCount = filteredData.filter(d => d.pctTambah === 5).length;

  elSum.innerHTML = `
    <div class="flex items-start gap-2.5">
      <span class="w-2.5 h-2.5 rounded-full bg-indigo-600 mt-1 shrink-0"></span>
      <div class="space-y-1.5">
        <div class="font-bold text-slate-900 dark:text-white text-xs">
          Rangkuman Instruksi Operasional Terpadu (${{totalSimpul}} Simpul Terpilih):
        </div>
        <div class="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed space-y-1">
          <div>
            • <strong>Total Kebutuhan Tambahan Armada:</strong> Diperlukan penambahan <strong>+${{numFmt(totalAdd)}} armada fisik/hari (+${{nationalAvgPct}}%)</strong> untuk menjaga kelancaran arus mudik & balik dari total ${{numFmt(totalCur)}} armada operasi puncak.
          </div>
          <div>
            • <strong>Distribusi Tingkat Urgensi:</strong> 
            <span class="font-semibold text-rose-600 dark:text-rose-400">${{criticalCount}} Simpul Sangat Kritis (+20%)</span>, 
            <span class="font-semibold text-orange-600 dark:text-orange-400">${{highCount}} Simpul Tinggi (+15%)</span>, 
            <span class="font-semibold text-amber-600 dark:text-amber-400">${{medCount}} Simpul Padat (+10%)</span>, dan 
            <span class="font-semibold text-emerald-600 dark:text-emerald-400">${{lowCount}} Simpul Terkendali/Siaga (+5%)</span>.
          </div>
          <div>
            • <strong>Instruksi Utama Lapangan:</strong> Prioritaskan rekayasa *Tiba Bongkar Berangkat* di Pelabuhan Merak-Bakauheni & Ketapang-Gilimanuk, izin slot *extra flight* malam di CGK Soetta & DPS Bali, serta rangkaian Kereta Api Tambahan (KLB) di Pasar Senen & Gambir.
          </div>
        </div>
      </div>
    </div>
  `;
}}

function renderSimpulSimulation() {{
  const allData = DATA.simpul_recommendations || [];
  const tbody = document.getElementById('tbody-simpul-matrix');
  if (!tbody) return;
  tbody.innerHTML = '';

  // 1. Filter
  let filtered = allData.filter(s => {{
    const matchModa = (simpulModaFilter === 'ALL' || s.moda === simpulModaFilter);
    const matchStatus = (simpulStatusFilter === 'ALL' || String(s.pctTambah) === String(simpulStatusFilter));
    const matchSearch = !simpulSearchQuery || 
      (s.name && s.name.toLowerCase().includes(simpulSearchQuery)) ||
      (s.prov && s.prov.toLowerCase().includes(simpulSearchQuery)) ||
      (s.modaLabel && s.modaLabel.toLowerCase().includes(simpulSearchQuery));
    return matchModa && matchStatus && matchSearch;
  }});

  // 2. Sort
  filtered.sort((a, b) => {{
    if (simpulSortBy === 'pnp_desc') return (b.pnpPuncak || 0) - (a.pnpPuncak || 0);
    if (simpulSortBy === 'pnp_asc') return (a.pnpPuncak || 0) - (b.pnpPuncak || 0);
    if (simpulSortBy === 'ratio_desc') return (b.loadRatio || 0) - (a.loadRatio || 0);
    if (simpulSortBy === 'pct_desc') return (b.pctTambah - a.pctTambah) || ((b.pnpPuncak || 0) - (a.pnpPuncak || 0));
    if (simpulSortBy === 'add_desc') return (b.addArm || 0) - (a.addArm || 0);
    if (simpulSortBy === 'name_asc') return a.name.localeCompare(b.name);
    return 0;
  }});

  const totalFiltered = filtered.length;
  let itemsToRender = filtered;
  let totalPages = 1;

  // 3. Pagination or Limit Handling
  const paginationNav = document.getElementById('simpulPaginationNav');
  if (simpulDisplayLimit === 'all') {{
    itemsToRender = filtered;
    if (paginationNav) paginationNav.classList.add('hidden');
  }} else {{
    const limit = parseInt(simpulDisplayLimit, 10);
    totalPages = Math.max(1, Math.ceil(totalFiltered / limit));
    if (simpulCurrentPage > totalPages) simpulCurrentPage = totalPages;
    if (simpulCurrentPage < 1) simpulCurrentPage = 1;

    const startIdx = (simpulCurrentPage - 1) * limit;
    const endIdx = startIdx + limit;
    itemsToRender = filtered.slice(startIdx, endIdx);

    if (paginationNav) {{
      paginationNav.classList.remove('hidden');
      const prevBtn = document.getElementById('btn-simpul-prev');
      const nextBtn = document.getElementById('btn-simpul-next');
      const pageLbl = document.getElementById('label-simpul-page');
      if (prevBtn) prevBtn.disabled = (simpulCurrentPage <= 1);
      if (nextBtn) nextBtn.disabled = (simpulCurrentPage >= totalPages);
      if (pageLbl) pageLbl.innerText = `Halaman ${{simpulCurrentPage}} dari ${{totalPages}}`;
    }}
  }}

  // 4. Update Badge Count
  const badgeCount = document.getElementById('badge-simpul-count');
  if (badgeCount) {{
    if (totalFiltered === 0) {{
      badgeCount.innerText = 'Tidak ada simpul yang cocok.';
    }} else if (simpulDisplayLimit === 'all') {{
      badgeCount.innerText = `Menampilkan Seluruh ${{totalFiltered}} Simpul (dari total ${{allData.length}} Simpul Nasional)`;
    }} else {{
      const limit = parseInt(simpulDisplayLimit, 10);
      const start = (simpulCurrentPage - 1) * limit + 1;
      const end = Math.min(simpulCurrentPage * limit, totalFiltered);
      badgeCount.innerText = `Menampilkan ${{start}} - ${{end}} dari ${{totalFiltered}} Simpul (Total Terdaftar: ${{allData.length}} Simpul Nasional)`;
    }}
  }}

  // 5. Update Dynamic Highlight Cards
  renderDynamicSimpulHighlights(filtered);

  // 6. Render Table Rows
  if (itemsToRender.length === 0) {{
    tbody.innerHTML = `
      <tr>
        <td colspan="10" class="py-12 text-center text-slate-400 font-sans">
          Tidak ada simpul prasarana yang memenuhi kriteria filter atau kata kunci pencarian.
        </td>
      </tr>
    `;
    renderDynamicSimpulSummary(filtered);
    return;
  }}

  const offset = (simpulDisplayLimit === 'all') ? 0 : (simpulCurrentPage - 1) * parseInt(simpulDisplayLimit, 10);

  itemsToRender.forEach((s, idx) => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-3 px-3 font-sans">
        <div class="flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-500 shrink-0">${{offset + idx + 1}}</span>
          <div>
            <div class="font-bold text-slate-900 dark:text-white">${{s.name}}</div>
            <div class="text-[10px] text-slate-500">${{s.prov}} • ${{s.modaLabel}}</div>
          </div>
        </div>
      </td>
      <td class="py-3 px-3 font-sans text-slate-700 dark:text-slate-300">
        <div class="font-medium">${{s.saranaType}}</div>
      </td>
      <td class="py-3 px-3 font-mono text-slate-600 dark:text-slate-400">
        <div>${{numFmt(s.pnpBiasa)}} pnp/h</div>
        <div class="text-[10px] text-slate-400 font-sans">${{numFmt(s.armBiasa)}} ${{s.saranaUnit}} (LF: ${{s.lfBiasa}})</div>
      </td>
      <td class="py-3 px-3 font-mono text-slate-900 dark:text-white font-semibold">
        <div>${{numFmt(s.pnpPuncak)}} pnp/h</div>
        <div class="text-[10px] text-rose-600 dark:text-rose-400 font-sans">${{numFmt(s.armPuncak)}} ${{s.saranaUnit}} (LF: ${{s.lfPuncak}})</div>
      </td>
      <td class="py-3 px-3 font-mono text-center">
        <span class="font-bold text-indigo-600 dark:text-indigo-400 text-xs">${{s.loadRatio}}x</span>
        <span class="text-[10px] text-slate-400 block font-sans">naik vs biasa</span>
      </td>
      <td class="py-3 px-3 text-center">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${{s.statusBadge}}">${{s.statusText}}</span>
      </td>
      <td class="py-3 px-3 text-center font-mono">
        <span class="px-2.5 py-1 rounded-md text-xs font-black bg-indigo-600 text-white shadow-xs">+${{s.pctTambah}}%</span>
      </td>
      <td class="py-3 px-3 text-right font-mono font-bold text-indigo-700 dark:text-indigo-400">
        +${{numFmt(s.addArm)}}
        <span class="text-[10px] font-normal text-slate-500 block font-sans">${{s.saranaUnit}}/hari</span>
      </td>
      <td class="py-3 px-3 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
        ${{numFmt(s.totalArm)}}
        <span class="text-[10px] font-normal text-slate-500 block font-sans">operasi harian</span>
      </td>
      <td class="py-3 px-3 font-sans text-xs text-slate-600 dark:text-slate-300 max-w-[260px] leading-relaxed">
        ${{s.fieldAction}}
      </td>
    `;
    tbody.appendChild(tr);
  }});

  // 7. Update Operational Summary
  renderDynamicSimpulSummary(filtered);
}}

const renderArmadaSimulation = renderSimpulSimulation;

function renderForecastWorkspace() {{
  renderForecastSummaryCards();
  renderForecastComparisonTable();
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
  const filenameRange = currentTimelineRange === 'custom' ? `${{customStartDate}}_sd_${{customEndDate}}` : currentTimelineRange;
  link.setAttribute('download', `strategihub_kemenhub_multimoda_${{filenameRange}}_${{currentMetric}}.csv`);
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
  updateDashboardMetricAndDirection();
}});
</script>
</body>
</html>
"""
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
        
    index_html = os.path.join(os.path.dirname(OUTPUT_HTML), "index.html")
    with open(index_html, 'w', encoding='utf-8') as f:
        f.write(html)
        
    # Also sync to local 'dashboard utama' folder if exists
    for folder_name in ["dashboard utama", "dashboard_utama"]:
        target_dir = os.path.join(os.path.dirname(OUTPUT_HTML), folder_name)
        if os.path.exists(target_dir):
            with open(os.path.join(target_dir, "index.html"), 'w', encoding='utf-8') as f:
                f.write(html)
            with open(os.path.join(target_dir, "Dashboard_Mobilitas_Nasional_2026.html"), 'w', encoding='utf-8') as f:
                f.write(html)
        
    print(f"Production dashboard successfully generated: {OUTPUT_HTML} and {index_html}")
    print(f"File size: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")

if __name__ == '__main__':
    generate_dashboard()
