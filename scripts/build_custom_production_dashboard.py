"""
build_custom_production_dashboard.py
Purpose-built, custom-designed production-grade analytics console for SIASATI Kemenhub 2026.
Designed with human UI/UX discipline:
- No generic SaaS cards or AI template aesthetic (no random gradients, no glowing borders, no glassmorphism blur)
- Clear institutional hierarchy (Kementerian Perhubungan - Pusat Data dan Informasi)
- Integrated Executive Context Strip (inline metrics with vertical hairline rules)
- 6 Substantive Analytical Workspaces with natural layout variations:
  1. Kronologi Mobilitas Harian (271 Hari) + Split Panel Bulanan & Hari Seminggu
  2. Analisis Operasional Puncak Lebaran (Phase Scrubber H-8 s.d. H+15 + Deep Inspector + Surge Matrix)
  3. Pangsa Pasar Antar-Moda (100% Stacked Area + Komparasi Normal vs Peak)
  4. Rasio Beban & Utilisasi Armada (Load Factor Proxy)
  5. Master Registri Prasarana (Top Simpul Nasional dengan live search & multi-mode filter)
  6. Matriks Rekapitulasi 13 Indikator Multimoda
- Realistic interaction states (empty search states, active counters, status badges, CSV export)
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
<title>SIASATI Multimoda 2026 • Pusat Data dan Informasi Kemenhub</title>

<!-- Standard Institutional Typography -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Tailwind CSS Play CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<script>
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        fontFamily: {{
          sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
          mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
        }},
        colors: {{
          kemenhub: {{
            50: '#f0f5fa',
            100: '#e1ecf5',
            800: '#0f2d59',
            900: '#0a1d3a',
          }},
          moda: {{
            udara: '#0284c7',   // Sky 600
            ka: '#d97706',      // Amber 600
            bus: '#16a34a',     // Green 600
            asdp: '#9333ea',    // Purple 600
            laut: '#0891b2',    // Cyan 600
          }}
        }}
      }}
    }}
  }};
</script>

<!-- Chart.js 4.4 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>
  body {{
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
  }}
  .num-mono {{
    font-family: 'JetBrains Mono', monospace;
    font-feature-settings: "tnum" 1;
  }}
  /* Crisp Enterprise Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
  .dark ::-webkit-scrollbar-thumb {{ background: #334155; }}
  
  /* Focus accessibility */
  button:focus-visible, input:focus-visible {{
    outline: 2px solid #0284c7;
    outline-offset: 1px;
  }}
</style>
</head>

<body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 min-h-screen antialiased flex flex-col transition-colors duration-150">

  <!-- ============================================================= -->
  <!-- 1. INSTITUTIONAL TOP BAR (GOVERNMENT / ENTERPRISE STANDARD)   -->
  <!-- ============================================================= -->
  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40">
    <div class="max-w-[1680px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
      
      <!-- Brand & Identification -->
      <div class="flex items-center gap-3.5 min-w-0">
        <div class="w-10 h-10 rounded-lg bg-kemenhub-900 dark:bg-blue-900 flex items-center justify-center text-white font-extrabold text-sm tracking-tighter shrink-0 border border-slate-700">
          ST
        </div>
        <div class="leading-tight truncate">
          <div class="flex items-center gap-2">
            <h1 class="text-sm font-bold tracking-tight text-slate-900 dark:text-white uppercase truncate">SIASATI MULTIMODA 2026</h1>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
              PRODUKSI RESMI
            </span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Pusat Data dan Informasi (PUSDATIN) • Kementerian Perhubungan RI</p>
        </div>
      </div>

      <!-- Utilities & Actions -->
      <div class="flex items-center gap-2.5 shrink-0">
        <!-- Dataset Verification Info -->
        <div class="hidden md:flex flex-col text-right pr-3 border-r border-slate-200 dark:border-slate-800">
          <span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 num-mono">283.116 Transaksi Valid</span>
          <span class="text-[10px] text-slate-500">01 Jan 2026 - 28 Sep 2026</span>
        </div>

        <!-- Metric Selector (Global) -->
        <div class="inline-flex rounded-md border border-slate-300 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
          <button id="btn-metric-pnp" onclick="setGlobalMetric('pnp')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">
            Penumpang
          </button>
          <button id="btn-metric-arm" onclick="setGlobalMetric('arm')" class="px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">
            Armada
          </button>
        </div>

        <!-- CSV Export Action -->
        <button onclick="exportActiveCSV()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 shadow-xs transition-all">
          <svg class="w-3.5 h-3.5 text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          <span class="hidden sm:inline">Ekspor CSV</span>
        </button>

        <!-- Dark/Light Theme Toggle -->
        <button onclick="toggleTheme()" class="p-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all" title="Ganti Mode Tampilan (Terang/Gelap)">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </div>

    </div>
  </header>

  <!-- ============================================================= -->
  <!-- 2. PRIMARY NAVIGATION TABS (WORKSPACES)                       -->
  <!-- ============================================================= -->
  <nav class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
    <div class="max-w-[1680px] mx-auto px-4 sm:px-6 flex overflow-x-auto space-x-1" role="tablist">
      
      <button onclick="switchTab('tab-timeline', this)" class="tab-btn active inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-kemenhub-800 dark:border-blue-500 font-semibold text-xs text-kemenhub-800 dark:text-blue-400 whitespace-nowrap transition-colors">
        <span>1. Kronologi Harian (271 Hari)</span>
      </button>

      <button onclick="switchTab('tab-lebaran', this)" class="tab-btn inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-transparent font-medium text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 whitespace-nowrap transition-colors">
        <span>2. Puncak Lebaran 2026 (Mudik & Balik)</span>
      </button>

      <button onclick="switchTab('tab-modal-share', this)" class="tab-btn inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-transparent font-medium text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 whitespace-nowrap transition-colors">
        <span>3. Pangsa Pasar Antar-Moda</span>
      </button>

      <button onclick="switchTab('tab-load-factor', this)" class="tab-btn inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-transparent font-medium text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 whitespace-nowrap transition-colors">
        <span>4. Rasio Beban Armada (Load Factor)</span>
      </button>

      <button onclick="switchTab('tab-top-hubs', this)" class="tab-btn inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-transparent font-medium text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 whitespace-nowrap transition-colors">
        <span>5. Registri Simpul Transportasi (Top 30)</span>
      </button>

      <button onclick="switchTab('tab-matrix', this)" class="tab-btn inline-flex items-center gap-2 py-3 px-3.5 border-b-2 border-transparent font-medium text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 whitespace-nowrap transition-colors">
        <span>6. Matriks Rekapitulasi 13 Indikator</span>
      </button>

    </div>
  </nav>

  <!-- ============================================================= -->
  <!-- 3. INTEGRATED EXECUTIVE OPERATIONAL STRIP                      -->
  <!-- ============================================================= -->
  <section class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
    <div class="max-w-[1680px] mx-auto px-4 sm:px-6 py-3.5">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-slate-800">
        
        <!-- Metric 1: Total Volume YTD (Anchor) -->
        <div class="pt-2 md:pt-0 pr-4">
          <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5">
            Total Mobilitas Penumpang YTD
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-pnp">371.321.202</span>
            <span class="text-xs text-slate-500 font-medium">penumpang</span>
          </div>
          <div class="text-[11px] text-slate-500 mt-1 num-mono">
            Rata-rata: <span class="font-semibold text-slate-700 dark:text-slate-300">1.370.189</span> pnp/hari (271 hari)
          </div>
        </div>

        <!-- Metric 2: All-Time Peak (24 Mar) -->
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

        <!-- Metric 3: Mudik Peak (18 Mar) -->
        <div class="pt-3 md:pt-0 md:pl-4 pr-4">
          <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5 flex items-center justify-between">
            <span>Puncak Arus Mudik</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">MUDIK PEAK</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-bold text-purple-700 dark:text-purple-400 num-mono tracking-tight">2.258.518</span>
            <span class="text-xs text-slate-500 font-medium">penumpang</span>
          </div>
          <div class="text-[11px] text-slate-500 mt-1 num-mono">
            18 Mar 2026 (H-2 Mudik) • <span class="font-semibold text-purple-700 dark:text-purple-400">+90,0%</span> vs normal
          </div>
        </div>

        <!-- Metric 4: Fleet & Operations -->
        <div class="pt-3 md:pt-0 md:pl-4">
          <div class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5">
            Total Perjalanan Armada
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-bold text-slate-900 dark:text-white num-mono tracking-tight" id="strip-total-arm">10.014.449</span>
            <span class="text-xs text-slate-500 font-medium">trip/flight</span>
          </div>
          <div class="text-[11px] text-slate-500 mt-1 num-mono">
            Rata-rata: <span class="font-semibold text-slate-700 dark:text-slate-300">36.953</span> trip/hari • Rasio YTD: 37,1
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- ============================================================= -->
  <!-- 4. MAIN OPERATIONAL WORKSPACES                                -->
  <!-- ============================================================= -->
  <main class="max-w-[1680px] w-full mx-auto px-4 sm:px-6 py-6 flex-1 space-y-6">

    <!-- =========================================================== -->
    <!-- TAB 1: KRONOLOGI MOBILITAS HARIAN (271 HARI)                -->
    <!-- =========================================================== -->
    <div id="tab-timeline" class="tab-content space-y-6">
      
      <!-- Timeline Control Bar & Chart -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
        <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h2 id="timeline-chart-heading" class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
              Kronologi Mobilitas Multimoda Nasional 2026
            </h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Volume harian agregat: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut (01 Jan s.d. 28 Sep 2026)
            </p>
          </div>

          <!-- Date Range Filter Buttons -->
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-500 dark:text-slate-400">Rentang Waktu:</span>
            <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-50 dark:bg-slate-800 text-xs font-medium">
              <button onclick="setTimelineFilter('all', this)" class="btn-range active px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-semibold shadow-xs">
                Sepanjang 2026 (271H)
              </button>
              <button onclick="setTimelineFilter('lebaran', this)" class="btn-range px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                Puncak Lebaran (27H)
              </button>
              <button onclick="setTimelineFilter('libur_sekolah', this)" class="btn-range px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                Libur Sekolah (31H)
              </button>
              <button onclick="setTimelineFilter('tahun_baru', this)" class="btn-range px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                Tahun Baru (15H)
              </button>
            </div>
          </div>
        </div>

        <!-- Full-Width Chart Canvas -->
        <div class="relative w-full h-[420px] pt-4">
          <canvas id="chartTimelineCanvas"></canvas>
        </div>

        <!-- Chart Footnote with Direct Mode Badges -->
        <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-500">
          <div class="flex items-center gap-4 flex-wrap">
            <span class="font-medium text-slate-700 dark:text-slate-300">Legenda Moda:</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-600"></span> Udara (32,0%)</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-600"></span> Kereta Api (22,2%)</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-green-600"></span> Bus AKAP (20,2%)</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-purple-600"></span> ASDP (11,5%)</span>
            <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-600"></span> Laut (14,1%)</span>
          </div>
          <div class="num-mono text-[11px] text-slate-400">
            Sumber: Raw Log SIASATI Pusdatin Kemenhub
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
                  <th class="py-2 px-2.5 text-right font-bold text-slate-900 dark:text-white">Rata-rata</th>
                </tr>
              </thead>
              <tbody id="tbody-dow" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>

    <!-- =========================================================== -->
    <!-- TAB 2: PUNCAK LEBARAN 2026                                 -->
    <!-- =========================================================== -->
    <div id="tab-lebaran" class="tab-content hidden space-y-6">
      
      <!-- Phase Scrubber (Chronological Strip) -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">
              Pilih Tanggal Spesifik Angkutan Lebaran 2026 (H-8 s.d. H+15)
            </h3>
            <p class="text-[11px] text-slate-500">Klik salah satu tanggal untuk menginspeksi breakdown rincian volume 5 moda operasional</p>
          </div>
          <div class="flex items-center gap-3 text-xs">
            <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-rose-600"></span> Puncak Balik</span>
            <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-purple-600"></span> Puncak Mudik</span>
          </div>
        </div>

        <!-- Scrubber Buttons Strip -->
        <div class="flex gap-2 overflow-x-auto pb-2" id="lebaran-scrubber">
        </div>
      </div>

      <!-- Active Day Contextual Inspector (Full-Width Strip) -->
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

      <!-- Side-by-Side: Dynamic Curve vs Surge Comparison -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
            Dinamika Harian 5 Moda Angkutan Lebaran 2026
          </h3>
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
                <th class="py-2.5 px-3">Normal (Februari)</th>
                <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">Peak Mudik (18 Mar)</th>
                <th class="py-2.5 px-3 text-purple-700 dark:text-purple-400">Lonjakan Mudik (%)</th>
                <th class="py-2.5 px-3 text-rose-700 dark:text-rose-400">Peak Balik 1 (24 Mar)</th>
                <th class="py-2.5 px-3 text-rose-700 dark:text-rose-400">Lonjakan Balik 1 (%)</th>
                <th class="py-2.5 px-3 text-slate-700 dark:text-slate-300">Peak Balik 2 (29 Mar)</th>
                <th class="py-2.5 px-3 text-slate-700 dark:text-slate-300">Lonjakan Balik 2 (%)</th>
              </tr>
            </thead>
            <tbody id="tbody-surge" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- =========================================================== -->
    <!-- TAB 3: PANGSA PASAR ANTAR-MODA (MODAL SHARE)               -->
    <!-- =========================================================== -->
    <div id="tab-modal-share" class="tab-content hidden space-y-6">
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- 100% Stacked Area Chart (8 Cols) -->
        <div class="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Evolusi Pangsa Pasar Bulanan (100% Stacked Area)</h3>
              <p class="text-[11px] text-slate-500">Pergeseran porsi penumpang antar-moda setiap bulan sepanjang 2026</p>
            </div>
            <span class="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">Proporsi 100%</span>
          </div>

          <div class="relative w-full h-[320px] mt-3">
            <canvas id="chartModalShareAreaCanvas"></canvas>
          </div>
        </div>

        <!-- Normal vs Peak Comparison (4 Cols) -->
        <div class="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
          <div class="pb-3 border-b border-slate-100 dark:border-slate-800">
            <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Komparasi Proporsi Moda</h3>
            <p class="text-[11px] text-slate-500">Bulan Normal (Februari) vs Puncak Lebaran (Maret)</p>
          </div>

          <div class="grid grid-cols-2 gap-3 my-auto py-2">
            <div class="text-center">
              <span class="text-[11px] font-semibold text-slate-500">Normal (Feb)</span>
              <div class="relative w-full h-[180px] mt-1">
                <canvas id="donutNormalCanvas"></canvas>
              </div>
            </div>
            <div class="text-center">
              <span class="text-[11px] font-semibold text-rose-600 dark:text-rose-400">Puncak (Mar)</span>
              <div class="relative w-full h-[180px] mt-1">
                <canvas id="donutPeakCanvas"></canvas>
              </div>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
            Porsi ASDP meningkat dari <span class="font-bold text-slate-700 dark:text-slate-300">10,6%</span> menjadi <span class="font-bold text-purple-600">15,6%</span> pada masa Lebaran.
          </div>
        </div>
      </div>

      <!-- Monthly Share Data Table -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
        <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight pb-3 border-b border-slate-100 dark:border-slate-800">
          Tabel Persentase Pangsa Pasar Bulanan (%) per Moda Transportasi
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
                <th class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">Total Penumpang (Volume)</th>
              </tr>
            </thead>
            <tbody id="tbody-share" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- =========================================================== -->
    <!-- TAB 4: RASIO BEBAN ARMADA (LOAD FACTOR)                    -->
    <!-- =========================================================== -->
    <div id="tab-load-factor" class="tab-content hidden space-y-6">
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Load Factor Bar Chart (6 Cols) -->
        <div class="lg:col-span-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5">
          <div class="pb-3 border-b border-slate-100 dark:border-slate-800">
            <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Rasio Intensitas Penumpang per Armada</h3>
            <p class="text-[11px] text-slate-500">Perbandingan rata-rata harian penumpang per unit armada (Normal vs Puncak Lebaran)</p>
          </div>

          <div class="relative w-full h-[320px] mt-3">
            <canvas id="chartLoadFactorCanvas"></canvas>
          </div>
        </div>

        <!-- Load Factor Detailed Table (6 Cols) -->
        <div class="lg:col-span-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-5 flex flex-col justify-between">
          <div>
            <div class="pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Tabel Utilisasi Keterisian Armada (Load Factor Proxy)</h3>
              <p class="text-[11px] text-slate-500">Pertumbuhan beban operasional kendaraan/kapal/pesawat pada periode puncak</p>
            </div>

            <div class="overflow-x-auto mt-3">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Moda</th>
                    <th class="py-2.5 px-3">Rasio Normal (Feb)</th>
                    <th class="py-2.5 px-3 text-rose-600 dark:text-rose-400 font-bold">Rasio Puncak (Mar)</th>
                    <th class="py-2.5 px-3 text-emerald-600 dark:text-emerald-400 font-bold">Pertumbuhan (%)</th>
                    <th class="py-2.5 px-3 text-slate-500">Satuan Metrik</th>
                  </tr>
                </thead>
                <tbody id="tbody-load-factor" class="divide-y divide-slate-100 dark:divide-slate-800 num-mono text-slate-800 dark:text-slate-200">
                </tbody>
              </table>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
            ASDP mengalami lonjakan intensitas terbesar (+121,9%), di mana 1 kapal melayani rata-rata 245 penumpang per trip saat puncak.
          </div>
        </div>
      </div>

    </div>

    <!-- =========================================================== -->
    <!-- TAB 5: REGISTRI SIMPUL TRANSPORTASI (TOP 30)                -->
    <!-- =========================================================== -->
    <div id="tab-top-hubs" class="tab-content hidden space-y-4">
      
      <!-- Toolbar: Moda Filter, Search & Period Toggle -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4">
        
        <!-- Moda Filter Pills -->
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-xs font-semibold text-slate-500 dark:text-slate-400">Filter Moda:</span>
          <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-50 dark:bg-slate-800 text-xs font-medium">
            <button onclick="filterHubModa('ALL', this)" class="btn-hub-moda active px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-semibold shadow-xs">
              Semua (Multimoda)
            </button>
            <button onclick="filterHubModa('UDARA', this)" class="btn-hub-moda px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Bandara
            </button>
            <button onclick="filterHubModa('KA', this)" class="btn-hub-moda px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Stasiun KA
            </button>
            <button onclick="filterHubModa('BUS', this)" class="btn-hub-moda px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Terminal Bus
            </button>
            <button onclick="filterHubModa('ASDP', this)" class="btn-hub-moda px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Pelabuhan ASDP
            </button>
            <button onclick="filterHubModa('LAUT', this)" class="btn-hub-moda px-2.5 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Pelabuhan Laut
            </button>
          </div>
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

    <!-- =========================================================== -->
    <!-- TAB 6: MATRIKS REKAPITULASI 13 INDIKATOR MULTIMODA         -->
    <!-- =========================================================== -->
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

  </main>

  <!-- ============================================================= -->
  <!-- 5. INSTITUTIONAL FOOTER                                       -->
  <!-- ============================================================= -->
  <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-4 mt-auto">
    <div class="max-w-[1680px] mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
      <div class="flex items-center gap-3">
        <span class="font-semibold text-slate-700 dark:text-slate-300">Pusat Data dan Informasi (PUSDATIN) Kemenhub</span>
        <span>•</span>
        <span>Sistem Analitik Mobilitas SIASATI 2026</span>
      </div>
      <div class="num-mono text-[11px]">
        Terverifikasi Bersih: 283.116 baris • 1 Jan - 28 Sep 2026
      </div>
    </div>
  </footer>

<!-- APPLICATION DATA & CONTROLLER -->
<script>
const DATA = {json_data_str};

const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// State Variables
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
// TAB SWITCHING LOGIC
// ---------------------------------------------------------------
function switchTab(targetId, btn) {{
  document.querySelectorAll('.tab-btn').forEach(b => {{
    b.classList.remove('active', 'border-kemenhub-800', 'dark:border-blue-500', 'font-semibold', 'text-kemenhub-800', 'dark:text-blue-400');
    b.classList.add('border-transparent', 'font-medium', 'text-slate-500');
  }});
  document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

  btn.classList.add('active', 'border-kemenhub-800', 'dark:border-blue-500', 'font-semibold', 'text-kemenhub-800', 'dark:text-blue-400');
  btn.classList.remove('border-transparent', 'font-medium', 'text-slate-500');

  const content = document.getElementById(targetId);
  if (content) content.classList.remove('hidden');

  setTimeout(() => {{
    if (targetId === 'tab-timeline' && chartTimeline) chartTimeline.resize();
    if (targetId === 'tab-lebaran') renderLebaranWorkspace();
    if (targetId === 'tab-modal-share') renderModalShareWorkspace();
    if (targetId === 'tab-load-factor') renderLoadFactorWorkspace();
    if (targetId === 'tab-top-hubs') renderHubsTable();
    if (targetId === 'tab-matrix') renderMatrixTable();
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
  }}, 100);
}}

function setGlobalMetric(metric) {{
  currentMetric = metric;
  const isPnp = metric === 'pnp';

  document.getElementById('btn-metric-pnp').classList.toggle('bg-white', isPnp);
  document.getElementById('btn-metric-pnp').classList.toggle('dark:bg-slate-900', isPnp);
  document.getElementById('btn-metric-pnp').classList.toggle('text-slate-900', isPnp);
  document.getElementById('btn-metric-pnp').classList.toggle('dark:text-white', isPnp);
  document.getElementById('btn-metric-pnp').classList.toggle('shadow-xs', isPnp);
  document.getElementById('btn-metric-pnp').classList.toggle('text-slate-600', !isPnp);

  document.getElementById('btn-metric-arm').classList.toggle('bg-white', !isPnp);
  document.getElementById('btn-metric-arm').classList.toggle('dark:bg-slate-900', !isPnp);
  document.getElementById('btn-metric-arm').classList.toggle('text-slate-900', !isPnp);
  document.getElementById('btn-metric-arm').classList.toggle('dark:text-white', !isPnp);
  document.getElementById('btn-metric-arm').classList.toggle('shadow-xs', !isPnp);
  document.getElementById('btn-metric-arm').classList.toggle('text-slate-600', isPnp);

  document.getElementById('timeline-chart-heading').innerText = isPnp 
    ? 'Kronologi Mobilitas Multimoda Nasional 2026 (Penumpang)'
    : 'Kronologi Mobilitas Multimoda Nasional 2026 (Armada Beroperasi)';

  renderTimelineChart();
}}

// ---------------------------------------------------------------
// TAB 1: KRONOLOGI MOBILITAS CONTROLLER
// ---------------------------------------------------------------
function getFilteredTimelineData() {{
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') return all.filter(d => d.date >= '2026-03-10' && d.date <= '2026-04-05');
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
        legend: {{ display: false }}, // Described directly in footnote below
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
}}

function setTimelineFilter(rangeKey, btn) {{
  currentTimelineRange = rangeKey;
  document.querySelectorAll('.btn-range').forEach(b => {{
    b.classList.remove('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
  btn.classList.remove('text-slate-600', 'dark:text-slate-400');
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

  document.getElementById('insp-tag').innerText = day.tag;
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

  // Build Scrubber Buttons
  const strip = document.getElementById('lebaran-scrubber');
  strip.innerHTML = '';
  DATA.lebaran_daily.forEach(d => {{
    const btn = document.createElement('button');
    const isPeak = d.is_peak_balik1 || d.is_peak_mudik;
    btn.className = `shrink-0 text-left px-2.5 py-1.5 rounded border text-xs transition-all ${{
      isPeak 
        ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200 font-semibold' 
        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-400'
    }}`;
    btn.innerHTML = `
      <div class="text-[9px] uppercase tracking-wider text-slate-500">${{d.tag.split(' ')[0]}}</div>
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
  selectLebaranDate('2026-03-24');

  // Curve Chart
  const isDark = document.documentElement.classList.contains('dark');
  const ctxLine = document.getElementById('chartLebaranLineCanvas').getContext('2d');
  const ld = DATA.lebaran_daily;
  chartLebaranLine = new Chart(ctxLine, {{
    type: 'line',
    data: {{
      labels: ld.map(d => d.date.substring(5) + ' (' + d.tag.split(' ')[0] + ')'),
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
      plugins: {{ legend: {{ labels: {{ color: isDark ? '#cbd5e1' : '#475569', font: {{ size: 10 }} }} }} }},
      scales: {{
        x: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', maxRotation: 45, font: {{ size: 9, family: 'JetBrains Mono' }} }} }},
        y: {{ grid: {{ color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}, ticks: {{ color: isDark ? '#94a3b8' : '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e3).toFixed(0) + 'k' }} }}
      }}
    }}
  }});

  // Surge Bar
  const ctxSurge = document.getElementById('chartSurgeBarCanvas').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
  const labelsSurge = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Laut', 'Udara', 'TOTAL'];
  chartSurgeBar = new Chart(ctxSurge, {{
    type: 'bar',
    data: {{
      labels: labelsSurge,
      datasets: [
        {{ label: 'Mudik 18 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_mudik_pct), backgroundColor: '#9333ea', borderRadius: 3 }},
        {{ label: 'Balik 24 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik1_pct), backgroundColor: '#0284c7', borderRadius: 3 }},
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

  // Surge Table
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

  // Dual Donut Charts
  const feb = ms.find(m => m.bulan === '2026-02');
  const mar = ms.find(m => m.bulan === '2026-03');
  const labels = ['Udara', 'KA', 'Bus', 'ASDP', 'Laut'];
  const colors = [COLOR.UDARA, COLOR.KA, COLOR.BUS, COLOR.ASDP, COLOR.LAUT];

  const ctxNorm = document.getElementById('donutNormalCanvas').getContext('2d');
  chartDonutNormal = new Chart(ctxNorm, {{
    type: 'doughnut',
    data: {{ labels, datasets: [{{ data: [feb.share_UDARA, feb.share_KA, feb.share_BUS, feb.share_ASDP, feb.share_LAUT], backgroundColor: colors, borderWidth: 1 }}] }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
  }});

  const ctxPeak = document.getElementById('donutPeakCanvas').getContext('2d');
  chartDonutPeak = new Chart(ctxPeak, {{
    type: 'doughnut',
    data: {{ labels, datasets: [{{ data: [mar.share_UDARA, mar.share_KA, mar.share_BUS, mar.share_ASDP, mar.share_LAUT], backgroundColor: colors, borderWidth: 1 }}] }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
  }});

  // Table Share
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
      <td class="py-2.5 px-3 font-bold text-purple-700 dark:text-purple-400">${{m.share_ASDP}}%</td>
      <td class="py-2.5 px-3">${{m.share_LAUT}}%</td>
      <td class="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">${{numFmt(m.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 4: LOAD FACTOR CONTROLLER
// ---------------------------------------------------------------
function renderLoadFactorWorkspace() {{
  if (chartLoadFactor) return;

  const isDark = document.documentElement.classList.contains('dark');
  const ctx = document.getElementById('chartLoadFactorCanvas').getContext('2d');
  const lf = DATA.load_factor_stats;
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labels = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Laut', 'Udara'];

  chartLoadFactor = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [
        {{ label: 'Baseline Normal (Feb)', data: modas.map(m => lf[m].normal_ratio), backgroundColor: isDark ? '#475569' : '#94a3b8', borderRadius: 3 }},
        {{ label: 'Puncak Lebaran (Mar)', data: modas.map(m => lf[m].peak_ratio), backgroundColor: '#0284c7', borderRadius: 3 }},
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
  modas.forEach(m => {{
    const row = lf[m];
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{m}}</td>
      <td class="py-2.5 px-3">${{row.normal_ratio}}</td>
      <td class="py-2.5 px-3 font-bold text-sky-700 dark:text-sky-400">${{row.peak_ratio}}</td>
      <td class="py-2.5 px-3 text-emerald-700 dark:text-emerald-400 font-bold">+${{row.growth_pct}}%</td>
      <td class="py-2.5 px-3 text-slate-500 font-sans">${{row.unit}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 5: TOP HUBS CONTROLLER
// ---------------------------------------------------------------
function filterHubModa(m, btn) {{
  currentHubModa = m;
  document.querySelectorAll('.btn-hub-moda').forEach(b => {{
    b.classList.remove('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
    b.classList.add('text-slate-600', 'dark:text-slate-400');
  }});
  btn.classList.add('active', 'bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'font-semibold', 'shadow-xs');
  btn.classList.remove('text-slate-600', 'dark:text-slate-400');
  renderHubsTable();
}}

function setHubPeriod(p) {{
  currentHubPeriod = p;
  const isPeak = p === 'peak';

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

function handleHubSearch(val) {{
  currentHubSearchTerm = val.toLowerCase().trim();
  renderHubsTable();
}}

function renderHubsTable() {{
  const tbody = document.getElementById('tbody-hubs');
  tbody.innerHTML = '';

  const src = currentHubPeriod === 'peak' ? DATA.top_hubs_peak : DATA.top_hubs_ytd;
  let list = [];

  if (currentHubModa === 'ALL') {{
    Object.keys(src).forEach(m => {{
      src[m].forEach(item => list.push({{ ...item, moda: m }}));
    }});
    list.sort((a, b) => b.pnp - a.pnp);
    list = list.slice(0, 30);
  }} else {{
    list = (src[currentHubModa] || []).map(item => ({{ ...item, moda: currentHubModa }}));
  }}

  if (currentHubSearchTerm) {{
    list = list.filter(i => 
      (i.nama_prasarana || '').toLowerCase().includes(currentHubSearchTerm) ||
      (i.provinsi || '').toLowerCase().includes(currentHubSearchTerm)
    );
  }}

  document.getElementById('hub-result-count').innerText = `Menampilkan ${{list.length}} prasarana transportasi terfilter`;

  if (list.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="7" class="py-8 text-center text-slate-500 font-sans">Tidak ditemukan data simpul yang sesuai dengan kriteria pencarian.</td></tr>';
    return;
  }}

  const maxVal = list[0].pnp || 1;
  list.forEach((item, idx) => {{
    const pct = ((item.pnp / maxVal) * 100).toFixed(0);
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors';
    
    let rankBadge = `<span class="text-slate-400 font-mono">#${{idx + 1}}</span>`;
    if (idx === 0) rankBadge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">#1</span>`;
    else if (idx === 1) rankBadge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-200">#2</span>`;
    else if (idx === 2) rankBadge = `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-300">#3</span>`;

    tr.innerHTML = `
      <td class="py-2.5 px-3 text-center num-mono font-semibold">${{rankBadge}}</td>
      <td class="py-2.5 px-3 font-sans font-semibold text-slate-900 dark:text-slate-100">${{item.nama_prasarana}}</td>
      <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-sans">${{item.moda}}</span></td>
      <td class="py-2.5 px-3 text-slate-500 font-sans">${{item.provinsi || '-'}}</td>
      <td class="py-2.5 px-3 font-bold text-slate-900 dark:text-white num-mono">${{numFmt(item.pnp)}}</td>
      <td class="py-2.5 px-3 text-slate-500 num-mono">${{numFmt(item.arm)}}</td>
      <td class="py-2.5 px-3">
        <div class="flex items-center gap-2">
          <div class="flex-1 h-2 rounded bg-slate-100 dark:bg-slate-800 overflow-hidden">
            <div class="h-full bg-slate-700 dark:bg-blue-500 rounded" style="width: ${{pct}}%;"></div>
          </div>
          <span class="text-[10px] text-slate-400 num-mono w-7 text-right">${{pct}}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ---------------------------------------------------------------
// TAB 6: MATRIKS 13 INDIKATOR CONTROLLER
// ---------------------------------------------------------------
function renderMatrixTable() {{
  const tbody = document.getElementById('tbody-matrix');
  tbody.innerHTML = '';

  const rows = [
    {{ label: '1. Total Penumpang YTD (1 Jan - 28 Sep)', u: '118.806.525', ka: '82.474.740', bus: '75.058.489', asdp: '42.793.848', laut: '52.187.600', tot: '371.321.202' }},
    {{ label: '2. Pangsa Pasar Volume Nasional (%)', u: '32,0%', ka: '22,2%', bus: '20,2%', asdp: '11,5%', laut: '14,1%', tot: '100,0%' }},
    {{ label: '3. Total Armada Beroperasi (Trip/Flight)', u: '979.791', ka: '1.966.764', bus: '6.467.437', asdp: '388.461', laut: '211.996', tot: '10.014.449' }},
    {{ label: '4. Rata-rata Normal Harian (Februari)', u: '426.901', ka: '260.774', bus: '240.999', asdp: '126.518', laut: '133.709', tot: '1.188.900' }},
    {{ label: '5. Puncak Arus Mudik (18 Mar 2026)', u: '613.202', ka: '462.032', bus: '467.159', asdp: '445.532', laut: '270.593', tot: '2.258.518' }},
    {{ label: '6. Persentase Lonjakan Mudik (%)', u: '+43,6%', ka: '+77,2%', bus: '+93,8%', asdp: '+252,1%', laut: '+102,4%', tot: '+90,0%' }},
    {{ label: '7. Puncak Arus Balik 1 (24 Mar 2026)', u: '628.221', ka: '565.264', bus: '538.867', asdp: '409.502', laut: '273.442', tot: '2.415.296' }},
    {{ label: '8. Persentase Lonjakan Balik 1 (%)', u: '+47,2%', ka: '+116,8%', bus: '+123,6%', asdp: '+223,7%', laut: '+104,5%', tot: '+103,2%' }},
    {{ label: '9. Puncak Arus Balik 2 (29 Mar 2026)', u: '649.254', ka: '513.634', bus: '495.918', asdp: '371.497', laut: '295.192', tot: '2.325.495' }},
    {{ label: '10. Rasio Penumpang/Armada (Normal)', u: '101,3', ka: '41,9', bus: '11,6', asdp: '110,5', laut: '51,0', tot: '37,1' }},
    {{ label: '11. Rasio Penumpang/Armada (Puncak)', u: '120,7', ka: '62,1', bus: '17,2', asdp: '245,2', laut: '75,8', tot: '58,6' }},
    {{ label: '12. Pertumbuhan Beban Armada (%)', u: '+19,2%', ka: '+48,2%', bus: '+48,3%', asdp: '+121,9%', laut: '+48,6%', tot: '+57,9%' }},
    {{ label: '13. Simpul Tersibuk Utama (Peak)', u: 'Soekarno-Hatta', ka: 'Pasar Senen', bus: 'Purabaya', asdp: 'Bakauheni', laut: 'Batam', tot: 'Bakauheni (952k)' }},
  ];

  rows.forEach((r, idx) => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ' + (idx % 2 === 0 ? 'bg-slate-50/50 dark:bg-slate-800/20' : '');
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
  link.setAttribute('download', `siasati_kemenhub_multimoda_${{currentTimelineRange}}_${{currentMetric}}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

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
        
    print(f"Production-grade custom dashboard successfully generated: {OUTPUT_HTML}")
    print(f"File size: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")

if __name__ == '__main__':
    generate_dashboard()
