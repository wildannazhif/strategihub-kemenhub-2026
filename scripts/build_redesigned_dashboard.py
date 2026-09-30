"""
build_redesigned_dashboard.py
Total UI Overhaul for SIASATI Transportation Mobility Intelligence Dashboard 2026.
Features:
- Next-Gen Bento Grid & Glassmorphism Design System (inspired by Linear, Vercel, Apple Analytics)
- Dual-State Collapsible Sidebar Rail (Expanded 260px <-> Collapsed 72px Icon Dock with Floating Tooltips)
- 5 Bento KPI Cards with Integrated Multi-Point SVG Sparklines & Trend Indicators
- Zero AI Commentary (Strictly Pure Quantitative Data, Metrics, Tables, and Charts)
- TW-Elements UI Components + Tailwind CSS + Chart.js 4.4 Spline Area Visualizations
- 6 Modular Analytics Views with Search, Filters, Scrubber, and Dynamic Matrix
"""

import json
import os

BUNDLE_PATH = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
OUTPUT_HTML = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html"

def make_svg_sparkline(values, stroke_color, fill_grad_id, width=150, height=38):
    if not values:
        return ""
    min_v = min(values)
    max_v = max(values)
    rng = max_v - min_v if max_v != min_v else 1
    n = len(values)
    
    pts = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * width
        y = height - ((v - min_v) / rng) * (height - 8) - 4
        pts.append(f"{x:.1f},{y:.1f}")
    
    line_path = "M " + " L ".join(pts)
    area_path = f"M 0,{height} L " + " L ".join(pts) + f" L {width:.1f},{height} Z"
    
    svg = f"""<svg class="w-full h-9 overflow-visible" viewBox="0 0 {width} {height}" fill="none" preserveAspectRatio="none">
  <defs>
    <linearGradient id="{fill_grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{stroke_color}" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="{stroke_color}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
  <path d="{area_path}" fill="url(#{fill_grad_id})"/>
  <path d="{line_path}" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
    return svg

def build_dashboard():
    with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    daily = data['daily_timeline']
    lebaran = data['lebaran_daily']
    
    # Pre-generate Sparklines
    spark_pnp = make_svg_sparkline([x['TOTAL'] for x in daily], "#38bdf8", "grad_pnp")
    spark_peak = make_svg_sparkline([x['TOTAL'] for x in lebaran], "#f43f5e", "grad_peak")
    spark_mudik = make_svg_sparkline([x['TOTAL'] for x in lebaran[:10]], "#a855f7", "grad_mudik")
    spark_asdp = make_svg_sparkline([x['ASDP'] for x in lebaran], "#f59e0b", "grad_asdp")
    spark_arm = make_svg_sparkline([x['arm_TOTAL'] for x in daily], "#10b981", "grad_arm")
    
    json_data_str = json.dumps(data)

    html = f"""<!DOCTYPE html>
<html lang="id" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SIASATI Intelligence • Multimoda Analytics 2026</title>

<!-- High-End Typography -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Tailwind CSS Play CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- TW-Elements Stylesheet -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tw-elements/css/tw-elements.min.css" />

<script>
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        fontFamily: {{
          sans: ['Plus Jakarta Sans', 'system-ui', '-apple-system', 'sans-serif'],
          mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
        }},
        colors: {{
          surface: {{
            base: '#080B11',
            card: 'rgba(15, 23, 42, 0.65)',
            border: 'rgba(255, 255, 255, 0.08)',
            hover: 'rgba(255, 255, 255, 0.12)',
          }},
          brand: {{
            blue: '#38bdf8',
            amber: '#f59e0b',
            emerald: '#10b981',
            purple: '#a855f7',
            rose: '#f43f5e',
            cyan: '#06b6d4',
          }}
        }},
        boxShadow: {{
          'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
          'glow': '0 0 20px -5px rgba(56, 189, 248, 0.25)',
        }}
      }}
    }}
  }};
</script>

<!-- Chart.js 4.4 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>
  body {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    background-color: #080B11;
    background-image: 
      radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.12) 0%, transparent 45%),
      radial-gradient(circle at 100% 50%, rgba(168, 85, 247, 0.06) 0%, transparent 40%);
    background-attachment: fixed;
  }}
  .num-mono {{
    font-family: 'JetBrains Mono', monospace;
    font-feature-settings: "tnum" 1;
  }}
  .glass-card {{
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .glass-card:hover {{
    border-color: rgba(255, 255, 255, 0.14);
  }}
  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: rgba(148, 163, 184, 0.2); border-radius: 9999px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: rgba(148, 163, 184, 0.4); }}
</style>
</head>

<body class="text-slate-100 min-h-screen antialiased selection:bg-blue-600 selection:text-white transition-colors duration-200">

  <!-- ============================================================= -->
  <!-- DUAL-STATE SIDEBAR RAIL (EXPANDED 260px <-> COLLAPSED 72px)    -->
  <!-- ============================================================= -->
  <aside id="sidebar-rail" class="fixed top-0 left-0 z-50 h-screen w-64 bg-slate-950/90 backdrop-blur-2xl border-r border-slate-800/80 flex flex-col justify-between transition-all duration-300 ease-in-out shadow-2xl">
    
    <!-- Top Brand & Header -->
    <div>
      <div class="h-16 px-4 flex items-center justify-between border-b border-slate-800/70">
        <div class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center text-white font-black text-sm shadow-md shadow-blue-500/20 shrink-0">
            ST
          </div>
          <div class="sidebar-label transition-opacity duration-200 leading-tight">
            <h1 class="text-xs font-black tracking-wider uppercase text-white">SIASATI DATA</h1>
            <p class="text-[10px] text-slate-400 font-semibold">PUSDATIN KEMENHUB</p>
          </div>
        </div>

        <button onclick="toggleSidebar()" class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-all shrink-0" title="Collapse / Expand Sidebar">
          <svg id="icon-collapse-left" class="w-4 h-4 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
      </div>

      <!-- Navigation Modules List -->
      <div class="p-3 space-y-5 overflow-y-auto max-h-[calc(100vh-140px)]">
        <div>
          <p class="sidebar-label px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Modul Data</p>
          <nav class="space-y-1">
            
            <!-- Tab 1: Tren Harian -->
            <button onclick="selectView('view-timeline', 'Tren Mobilitas Multimoda (271 Hari)', this)" class="nav-btn active group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-white bg-blue-600/20 border border-blue-500/30 transition-all text-left">
              <span class="shrink-0 text-blue-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
              </span>
              <span class="sidebar-label truncate">Tren Harian (271 Hari)</span>
              <!-- Tooltip on collapsed rail -->
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Tren Harian</span>
            </button>

            <!-- Tab 2: Puncak Lebaran -->
            <button onclick="selectView('view-lebaran', 'Puncak Lebaran 2026 (Mudik & Balik)', this)" class="nav-btn group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent transition-all text-left">
              <span class="shrink-0 text-rose-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </span>
              <span class="sidebar-label truncate">Puncak Lebaran 2026</span>
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Puncak Lebaran</span>
            </button>

            <!-- Tab 3: Modal Share -->
            <button onclick="selectView('view-modal-share', 'Pangsa Pasar Antar-Moda (Modal Share)', this)" class="nav-btn group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent transition-all text-left">
              <span class="shrink-0 text-amber-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>
              </span>
              <span class="sidebar-label truncate">Pangsa Pasar (Share %)</span>
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Pangsa Pasar</span>
            </button>

            <!-- Tab 4: Load Factor -->
            <button onclick="selectView('view-load-factor', 'Beban & Okupansi Armada (Load Factor)', this)" class="nav-btn group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent transition-all text-left">
              <span class="shrink-0 text-emerald-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>
              </span>
              <span class="sidebar-label truncate">Beban Armada</span>
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Beban Armada</span>
            </button>

            <!-- Tab 5: Top Simpul -->
            <button onclick="selectView('view-top-hubs', 'Top 30 Simpul Prasarana Nasional', this)" class="nav-btn group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent transition-all text-left">
              <span class="shrink-0 text-purple-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              </span>
              <span class="sidebar-label truncate">Top 30 Simpul Nasional</span>
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Top Simpul</span>
            </button>

            <!-- Tab 6: Matriks Angka Kritis -->
            <button onclick="selectView('view-matrix', 'Matriks Komparasi 13 Indikator Multimoda', this)" class="nav-btn group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent transition-all text-left">
              <span class="shrink-0 text-cyan-400">
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
              </span>
              <span class="sidebar-label truncate">Matriks Angka Kritis</span>
              <span class="rail-tooltip absolute left-14 hidden px-2 py-1 bg-slate-900 border border-slate-700 text-white text-[11px] rounded shadow-lg whitespace-nowrap z-50">Matriks Kritis</span>
            </button>
          </nav>
        </div>

        <!-- Filter Periode Cepat -->
        <div class="sidebar-extra">
          <p class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Rentang Waktu</p>
          <div class="space-y-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800">
            <button onclick="setPeriodFilter('all', this)" class="btn-period active w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-white bg-blue-600 transition-all">
              <span>Sepanjang 2026</span>
              <span class="num-mono text-[10px] opacity-75">271H</span>
            </button>
            <button onclick="setPeriodFilter('lebaran', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/80 transition-all">
              <span>Puncak Lebaran</span>
              <span class="num-mono text-[10px] opacity-75">27H</span>
            </button>
            <button onclick="setPeriodFilter('libur_sekolah', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/80 transition-all">
              <span>Libur Sekolah</span>
              <span class="num-mono text-[10px] opacity-75">31H</span>
            </button>
            <button onclick="setPeriodFilter('tahun_baru', this)" class="btn-period w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/80 transition-all">
              <span>Tahun Baru</span>
              <span class="num-mono text-[10px] opacity-75">15H</span>
            </button>
          </div>
        </div>

        <!-- Metric Switcher -->
        <div class="sidebar-extra">
          <p class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Metrik Data</p>
          <div class="grid grid-cols-2 gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
            <button id="sb-metric-pnp" onclick="setMetric('pnp')" class="py-1.5 rounded-lg text-xs font-semibold text-center text-white bg-blue-600 transition-all">
              Penumpang
            </button>
            <button id="sb-metric-arm" onclick="setMetric('arm')" class="py-1.5 rounded-lg text-xs font-semibold text-center text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
              Armada
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Sidebar Bottom Footer -->
    <div class="p-3 border-t border-slate-800/70 space-y-2">
      <button onclick="exportCSV()" class="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-800 transition-all shadow-sm">
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
        <span class="sidebar-label">Ekspor CSV</span>
      </button>

      <div class="sidebar-extra px-2.5 py-1.5 rounded-lg bg-emerald-950/20 border border-emerald-800/20 flex items-center justify-between text-[10px]">
        <span class="text-emerald-400 font-semibold flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> VERIFIED
        </span>
        <span class="num-mono text-slate-400">283.116 ROW</span>
      </div>
    </div>
  </aside>

  <!-- ============================================================= -->
  <!-- MAIN WORKSPACE                                                -->
  <!-- ============================================================= -->
  <div id="main-area" class="pl-64 transition-all duration-300 ease-in-out min-w-0">

    <!-- Top Executive Nav Header -->
    <header class="sticky top-0 z-40 h-16 bg-[#080B11]/80 backdrop-blur-xl border-b border-slate-800/80 px-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3 min-w-0">
        <button onclick="toggleSidebar()" class="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9-3 3 3 3"/></svg>
        </button>

        <div class="flex items-center gap-2 text-xs text-slate-400 truncate font-medium">
          <span>SIASATI</span>
          <span class="text-slate-600">/</span>
          <span>Multimoda 2026</span>
          <span class="text-slate-600">/</span>
          <span id="header-breadcrumb" class="text-white font-semibold truncate">Tren Harian (271 Hari)</span>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        <!-- Metric Quick Selector Pills -->
        <div class="hidden sm:inline-flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <button id="top-metric-pnp" onclick="setMetric('pnp')" class="px-3 py-1 rounded-lg font-semibold bg-blue-600 text-white transition-all">Penumpang</button>
          <button id="top-metric-arm" onclick="setMetric('arm')" class="px-3 py-1 rounded-lg font-semibold text-slate-400 hover:text-white transition-all">Armada</button>
        </div>

        <!-- Dark/Light Mode Toggle -->
        <button onclick="toggleDarkMode()" class="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all" title="Toggle Dark/Light Mode">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </button>
      </div>
    </header>

    <!-- Main Content Grid -->
    <main class="p-6 max-w-[1680px] mx-auto space-y-6">

      <!-- ========================================================= -->
      <!-- 5 BENTO KPI CARDS WITH LIVE SVG SPARKLINES                -->
      <!-- ========================================================= -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        
        <!-- KPI 1 -->
        <div class="glass-card rounded-2xl p-4 shadow-glass relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1">
            <span>Total Penumpang YTD</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">271 Hari</span>
          </div>
          <div class="text-2xl font-black text-white num-mono tracking-tight my-1" id="kpi-total-pnp">371.321.202</div>
          <div class="pt-2">
            {spark_pnp}
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 num-mono">
            <span>5 Moda Multimoda</span>
            <span class="text-blue-400 font-semibold">100% Valid</span>
          </div>
        </div>

        <!-- KPI 2 -->
        <div class="glass-card rounded-2xl p-4 shadow-glass relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1">
            <span>Puncak Tertinggi 2026</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">All-Time Peak</span>
          </div>
          <div class="text-2xl font-black text-rose-400 num-mono tracking-tight my-1">2.415.296</div>
          <div class="pt-2">
            {spark_peak}
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 num-mono">
            <span>24 Maret 2026</span>
            <span class="text-rose-400 font-semibold">H+3 Balik 1</span>
          </div>
        </div>

        <!-- KPI 3 -->
        <div class="glass-card rounded-2xl p-4 shadow-glass relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1">
            <span>Puncak Arus Mudik</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20">Mudik Peak</span>
          </div>
          <div class="text-2xl font-black text-purple-400 num-mono tracking-tight my-1">2.258.518</div>
          <div class="pt-2">
            {spark_mudik}
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 num-mono">
            <span>18 Maret 2026</span>
            <span class="text-purple-400 font-semibold">H-2 Mudik</span>
          </div>
        </div>

        <!-- KPI 4 -->
        <div class="glass-card rounded-2xl p-4 shadow-glass relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1">
            <span>Lonjakan Tertinggi</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">Delta Peak</span>
          </div>
          <div class="text-2xl font-black text-amber-400 num-mono tracking-tight my-1">+252,1%</div>
          <div class="pt-2">
            {spark_asdp}
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 num-mono">
            <span>Penyeberangan ASDP</span>
            <span class="text-amber-400 font-semibold">445.532 Pnp</span>
          </div>
        </div>

        <!-- KPI 5 -->
        <div class="glass-card rounded-2xl p-4 shadow-glass relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1">
            <span>Total Armada YTD</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Trip Operasional</span>
          </div>
          <div class="text-2xl font-black text-emerald-400 num-mono tracking-tight my-1" id="kpi-total-arm">10.014.449</div>
          <div class="pt-2">
            {spark_arm}
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 num-mono">
            <span>Flight, KA, Bus, Kapal</span>
            <span class="text-emerald-400 font-semibold">36.953/Hari</span>
          </div>
        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 1: TREN MOBILITAS HARIAN (271 HARI)                  -->
      <!-- ========================================================= -->
      <section id="view-timeline" class="view-panel space-y-6">
        
        <!-- Large Chart Card -->
        <div class="glass-card rounded-2xl p-6 shadow-glass space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 id="timeline-chart-title" class="text-base font-bold text-white tracking-tight">Pergerakan Harian Penumpang Multimoda 2026</h2>
              <p class="text-xs text-slate-400">Distribusi volume harian 5 moda: Udara, Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut</p>
            </div>
            
            <div class="flex items-center gap-2">
              <span id="timeline-badge-info" class="text-xs font-mono text-slate-300 px-3 py-1 bg-slate-950 rounded-xl border border-slate-800">
                1 Jan 2026 - 28 Sep 2026 (271 Hari)
              </span>
            </div>
          </div>

          <div class="relative w-full h-[400px]">
            <canvas id="chartTimeline"></canvas>
          </div>
        </div>

        <!-- Monthly & Day of Week Dual Bento -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <!-- Monthly Data Table & Bar -->
          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-bold text-white tracking-tight">Volume Bulanan per Moda Transportasi</h3>
              <span class="text-[11px] font-mono text-slate-400">Januari - September 2026</span>
            </div>
            
            <div class="relative w-full h-[260px]">
              <canvas id="chartMonthly"></canvas>
            </div>

            <div class="overflow-x-auto rounded-xl border border-slate-800/80">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">Bulan</th>
                    <th class="py-2.5 px-3 text-sky-400">UDARA</th>
                    <th class="py-2.5 px-3 text-amber-400">KA</th>
                    <th class="py-2.5 px-3 text-emerald-400">BUS</th>
                    <th class="py-2.5 px-3 text-purple-400">ASDP</th>
                    <th class="py-2.5 px-3 text-cyan-400">LAUT</th>
                    <th class="py-2.5 px-3 text-right text-white">TOTAL</th>
                  </tr>
                </thead>
                <tbody id="tbody-monthly" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>

          <!-- Day of Week Distribution -->
          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-bold text-white tracking-tight">Rata-rata Penumpang Harian per Hari dalam Seminggu</h3>
              <span class="text-[11px] font-mono text-slate-400">Senin s.d. Minggu</span>
            </div>

            <div class="relative w-full h-[260px]">
              <canvas id="chartDOW"></canvas>
            </div>

            <div class="overflow-x-auto rounded-xl border border-slate-800/80">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">Hari</th>
                    <th class="py-2.5 px-3 text-sky-400">UDARA</th>
                    <th class="py-2.5 px-3 text-amber-400">KA</th>
                    <th class="py-2.5 px-3 text-emerald-400">BUS</th>
                    <th class="py-2.5 px-3 text-purple-400">ASDP</th>
                    <th class="py-2.5 px-3 text-cyan-400">LAUT</th>
                    <th class="py-2.5 px-3 text-right text-white">RATA-RATA</th>
                  </tr>
                </thead>
                <tbody id="tbody-dow" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>

        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 2: PUNCAK LEBARAN 2026                               -->
      <!-- ========================================================= -->
      <section id="view-lebaran" class="view-panel hidden space-y-6">
        
        <!-- Day by Day Horizontal Scrubber -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs font-bold text-slate-400 uppercase tracking-wider">
            <span>PILIH TANGGAL ANGKUTAN LEBARAN 2026 (H-8 s.d. H+15):</span>
            <span class="text-[11px] text-blue-400 font-normal">Klik tanggal untuk inspeksi rincian 5 moda</span>
          </div>
          <div class="flex gap-2 overflow-x-auto pb-2" id="lebaran-strip"></div>
        </div>

        <!-- Selected Day Inspector Box -->
        <div class="glass-card rounded-2xl p-5 shadow-glass flex flex-wrap items-center justify-between gap-6 border-l-4 border-l-rose-500">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span id="box-tag" class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">H+3 BALIK 1</span>
              <span id="box-phase-name" class="text-xs text-slate-400 font-medium">Puncak Arus Balik Terbesar 2026</span>
            </div>
            <h3 id="box-date" class="text-xl font-black text-white num-mono">24 Maret 2026</h3>
            <p id="box-total-text" class="text-xs text-slate-400 num-mono mt-1">Total Penumpang: 2.415.296 • Total Armada: 45.835 Trip</p>
          </div>

          <div id="box-breakdown-pills" class="flex flex-wrap gap-2.5"></div>
        </div>

        <!-- Lebaran Curves & Surge Bars -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Kurva Harian Dinamika 5 Moda Angkutan Lebaran 2026</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartLebaranLine"></canvas>
            </div>
          </div>

          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Persentase Lonjakan (%) terhadap Rata-rata Normal Februari</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartSurgeBar"></canvas>
            </div>
          </div>
        </div>

        <!-- Tabel Detail Lonjakan Murni -->
        <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
          <h3 class="text-sm font-bold text-white tracking-tight">Tabel Data Kuantitatif Lonjakan Angkutan Lebaran 2026</h3>
          <div class="overflow-x-auto rounded-xl border border-slate-800/80">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th class="py-3 px-3.5">Moda Transportasi</th>
                  <th class="py-3 px-3.5">Normal (Feb)</th>
                  <th class="py-3 px-3.5 text-rose-400">Peak Mudik (18 Mar)</th>
                  <th class="py-3 px-3.5 text-rose-400">Delta Mudik (%)</th>
                  <th class="py-3 px-3.5 text-cyan-400">Peak Balik 1 (24 Mar)</th>
                  <th class="py-3 px-3.5 text-cyan-400">Delta Balik 1 (%)</th>
                  <th class="py-3 px-3.5 text-blue-400">Peak Balik 2 (29 Mar)</th>
                  <th class="py-3 px-3.5 text-blue-400">Delta Balik 2 (%)</th>
                </tr>
              </thead>
              <tbody id="tbody-surge" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 3: MODAL SHARE (PANGSA PASAR)                        -->
      <!-- ========================================================= -->
      <section id="view-modal-share" class="view-panel hidden space-y-6">
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Pergerakan Proporsi Pangsa Pasar Bulanan (100% Stacked Area)</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartModalShareArea"></canvas>
            </div>
          </div>

          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Komparasi Proporsi Moda: Baseline Normal vs Puncak Lebaran</h3>
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

        <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
          <h3 class="text-sm font-bold text-white tracking-tight">Tabel Data Pangsa Pasar Bulanan (%) per Moda Transportasi</h3>
          <div class="overflow-x-auto rounded-xl border border-slate-800/80">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th class="py-3 px-3.5">Bulan</th>
                  <th class="py-3 px-3.5 text-sky-400">UDARA (%)</th>
                  <th class="py-3 px-3.5 text-amber-400">KERETA API (%)</th>
                  <th class="py-3 px-3.5 text-emerald-400">BUS AKAP (%)</th>
                  <th class="py-3 px-3.5 text-purple-400">ASDP (%)</th>
                  <th class="py-3 px-3.5 text-cyan-400">LAUT (%)</th>
                  <th class="py-3 px-3.5 text-right text-white">TOTAL VOLUME (PNP)</th>
                </tr>
              </thead>
              <tbody id="tbody-share" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 4: BEBAN & OKUPANSI ARMADA (LOAD FACTOR)             -->
      <!-- ========================================================= -->
      <section id="view-load-factor" class="view-panel hidden space-y-6">
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Rasio Penumpang per Armada (Normal vs Puncak Lebaran)</h3>
            <div class="relative w-full h-[320px]">
              <canvas id="chartLoadFactor"></canvas>
            </div>
          </div>

          <div class="glass-card rounded-2xl p-5 shadow-glass space-y-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Data Utilisasi Keterisian Armada (Load Factor Proxy)</h3>
            <div class="overflow-x-auto rounded-xl border border-slate-800/80">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-3 px-3.5">Moda</th>
                    <th class="py-3 px-3.5">Rasio Normal (Feb)</th>
                    <th class="py-3 px-3.5 text-blue-400">Rasio Puncak (Mar)</th>
                    <th class="py-3 px-3.5 text-emerald-400">Pertumbuhan (%)</th>
                    <th class="py-3 px-3.5">Satuan Metrik</th>
                  </tr>
                </thead>
                <tbody id="tbody-load-factor" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
              </table>
            </div>
          </div>
        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 5: TOP 30 SIMPUL NASIONAL                            -->
      <!-- ========================================================= -->
      <section id="view-top-hubs" class="view-panel hidden space-y-4">
        
        <!-- Filter Toolbar -->
        <div class="glass-card rounded-2xl p-4 shadow-glass flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Moda:</span>
            <div class="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800" id="hub-moda-bar">
              <button onclick="setHubModaFilter('ALL', this)" class="btn-hub-moda active px-3 py-1 text-xs font-semibold rounded-lg bg-blue-600 text-white">Semua</button>
              <button onclick="setHubModaFilter('UDARA', this)" class="btn-hub-moda px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Bandara</button>
              <button onclick="setHubModaFilter('KA', this)" class="btn-hub-moda px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Stasiun</button>
              <button onclick="setHubModaFilter('BUS', this)" class="btn-hub-moda px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Terminal</button>
              <button onclick="setHubModaFilter('ASDP', this)" class="btn-hub-moda px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Penyeberangan</button>
              <button onclick="setHubModaFilter('LAUT', this)" class="btn-hub-moda px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Pelabuhan Laut</button>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Search Bar -->
            <div class="relative">
              <input type="text" id="hub-search" placeholder="Cari nama simpul, kota, provinsi..." onkeyup="searchHub(this.value)" class="w-64 bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-xl px-3.5 py-1.5 outline-none focus:border-blue-500 transition-all">
            </div>

            <!-- Period Switch -->
            <div class="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800">
              <button id="btn-period-peak" onclick="setHubPeriodFilter('peak')" class="px-3 py-1 text-xs font-semibold rounded-lg bg-blue-600 text-white">Puncak Lebaran</button>
              <button id="btn-period-ytd" onclick="setHubPeriodFilter('ytd')" class="px-3 py-1 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Sepanjang 2026</button>
            </div>
          </div>
        </div>

        <!-- Table -->
        <div class="glass-card rounded-2xl overflow-hidden shadow-glass">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th class="py-3 px-3.5 w-16">Rank</th>
                  <th class="py-3 px-3.5">Nama Simpul / Prasarana</th>
                  <th class="py-3 px-3.5">Moda</th>
                  <th class="py-3 px-3.5">Provinsi</th>
                  <th class="py-3 px-3.5">Total Penumpang</th>
                  <th class="py-3 px-3.5">Total Armada</th>
                  <th class="py-3 px-3.5 w-60">Skala Volume Relatif</th>
                </tr>
              </thead>
              <tbody id="tbody-hubs" class="divide-y divide-slate-800/50 text-slate-200"></tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ========================================================= -->
      <!-- VIEW 6: MATRIKS KOMPARASI 13 INDIKATOR MULTIMODA          -->
      <!-- ========================================================= -->
      <section id="view-matrix" class="view-panel hidden space-y-4">
        
        <div class="glass-card rounded-2xl p-5 shadow-glass space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-white tracking-tight">Matriks Data Rekapitulasi Komparatif 5 Moda Transportasi Nasional 2026</h3>
              <p class="text-xs text-slate-400">Ringkasan kuantitatif 13 indikator utama pergerakan multimoda 2026</p>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono">13 Indikator</span>
          </div>

          <div class="overflow-x-auto rounded-xl border border-slate-800/80">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-950/70 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th class="py-3 px-3.5">Indikator Kuantitatif</th>
                  <th class="py-3 px-3.5 text-sky-400">UDARA</th>
                  <th class="py-3 px-3.5 text-amber-400">KERETA API</th>
                  <th class="py-3 px-3.5 text-emerald-400">BUS AKAP</th>
                  <th class="py-3 px-3.5 text-purple-400">ASDP</th>
                  <th class="py-3 px-3.5 text-cyan-400">LAUT</th>
                  <th class="py-3 px-3.5 text-right text-white">TOTAL NASIONAL</th>
                </tr>
              </thead>
              <tbody id="tbody-matrix" class="divide-y divide-slate-800/50 num-mono text-slate-200"></tbody>
            </table>
          </div>
        </div>

      </section>

    </main>
  </div>

<!-- TW-Elements JS -->
<script src="https://cdn.jsdelivr.net/npm/tw-elements/js/tw-elements.umd.min.js"></script>

<!-- JAVASCRIPT APPLICATION LOGIC -->
<script>
const DATA = {json_data_str};

const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// State
let isSidebarExpanded = true;
let currentMetric = 'pnp'; // 'pnp' or 'arm'
let currentTimelineRange = 'all';
let currentHubModa = 'ALL';
let currentHubPeriod = 'peak'; // 'peak' or 'ytd'
let currentSearchTerm = '';

// Chart Instances
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
  ASDP: '#a855f7',
  LAUT: '#06b6d4',
  TOTAL: '#ffffff'
}};

// -------------------------------------------------------------
// DUAL-STATE SIDEBAR CONTROLLER (EXPANDED <-> COLLAPSED RAIL)
// -------------------------------------------------------------
function toggleSidebar() {{
  const sb = document.getElementById('sidebar-rail');
  const main = document.getElementById('main-area');
  const icon = document.getElementById('icon-collapse-left');
  const labels = document.querySelectorAll('.sidebar-label');
  const extras = document.querySelectorAll('.sidebar-extra');
  const tooltips = document.querySelectorAll('.rail-tooltip');

  isSidebarExpanded = !isSidebarExpanded;

  if (isSidebarExpanded) {{
    sb.classList.remove('w-[72px]');
    sb.classList.add('w-64');
    main.classList.remove('pl-[72px]');
    main.classList.add('pl-64');
    icon.classList.remove('rotate-180');
    labels.forEach(l => l.classList.remove('hidden'));
    extras.forEach(e => e.classList.remove('hidden'));
    tooltips.forEach(t => t.classList.add('hidden'));
  }} else {{
    sb.classList.remove('w-64');
    sb.classList.add('w-[72px]');
    main.classList.remove('pl-64');
    main.classList.add('pl-[72px]');
    icon.classList.add('rotate-180');
    labels.forEach(l => l.classList.add('hidden'));
    extras.forEach(e => e.classList.add('hidden'));
    tooltips.forEach(t => t.classList.remove('hidden'));
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

function toggleDarkMode() {{
  document.documentElement.classList.toggle('dark');
}}

// -------------------------------------------------------------
// NAVIGATION VIEW SWITCHER
// -------------------------------------------------------------
function selectView(viewId, viewTitle, btn) {{
  document.querySelectorAll('.nav-btn').forEach(el => {{
    el.classList.remove('active', 'text-white', 'bg-blue-600/20', 'border-blue-500/30');
    el.classList.add('text-slate-400', 'border-transparent');
  }});
  document.querySelectorAll('.view-panel').forEach(p => p.classList.add('hidden'));

  btn.classList.add('active', 'text-white', 'bg-blue-600/20', 'border-blue-500/30');
  btn.classList.remove('text-slate-400', 'border-transparent');

  const panel = document.getElementById(viewId);
  if (panel) panel.classList.remove('hidden');

  document.getElementById('header-breadcrumb').innerText = viewTitle;

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
// TAB 1: TIMELINE CONTROLLER
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
    {{ label: 'Total Multimoda', data: data.map(d => d[p + 'TOTAL']), borderColor: '#ffffff', borderWidth: 2.2, pointRadius: 0, tension: 0.25 }},
    {{ label: 'Pesawat (Udara)', data: data.map(d => d[p + 'UDARA']), borderColor: PALETTE.UDARA, borderWidth: 1.6, pointRadius: 0, tension: 0.25 }},
    {{ label: 'Kereta Api (KA)', data: data.map(d => d[p + 'KA']), borderColor: PALETTE.KA, borderWidth: 1.6, pointRadius: 0, tension: 0.25 }},
    {{ label: 'Bus AKAP', data: data.map(d => d[p + 'BUS']), borderColor: PALETTE.BUS, borderWidth: 1.6, pointRadius: 0, tension: 0.25 }},
    {{ label: 'Penyeberangan (ASDP)', data: data.map(d => d[p + 'ASDP']), borderColor: PALETTE.ASDP, borderWidth: 1.6, pointRadius: 0, tension: 0.25 }},
    {{ label: 'Kapal Laut', data: data.map(d => d[p + 'LAUT']), borderColor: PALETTE.LAUT, borderWidth: 1.6, pointRadius: 0, tension: 0.25 }},
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
          backgroundColor: 'rgba(8,11,17,0.95)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(56,189,248,0.3)',
          borderWidth: 1,
          padding: 10,
          callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{currentMetric === 'pnp' ? 'pnp' : 'armada'}}` }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: 'rgba(255,255,255,0.04)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 14, font: {{ family: 'JetBrains Mono', size: 10 }} }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#64748b', font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v/1e3).toFixed(0) + 'k') }} }}
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
  
  // Sidebar
  document.getElementById('sb-metric-pnp').classList.toggle('bg-blue-600', m === 'pnp');
  document.getElementById('sb-metric-pnp').classList.toggle('text-white', m === 'pnp');
  document.getElementById('sb-metric-pnp').classList.toggle('text-slate-400', m !== 'pnp');
  document.getElementById('sb-metric-arm').classList.toggle('bg-blue-600', m === 'arm');
  document.getElementById('sb-metric-arm').classList.toggle('text-white', m === 'arm');
  document.getElementById('sb-metric-arm').classList.toggle('text-slate-400', m !== 'arm');

  // Topbar
  document.getElementById('top-metric-pnp').classList.toggle('bg-blue-600', m === 'pnp');
  document.getElementById('top-metric-pnp').classList.toggle('text-white', m === 'pnp');
  document.getElementById('top-metric-pnp').classList.toggle('text-slate-400', m !== 'pnp');
  document.getElementById('top-metric-arm').classList.toggle('bg-blue-600', m === 'arm');
  document.getElementById('top-metric-arm').classList.toggle('text-white', m === 'arm');
  document.getElementById('top-metric-arm').classList.toggle('text-slate-400', m !== 'arm');

  document.getElementById('timeline-chart-title').innerText = m === 'pnp' ? 'Pergerakan Harian Penumpang Multimoda 2026' : 'Pergerakan Harian Armada Multimoda 2026';
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
  link.setAttribute('download', `siasati_multimoda_${{currentTimelineRange}}_${{currentMetric}}.csv`);
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
      datasets: [{{ label: 'Rata-rata Penumpang Harian', data: dow.map(d => d.TOTAL), backgroundColor: 'rgba(56, 189, 248, 0.4)', borderColor: '#38bdf8', borderWidth: 1.5, borderRadius: 6 }}]
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
// TAB 2: LEBARAN CONTROLLER
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
    <div class="px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-sky-400">UDARA</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.UDARA)}}</div>
    </div>
    <div class="px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-amber-400">KERETA API</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.KA)}}</div>
    </div>
    <div class="px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-emerald-400">BUS</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.BUS)}}</div>
    </div>
    <div class="px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
      <div class="text-[10px] font-bold text-purple-400">ASDP</div>
      <div class="num-mono text-xs font-bold text-white">${{numFmt(day.ASDP)}}</div>
    </div>
    <div class="px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
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
    btn.className = `shrink-0 text-left p-2.5 rounded-xl border transition-all ${{isPeak ? 'bg-rose-950/30 border-rose-500/50 text-rose-300' : 'bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700'}}`;
    btn.innerHTML = `
      <div class="text-[9px] font-bold uppercase tracking-wider opacity-75">${{d.tag.split(' ')[0]}}</div>
      <div class="text-sm font-black num-mono">${{(d.TOTAL/1e6).toFixed(2)}}M</div>
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
        {{ label: 'Total Multimoda', data: ld.map(d => d.TOTAL), borderColor: '#ffffff', borderWidth: 2.2, pointRadius: 2, tension: 0.2 }},
        {{ label: 'Pesawat', data: ld.map(d => d.UDARA), borderColor: PALETTE.UDARA, borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Kereta Api', data: ld.map(d => d.KA), borderColor: PALETTE.KA, borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Bus', data: ld.map(d => d.BUS), borderColor: PALETTE.BUS, borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
        {{ label: 'ASDP', data: ld.map(d => d.ASDP), borderColor: PALETTE.ASDP, borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Laut', data: ld.map(d => d.LAUT), borderColor: PALETTE.LAUT, borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
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
        {{ label: 'Lonjakan Mudik 18 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_mudik_pct), backgroundColor: 'rgba(244, 63, 94, 0.75)', borderRadius: 5 }},
        {{ label: 'Lonjakan Balik 24 Mar (%)', data: modas.map(m => DATA.surge_summary[m].surge_balik1_pct), backgroundColor: 'rgba(6, 182, 212, 0.75)', borderRadius: 5 }},
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
// TAB 3: MODAL SHARE CONTROLLER
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
        {{ label: 'ASDP', data: ms.map(m => m.share_ASDP), borderColor: PALETTE.ASDP, backgroundColor: 'rgba(168, 85, 247, 0.35)', fill: true, tension: 0.2 }},
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
// TAB 4: LOAD FACTOR CONTROLLER
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
        {{ label: 'Baseline Normal (Feb)', data: modas.map(m => lf[m].normal_ratio), backgroundColor: 'rgba(148,163,184,0.3)', borderRadius: 5 }},
        {{ label: 'Puncak Lebaran (Mar)', data: modas.map(m => lf[m].peak_ratio), backgroundColor: 'rgba(56, 189, 248, 0.85)', borderRadius: 5 }},
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
      <td class="py-2.5 px-3.5 font-bold text-sky-400">${{row.peak_ratio}}</td>
      <td class="py-2.5 px-3.5 text-emerald-400 font-bold">+${{row.growth_pct}}%</td>
      <td class="py-2.5 px-3.5 text-slate-400 font-sans">${{row.unit}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 5: TOP HUBS CONTROLLER
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
    tbody.innerHTML = '<tr><td colspan="7" class="py-8 text-center text-slate-500 font-sans">Tidak ada data simpul yang sesuai filter pencarian.</td></tr>';
    return;
  }}

  const maxVal = list[0].pnp || 1;
  list.forEach((item, idx) => {{
    const pct = ((item.pnp / maxVal) * 100).toFixed(0);
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-800/40 transition-colors';
    
    let rankBadge = `<span class="text-slate-500">#${{idx + 1}}</span>`;
    if (idx === 0) rankBadge = `<span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">#1</span>`;
    else if (idx === 1) rankBadge = `<span class="px-2 py-0.5 rounded-full bg-slate-400/20 text-slate-200 border border-slate-400/30 font-bold">#2</span>`;
    else if (idx === 2) rankBadge = `<span class="px-2 py-0.5 rounded-full bg-amber-700/20 text-amber-400 border border-amber-700/30 font-bold">#3</span>`;

    tr.innerHTML = `
      <td class="py-2.5 px-3.5 font-bold num-mono">${{rankBadge}}</td>
      <td class="py-2.5 px-3.5 font-sans font-semibold text-white">${{item.nama_prasarana}}</td>
      <td class="py-2.5 px-3.5"><span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-950 text-slate-300 border border-slate-800 font-sans">${{item.moda}}</span></td>
      <td class="py-2.5 px-3.5 text-slate-400 font-sans">${{item.provinsi || '-'}}</td>
      <td class="py-2.5 px-3.5 font-bold text-white num-mono">${{numFmt(item.pnp)}}</td>
      <td class="py-2.5 px-3.5 text-slate-400 num-mono">${{numFmt(item.arm)}}</td>
      <td class="py-2.5 px-3.5">
        <div class="flex items-center gap-2">
          <div class="flex-1 h-1.5 rounded-full bg-slate-950 overflow-hidden">
            <div class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" style="width: ${{pct}}%;"></div>
          </div>
          <span class="text-[10px] text-slate-500 num-mono w-7 text-right">${{pct}}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 6: MATRIKS ANGKA KRITIS MULTIMODA
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
    tr.className = 'hover:bg-slate-800/40 ' + (idx % 2 === 0 ? 'bg-slate-950/30' : '');
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
// INITIALIZATION
// -------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {{
  renderTimelineChart();
  renderMonthlyView();
  renderDOWView();
}});
</script>
</body>
</html>
"""
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Total Redesigned Dashboard successfully built: {OUTPUT_HTML}")
    print(f"File size: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")

if __name__ == '__main__':
    build_dashboard()
