import json
import os

bundle_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
out_html = r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html"

with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

json_data_str = json.dumps(bundle, ensure_ascii=False)

icons = {
    'plane': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>',
    'train': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="3" rx="2"/><path d="M4 11h16"/><path d="M12 3v8"/><path d="m8 19-2 3"/><path d="m18 22-2-3"/><circle cx="8" cy="15" r="1"/><circle cx="16" cy="15" r="1"/></svg>',
    'bus': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6v6"/><path d="M16 6v6"/><path d="M4 6h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6z"/><path d="M4 11h16"/><path d="m6 18-1.5 2.5"/><path d="m18 18 1.5 2.5"/><circle cx="7.5" cy="14.5" r="1"/><circle cx="16.5" cy="14.5" r="1"/></svg>',
    'asdp': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20a4 4 0 0 0 8 0 4 4 0 0 0 8 0 4 4 0 0 0 4 0"/><path d="M4 17 2 9h20l-2 8"/><path d="M6 9V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v5"/><path d="M10 3v6"/><path d="M14 3v6"/></svg>',
    'ship': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><path d="M12 10v4"/><path d="M12 2v3"/></svg>',
    'trending_up': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    'calendar': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    'activity': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'users': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'truck': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>',
    'shield': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    'search': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    'sun': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
    'moon': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    'kemenhub': '<svg class="icon logo-svg" xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/></svg>',
    'layers': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    'pie': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    'download': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    'sidebar_toggle': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9-3 3 3 3"/></svg>',
    'filter': '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>'
}

html_code = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SIASATI Analytics • Platform Mobilitas Multimoda Nasional 2026</title>

<!-- Fonts: Plus Jakarta Sans + JetBrains Mono -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>
/* -------------------------------------------------------------
   DESIGN SYSTEM TOKENS (ui-ux-pro-max-skill)
   ------------------------------------------------------------- */
:root {{
  --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Theme: Dark Slate / Navy Enterprise (Default) */
  --bg-app: #080d1a;
  --bg-gradient: radial-gradient(1400px 700px at 75% -10%, #111e38 0%, #080d1a 75%);
  --sidebar-bg: #0b1329;
  --surface-card: #0f172a;
  --surface-raised: #1e293b;
  --surface-input: #080e1c;
  --border: #1e293b;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: #3b82f6;

  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;

  --primary: #2563eb;
  --primary-light: #3b82f6;
  --primary-glow: rgba(59, 130, 246, 0.16);
  --accent-cyan: #06b6d4;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;
  --accent-rose: #f43f5e;
  --accent-purple: #8b5cf6;

  --color-udara: #38bdf8;
  --color-ka: #f59e0b;
  --color-bus: #10b981;
  --color-asdp: #8b5cf6;
  --color-laut: #06b6d4;

  --sidebar-w: 290px;
  --sidebar-w-collapsed: 0px;
  --header-h: 60px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
}}

html.light {{
  --bg-app: #f8fafc;
  --bg-gradient: radial-gradient(1400px 700px at 75% -10%, #e2e8f0 0%, #f8fafc 75%);
  --sidebar-bg: #ffffff;
  --surface-card: #ffffff;
  --surface-raised: #f1f5f9;
  --surface-input: #f8fafc;
  --border: #e2e8f0;
  --border-subtle: rgba(0, 0, 0, 0.06);
  --border-focus: #2563eb;

  --text-main: #0f172a;
  --text-muted: #475569;
  --text-dim: #94a3b8;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: var(--font-sans);
  background: var(--bg-gradient);
  background-color: var(--bg-app);
  color: var(--text-main);
  min-height: 100vh;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  display: flex;
  overflow-x: hidden;
  transition: background-color 0.2s ease, color 0.2s ease;
}}

.num-mono {{
  font-family: var(--font-mono);
  font-feature-settings: "tnum" 1;
  letter-spacing: -0.02em;
}}

.icon {{
  display: inline-block;
  vertical-align: middle;
  stroke-width: 2;
  flex-shrink: 0;
}}

/* -------------------------------------------------------------
   COLLAPSIBLE SIDEBAR LAYOUT
   ------------------------------------------------------------- */
aside.sidebar {{
  width: var(--sidebar-w);
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25);
}}

/* Collapsed State */
body.sidebar-collapsed aside.sidebar {{
  transform: translateX(-100%);
}}

.sidebar-header {{
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}}

.sidebar-brand {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.sidebar-logo {{
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
}}
.sidebar-brand-text h2 {{
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--text-main);
}}
.sidebar-brand-text p {{
  font-size: 11px;
  color: var(--text-dim);
}}

.sidebar-btn-close {{
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}}
.sidebar-btn-close:hover {{
  color: var(--text-main);
  background: var(--surface-raised);
}}

.sidebar-content {{
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  flex: 1;
}}

.sidebar-group-label {{
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  margin-bottom: 8px;
  padding-left: 6px;
}}

.side-nav-list {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 3px;
}}

.side-nav-item {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  user-select: none;
}}
.side-nav-item:hover {{
  color: var(--text-main);
  background: var(--surface-raised);
}}
.side-nav-item.active {{
  color: var(--primary-light);
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(37, 99, 235, 0.25);
  font-weight: 700;
}}

.side-control-card {{
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 12px;
}}

.side-btn-pill {{
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  margin-bottom: 4px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
}}
.side-btn-pill:hover {{
  background: var(--surface-raised);
  color: var(--text-main);
}}
.side-btn-pill.active {{
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}}

/* -------------------------------------------------------------
   MAIN CONTENT WRAPPER
   ------------------------------------------------------------- */
main.main-content {{
  flex: 1;
  margin-left: var(--sidebar-w);
  padding: 20px 28px;
  transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
}}

body.sidebar-collapsed main.main-content {{
  margin-left: 0;
}}

/* Top Sticky Bar */
.top-action-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 22px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}}

.bar-left {{
  display: flex;
  align-items: center;
  gap: 12px;
}}

.btn-sidebar-toggle {{
  background: var(--surface-raised);
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  font-weight: 600;
  transition: all 0.18s;
}}
.btn-sidebar-toggle:hover {{
  border-color: var(--border-focus);
  color: var(--primary-light);
}}

.breadcrumb {{
  font-size: 12.5px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}}
.breadcrumb strong {{
  color: var(--text-main);
}}

.bar-right {{
  display: flex;
  align-items: center;
  gap: 8px;
}}

/* KPI Hero */
.kpi-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}}
.kpi-box {{
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, border-color 0.2s ease;
}}
.kpi-box:hover {{
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
}}
.kpi-top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}}
.kpi-title {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
}}
.kpi-value {{
  font-size: 25px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--text-main);
  margin-bottom: 4px;
}}
.kpi-delta {{
  font-size: 11.5px;
  color: var(--text-muted);
}}
.kpi-delta strong {{
  color: var(--accent-emerald);
}}

/* Cards & Layout */
.grid-2 {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  gap: 18px;
  margin-bottom: 20px;
}}
.grid-3 {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}}

.card-panel {{
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
}}
.panel-header {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}}
.panel-title h3 {{
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}}
.panel-title p {{
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}}

.chart-container {{
  position: relative;
  width: 100%;
  height: 330px;
}}
.chart-container.tall {{
  height: 420px;
}}

/* Tables */
.table-scroll {{
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}}
table.data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
  text-align: left;
}}
table.data-table th {{
  background: var(--surface-raised);
  color: var(--text-muted);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.05em;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}}
table.data-table td {{
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-main);
  vertical-align: middle;
}}
table.data-table tr:hover td {{
  background: rgba(59, 130, 246, 0.05);
}}

.moda-pill {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}}
.moda-pill.udara {{ background: rgba(56, 189, 248, 0.15); color: var(--color-udara); }}
.moda-pill.ka {{ background: rgba(245, 158, 11, 0.15); color: var(--color-ka); }}
.moda-pill.bus {{ background: rgba(16, 185, 129, 0.15); color: var(--color-bus); }}
.moda-pill.asdp {{ background: rgba(139, 92, 246, 0.15); color: var(--color-asdp); }}
.moda-pill.laut {{ background: rgba(6, 182, 212, 0.15); color: var(--color-laut); }}

.progress-cell {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.progress-rail {{
  flex: 1;
  height: 6px;
  background: var(--surface-input);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}}
.progress-fill {{
  height: 100%;
  border-radius: 3px;
}}

/* Lebaran Day Strip */
.day-strip-scroll {{
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 14px;
}}
.day-badge-card {{
  min-width: 135px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.18s ease;
  user-select: none;
}}
.day-badge-card:hover {{
  border-color: var(--primary-light);
  transform: translateY(-2px);
}}
.day-badge-card.active {{
  border-color: var(--primary-light);
  background: rgba(37, 99, 235, 0.12);
  box-shadow: 0 0 14px rgba(37, 99, 235, 0.25);
}}
.day-badge-card.peak-mudik {{
  border-color: var(--accent-rose);
  background: rgba(244, 63, 94, 0.08);
}}
.day-badge-card.peak-balik {{
  border-color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.08);
}}
.day-phase {{
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-dim);
}}
.day-vol {{
  font-size: 16px;
  font-weight: 800;
  margin: 3px 0 1px;
}}
.day-sub {{
  font-size: 10.5px;
  color: var(--text-dim);
}}

.day-detail-banner {{
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}}

/* Policy Cards */
.policy-card {{
  background: var(--surface-card);
  border: 1px solid var(--border);
  border-left: 4px solid var(--primary-light);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 16px 18px;
  margin-bottom: 12px;
}}
.policy-card.critical {{ border-left-color: var(--accent-rose); }}
.policy-card.warning {{ border-left-color: var(--accent-amber); }}
.policy-card.strategic {{ border-left-color: var(--accent-purple); }}
.policy-card.operational {{ border-left-color: var(--accent-emerald); }}
.policy-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}}
.policy-title {{
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-main);
}}
.policy-badge {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
}}
.policy-badge.critical {{ background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }}
.policy-badge.warning {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }}
.policy-badge.strategic {{ background: rgba(139, 92, 246, 0.15); color: var(--accent-purple); }}
.policy-badge.operational {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }}
.policy-text {{
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
}}

.tab-pane {{ display: none; }}
.tab-pane.active {{ display: block; animation: tabFade 0.2s ease-in-out; }}
@keyframes tabFade {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* Segmented & Inputs */
.segmented-control {{
  display: inline-flex;
  background: var(--surface-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 2px;
  gap: 2px;
}}
.btn-seg {{
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.btn-seg:hover {{ color: var(--text-main); }}
.btn-seg.active {{
  background: var(--primary);
  color: #fff;
}}

.search-box {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--surface-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 5px 12px;
}}
.search-box input {{
  background: transparent;
  border: none;
  color: var(--text-main);
  font-family: var(--font-sans);
  font-size: 12px;
  outline: none;
  width: 220px;
}}

@media (max-width: 1024px) {{
  aside.sidebar {{
    transform: translateX(-100%);
  }}
  body.sidebar-open-mobile aside.sidebar {{
    transform: translateX(0);
  }}
  main.main-content {{
    margin-left: 0;
  }}
}}
</style>
</head>
<body>

  <!-- ============================================================= -->
  <!-- COLLAPSIBLE SIDEBAR CONSOLE (FITUR-FITUR DI SAMPING)          -->
  <!-- ============================================================= -->
  <aside class="sidebar" id="sidebar-panel">
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <div class="sidebar-logo">
          {icons['kemenhub']}
        </div>
        <div class="sidebar-brand-text">
          <h2>SIASATI MOBILITY</h2>
          <p>PUSDATIN KEMENHUB RI</p>
        </div>
      </div>
      <button class="sidebar-btn-close" onclick="toggleSidebar()" title="Sembunyikan Sidebar">
        {icons['sidebar_toggle']}
      </button>
    </div>

    <div class="sidebar-content">
      <!-- 1. Menu Fitur Analisis -->
      <div>
        <div class="sidebar-group-label">Modul Analisis (Fitur)</div>
        <ul class="side-nav-list" role="tablist">
          <li class="side-nav-item active" onclick="switchNavTab('tab-timeline', 'Tren Mobilitas 271 Hari', this)">
            {icons['trending_up']} <span>Tren Mobilitas 271 Hari</span>
          </li>
          <li class="side-nav-item" onclick="switchNavTab('tab-lebaran', 'Anatomi Puncak Lebaran 2026', this)">
            {icons['activity']} <span>Puncak Lebaran 2026</span>
          </li>
          <li class="side-nav-item" onclick="switchNavTab('tab-modal-share', 'Dinamika Pangsa Pasar', this)">
            {icons['pie']} <span>Pangsa Pasar (Modal Share)</span>
          </li>
          <li class="side-nav-item" onclick="switchNavTab('tab-load-factor', 'Beban & Okupansi Armada', this)">
            {icons['layers']} <span>Beban & Okupansi Armada</span>
          </li>
          <li class="side-nav-item" onclick="switchNavTab('tab-top-hubs', 'Top Simpul Transportasi', this)">
            {icons['search']} <span>Top Simpul Transportasi</span>
          </li>
          <li class="side-nav-item" onclick="switchNavTab('tab-policy', 'Rekomendasi Kebijakan', this)">
            {icons['shield']} <span>Rekomendasi Kebijakan</span>
          </li>
        </ul>
      </div>

      <!-- 2. Kontrol Filter Cepat di Sidebar -->
      <div>
        <div class="sidebar-group-label">{icons['filter']} Filter Periode Cepat</div>
        <div class="side-control-card">
          <button class="side-btn-pill active" onclick="setTimelineFilter('all', this)">
            <span>Sepanjang 2026</span>
            <span class="num-mono" style="font-size:10px; opacity:0.8;">271 Hari</span>
          </button>
          <button class="side-btn-pill" onclick="setTimelineFilter('lebaran', this)">
            <span>Puncak Lebaran 2026</span>
            <span class="num-mono" style="font-size:10px; opacity:0.8;">10 Mar - 5 Apr</span>
          </button>
          <button class="side-btn-pill" onclick="setTimelineFilter('libur_sekolah', this)">
            <span>Libur Sekolah</span>
            <span class="num-mono" style="font-size:10px; opacity:0.8;">15 Jun - 15 Jul</span>
          </button>
          <button class="side-btn-pill" onclick="setTimelineFilter('tahun_baru', this)">
            <span>Tahun Baru 2026</span>
            <span class="num-mono" style="font-size:10px; opacity:0.8;">1 - 15 Jan</span>
          </button>
        </div>
      </div>

      <!-- 3. Toggle Tampilan Metrik -->
      <div>
        <div class="sidebar-group-label">Metrik Operasional</div>
        <div class="side-control-card">
          <button class="side-btn-pill active" id="side-btn-pnp" onclick="setMetricMode('pnp')">
            <span>Volume Penumpang</span>
            <span>{icons['users']}</span>
          </button>
          <button class="side-btn-pill" id="side-btn-arm" onclick="setMetricMode('arm')">
            <span>Perjalanan Armada</span>
            <span>{icons['truck']}</span>
          </button>
        </div>
      </div>

      <!-- 4. Quick Actions -->
      <div>
        <div class="sidebar-group-label">Aksi & Ekspor Data</div>
        <button class="side-btn-pill" onclick="exportTimelineCSV()" style="background:var(--surface-raised); border:1px solid var(--border);">
          <span>Unduh Dataset (CSV)</span>
          <span>{icons['download']}</span>
        </button>
      </div>

      <!-- 5. Metadata Status Feed -->
      <div style="margin-top:auto; padding:12px; background:var(--surface-card); border:1px solid var(--border); border-radius:var(--radius-md);">
        <div style="font-size:10.5px; font-weight:700; color:var(--accent-emerald); text-transform:uppercase; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
          <span style="width:6px; height:6px; border-radius:50%; background:var(--accent-emerald);"></span> DATA CLEANSED & VERIFIED
        </div>
        <div style="font-size:11px; color:var(--text-muted);">
          Total 283.116 baris data harian terverifikasi tanpa anomali.
        </div>
      </div>
    </div>
  </aside>

  <!-- ============================================================= -->
  <!-- MAIN WORKSPACE CONTENT                                        -->
  <!-- ============================================================= -->
  <main class="main-content">

    <!-- TOP ACTION / BREADCRUMB BAR -->
    <div class="top-action-bar">
      <div class="bar-left">
        <button class="btn-sidebar-toggle" onclick="toggleSidebar()" title="Buka/Tutup Sidebar Fitur">
          {icons['sidebar_toggle']}
          <span id="btn-toggle-label">Sembunyikan Menu</span>
        </button>

        <div class="breadcrumb">
          <span>SIASATI</span>
          <span>/</span>
          <span>Mobilitas Multimoda</span>
          <span>/</span>
          <strong id="active-breadcrumb-tab">Tren Mobilitas 271 Hari</strong>
        </div>
      </div>

      <div class="bar-right">
        <div class="status-chip verified" style="font-size:11.5px; padding:4px 10px;">
          <span>1 Jan – 28 Sep 2026</span>
        </div>
        <button class="btn-icon" id="btn-theme-toggle" onclick="toggleTheme()" title="Ganti Tema (Dark / Light)" style="width:34px; height:34px;">
          {icons['sun']}
        </button>
      </div>
    </div>

    <!-- KPI HERO BAR -->
    <section class="kpi-row">
      <div class="kpi-box">
        <div class="kpi-top">
          <span class="kpi-title">Total Penumpang YTD</span>
          <span style="color:var(--primary-light);">{icons['users']}</span>
        </div>
        <div class="kpi-value num-mono" id="val-total-pnp">-</div>
        <div class="kpi-delta">Agregasi 5 moda transportasi nasional (Clean)</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-top">
          <span class="kpi-title">Puncak Tertinggi All-Time</span>
          <span style="color:var(--accent-rose);">{icons['activity']}</span>
        </div>
        <div class="kpi-value num-mono" style="color:var(--accent-rose);">2.415.296</div>
        <div class="kpi-delta"><strong>Selasa, 24 Maret 2026</strong> (H+3 Balik)</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-top">
          <span class="kpi-title">Lonjakan Tertinggi (Moda)</span>
          <span style="color:var(--accent-purple);">{icons['asdp']}</span>
        </div>
        <div class="kpi-value num-mono" style="color:var(--accent-purple);">+252,1%</div>
        <div class="kpi-delta">Moda <strong>ASDP Penyeberangan</strong> saat Mudik</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-top">
          <span class="kpi-title">Bulan Tersibuk Nasional</span>
          <span style="color:var(--accent-emerald);">{icons['trending_up']}</span>
        </div>
        <div class="kpi-value num-mono">50,51 Juta</div>
        <div class="kpi-delta"><strong>Maret 2026</strong> (Angkutan Lebaran)</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-top">
          <span class="kpi-title">Perjalanan Armada YTD</span>
          <span style="color:var(--accent-amber);">{icons['truck']}</span>
        </div>
        <div class="kpi-value num-mono" id="val-total-arm">-</div>
        <div class="kpi-delta">Penerbangan, KA, bus, kapal & Ro-Ro</div>
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 1: TIMELINE -->
    <!-- ============================================================= -->
    <div id="tab-timeline" class="tab-pane active">
      <div class="card-panel" style="margin-bottom: 20px;">
        <div class="panel-header">
          <div class="panel-title">
            <h3 id="timeline-chart-heading">Kurva Pergerakan Harian Multimoda Transportasi Nasional 2026</h3>
            <p>Tren harian 5 moda: Udara (Pesawat), Kereta Api, Bus AKAP, Penyeberangan ASDP, dan Laut</p>
          </div>
          <span class="status-chip" id="chip-timeline-days">271 Hari Pengamatan</span>
        </div>
        <div class="chart-container tall">
          <canvas id="chartTimeline"></canvas>
        </div>
      </div>

      <div class="grid-2">
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Agregat Pergerakan Bulanan (Januari s.d. September 2026)</h3>
              <p>Pola musiman: Puncak Lebaran (Maret) dan Puncak Libur Sekolah (Juni-Juli)</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartMonthly"></canvas>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Rata-rata Mobilitas Berdasarkan Hari dalam Seminggu</h3>
              <p>Identifikasi beban operasional hari kerja vs akhir pekan (Weekend Surge)</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartDOW"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 2: LEBARAN 2026 -->
    <!-- ============================================================= -->
    <div id="tab-lebaran" class="tab-pane">
      <div style="margin-bottom: 8px;">
        <span style="font-size:11px; font-weight:700; color:var(--text-dim); text-transform:uppercase;">
          INSPEKSI TANGGAL ANGKUTAN LEBARAN 2026 (H-8 s.d. H+15):
        </span>
      </div>
      <div class="day-strip-scroll" id="lebaran-strip"></div>

      <!-- Active Day Detail Card -->
      <div class="day-detail-banner" id="lebaran-day-banner">
        <div>
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span class="policy-badge critical" id="banner-tag">PUNCAK ARUS BALIK</span>
            <span style="font-size:11px; color:var(--text-dim);" id="banner-phase-desc">Rekor All-Time Nasional</span>
          </div>
          <h2 style="font-size:19px; font-weight:800; letter-spacing:-0.01em;" id="banner-date">Selasa, 24 Maret 2026</h2>
          <p style="font-size:12.5px; color:var(--text-muted); margin-top:2px;" id="banner-desc">Total pergerakan 2.415.296 penumpang melintasi seluruh moda transportasi.</p>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;" id="banner-pills"></div>
      </div>

      <div class="grid-2">
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Dinamika Dual-Wave Arus Mudik vs Arus Balik 2026</h3>
              <p>Terbelahnya arus balik: Gelombang 1 (Darat/KA) vs Gelombang 2 (Udara/Laut)</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartLebaranLine"></canvas>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Komparasi Lonjakan (Surge %) terhadap Baseline Normal</h3>
              <p>Persentase kenaikan penumpang saat Peak Mudik (18 Mar) dan Peak Balik (24 Mar) vs Normal Februari</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartSurgeBar"></canvas>
          </div>
        </div>
      </div>

      <div class="card-panel">
        <div class="panel-header">
          <div class="panel-title">
            <h3>Tabel Evaluasi Kinerja Lonjakan Periode Angkutan Lebaran 2026</h3>
            <p>Angka baseline harian normal (Februari) dibandingkan titik puncak kritis</p>
          </div>
        </div>
        <div class="table-scroll">
          <table class="data-table" id="table-surge">
            <thead>
              <tr>
                <th>Moda Transportasi</th>
                <th>Baseline Normal (Feb)</th>
                <th>Puncak Mudik (18 Mar)</th>
                <th>Lonjakan Mudik (%)</th>
                <th>Puncak Balik 1 (24 Mar)</th>
                <th>Lonjakan Balik 1 (%)</th>
                <th>Puncak Balik 2 (29 Mar)</th>
                <th>Lonjakan Balik 2 (%)</th>
                <th>Catatan Operasional Lapangan</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 3: MODAL SHARE -->
    <!-- ============================================================= -->
    <div id="tab-modal-share" class="tab-pane">
      <div class="grid-2">
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Dinamika Pangsa Pasar Bulanan (100% Stacked Area)</h3>
              <p>Pergeseran pangsa pasar transportasi publik nasional dari Januari hingga September 2026</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartModalShareArea"></canvas>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Komparasi Proporsi Pangsa: Normal vs Puncak Lebaran</h3>
              <p>Pergeseran signifikan ke moda ASDP (+4,2%) dan Kereta Api saat Angkutan Lebaran</p>
            </div>
          </div>
          <div style="display:flex; gap:16px; justify-content:space-around; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px; text-align:center;">
              <div style="font-size:12px; font-weight:700; color:var(--text-muted); margin-bottom:8px;">Baseline Normal (Februari)</div>
              <div class="chart-container" style="height:240px;"><canvas id="donutNormal"></canvas></div>
            </div>
            <div style="flex:1; min-width:200px; text-align:center;">
              <div style="font-size:12px; font-weight:700; color:var(--primary-light); margin-bottom:8px;">Puncak Lebaran (Maret)</div>
              <div class="chart-container" style="height:240px;"><canvas id="donutPeak"></canvas></div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid-3">
        <div class="policy-card operational">
          <div class="policy-head">
            <span class="policy-title">Lonjakan Pangsa ASDP (+4,2%)</span>
            <span class="policy-badge operational">Modal Shift</span>
          </div>
          <p class="policy-text">Pangsa pasar penyeberangan naik dari 10,6% di hari biasa menjadi 14,8% saat Lebaran karena tingginya volume pemudik yang membawa kendaraan pribadi via Merak-Bakauheni dan Ketapang-Gilimanuk.</p>
        </div>

        <div class="policy-card warning">
          <div class="policy-head">
            <span class="policy-title">Daya Tarik Kereta Api Pasca-Lebaran</span>
            <span class="policy-badge warning">Konsistensi</span>
          </div>
          <p class="policy-text">Pangsa Kereta Api meningkat hingga 24,6% di bulan Mei dan tetap stabil di atas 22% saat arus balik karena kepastian jadwal waktu tempuh yang bebas hambatan kemacetan tol.</p>
        </div>

        <div class="policy-card strategic">
          <div class="policy-head">
            <span class="policy-title">Puncak Wisata Maritim di Liburan Sekolah</span>
            <span class="policy-badge strategic">Musim Panas</span>
          </div>
          <p class="policy-text">Moda transportasi laut mencapai pangsa pasar tertinggi tahunan pada bulan Juli (14,8%) didorong tingginya pariwisata bahari domestik (Bali, Nusa Penida, Labuan Bajo, Kepri).</p>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 4: LOAD FACTOR -->
    <!-- ============================================================= -->
    <div id="tab-load-factor" class="tab-pane">
      <div class="grid-2">
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Rasio Intensitas Penumpang per Armada (Load Factor Proxy)</h3>
              <p>Beban keterisian rata-rata armada: Hari Biasa vs Masa Puncak Lebaran</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartLoadFactor"></canvas>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Evaluasi Kepadatan & Batas Kapasitas Operasional</h3>
              <p>Tingkat utilisasi armada dan potensi bottleneck operasional per moda</p>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div class="policy-card critical">
              <div class="policy-head">
                <span class="policy-title">ASDP: Kenaikan Beban +121,9% (245,2 Pnp/Trip)</span>
                <span class="policy-badge critical">Kritis</span>
              </div>
              <p class="policy-text">Setiap keberangkatan kapal penyeberangan mengangkut lebih dari 2 kali lipat rata-rata penumpang hari biasa. Waktu sandar (port time) dan kapasitas dermaga merupakan titik kritis utama antrean pelabuhan.</p>
            </div>

            <div class="policy-card strategic">
              <div class="policy-head">
                <span class="policy-title">UDARA: Seat Load Factor Mendekati 90% (120,7 Pnp/Flight)</span>
                <span class="policy-badge strategic">Optimal</span>
              </div>
              <p class="policy-text">Penerbangan didominasi armada narrow-body (A320/B737 berkapasitas 150-180 kursi). Kenaikan rasio menandakan hampir seluruh kursi penerbangan reguler dan extra flight terisi penuh.</p>
            </div>

            <div class="policy-card operational">
              <div class="policy-head">
                <span class="policy-title">BUS: Kenaikan Okupansi +48,3% (17,2 Pnp/Bus)</span>
                <span class="policy-badge operational">Terkendali</span>
              </div>
              <p class="policy-text">Terjadi pemanfaatan maksimal bus AKAP Antar Kota Antar Provinsi serta program Mudik Gratis Kemenhub dan BUMN yang menahan lonjakan kendaraan roda dua di jalan nasional.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 5: TOP HUBS -->
    <!-- ============================================================= -->
    <div id="tab-top-hubs" class="tab-pane">
      <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <span style="font-size:11px; font-weight:700; color:var(--text-dim); text-transform:uppercase;">Filter Moda:</span>
          <div class="segmented-control">
            <button class="btn-seg active" onclick="setHubModa('ALL', this)">Semua</button>
            <button class="btn-seg" onclick="setHubModa('UDARA', this)">Bandara</button>
            <button class="btn-seg" onclick="setHubModa('KA', this)">Stasiun KA</button>
            <button class="btn-seg" onclick="setHubModa('BUS', this)">Terminal Bus</button>
            <button class="btn-seg" onclick="setHubModa('ASDP', this)">Penyeberangan</button>
            <button class="btn-seg" onclick="setHubModa('LAUT', this)">Pelabuhan Laut</button>
          </div>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">
          <div class="search-box">
            {icons['search']}
            <input type="text" id="hub-search-input" placeholder="Cari nama simpul, kota, provinsi..." onkeyup="filterHubTable(this.value)">
          </div>

          <div class="segmented-control">
            <button class="btn-seg active" id="btn-period-peak" onclick="setHubPeriod('peak')">Puncak Lebaran</button>
            <button class="btn-seg" id="btn-period-ytd" onclick="setHubPeriod('ytd')">Sepanjang 2026</button>
          </div>
        </div>
      </div>

      <div class="card-panel">
        <div class="panel-header">
          <div class="panel-title">
            <h3 id="hub-table-heading">Peringkat Simpul Transportasi Terpadat Nasional (Puncak Lebaran 18-29 Maret 2026)</h3>
            <p id="hub-table-sub">Berdasarkan akumulasi total penumpang yang terlayani pada periode terpilih</p>
          </div>
        </div>
        <div class="table-scroll">
          <table class="data-table" id="table-hubs">
            <thead>
              <tr>
                <th style="width: 55px;">Rank</th>
                <th>Nama Prasarana / Simpul</th>
                <th>Moda</th>
                <th>Provinsi</th>
                <th>Total Penumpang Terlayani</th>
                <th>Total Armada</th>
                <th style="width: 260px;">Visualisasi Skala Volume</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 6: POLICY -->
    <!-- ============================================================= -->
    <div id="tab-policy" class="tab-pane">
      <div class="grid-2">
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>4 Rekomendasi Kebijakan Operasional Berbasis Data</h3>
              <p>Untuk Pengambil Keputusan Kementerian Perhubungan dan Stakeholder Terkait</p>
            </div>
          </div>

          <div class="policy-card critical">
            <div class="policy-head">
              <span class="policy-title">1. Early Warning System Berbasis Kuota Tiket Online Ferizy ASDP</span>
              <span class="policy-badge critical">Lead Time 48 Jam</span>
            </div>
            <p class="policy-text">Data empiris menunjukkan ASDP mencapai puncak lonjakan pada <strong>H-2 (18 Maret)</strong>, mendahului lonjakan moda Kereta Api dan Udara pada H+3. Pemantauan real-time sisa kuota tiket Ferizy harus menjadi <em>leading indicator</em> peringatan dini bagi Korlantas Polri dan BPJT untuk mengaktifkan delaying system dan rekayasa contraflow di Tol Trans-Jawa.</p>
          </div>

          <div class="policy-card strategic">
            <div class="policy-head">
              <span class="policy-title">2. Manajemen Operasional Arus Balik Dua Gelombang (Dual-Wave Return)</span>
              <span class="policy-badge strategic">Mitigasi Kemacetan</span>
            </div>
            <p class="policy-text">Arus balik Lebaran terbukti tidak terkonsentrasi pada satu hari, melainkan terbelah menjadi <strong>Gelombang 1 (H+3 s.d. H+4, 24-25 Maret)</strong> untuk pekerja sektor formal/darat, dan <strong>Gelombang 2 (H+7 s.d. H+8, 28-29 Maret)</strong> untuk moda Udara dan Laut. Alokasi petugas posko dan diskon tarif tol/tiket harus dibagi merata pada kedua gelombang ini.</p>
          </div>

          <div class="policy-card warning">
            <div class="policy-head">
              <span class="policy-title">3. Penguatan Manajemen Simpul Sekunder di Jawa Tengah & Jawa Timur</span>
              <span class="policy-badge warning">Distribusi Armada</span>
            </div>
            <p class="policy-text">Stasiun Yogyakarta (307k) dan Purwokerto (200k) serta Terminal Bus Kertonegoro Ngawi (445k) dan Purabaya Surabaya (446k) mengalami kepadatan yang luar biasa saat arus balik. Perluasan ruang tunggu sementara dan ketersediaan armada feeder lokal sangat esensial agar tidak terjadi penumpukan penumpang di luar terminal.</p>
          </div>

          <div class="policy-card operational">
            <div class="policy-head">
              <span class="policy-title">4. Standarisasi Validasi Data Real-Time (Data Governance PUSDATIN)</span>
              <span class="policy-badge operational">Integritas Data</span>
            </div>
            <p class="policy-text">Dengan teridentifikasinya 7.226 baris duplikat sama persis dan 34.229 baris dummy nol pada data SIASATI harian, Pusdatin Kemenhub disarankan memasang filter validasi otomatis pada API penerima data agar tidak terjadi inflasi statistik penumpang resmi kementerian.</p>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">
              <h3>Matriks Kesiapan Angkutan Lebaran Mendatang</h3>
              <p>Peta kerawanan dan tindakan mitigasi prioritas per moda transportasi</p>
            </div>
          </div>

          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Moda</th>
                  <th>Titik Kritis Utama</th>
                  <th>Hari Paling Padat</th>
                  <th>Solusi Mitigasi Rekomendasi</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><span class="moda-pill asdp">{icons['asdp']} ASDP</span></td>
                  <td>Antrean Dermaga Merak-Bakauheni</td>
                  <td><span class="num-mono" style="color:var(--accent-rose); font-weight:700;">H-2 Mudik (18 Mar)</span></td>
                  <td>Delaying System Rest Area & Geofencing Radius Beli Tiket</td>
                </tr>
                <tr>
                  <td><span class="moda-pill ka">{icons['train']} KERETA API</span></td>
                  <td>Kapasitas Kursi & Sirkulasi Stasiun</td>
                  <td><span class="num-mono" style="color:var(--accent-rose); font-weight:700;">H+3 Balik (24 Mar)</span></td>
                  <td>Penambahan Kereta Tambahan & Pengaturan Alur Masuk Penumpang</td>
                </tr>
                <tr>
                  <td><span class="moda-pill bus">{icons['bus']} BUS</span></td>
                  <td>Kemacetan Akses Menuju Terminal</td>
                  <td><span class="num-mono" style="color:var(--accent-rose); font-weight:700;">H+4 Balik (25 Mar)</span></td>
                  <td>Sterilisasi Jalur Keluar-Masuk Terminal Tipe A Jawa Timur & Jateng</td>
                </tr>
                <tr>
                  <td><span class="moda-pill udara">{icons['plane']} UDARA</span></td>
                  <td>Kepadatan Check-In & Bagasi Bandara</td>
                  <td><span class="num-mono" style="color:var(--accent-cyan); font-weight:700;">H+8 Balik (29 Mar)</span></td>
                  <td>Optimalisasi Self Check-In & Slot Time Malam/Dini Hari</td>
                </tr>
                <tr>
                  <td><span class="moda-pill laut">{icons['ship']} LAUT</span></td>
                  <td>Ketersediaan Kapal Rute Kepulauan</td>
                  <td><span class="num-mono" style="color:var(--accent-cyan); font-weight:700;">H+8 Balik (29 Mar)</span></td>
                  <td>Penugasan Kapal Cadangan Perintis & Pengawasan Manifest Penumpang</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </main>

</div>

<!-- SCRIPT LOGIC -->
<script>
const DATA = {json_data_str};

// Helper Formatter
const numFmt = (n) => (n !== null && n !== undefined) ? Number(n).toLocaleString('id-ID') : '-';

// State
let isSidebarOpen = true;
let currentTheme = 'dark';
let currentMetric = 'pnp'; // 'pnp' or 'arm'
let currentTimelineRange = 'all';
let currentHubModa = 'ALL';
let currentHubPeriod = 'peak'; // 'peak' or 'ytd'
let currentSearchTerm = '';

// Charts
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
// SIDEBAR COLLAPSE / EXPAND TOGGLE
// -------------------------------------------------------------
function toggleSidebar() {{
  isSidebarOpen = !isSidebarOpen;
  document.body.classList.toggle('sidebar-collapsed', !isSidebarOpen);
  
  const lbl = document.getElementById('btn-toggle-label');
  if (lbl) {{
    lbl.innerText = isSidebarOpen ? 'Sembunyikan Menu' : 'Buka Menu Fitur';
  }}

  // Resize charts smoothly after transition
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
  }}, 300);
}}

// -------------------------------------------------------------
// THEME SWITCHER
// -------------------------------------------------------------
function toggleTheme() {{
  const isLight = document.documentElement.classList.toggle('light');
  currentTheme = isLight ? 'light' : 'dark';
  document.getElementById('btn-theme-toggle').innerHTML = isLight ? `{icons['moon']}` : `{icons['sun']}`;

  if (chartTimelineInst) {{ chartTimelineInst.destroy(); chartTimelineInst = null; renderTimelineChart(); }}
  if (chartMonthlyInst) {{ chartMonthlyInst.destroy(); chartMonthlyInst = null; renderMonthlyChart(); }}
  if (chartDOWInst) {{ chartDOWInst.destroy(); chartDOWInst = null; renderDOWChart(); }}
  if (chartLebaranInst) {{ chartLebaranInst.destroy(); chartLebaranInst = null; renderLebaranCharts(); }}
  if (chartSurgeInst) {{ chartSurgeInst.destroy(); chartSurgeInst = null; renderLebaranCharts(); }}
  if (chartModalShareAreaInst) {{ chartModalShareAreaInst.destroy(); chartModalShareAreaInst = null; renderModalShareCharts(); }}
  if (chartLoadFactorInst) {{ chartLoadFactorInst.destroy(); chartLoadFactorInst = null; renderLoadFactorCharts(); }}
}}

// -------------------------------------------------------------
// NAVIGATION SWITCHER (FROM SIDEBAR)
// -------------------------------------------------------------
function switchNavTab(tabId, tabTitle, el) {{
  document.querySelectorAll('.side-nav-item').forEach(i => i.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

  if (el) el.classList.add('active');
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');

  const bcrumb = document.getElementById('active-breadcrumb-tab');
  if (bcrumb) bcrumb.innerText = tabTitle;

  setTimeout(() => {{
    if (tabId === 'tab-timeline' && chartTimelineInst) chartTimelineInst.resize();
    if (tabId === 'tab-lebaran') renderLebaranCharts();
    if (tabId === 'tab-modal-share') renderModalShareCharts();
    if (tabId === 'tab-load-factor') renderLoadFactorCharts();
    if (tabId === 'tab-top-hubs') renderHubTable();
  }}, 60);
}}

// -------------------------------------------------------------
// TAB 1: TIMELINE
// -------------------------------------------------------------
function getTimelineFilteredData() {{
  const all = DATA.daily_timeline;
  if (currentTimelineRange === 'lebaran') {{
    return all.filter(d => d.date >= '2026-03-10' && d.date <= '2026-04-05');
  }} else if (currentTimelineRange === 'libur_sekolah') {{
    return all.filter(d => d.date >= '2026-06-15' && d.date <= '2026-07-15');
  }} else if (currentTimelineRange === 'tahun_baru') {{
    return all.filter(d => d.date >= '2026-01-01' && d.date <= '2026-01-15');
  }}
  return all;
}}

function renderTimelineChart() {{
  const data = getTimelineFilteredData();
  const ctx = document.getElementById('chartTimeline').getContext('2d');
  const labels = data.map(d => d.date);
  const prefix = currentMetric === 'pnp' ? '' : 'arm_';

  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  const datasets = [
    {{ label: 'Total Multimoda', data: data.map(d => d[prefix + 'TOTAL']), borderColor: (currentTheme === 'light' ? '#0f172a' : '#ffffff'), backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 2.4, pointRadius: 0, tension: 0.2 }},
    {{ label: 'Pesawat (Udara)', data: data.map(d => d[prefix + 'UDARA']), borderColor: PALETTE.UDARA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
    {{ label: 'Kereta Api (KA)', data: data.map(d => d[prefix + 'KA']), borderColor: PALETTE.KA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
    {{ label: 'Bus AKAP', data: data.map(d => d[prefix + 'BUS']), borderColor: PALETTE.BUS, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
    {{ label: 'Penyeberangan (ASDP)', data: data.map(d => d[prefix + 'ASDP']), borderColor: PALETTE.ASDP, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
    {{ label: 'Kapal Laut', data: data.map(d => d[prefix + 'LAUT']), borderColor: PALETTE.LAUT, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
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
        legend: {{ labels: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans', size: 11, weight: '600' }} }} }},
        tooltip: {{
          backgroundColor: (currentTheme === 'light' ? 'rgba(255,255,255,0.96)' : 'rgba(15,23,42,0.96)'),
          titleColor: (currentTheme === 'light' ? '#0f172a' : '#ffffff'),
          bodyColor: (currentTheme === 'light' ? '#334155' : '#cbd5e1'),
          borderColor: 'rgba(59,130,246,0.3)',
          borderWidth: 1,
          padding: 10,
          callbacks: {{
            label: (ctx) => `${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} ${{currentMetric === 'pnp' ? 'pnp' : 'armada'}}`
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, maxTicksLimit: 14, font: {{ family: 'JetBrains Mono', size: 10 }} }} }},
        y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : (v/1e3).toFixed(0) + 'k') }} }}
      }}
    }}
  }});
}}

function setTimelineFilter(range, btn) {{
  currentTimelineRange = range;
  document.querySelectorAll('.side-control-card .side-btn-pill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const labelMap = {{
    'all': '271 Hari Pengamatan (1 Jan - 28 Sep 2026)',
    'lebaran': '27 Hari Periode Angkutan Lebaran 2026',
    'libur_sekolah': '31 Hari Periode Libur Sekolah 2026',
    'tahun_baru': '15 Hari Periode Libur Tahun Baru 2026'
  }};
  document.getElementById('chip-timeline-days').innerText = labelMap[range] || '';
  renderTimelineChart();
}}

function setMetricMode(m) {{
  currentMetric = m;
  document.getElementById('side-btn-pnp').classList.toggle('active', m === 'pnp');
  document.getElementById('side-btn-arm').classList.toggle('active', m === 'arm');
  document.getElementById('timeline-chart-heading').innerText = m === 'pnp' ? 'Kurva Pergerakan Harian Penumpang Multimoda 2026' : 'Kurva Pergerakan Harian Armada Multimoda 2026';
  renderTimelineChart();
}}

function exportTimelineCSV() {{
  const data = getTimelineFilteredData();
  let csv = 'tanggal,moda_udara,moda_ka,moda_bus,moda_asdp,moda_laut,total_penumpang,armada_udara,armada_ka,armada_bus,armada_asdp,armada_laut,total_armada\\n';
  data.forEach(d => {{
    csv += `${{d.date}},${{d.UDARA}},${{d.KA}},${{d.BUS}},${{d.ASDP}},${{d.LAUT}},${{d.TOTAL}},${{d.arm_UDARA}},${{d.arm_KA}},${{d.arm_BUS}},${{d.arm_ASDP}},${{d.arm_LAUT}},${{d.arm_TOTAL}}\\n`;
  }});
  const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', `siasati_timeline_${{currentTimelineRange}}_${{currentMetric}}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

function renderMonthlyChart() {{
  const ctx = document.getElementById('chartMonthly').getContext('2d');
  const ms = DATA.monthly_summary;
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  chartMonthlyInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: ms.map(m => m.label),
      datasets: [
        {{ label: 'Pesawat (Udara)', data: ms.map(m => m.UDARA), backgroundColor: PALETTE.UDARA }},
        {{ label: 'Kereta Api (KA)', data: ms.map(m => m.KA), backgroundColor: PALETTE.KA }},
        {{ label: 'Bus AKAP', data: ms.map(m => m.BUS), backgroundColor: PALETTE.BUS }},
        {{ label: 'ASDP Penyeberangan', data: ms.map(m => m.ASDP), backgroundColor: PALETTE.ASDP }},
        {{ label: 'Kapal Laut', data: ms.map(m => m.LAUT), backgroundColor: PALETTE.LAUT }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ labels: {{ color: tickColor, font: {{ size: 10.5, family: 'Plus Jakarta Sans' }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} pnp` }} }}
      }},
      scales: {{
        x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: tickColor, font: {{ size: 10, family: 'Plus Jakarta Sans' }} }} }},
        y: {{ stacked: true, grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e6).toFixed(0) + 'M' }} }}
      }}
    }}
  }});
}}

function renderDOWChart() {{
  const ctx = document.getElementById('chartDOW').getContext('2d');
  const dow = DATA.dow_summary;
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  chartDOWInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: dow.map(d => d.dow),
      datasets: [
        {{ label: 'Rata-rata Penumpang Harian', data: dow.map(d => d.TOTAL), backgroundColor: 'rgba(59, 130, 246, 0.4)', borderColor: 'rgba(59, 130, 246, 0.9)', borderWidth: 1.5, borderRadius: 4 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ callbacks: {{ label: ctx => `Rata-rata: ${{numFmt(ctx.raw)}} pnp/hari` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e6).toFixed(1) + 'M' }} }}
      }}
    }}
  }});
}}

// -------------------------------------------------------------
// TAB 2: LEBARAN 2026
// -------------------------------------------------------------
function selectDay(dateStr) {{
  const day = DATA.lebaran_daily.find(d => d.date === dateStr);
  if (!day) return;

  document.getElementById('banner-tag').innerText = day.tag;
  document.getElementById('banner-tag').className = 'policy-badge ' + (day.is_peak_balik1 || day.is_peak_mudik ? 'critical' : (day.is_h_day ? 'warning' : 'operational'));
  document.getElementById('banner-phase-desc').innerText = day.desc;
  document.getElementById('banner-date').innerText = `${{day.date}} • ${{day.tag}}`;
  document.getElementById('banner-desc').innerText = `Total Penumpang: ${{numFmt(day.TOTAL)}} orang • Total Perjalanan Armada: ${{numFmt(day.arm_TOTAL)}} trip`;

  const pillsBox = document.getElementById('banner-pills');
  pillsBox.innerHTML = `
    <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:var(--color-udara); font-weight:700;">UDARA</div>
      <div class="num-mono" style="font-size:13px; font-weight:800;">${{numFmt(day.UDARA)}}</div>
    </div>
    <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:var(--color-ka); font-weight:700;">KERETA API</div>
      <div class="num-mono" style="font-size:13px; font-weight:800;">${{numFmt(day.KA)}}</div>
    </div>
    <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:var(--color-bus); font-weight:700;">BUS</div>
      <div class="num-mono" style="font-size:13px; font-weight:800;">${{numFmt(day.BUS)}}</div>
    </div>
    <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:var(--color-asdp); font-weight:700;">ASDP</div>
      <div class="num-mono" style="font-size:13px; font-weight:800;">${{numFmt(day.ASDP)}}</div>
    </div>
    <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; text-align:center;">
      <div style="font-size:10px; color:var(--color-laut); font-weight:700;">LAUT</div>
      <div class="num-mono" style="font-size:13px; font-weight:800;">${{numFmt(day.LAUT)}}</div>
    </div>
  `;
}}

function renderLebaranCharts() {{
  if (chartLebaranInst) return;

  const strip = document.getElementById('lebaran-strip');
  strip.innerHTML = '';
  DATA.lebaran_daily.forEach(d => {{
    const card = document.createElement('div');
    card.className = 'day-badge-card' + (d.is_peak_balik1 ? ' active peak-balik' : (d.is_peak_mudik ? ' peak-mudik' : ''));
    card.innerHTML = `
      <div class="day-phase">${{d.tag.split(' ')[0]}}</div>
      <div class="day-vol num-mono">${{(d.TOTAL / 1e6).toFixed(2)}}M</div>
      <div class="day-sub">${{d.date.substring(5)}}</div>
    `;
    card.onclick = () => {{
      document.querySelectorAll('.day-badge-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      selectDay(d.date);
    }};
    strip.appendChild(card);
  }});
  selectDay('2026-03-24');

  const ctxLine = document.getElementById('chartLebaranLine').getContext('2d');
  const ld = DATA.lebaran_daily;
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  chartLebaranInst = new Chart(ctxLine, {{
    type: 'line',
    data: {{
      labels: ld.map(d => d.date.substring(5) + ' (' + d.tag.split(' ')[0] + ')'),
      datasets: [
        {{ label: 'Total Penumpang', data: ld.map(d => d.TOTAL), borderColor: (currentTheme === 'light' ? '#0f172a' : '#ffffff'), borderWidth: 2.8, pointRadius: 2.5, tension: 0.2 }},
        {{ label: 'Pesawat (Udara)', data: ld.map(d => d.UDARA), borderColor: PALETTE.UDARA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Kereta Api (KA)', data: ld.map(d => d.KA), borderColor: PALETTE.KA, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Bus AKAP', data: ld.map(d => d.BUS), borderColor: PALETTE.BUS, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
        {{ label: 'ASDP Penyeberangan', data: ld.map(d => d.ASDP), borderColor: PALETTE.ASDP, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
        {{ label: 'Kapal Laut', data: ld.map(d => d.LAUT), borderColor: PALETTE.LAUT, borderWidth: 1.8, pointRadius: 0, tension: 0.2 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ labels: {{ color: tickColor, font: {{ size: 10, family: 'Plus Jakarta Sans' }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{numFmt(ctx.raw)}} pnp` }} }}
      }},
      scales: {{
        x: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, maxRotation: 45, font: {{ size: 9, family: 'JetBrains Mono' }} }} }},
        y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono', size: 10 }}, callback: v => (v/1e3).toFixed(0) + 'k' }} }}
      }}
    }}
  }});

  const ctxSurge = document.getElementById('chartSurgeBar').getContext('2d');
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA', 'TOTAL'];
  const labelsSurge = ['ASDP', 'Bus AKAP', 'Kereta Api', 'Kapal Laut', 'Pesawat Udara', 'TOTAL'];

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
      plugins: {{
        legend: {{ labels: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}: +${{ctx.raw}}%` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono' }}, callback: v => '+' + v + '%' }} }}
      }}
    }}
  }});

  const tbody = document.querySelector('#table-surge tbody');
  tbody.innerHTML = '';
  const notes = {{
    'ASDP': 'Lonjakan paling awal (H-2) & paling ekstrem (+252,1%) karena pergerakan mobil pribadi via Ro-Ro.',
    'BUS': 'Puncak arus balik di 25 Mar (556k pnp), dipicu serapan pemudik yang kembali ke Jabodetabek/Surabaya.',
    'KA': 'Puncak tertinggi pada 24 Mar (565k pnp); keterisian kursi kereta komersial 100%.',
    'LAUT': 'Mencapai puncak arus balik kedua di 29 Mar (295k pnp) pada jalur kepulauan dan pesisir.',
    'UDARA': 'Mencapai volume tertinggi di akhir masa libur (29 Mar, 649k pnp) seiring kembalinya pekerja eksekutif/ASN.',
    'TOTAL': 'Puncak tertinggi nasional all-time pada Selasa, 24 Maret 2026 (2.415.296 penumpang).'
  }};

  modas.forEach((m, idx) => {{
    const s = DATA.surge_summary[m];
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${{labelsSurge[idx]}}</strong></td>
      <td class="num-mono">${{numFmt(s.baseline)}}</td>
      <td class="num-mono" style="color:var(--accent-rose); font-weight:700;">${{numFmt(s.peak_mudik)}}</td>
      <td><span class="policy-badge critical">+${{s.surge_mudik_pct}}%</span></td>
      <td class="num-mono" style="color:var(--accent-cyan); font-weight:700;">${{numFmt(s.peak_balik1)}}</td>
      <td><span class="policy-badge operational">+${{s.surge_balik1_pct}}%</span></td>
      <td class="num-mono">${{numFmt(s.peak_balik2)}}</td>
      <td class="num-mono">+${{s.surge_balik2_pct}}%</td>
      <td style="font-size:12px; color:var(--text-muted);">${{notes[m]}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// TAB 3: MODAL SHARE
// -------------------------------------------------------------
function renderModalShareCharts() {{
  if (chartModalShareAreaInst) return;

  const ctxArea = document.getElementById('chartModalShareArea').getContext('2d');
  const ms = DATA.monthly_summary;
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  chartModalShareAreaInst = new Chart(ctxArea, {{
    type: 'line',
    data: {{
      labels: ms.map(m => m.label),
      datasets: [
        {{ label: 'Udara', data: ms.map(m => m.share_UDARA), borderColor: PALETTE.UDARA, backgroundColor: 'rgba(56, 189, 248, 0.35)', fill: true, tension: 0.3 }},
        {{ label: 'Kereta Api', data: ms.map(m => m.share_KA), borderColor: PALETTE.KA, backgroundColor: 'rgba(245, 158, 11, 0.35)', fill: true, tension: 0.3 }},
        {{ label: 'Bus AKAP', data: ms.map(m => m.share_BUS), borderColor: PALETTE.BUS, backgroundColor: 'rgba(16, 185, 129, 0.35)', fill: true, tension: 0.3 }},
        {{ label: 'ASDP Penyeberangan', data: ms.map(m => m.share_ASDP), borderColor: PALETTE.ASDP, backgroundColor: 'rgba(139, 92, 246, 0.35)', fill: true, tension: 0.3 }},
        {{ label: 'Kapal Laut', data: ms.map(m => m.share_LAUT), borderColor: PALETTE.LAUT, backgroundColor: 'rgba(6, 182, 212, 0.35)', fill: true, tension: 0.3 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ labels: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw}}% pangsa pasar` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: tickColor, font: {{ size: 10, family: 'Plus Jakarta Sans' }} }} }},
        y: {{ stacked: true, max: 100, grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono' }}, callback: v => v + '%' }} }}
      }}
    }}
  }});

  const feb = ms.find(m => m.bulan === '2026-02');
  const mar = ms.find(m => m.bulan === '2026-03');
  const labels = ['Udara', 'Kereta Api', 'Bus', 'ASDP', 'Laut'];
  const colors = [PALETTE.UDARA, PALETTE.KA, PALETTE.BUS, PALETTE.ASDP, PALETTE.LAUT];

  const ctxNorm = document.getElementById('donutNormal').getContext('2d');
  donutNormalInst = new Chart(ctxNorm, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [feb.share_UDARA, feb.share_KA, feb.share_BUS, feb.share_ASDP, feb.share_LAUT],
        backgroundColor: colors,
        borderWidth: 0
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom', labels: {{ color: tickColor, font: {{ size: 10 }} }} }} }}
    }}
  }});

  const ctxPeak = document.getElementById('donutPeak').getContext('2d');
  donutPeakInst = new Chart(ctxPeak, {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{
        data: [mar.share_UDARA, mar.share_KA, mar.share_BUS, mar.share_ASDP, mar.share_LAUT],
        backgroundColor: colors,
        borderWidth: 0
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom', labels: {{ color: tickColor, font: {{ size: 10 }} }} }} }}
    }}
  }});
}}

// -------------------------------------------------------------
// TAB 4: LOAD FACTOR
// -------------------------------------------------------------
function renderLoadFactorCharts() {{
  if (chartLoadFactorInst) return;

  const ctx = document.getElementById('chartLoadFactor').getContext('2d');
  const lf = DATA.load_factor_stats;
  const modas = ['ASDP', 'BUS', 'KA', 'LAUT', 'UDARA'];
  const labels = ['ASDP (pnp/trip)', 'Bus (pnp/bus)', 'KA (pnp/trip)', 'Laut (pnp/kapal)', 'Udara (pnp/flight)'];
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.05)';
  const tickColor = currentTheme === 'light' ? '#64748b' : '#94a3b8';

  chartLoadFactorInst = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [
        {{ label: 'Hari Normal (Februari)', data: modas.map(m => lf[m].normal_ratio), backgroundColor: (currentTheme === 'light' ? 'rgba(148,163,184,0.6)' : 'rgba(148,163,184,0.3)'), borderRadius: 4 }},
        {{ label: 'Puncak Lebaran (Maret)', data: modas.map(m => lf[m].peak_ratio), backgroundColor: 'rgba(59, 130, 246, 0.85)', borderRadius: 4 }},
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ labels: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw}} rasio penumpang/armada` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: tickColor, font: {{ family: 'Plus Jakarta Sans' }} }} }},
        y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, font: {{ family: 'JetBrains Mono' }} }} }}
      }}
    }}
  }});
}}

// -------------------------------------------------------------
// TAB 5: TOP HUBS
// -------------------------------------------------------------
function setHubModa(m, btn) {{
  currentHubModa = m;
  document.querySelectorAll('#tab-top-hubs .segmented-control:first-child .btn-seg').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHubTable();
}}

function setHubPeriod(p) {{
  currentHubPeriod = p;
  document.getElementById('btn-period-peak').classList.toggle('active', p === 'peak');
  document.getElementById('btn-period-ytd').classList.toggle('active', p === 'ytd');
  document.getElementById('hub-table-heading').innerText = p === 'peak' ? 'Peringkat Simpul Transportasi Terpadat (Puncak Lebaran 18-29 Maret 2026)' : 'Peringkat Simpul Transportasi Terpadat Sepanjang Tahun 2026 (YTD)';
  renderHubTable();
}}

function filterHubTable(term) {{
  currentSearchTerm = term.toLowerCase().trim();
  renderHubTable();
}}

function renderHubTable() {{
  const tbody = document.querySelector('#table-hubs tbody');
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
    list = list.filter(item => 
      (item.nama_prasarana || '').toLowerCase().includes(currentSearchTerm) ||
      (item.provinsi || '').toLowerCase().includes(currentSearchTerm)
    );
  }}

  if (list.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:32px; color:var(--text-muted);">Tidak ditemukan simpul yang sesuai dengan kriteria pencarian.</td></tr>';
    return;
  }}

  const maxVal = list[0].pnp || 1;
  const pillIcons = {{
    UDARA: `{icons['plane']}`,
    KA: `{icons['train']}`,
    BUS: `{icons['bus']}`,
    ASDP: `{icons['asdp']}`,
    LAUT: `{icons['ship']}`
  }};

  list.forEach((item, idx) => {{
    const tr = document.createElement('tr');
    const pct = ((item.pnp / maxVal) * 100).toFixed(0);
    const mColor = PALETTE[item.moda] || '#38bdf8';

    tr.innerHTML = `
      <td class="num-mono" style="font-weight:800; color: ${{idx < 3 ? 'var(--accent-amber)' : 'var(--text-dim)'}};">#${{idx + 1}}</td>
      <td><strong>${{item.nama_prasarana}}</strong></td>
      <td><span class="moda-pill ${{item.moda.toLowerCase()}}">${{pillIcons[item.moda] || ''}} ${{item.moda}}</span></td>
      <td style="color:var(--text-muted);">${{item.provinsi || '-'}}</td>
      <td class="num-mono" style="font-weight:700; color:var(--text-main);">${{numFmt(item.pnp)}} pnp</td>
      <td class="num-mono" style="color:var(--text-muted);">${{numFmt(item.arm)}} armada</td>
      <td>
        <div class="progress-cell">
          <div class="progress-rail">
            <div class="progress-fill" style="width: ${{pct}}%; background: ${{mColor}};"></div>
          </div>
          <span class="num-mono" style="font-size:10.5px; color:var(--text-dim); min-width:30px;">${{pct}}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

// -------------------------------------------------------------
// INITIALIZATION
// -------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {{
  document.getElementById('val-total-pnp').innerText = numFmt(DATA.meta.total_passengers_ytd);
  document.getElementById('val-total-arm').innerText = numFmt(DATA.meta.total_armada_ytd);

  renderTimelineChart();
  renderMonthlyChart();
  renderDOWChart();
}});
</script>
</body>
</html>
"""

with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"File Dashboard dengan Collapsible Sidebar berhasil dibuat: {out_html}")
print(f"Ukuran file: {os.path.getsize(out_html) / 1024:.1f} KB")
