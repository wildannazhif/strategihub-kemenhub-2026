import json
import os

bundle_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
out_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html"

with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

json_data_str = json.dumps(bundle, ensure_ascii=False)

# SVG Icons Definitions
icons = {
    'plane': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>',
    'train': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="3" rx="2"/><path d="M4 11h16"/><path d="M12 3v8"/><path d="m8 19-2 3"/><path d="m18 22-2-3"/><circle cx="8" cy="15" r="1"/><circle cx="16" cy="15" r="1"/></svg>',
    'bus': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6v6"/><path d="M16 6v6"/><path d="M4 6h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6z"/><path d="M4 11h16"/><path d="m6 18-1.5 2.5"/><path d="m18 18 1.5 2.5"/><circle cx="7.5" cy="14.5" r="1"/><circle cx="16.5" cy="14.5" r="1"/></svg>',
    'asdp': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20a4 4 0 0 0 8 0 4 4 0 0 0 8 0 4 4 0 0 0 4 0"/><path d="M4 17 2 9h20l-2 8"/><path d="M6 9V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v5"/><path d="M10 3v6"/><path d="M14 3v6"/></svg>',
    'ship': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><path d="M12 10v4"/><path d="M12 2v3"/></svg>',
    'trending_up': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    'calendar': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    'activity': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'users': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'truck': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>',
    'search': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    'layers': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    'pie': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    'download': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    'sidebar_toggle': '<svg class="w-5 h-5 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9-3 3 3 3"/></svg>',
    'sun': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
    'moon': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    'matrix': '<svg class="w-4 h-4 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>'
}

html_code = f"""<!DOCTYPE html>
<html lang="id" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SIASATI Analytics • Platform Data Mobilitas Multimoda Nasional 2026</title>

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Tailwind CSS Play CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- TW-Elements Stylesheet & Config -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tw-elements/css/tw-elements.min.css" />
<script>
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        fontFamily: {{
          sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
          mono: ['JetBrains Mono', 'monospace'],
        }},
        colors: {{
          primary: {{
            50: '#eff6ff',
            100: '#dbeafe',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
            800: '#1e40af',
            900: '#1e3a8a',
            950: '#0f172a'
          }}
        }}
      }}
    }}
  }};
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>
  body {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  }}
  .num-mono {{
    font-family: 'JetBrains Mono', monospace;
    font-feature-settings: "tnum" 1;
  }}
  /* Custom Scrollbars */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: rgba(148, 163, 184, 0.25); border-radius: 3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: rgba(148, 163, 184, 0.45); }}
</style>
</head>
<body class="bg-slate-950 text-slate-100 dark:bg-slate-950 dark:text-slate-100 flex min-h-screen antialiased selection:bg-blue-600 selection:text-white transition-colors duration-200">

  <!-- ============================================================= -->
  <!-- COLLAPSIBLE SIDEBAR DRAWER (TW-ELEMENTS STYLE)                -->
  <!-- ============================================================= -->
  <aside id="sidebar" class="fixed top-0 left-0 z-40 h-screen w-72 transition-transform duration-300 ease-in-out bg-slate-900 border-r border-slate-800 flex flex-col shadow-2xl dark:bg-slate-900 dark:border-slate-800">
    
    <!-- Sidebar Header -->
    <div class="px-5 py-4 flex items-center justify-between border-b border-slate-800">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
          ST
        </div>
        <div>
          <h1 class="text-sm font-extrabold tracking-tight text-white leading-tight">SIASATI DATA</h1>
          <p class="text-[11px] text-slate-400 font-medium">PUSDATIN KEMENHUB</p>
        </div>
      </div>
      <button onclick="toggleSidebar()" class="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" title="Sembunyikan Sidebar">
        {icons['sidebar_toggle']}
      </button>
    </div>

    <!-- Sidebar Scroll Area -->
    <div class="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
      
      <!-- Nav Modules -->
      <div>
        <p class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Modul Data Analitik</p>
        <nav class="space-y-1" role="tablist">
          <button onclick="selectView('view-timeline', 'Tren Mobilitas Harian (271 Hari)', this)" class="nav-item active w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-blue-400 bg-blue-600/10 border border-blue-500/30 transition-all text-left">
            {icons['trending_up']} <span>Tren Harian (271 Hari)</span>
          </button>
          <button onclick="selectView('view-lebaran', 'Data Puncak Lebaran 2026', this)" class="nav-item w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent transition-all text-left">
            {icons['activity']} <span>Puncak Lebaran 2026</span>
          </button>
          <button onclick="selectView('view-modal-share', 'Pangsa Pasar Antar-Moda', this)" class="nav-item w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent transition-all text-left">
            {icons['pie']} <span>Pangsa Pasar (Share %)</span>
          </button>
          <button onclick="selectView('view-load-factor', 'Beban & Okupansi Armada', this)" class="nav-item w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent transition-all text-left">
            {icons['layers']} <span>Beban Armada (Ratio)</span>
          </button>
          <button onclick="selectView('view-top-hubs', 'Peringkat Simpul Transportasi', this)" class="nav-item w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent transition-all text-left">
            {icons['search']} <span>Top 30 Simpul Nasional</span>
          </button>
          <button onclick="selectView('view-matrix', 'Matriks Komparasi 5 Moda', this)" class="nav-item w-full flex items-center gap-3 px-3 py-2 text-xs font-semibold rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent transition-all text-left">
            {icons['matrix']} <span>Matriks Angka Kritis</span>
          </button>
        </nav>
      </div>

      <!-- Quick Filter Deck -->
      <div>
        <p class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Filter Rentang Waktu</p>
        <div class="bg-slate-950/60 rounded-lg p-1.5 border border-slate-800 space-y-1">
          <button onclick="setPeriodFilter('all', this)" class="btn-period active w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-medium text-white bg-blue-600 transition-all">
            <span>Sepanjang 2026</span>
            <span class="num-mono text-[10px] opacity-80">271 Hari</span>
          </button>
          <button onclick="setPeriodFilter('lebaran', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
            <span>Puncak Lebaran</span>
            <span class="num-mono text-[10px] opacity-80">27 Hari</span>
          </button>
          <button onclick="setPeriodFilter('libur_sekolah', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
            <span>Libur Sekolah</span>
            <span class="num-mono text-[10px] opacity-80">31 Hari</span>
          </button>
          <button onclick="setPeriodFilter('tahun_baru', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
            <span>Tahun Baru</span>
            <span class="num-mono text-[10px] opacity-80">15 Hari</span>
          </button>
        </div>
      </div>

      <!-- Metrik Switch -->
      <div>
        <p class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Metrik Data</p>
        <div class="grid grid-cols-2 gap-1.5 bg-slate-950/60 p-1 rounded-lg border border-slate-800">
          <button id="btn-metric-pnp" onclick="setMetric('pnp')" class="py-1.5 px-2 rounded-md text-xs font-semibold text-center text-white bg-blue-600 transition-all">
            Penumpang
          </button>
          <button id="btn-metric-arm" onclick="setMetric('arm')" class="py-1.5 px-2 rounded-md text-xs font-semibold text-center text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
            Armada
          </button>
        </div>
      </div>

      <!-- Export Button -->
      <div>
        <button onclick="exportCSV()" class="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all shadow-sm">
          {icons['download']} <span>Ekspor Data (CSV)</span>
        </button>
      </div>

      <!-- Dataset Verification Footnote -->
      <div class="pt-3 border-t border-slate-800/80">
        <div class="px-2 py-2 rounded-md bg-emerald-950/30 border border-emerald-800/30">
          <div class="flex items-center gap-1.5 text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            DATA VERIFIKASI BERSIH
          </div>
          <p class="text-[11px] text-slate-400 mt-1 num-mono">283.116 Baris Transaksi</p>
          <p class="text-[10px] text-slate-500">01 Jan 2026 - 28 Sep 2026</p>
        </div>
      </div>

    </div>
  </aside>

  <!-- ============================================================= -->
  <!-- MAIN WORKSPACE                                                -->
  <!-- ============================================================= -->
  <div id="main-area" class="flex-1 ml-72 transition-all duration-300 ease-in-out min-w-0">

    <!-- Top Navigation Bar -->
    <header class="sticky top-0 z-30 bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3 min-w-0">
        <button onclick="toggleSidebar()" class="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700 text-xs font-semibold flex items-center gap-2 transition-colors">
          {icons['sidebar_toggle']}
          <span id="txt-sidebar-toggle">Sembunyikan Menu</span>
        </button>

        <div class="flex items-center gap-2 text-xs text-slate-400 truncate">
          <span>SIASATI</span>
          <span>/</span>
          <span>Multimoda 2026</span>
          <span>/</span>
          <span id="active-breadcrumb" class="text-white font-semibold truncate">Tren Harian (271 Hari)</span>
        </div>
      </div>

      <div class="flex items-center gap-3 flex-shrink-0">
        <span class="hidden sm:inline-block px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-xs font-mono border border-slate-700">
          271 HARI PENGAMATAN
        </span>
        <button onclick="toggleDarkMode()" class="p-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors" title="Ganti Tema Gelap / Terang">
          {icons['sun']}
        </button>
      </div>
    </header>

    <!-- Content Container -->
    <main class="p-6 max-w-[1600px] mx-auto space-y-6">

      <!-- KPI METRIC CARDS (5 Core Exact Metrics) -->
      <section class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div class="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            <span>Total Penumpang YTD</span>
            <span class="text-blue-400">{icons['users']}</span>
          </div>
          <div class="text-2xl font-extrabold text-white num-mono tracking-tight" id="kpi-total-pnp">-</div>
          <div class="text-[11px] text-slate-400 mt-1 num-mono">5 Moda Transportasi</div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div class="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            <span>Puncak Tertinggi 2026</span>
            <span class="text-rose-400">{icons['activity']}</span>
          </div>
          <div class="text-2xl font-extrabold text-rose-400 num-mono tracking-tight">2.415.296</div>
          <div class="text-[11px] text-slate-400 mt-1 num-mono">24/03/2026 (H+3 Balik)</div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div class="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            <span>Puncak Arus Mudik</span>
            <span class="text-purple-400">{icons['asdp']}</span>
          </div>
          <div class="text-2xl font-extrabold text-purple-400 num-mono tracking-tight">2.258.518</div>
          <div class="text-[11px] text-slate-400 mt-1 num-mono">18/03/2026 (H-2 Mudik)</div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div class="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            <span>Lonjakan Tertinggi</span>
            <span class="text-amber-400">{icons['trending_up']}</span>
          </div>
          <div class="text-2xl font-extrabold text-amber-400 num-mono tracking-tight">+252,1%</div>
          <div class="text-[11px] text-slate-400 mt-1 num-mono">Moda ASDP (445.532 Pnp)</div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm col-span-2 sm:col-span-1">
          <div class="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            <span>Total Armada YTD</span>
            <span class="text-emerald-400">{icons['truck']}</span>
          </div>
          <div class="text-2xl font-extrabold text-white num-mono tracking-tight" id="kpi-total-arm">-</div>
          <div class="text-[11px] text-slate-400 mt-1 num-mono">Flight, Trip KA, Bus, Kapal</div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 1: TIMELINE & BULANAN                                -->
      <!-- ========================================================= -->
      <div id="view-timeline" class="view-panel space-y-6">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <h2 class="text-sm font-bold text-white tracking-tight" id="timeline-chart-title">Data Pergerakan Harian Penumpang Multimoda 2026</h2>
              <p class="text-xs text-slate-400">Volume harian: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut</p>
            </div>
            <div class="flex items-center gap-2">
              <span id="timeline-badge-info" class="text-xs font-mono text-slate-300 px-2.5 py-1 bg-slate-800 rounded border border-slate-700">
                1 Jan 2026 - 28 Sep 2026
              </span>
            </div>
          </div>
          <div class="relative w-full h-[380px]">
            <canvas id="chartTimeline"></canvas>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Monthly Data Table & Bar -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
            <h3 class="text-sm font-bold text-white tracking-tight">Akumulasi Bulanan per Moda (Januari s.d. September 2026)</h3>
            <div class="relative w-full h-[280px]">
              <canvas id="chartMonthly"></canvas>
            </div>
            <div class="overflow-x-auto rounded-lg border border-slate-800">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Bulan</th>
                    <th class="py-2.5 px-3">UDARA</th>
                    <th class="py-2.5 px-3">KA</th>
                    <th class="py-2.5 px-3">BUS</th>
                    <th class="py-2.5 px-3">ASDP</th>
                    <th class="py-2.5 px-3">LAUT</th>
                    <th class="py-2.5 px-3 text-right">TOTAL</th>
                  </tr>
                </thead>
                <tbody id="tbody-monthly" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>

          <!-- Day of Week Data Table & Bar -->
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
            <h3 class="text-sm font-bold text-white tracking-tight">Rata-rata Penumpang Harian per Hari dalam Seminggu</h3>
            <div class="relative w-full h-[280px]">
              <canvas id="chartDOW"></canvas>
            </div>
            <div class="overflow-x-auto rounded-lg border border-slate-800">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                  <tr>
                    <th class="py-2.5 px-3">Hari</th>
                    <th class="py-2.5 px-3">UDARA</th>
                    <th class="py-2.5 px-3">KA</th>
                    <th class="py-2.5 px-3">BUS</th>
                    <th class="py-2.5 px-3">ASDP</th>
                    <th class="py-2.5 px-3">LAUT</th>
                    <th class="py-2.5 px-3 text-right">RATA-RATA</th>
                  </tr>
                </thead>
                <tbody id="tbody-dow" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- VIEW 2: LEBARAN 2026                                      -->
      <!-- ========================================================= -->
      <div id="view-lebaran" class="view-panel hidden space-y-6">
        
        <!-- Day by Day Selector Strip -->
        <div class="space-y-2">
          <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">PILIH TANGGAL SPESIFIK ANGKUTAN LEBARAN (H-8 s.d. H+15):</p>
          <div class="flex gap-2 overflow-x-auto pb-2" id="lebaran-strip"></div>
        </div>

        <!-- Selected Day Inspector Box -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span id="box-tag" class="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">H-2 MUDIK</span>
              <span id="box-phase-name" class="text-xs text-slate-400">Puncak Arus Mudik</span>
            </div>
            <h3 id="box-date" class="text-lg font-bold text-white num-mono">18 Maret 2026</h3>
            <p id="box-total-text" class="text-xs text-slate-400 num-mono">Total Penumpang: 2.258.518 • Total Armada: 41.220</p>
          </div>
          <div id="box-breakdown-pills" class="flex flex-wrap gap-2"></div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Kurva Harian Dinamika 5 Moda Angkutan Lebaran 2026</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartLebaranLine"></canvas>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Perbandingan Persentase Lonjakan (%) terhadap Normal Februari</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartSurgeBar"></canvas>
            </div>
          </div>
        </div>

        <!-- Tabel Detail Lonjakan -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-white tracking-tight">Tabel Data Lonjakan Volume Penumpang Angkutan Lebaran 2026</h3>
          <div class="overflow-x-auto rounded-lg border border-slate-800">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                <tr>
                  <th class="py-3 px-3.5">Moda</th>
                  <th class="py-3 px-3.5">Normal (Feb)</th>
                  <th class="py-3 px-3.5">Peak Mudik (18 Mar)</th>
                  <th class="py-3 px-3.5">Delta Mudik (%)</th>
                  <th class="py-3 px-3.5">Peak Balik 1 (24 Mar)</th>
                  <th class="py-3 px-3.5">Delta Balik 1 (%)</th>
                  <th class="py-3 px-3.5">Peak Balik 2 (29 Mar)</th>
                  <th class="py-3 px-3.5">Delta Balik 2 (%)</th>
                </tr>
              </thead>
              <tbody id="tbody-surge" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- VIEW 3: MODAL SHARE                                       -->
      <!-- ========================================================= -->
      <div id="view-modal-share" class="view-panel hidden space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Pergerakan Proporsi Pangsa Pasar Bulanan (100% Stacked Area)</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartModalShareArea"></canvas>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Komparasi Proporsi Moda: Normal (Feb) vs Puncak Lebaran (Mar)</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="text-center">
                <p class="text-xs font-semibold text-slate-400 mb-2">Baseline Normal (Februari)</p>
                <div class="relative w-full h-[240px]"><canvas id="donutNormal"></canvas></div>
              </div>
              <div class="text-center">
                <p class="text-xs font-semibold text-blue-400 mb-2">Puncak Lebaran (Maret)</p>
                <div class="relative w-full h-[240px]"><canvas id="donutPeak"></canvas></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabel Angka Modal Share Murni -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-white tracking-tight">Tabel Data Pangsa Pasar Bulanan (%) per Moda Transportasi</h3>
          <div class="overflow-x-auto rounded-lg border border-slate-800">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                <tr>
                  <th class="py-3 px-3.5">Bulan</th>
                  <th class="py-3 px-3.5">UDARA (%)</th>
                  <th class="py-3 px-3.5">KERETA API (%)</th>
                  <th class="py-3 px-3.5">BUS AKAP (%)</th>
                  <th class="py-3 px-3.5">ASDP (%)</th>
                  <th class="py-3 px-3.5">LAUT (%)</th>
                  <th class="py-3 px-3.5 text-right">TOTAL VOLUME (PNP)</th>
                </tr>
              </thead>
              <tbody id="tbody-share" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- VIEW 4: LOAD FACTOR (BEBAN ARMADA)                        -->
      <!-- ========================================================= -->
      <div id="view-load-factor" class="view-panel hidden space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Rasio Intensitas Penumpang per Armada (Normal vs Puncak Lebaran)</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartLoadFactor"></canvas>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Data Utilisasi Keterisian Armada (Load Factor Proxy)</h3>
            <div class="overflow-x-auto rounded-lg border border-slate-800">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                  <tr>
                    <th class="py-3 px-3.5">Moda</th>
                    <th class="py-3 px-3.5">Rasio Normal (Feb)</th>
                    <th class="py-3 px-3.5">Rasio Puncak (Mar)</th>
                    <th class="py-3 px-3.5">Pertumbuhan Rasio (%)</th>
                    <th class="py-3 px-3.5">Satuan Metrik</th>
                  </tr>
                </thead>
                <tbody id="tbody-load-factor" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- VIEW 5: TOP SIMPUL                                        -->
      <!-- ========================================================= -->
      <div id="view-top-hubs" class="view-panel hidden space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900 p-4 border border-slate-800 rounded-xl">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold text-slate-400 uppercase">Filter Moda:</span>
            <div class="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800" id="hub-moda-bar">
              <button onclick="setHubModaFilter('ALL', this)" class="btn-hub-moda active px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 text-white">Semua</button>
              <button onclick="setHubModaFilter('UDARA', this)" class="btn-hub-moda px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Bandara</button>
              <button onclick="setHubModaFilter('KA', this)" class="btn-hub-moda px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Stasiun</button>
              <button onclick="setHubModaFilter('BUS', this)" class="btn-hub-moda px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Terminal</button>
              <button onclick="setHubModaFilter('ASDP', this)" class="btn-hub-moda px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Penyeberangan</button>
              <button onclick="setHubModaFilter('LAUT', this)" class="btn-hub-moda px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Pelabuhan Laut</button>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="relative">
              <input type="text" id="hub-search" placeholder="Cari nama simpul, kota..." onkeyup="searchHub(this.value)" class="w-56 bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 outline-none focus:border-blue-500">
            </div>

            <div class="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button id="btn-period-peak" onclick="setHubPeriodFilter('peak')" class="px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 text-white">Puncak Lebaran</button>
              <button id="btn-period-ytd" onclick="setHubPeriodFilter('ytd')" class="px-2.5 py-1 text-xs font-semibold rounded text-slate-400 hover:text-white">Sepanjang 2026</button>
            </div>
          </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                <tr>
                  <th class="py-3 px-3.5 w-14">Rank</th>
                  <th class="py-3 px-3.5">Nama Simpul / Prasarana</th>
                  <th class="py-3 px-3.5">Moda</th>
                  <th class="py-3 px-3.5">Provinsi</th>
                  <th class="py-3 px-3.5">Total Penumpang</th>
                  <th class="py-3 px-3.5">Total Armada</th>
                  <th class="py-3 px-3.5 w-60">Skala Volume</th>
                </tr>
              </thead>
              <tbody id="tbody-hubs" class="divide-y divide-slate-800/60 text-slate-200"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- VIEW 6: MATRIKS KOMPARASI 5 MODA                          -->
      <!-- ========================================================= -->
      <div id="view-matrix" class="view-panel hidden space-y-4">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-white tracking-tight">Matriks Data Rekapitulasi Komparatif 5 Moda Transportasi Nasional 2026</h3>
          <p class="text-xs text-slate-400">Ringkasan kuantitatif resmi seluruh indikator utama operasional multimoda 2026</p>
          <div class="overflow-x-auto rounded-lg border border-slate-800">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/80 text-slate-400 uppercase font-semibold border-b border-slate-700">
                <tr>
                  <th class="py-3 px-3.5">Indikator Kuantitatif</th>
                  <th class="py-3 px-3.5 text-blue-400">UDARA</th>
                  <th class="py-3 px-3.5 text-amber-400">KERETA API</th>
                  <th class="py-3 px-3.5 text-emerald-400">BUS AKAP</th>
                  <th class="py-3 px-3.5 text-purple-400">ASDP</th>
                  <th class="py-3 px-3.5 text-cyan-400">LAUT</th>
                  <th class="py-3 px-3.5 text-right font-bold text-white">TOTAL NASIONAL</th>
                </tr>
              </thead>
              <tbody id="tbody-matrix" class="divide-y divide-slate-800/60 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>
      </div>

    </main>
  </div>

<!-- TW-Elements JS CDN -->
<script src="https://cdn.jsdelivr.net/npm/tw-elements/js/tw-elements.umd.min.js"></script>

<!-- APPLICATION DATA & LOGIC SCRIPT -->
<script>
const DATA = {json_data_str};

const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// Application State
let isSidebarOpen = true;
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

const PALETTE = {{
  UDARA: '#38bdf8',
  KA: '#f59e0b',
  BUS: '#10b981',
  ASDP: '#8b5cf6',
  LAUT: '#06b6d4',
  TOTAL: '#ffffff'
}};

// -------------------------------------------------------------
// SIDEBAR COLLAPSE TOGGLE
// -------------------------------------------------------------
function toggleSidebar() {{
  const sb = document.getElementById('sidebar');
  const main = document.getElementById('main-area');
  const txt = document.getElementById('txt-sidebar-toggle');

  isSidebarOpen = !isSidebarOpen;
  if (isSidebarOpen) {{
    sb.classList.remove('-translate-x-full');
    main.classList.add('ml-72');
    txt.innerText = 'Sembunyikan Menu';
  }} else {{
    sb.classList.add('-translate-x-full');
    main.classList.remove('ml-72');
    txt.innerText = 'Buka Menu Fitur';
  }}

  setTimeout(() => {{
    if (chartTimelineInst) chartTimelineInst.resize();
    if (chartMonthlyInst) chartMonthlyInst.resize();
    if (chartDOWInst) chartDOWInst.resize();
    if (chartLebaranInst) chartLebaranInst.resize();
    if (chartSurgeInst) chartSurgeInst.resize();
    if (chartModalShareAreaInst) chartModalShareAreaInst.resize();
    if (donutNormalInst) donutNormalInst.resize();
    if (donutPeakInst) donutPeakInst.resize();
    if (chartLoadFactorInst) chartLoadFactorInst.resize();
  }}, 320);
}}

// -------------------------------------------------------------
// DARK/LIGHT MODE TOGGLE
// -------------------------------------------------------------
function toggleDarkMode() {{
  document.documentElement.classList.toggle('dark');
}}

// -------------------------------------------------------------
// NAVIGATION VIEW SWITCHER
// -------------------------------------------------------------
function selectView(viewId, viewTitle, btn) {{
  document.querySelectorAll('.nav-item').forEach(el => {{
    el.classList.remove('active', 'text-blue-400', 'bg-blue-600/10', 'border-blue-500/30');
    el.classList.add('text-slate-400', 'border-transparent');
  }});
  document.querySelectorAll('.view-panel').forEach(p => p.classList.add('hidden'));

  btn.classList.add('active', 'text-blue-400', 'bg-blue-600/10', 'border-blue-500/30');
  btn.classList.remove('text-slate-400', 'border-transparent');

  const panel = document.getElementById(viewId);
  if (panel) panel.classList.remove('hidden');

  document.getElementById('active-breadcrumb').innerText = viewTitle;

  setTimeout(() => {{
    if (viewId === 'view-timeline' && chartTimelineInst) chartTimelineInst.resize();
    if (viewId === 'view-lebaran') renderLebaranView();
    if (viewId === 'view-modal-share') renderModalShareView();
    if (viewId === 'view-load-factor') renderLoadFactorView();
    if (viewId === 'view-top-hubs') renderHubsTable();
    if (viewId === 'view-matrix') renderMatrixTable();
  }}, 50);
}}

// -------------------------------------------------------------
// TAB 1: TIMELINE
// -------------------------------------------------------------
function getTimelineData() {{
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') return all.filter(d => d.date >= '2026-03-10' && d.date <= '2026-04-05');
  if (currentTimelineRange === 'libur_sekolah') return all.filter(d => d.date >= '2026-06-15' && d.date <= '2026-07-15');
  if (currentTimelineRange === 'tahun_baru') return all.filter(d => d.date >= '2026-01-01' && d.date <= '2026-01-15');
  return all;
}}

function renderTimelineChart() {{
  const data = getTimelineData();
  const ctx = document.getElementById('chartTimeline').getContext('2d');
  const labels = data.map(d => d.date);
  const p = currentMetric === 'pnp' ? '' : 'arm_';

  const datasets = [
    {{ label: 'Total Multimoda', data: data.map(d => d[p + 'TOTAL']), borderColor: '#ffffff', borderWidth: 2.2, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Pesawat (Udara)', data: data.map(d => d[p + 'UDARA']), borderColor: PALETTE.UDARA, borderWidth: 1.6, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Kereta Api (KA)', data: data.map(d => d[p + 'KA']), borderColor: PALETTE.KA, borderWidth: 1.6, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Bus AKAP', data: data.map(d => d[p + 'BUS']), borderColor: PALETTE.BUS, borderWidth: 1.6, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Penyeberangan (ASDP)', data: data.map(d => d[p + 'ASDP']), borderColor: PALETTE.ASDP, borderWidth: 1.6, pointRadius: 0, tension: 0.15 }},
    {{ label: 'Kapal Laut', data: data.map(d => d[p + 'LAUT']), borderColor: PALETTE.LAUT, borderWidth: 1.6, pointRadius: 0, tension: 0.15 }},
  ];

  if (chartTimelineInst) chartTimelineInst.destroy();
  chartTimelineInst = new Chart(ctx, {{
    type: 'line',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ labels: {{ color: '#94a3b8', font: {{ family: 'Plus Jakarta Sans', size: 11 }} }} }},
        tooltip: {{
          backgroundColor: 'rgba(15,23,42,0.95)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(59,130,246,0.3)',
          borderWidth: 1,
          padding: 8,
          callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{currentMetric === 'pnp' ? 'pnp' : 'armada'}}` }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 14, font: {{ family: 'JetBrains Mono', size: 10 }} }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.06)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v/1e3).toFixed(0) + 'k') }} }}
      }}
    }}
  }});
}}

function setPeriodFilter(period, btn) {{
  currentTimelineRange = period;
  document.querySelectorAll('.btn-period').forEach(b => {{
    b.classList.remove('active', 'bg-blue-600', 'text-white');
    b.classList.add('text-slate-400');
  }});
  btn.classList.add('active', 'bg-blue-600', 'text-white');
  btn.classList.remove('text-slate-400');

  const labelMap = {{
    'all': '1 Jan 2026 - 28 Sep 2026 (271 Hari)',
    'lebaran': '10 Mar 2026 - 5 Apr 2026 (27 Hari)',
    'libur_sekolah': '15 Jun 2026 - 15 Jul 2026 (31 Hari)',
    'tahun_baru': '1 Jan 2026 - 15 Jan 2026 (15 Hari)'
  }};
  document.getElementById('timeline-badge-info').innerText = labelMap[period] || '';
  renderTimelineChart();
}}

function setMetric(m) {{
  currentMetric = m;
  document.getElementById('btn-metric-pnp').classList.toggle('bg-blue-600', m === 'pnp');
  document.getElementById('btn-metric-pnp').classList.toggle('text-white', m === 'pnp');
  document.getElementById('btn-metric-pnp').classList.toggle('text-slate-400', m !== 'pnp');

  document.getElementById('btn-metric-arm').classList.toggle('bg-blue-600', m === 'arm');
  document.getElementById('btn-metric-arm').classList.toggle('text-white', m === 'arm');
  document.getElementById('btn-metric-arm').classList.toggle('text-slate-400', m !== 'arm');

  document.getElementById('timeline-chart-title').innerText = m === 'pnp' ? 'Data Pergerakan Harian Penumpang Multimoda 2026' : 'Data Pergerakan Harian Armada Multimoda 2026';
  renderTimelineChart();
}}

function exportCSV() {{
  const data = getTimelineData();
  let csv = 'tanggal,udara_pnp,ka_pnp,bus_pnp,asdp_pnp,laut_pnp,total_pnp,udara_arm,ka_arm,bus_arm,asdp_arm,laut_arm,total_arm\\n';
  data.forEach(d => {{
    csv += `${{d.date}},${{d.UDARA}},${{d.KA}},${{d.BUS}},${{d.ASDP}},${{d.LAUT}},${{d.TOTAL}},${{d.arm_UDARA}},${{d.arm_KA}},${{d.arm_BUS}},${{d.arm_ASDP}},${{d.arm_LAUT}},${{d.arm_TOTAL}}\\n`;
  }});
  const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', `siasati_data_${{currentTimelineRange}}_${{currentMetric}}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

function renderMonthlyView() {{
  const ms = DATA.monthly_summary;
  const ctx = document.getElementById('chartMonthly').getContext('2d');
  
  if (chartMonthlyInst) chartMonthlyInst.destroy();
  chartMonthlyInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: ms.map(m => m.label.split(' ')[0]),
      datasets: [
        {{ label: 'Udara', data: ms.map(m => m.UDARA), backgroundColor: PALETTE.UDARA }},
        {{ label: 'KA', data: ms.map(m => m.KA), backgroundColor: PALETTE.KA }},
        {{ label: 'Bus', data: ms.map(m => m.BUS), backgroundColor: PALETTE.BUS }},
        {{ label: 'ASDP', data: ms.map(m => m.ASDP), backgroundColor: PALETTE.ASDP }},
        {{ label: 'Laut', data: ms.map(m => m.LAUT), backgroundColor: PALETTE.LAUT }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }},
      scales: {{
        x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }},
        y: {{ stacked: true, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e6).toFixed(0) + 'M' }} }}
      }}
    }}
  }});

  // Table Monthly
  const tbody = document.getElementById('tbody-monthly');
  tbody.innerHTML = '';
  ms.forEach(m => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2 px-3 font-sans font-medium text-slate-300">${{m.label}}</td>
      <td class="py-2 px-3">${{numFmt(m.UDARA)}}</td>
      <td class="py-2 px-3">${{numFmt(m.KA)}}</td>
      <td class="py-2 px-3">${{numFmt(m.BUS)}}</td>
      <td class="py-2 px-3">${{numFmt(m.ASDP)}}</td>
      <td class="py-2 px-3">${{numFmt(m.LAUT)}}</td>
      <td class="py-2 px-3 text-right font-bold text-white">${{numFmt(m.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderDOWView() {{
  const dow = DATA.dow_summary;
  const ctx = document.getElementById('chartDOW').getContext('2d');

  if (chartDOWInst) chartDOWInst.destroy();
  chartDOWInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: dow.map(d => d.dow),
      datasets: [{{ label: 'Rata-rata Penumpang Harian', data: dow.map(d => d.TOTAL), backgroundColor: 'rgba(59, 130, 246, 0.5)', borderColor: '#3b82f6', borderWidth: 1.5, borderRadius: 4 }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e6).toFixed(1) + 'M' }} }}
      }}
    }}
  }});

  const tbody = document.getElementById('tbody-dow');
  tbody.innerHTML = '';
  dow.forEach(d => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2 px-3 font-sans font-medium text-slate-300">${{d.dow}}</td>
      <td class="py-2 px-3">${{numFmt(d.UDARA)}}</td>
      <td class="py-2 px-3">${{numFmt(d.KA)}}</td>
      <td class="py-2 px-3">${{numFmt(d.BUS)}}</td>
      <td class="py-2 px-3">${{numFmt(d.ASDP)}}</td>
      <td class="py-2 px-3">${{numFmt(d.LAUT)}}</td>
      <td class="py-2 px-3 text-right font-bold text-white">${{numFmt(d.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 2: LEBARAN VIEW
// -------------------------------------------------------------
function selectLebaranDay(dateStr) {{
  const day = DATA.lebaran_daily.find(d => d.date === dateStr);
  if (!day) return;

  document.getElementById('box-tag').innerText = day.tag;
  document.getElementById('box-phase-name').innerText = day.desc;
  document.getElementById('box-date').innerText = day.date;
  document.getElementById('box-total-text').innerText = `Total Penumpang: ${{numFmt(day.TOTAL)}} • Total Armada: ${{numFmt(day.arm_TOTAL)}} Trip`;

  const pills = document.getElementById('box-breakdown-pills');
  pills.innerHTML = `
    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-sky-400">UDARA</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.UDARA)}}</div>
    </div>
    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-amber-400">KERETA API</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.KA)}}</div>
    </div>
    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-emerald-400">BUS</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.BUS)}}</div>
    </div>
    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-purple-400">ASDP</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.ASDP)}}</div>
    </div>
    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-cyan-400">LAUT</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.LAUT)}}</div>
    </div>
  `;
}}

function renderLebaranView() {{
  if (chartLebaranInst) return;

  const strip = document.getElementById('lebaran-strip');
  strip.innerHTML = '';
  DATA.lebaran_daily.forEach(d => {{
    const btn = document.createElement('button');
    const isPeak = d.is_peak_balik1 || d.is_peak_mudik;
    btn.className = `flex-shrink-0 text-left p-2.5 rounded-lg border transition-all ${{isPeak ? 'bg-rose-950/20 border-rose-500/40 text-rose-300' : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'}}`;
    btn.innerHTML = `
      <div class="text-[9.5px] font-bold uppercase tracking-wider opacity-75">${{d.tag.split(' ')[0]}}</div>
      <div class="text-sm font-extrabold num-mono">${{(d.TOTAL/1e6).toFixed(2)}}M</div>
      <div class="text-[10px] text-slate-500 font-mono">${{d.date.substring(5)}}</div>
    `;
    btn.onclick = () => {{
      document.querySelectorAll('#lebaran-strip button').forEach(b => b.classList.remove('ring-2', 'ring-blue-500'));
      btn.classList.add('ring-2', 'ring-blue-500');
      selectLebaranDay(d.date);
    }};
    strip.appendChild(btn);
  }});
  selectLebaranDay('2026-03-24');

  // Chart Line
  const ctxLine = document.getElementById('chartLebaranLine').getContext('2d');
  const ld = DATA.lebaran_daily;
  chartLebaranInst = new Chart(ctxLine, {{
    type: 'line',
    data: {{
      labels: ld.map(d => d.date.substring(5) + ' (' + d.tag.split(' ')[0] + ')'),
      datasets: [
        {{ label: 'Total Multimoda', data: ld.map(d => d.TOTAL), borderColor: '#ffffff', borderWidth: 2.4, pointRadius: 2, tension: 0.15 }},
        {{ label: 'Pesawat', data: ld.map(d => d.UDARA), borderColor: PALETTE.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Kereta Api', data: ld.map(d => d.KA), borderColor: PALETTE.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Bus', data: ld.map(d => d.BUS), borderColor: PALETTE.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'ASDP', data: ld.map(d => d.ASDP), borderColor: PALETTE.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
        {{ label: 'Laut', data: ld.map(d => d.LAUT), borderColor: PALETTE.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.15 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }},
      scales: {{
        x: {{ grid: {{ color: 'rgba(255,255,255,0.04)' }}, ticks: {{ color: '#64748b', maxRotation: 45, font: {{ size: 9, family: 'JetBrains Mono' }} }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e3).toFixed(0) + 'k' }} }}
      }}
    }}
  }});

  // Chart Surge
  const ctxSurge = document.getElementById('chartSurgeBar').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
  const labelsSurge = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Laut', 'Udara', 'TOTAL'];
  chartSurgeInst = new Chart(ctxSurge, {{
    type: 'bar',
    data: {{
      labels: labelsSurge,
      datasets: [
        {{ label: 'Lonjakan Mudik 18 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_mudik_pct), backgroundColor: 'rgba(244, 63, 94, 0.75)', borderRadius: 4 }},
        {{ label: 'Lonjakan Balik 24 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik1_pct), backgroundColor: 'rgba(6, 182, 212, 0.75)', borderRadius: 4 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono' }}, callback: v => '+' + v + '%' }} }}
      }}
    }}
  }});

  // Table Surge
  const tbody = document.getElementById('tbody-surge');
  tbody.innerHTML = '';
  modas.forEach((m, idx) => {{
    const s = DATA.surge_summary[m];
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-300">${{labelsSurge[idx]}}</td>
      <td class="py-2.5 px-3.5">${{numFmt(s.baseline)}}</td>
      <td class="py-2.5 px-3.5 font-bold text-rose-400">${{numFmt(s.peak_mudik)}}</td>
      <td class="py-2.5 px-3.5 text-rose-400">+${{s.surge_mudik_pct}}%</td>
      <td class="py-2.5 px-3.5 font-bold text-cyan-400">${{numFmt(s.peak_balik1)}}</td>
      <td class="py-2.5 px-3.5 text-cyan-400">+${{s.surge_balik1_pct}}%</td>
      <td class="py-2.5 px-3.5">${{numFmt(s.peak_balik2)}}</td>
      <td class="py-2.5 px-3.5">+${{s.surge_balik2_pct}}%</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 3: MODAL SHARE VIEW
// -------------------------------------------------------------
function renderModalShareView() {{
  if (chartModalShareAreaInst) return;

  const ms = DATA.monthly_summary;
  const ctx = document.getElementById('chartModalShareArea').getContext('2d');

  chartModalShareAreaInst = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: ms.map(m => m.label.split(' ')[0]),
      datasets: [
        {{ label: 'Udara', data: ms.map(m => m.share_UDARA), borderColor: PALETTE.UDARA, backgroundColor: 'rgba(56, 189, 248, 0.35)', fill: true, tension: 0.2 }},
        {{ label: 'KA', data: ms.map(m => m.share_KA), borderColor: PALETTE.KA, backgroundColor: 'rgba(245, 158, 11, 0.35)', fill: true, tension: 0.2 }},
        {{ label: 'Bus', data: ms.map(m => m.share_BUS), borderColor: PALETTE.BUS, backgroundColor: 'rgba(16, 185, 129, 0.35)', fill: true, tension: 0.2 }},
        {{ label: 'ASDP', data: ms.map(m => m.share_ASDP), borderColor: PALETTE.ASDP, backgroundColor: 'rgba(139, 92, 246, 0.35)', fill: true, tension: 0.2 }},
        {{ label: 'Laut', data: ms.map(m => m.share_LAUT), borderColor: PALETTE.LAUT, backgroundColor: 'rgba(6, 182, 212, 0.35)', fill: true, tension: 0.2 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
        y: {{ stacked: true, max: 100, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono' }}, callback: v => v + '%' }} }}
      }}
    }}
  }});

  const feb = ms.find(m => m.bulan === '2026-02');
  const mar = ms.find(m => m.bulan === '2026-03');
  const labels = ['Udara', 'KA', 'Bus', 'ASDP', 'Laut'];
  const colors = [PALETTE.UDARA, PALETTE.KA, PALETTE.BUS, PALETTE.ASDP, PALETTE.LAUT];

  const ctxNorm = document.getElementById('donutNormal').getContext('2d');
  donutNormalInst = new Chart(ctxNorm, {{
    type: 'doughnut',
    data: {{ labels, datasets: [{{ data: [feb.share_UDARA, feb.share_KA, feb.share_BUS, feb.share_ASDP, feb.share_LAUT], backgroundColor: colors, borderWidth: 0 }}] }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 9 }} }} }} }} }}
  }});

  const ctxPeak = document.getElementById('donutPeak').getContext('2d');
  donutPeakInst = new Chart(ctxPeak, {{
    type: 'doughnut',
    data: {{ labels, datasets: [{{ data: [mar.share_UDARA, mar.share_KA, mar.share_BUS, mar.share_ASDP, mar.share_LAUT], backgroundColor: colors, borderWidth: 0 }}] }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 9 }} }} }} }} }}
  }});

  // Table Share
  const tbody = document.getElementById('tbody-share');
  tbody.innerHTML = '';
  ms.forEach(m => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-300">${{m.label}}</td>
      <td class="py-2.5 px-3.5">${{m.share_UDARA}}%</td>
      <td class="py-2.5 px-3.5">${{m.share_KA}}%</td>
      <td class="py-2.5 px-3.5">${{m.share_BUS}}%</td>
      <td class="py-2.5 px-3.5 font-bold text-purple-400">${{m.share_ASDP}}%</td>
      <td class="py-2.5 px-3.5">${{m.share_LAUT}}%</td>
      <td class="py-2.5 px-3.5 text-right font-bold text-white">${{numFmt(m.TOTAL)}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 4: LOAD FACTOR VIEW
// -------------------------------------------------------------
function renderLoadFactorView() {{
  if (chartLoadFactorInst) return;

  const ctx = document.getElementById('chartLoadFactor').getContext('2d');
  const lf = DATA.load_factor_stats;
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labels = ['ASDP', 'Bus', 'KA', 'Laut', 'Udara'];

  chartLoadFactorInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [
        {{ label: 'Baseline Normal (Feb)', data: modas.map(m => lf[m].normal_ratio), backgroundColor: 'rgba(148,163,184,0.3)', borderRadius: 4 }},
        {{ label: 'Puncak Lebaran (Mar)', data: modas.map(m => lf[m].peak_ratio), backgroundColor: 'rgba(59, 130, 246, 0.85)', borderRadius: 4 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono' }} }} }}
      }}
    }}
  }});

  const tbody = document.getElementById('tbody-load-factor');
  tbody.innerHTML = '';
  modas.forEach(m => {{
    const row = lf[m];
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-300">${{m}}</td>
      <td class="py-2.5 px-3.5">${{row.normal_ratio}}</td>
      <td class="py-2.5 px-3.5 font-bold text-blue-400">${{row.peak_ratio}}</td>
      <td class="py-2.5 px-3.5 text-emerald-400 font-bold">+${{row.growth_pct}}%</td>
      <td class="py-2.5 px-3.5 text-slate-400 font-sans">${{row.unit}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 5: TOP HUBS VIEW
// -------------------------------------------------------------
function setHubModaFilter(m, btn) {{
  currentHubModa = m;
  document.querySelectorAll('.btn-hub-moda').forEach(b => {{
    b.classList.remove('active', 'bg-blue-600', 'text-white');
    b.classList.add('text-slate-400');
  }});
  btn.classList.add('active', 'bg-blue-600', 'text-white');
  btn.classList.remove('text-slate-400');
  renderHubsTable();
}}

function setHubPeriodFilter(p) {{
  currentHubPeriod = p;
  document.getElementById('btn-period-peak').classList.toggle('bg-blue-600', p === 'peak');
  document.getElementById('btn-period-peak').classList.toggle('text-white', p === 'peak');
  document.getElementById('btn-period-peak').classList.toggle('text-slate-400', p !== 'peak');

  document.getElementById('btn-period-ytd').classList.toggle('bg-blue-600', p === 'ytd');
  document.getElementById('btn-period-ytd').classList.toggle('text-white', p === 'ytd');
  document.getElementById('btn-period-ytd').classList.toggle('text-slate-400', p !== 'ytd');

  renderHubsTable();
}}

function searchHub(val) {{
  currentSearchTerm = val.toLowerCase().trim();
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

  if (currentSearchTerm) {{
    list = list.filter(i => 
      (i.nama_prasarana || '').toLowerCase().includes(currentSearchTerm) ||
      (i.provinsi || '').toLowerCase().includes(currentSearchTerm)
    );
  }}

  if (list.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="7" class="py-8 text-center text-slate-500 font-sans">Tidak ada data simpul yang sesuai filter.</td></tr>';
    return;
  }}

  const maxVal = list[0].pnp || 1;
  list.forEach((item, idx) => {{
    const pct = ((item.pnp / maxVal) * 100).toFixed(0);
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40';
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-bold num-mono ${{idx < 3 ? 'text-amber-400' : 'text-slate-500'}}">#${{idx + 1}}</td>
      <td class="py-2.5 px-3.5 font-sans font-semibold text-white">${{item.nama_prasarana}}</td>
      <td class="py-2.5 px-3.5"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700 font-sans">${{item.moda}}</span></td>
      <td class="py-2.5 px-3.5 text-slate-400 font-sans">${{item.provinsi || '-'}}</td>
      <td class="py-2.5 px-3.5 font-bold text-white num-mono">${{numFmt(item.pnp)}}</td>
      <td class="py-2.5 px-3.5 text-slate-400 num-mono">${{numFmt(item.arm)}}</td>
      <td class="py-2.5 px-3.5">
        <div class="flex items-center gap-2">
          <div class="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div class="h-full bg-blue-500 rounded-full" style="width: ${{pct}}%;"></div>
          </div>
          <span class="text-[10px] text-slate-500 num-mono w-7 text-right">${{pct}}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 6: MATRIKS KOMPARASI 5 MODA (PURE DATA)
// -------------------------------------------------------------
function renderMatrixTable() {{
  const tbody = document.getElementById('tbody-matrix');
  tbody.innerHTML = '';

  const rows = [
    {{ label: 'Total Penumpang YTD (1 Jan - 28 Sep)', u: '118.806.525', ka: '82.474.740', bus: '75.058.489', asdp: '42.793.848', laut: '52.187.600', tot: '371.321.202' }},
    {{ label: 'Pangsa Pasar Volume Nasional (%)', u: '32,0%', ka: '22,2%', bus: '20,2%', asdp: '11,5%', laut: '14,1%', tot: '100,0%' }},
    {{ label: 'Total Armada Beroperasi (Trip/Flight)', u: '979.791', ka: '1.966.764', bus: '6.467.437', asdp: '388.461', laut: '211.996', tot: '10.014.449' }},
    {{ label: 'Rata-rata Normal Harian (Februari)', u: '426.901', ka: '260.774', bus: '240.999', asdp: '126.518', laut: '133.709', tot: '1.188.900' }},
    {{ label: 'Puncak Arus Mudik (18 Mar 2026)', u: '613.202', ka: '462.032', bus: '467.159', asdp: '445.532', laut: '270.593', tot: '2.258.518' }},
    {{ label: 'Persentase Lonjakan Mudik (%)', u: '+43,6%', ka: '+77,2%', bus: '+93,8%', asdp: '+252,1%', laut: '+102,4%', tot: '+90,0%' }},
    {{ label: 'Puncak Arus Balik 1 (24 Mar 2026)', u: '628.221', ka: '565.264', bus: '538.867', asdp: '409.502', laut: '273.442', tot: '2.415.296' }},
    {{ label: 'Persentase Lonjakan Balik 1 (%)', u: '+47,2%', ka: '+116,8%', bus: '+123,6%', asdp: '+223,7%', laut: '+104,5%', tot: '+103,2%' }},
    {{ label: 'Puncak Arus Balik 2 (29 Mar 2026)', u: '649.254', ka: '513.634', bus: '495.918', asdp: '371.497', laut: '295.192', tot: '2.325.495' }},
    {{ label: 'Rasio Penumpang/Armada (Normal)', u: '101,3', ka: '41,9', bus: '11,6', asdp: '110,5', laut: '51,0', tot: '37,1' }},
    {{ label: 'Rasio Penumpang/Armada (Puncak)', u: '120,7', ka: '62,1', bus: '17,2', asdp: '245,2', laut: '75,8', tot: '58,6' }},
    {{ label: 'Pertumbuhan Beban Armada (%)', u: '+19,2%', ka: '+48,2%', bus: '+48,3%', asdp: '+121,9%', laut: '+48,6%', tot: '+57,9%' }},
    {{ label: 'Simpul Tersibuk Utama (Peak Lebaran)', u: 'Soekarno-Hatta (2,11M)', ka: 'Pasar Senen (428k)', bus: 'Purabaya (446k)', asdp: 'Bakauheni (952k)', laut: 'Batam (515k)', tot: 'Bakauheni (952k)' }},
  ];

  rows.forEach((r, idx) => {{
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40 ' + (idx % 2 === 0 ? 'bg-slate-900/40' : '');
    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-sans font-medium text-slate-300">${{r.label}}</td>
      <td class="py-2.5 px-3.5">${{r.u}}</td>
      <td class="py-2.5 px-3.5">${{r.ka}}</td>
      <td class="py-2.5 px-3.5">${{r.bus}}</td>
      <td class="py-2.5 px-3.5 font-bold text-purple-400">${{r.asdp}}</td>
      <td class="py-2.5 px-3.5">${{r.laut}}</td>
      <td class="py-2.5 px-3.5 text-right font-bold text-white">${{r.tot}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// INIT
// -------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {{
  document.getElementById('kpi-total-pnp').innerText = numFmt(DATA.meta.total_passengers_ytd);
  document.getElementById('kpi-total-arm').innerText = numFmt(DATA.meta.total_armada_ytd);

  renderTimelineChart();
  renderMonthlyView();
  renderDOWView();
}});
</script>
</body>
</html>
"""

with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"File Dashboard TW-Elements Data-Only berhasil dibuat: {out_html}")
print(f"Ukuran file: {os.path.getsize(out_html) / 1024:.1f} KB")
