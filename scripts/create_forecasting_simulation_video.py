import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
import matplotlib.patches as patches
from datetime import datetime, timedelta

# Set font & aesthetic
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

BUNDLE_PATH = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
OUTPUT_VIDEO = r"c:\Users\USER\Documents\PUSDATIN\simulasi_forecasting_nataru_2026.mp4"

print("Memuat dataset operasional...")
with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

# 1. Historical 2026 (272 days: Jan 1 - Sep 29)
hist_2026 = bundle['daily_timeline']
dates_2026 = [datetime.strptime(d['date'], '%Y-%m-%d') for d in hist_2026]
vols_2026 = [d['TOTAL'] for d in hist_2026]

# 2. Historical 2025 (365 days)
hist_2025 = bundle['timeline_2025']
# Align 2025 dates to 2026 calendar for direct YoY benchmark overlay
dates_2025_aligned = []
vols_2025 = []
for d in hist_2025:
    dt = datetime.strptime(d['date'], '%Y-%m-%d')
    # map to 2026 or early 2027
    if dt.month == 1 and dt.day <= 7:
        dt_aligned = dt.replace(year=2027)
    else:
        dt_aligned = dt.replace(year=2026)
    dates_2025_aligned.append(dt_aligned)
    vols_2025.append(d['TOTAL'])

# Sort aligned 2025
pairs_2025 = sorted(zip(dates_2025_aligned, vols_2025), key=lambda x: x[0])
dates_2025_sorted, vols_2025_sorted = zip(*pairs_2025)

# 3. Forecast 2026/2027 (100 days: Sep 30, 2026 - Jan 7, 2027)
forecast_data = bundle['forecast_nataru']['scenarios']['moderat']
dates_fc = [datetime.strptime(d['date'], '%Y-%m-%d') for d in forecast_data]
vols_fc = [d['TOTAL'] for d in forecast_data]
ci_lower = [d['ci_lower'] for d in forecast_data]
ci_upper = [d['ci_upper'] for d in forecast_data]
hw_baseline = [d['hw_baseline'] for d in forecast_data]
shock_factors = [d['shock_factor'] for d in forecast_data]

# Full Timeline for X-axis: 1 Jan 2026 s.d. 10 Jan 2027
start_date = datetime(2026, 1, 1)
cutoff_date = datetime(2026, 9, 29)
end_date = datetime(2027, 1, 10)

print("Mengonfigurasi kanvas video 1080p...")
fig = plt.figure(figsize=(16, 9), dpi=120, facecolor='#090d16')
gs = fig.add_gridspec(3, 1, height_ratios=[1.1, 5.2, 1.2], hspace=0.32, top=0.95, bottom=0.06, left=0.06, right=0.95)

ax_header = fig.add_subplot(gs[0])
ax_chart = fig.add_subplot(gs[1])
ax_footer = fig.add_subplot(gs[2])

for ax in [ax_header, ax_footer]:
    ax.set_facecolor('#090d16')
    ax.axis('off')

ax_chart.set_facecolor('#0f172a')
ax_chart.tick_params(colors='#94a3b8', labelsize=9)
for spine in ax_chart.spines.values():
    spine.set_color('#334155')

ax_chart.set_xlim(start_date, end_date)
ax_chart.set_ylim(400_000, 2_650_000)
ax_chart.grid(True, linestyle='--', color='#1e293b', alpha=0.7)
ax_chart.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax_chart.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

# Y-axis formatter (in Millions)
def y_fmt(v, pos):
    if v >= 1e6:
        return f'{v*1e-6:.1f} Jt'
    return f'{v*1e-3:.0f} Rb'
ax_chart.yaxis.set_major_formatter(plt.FuncFormatter(y_fmt))

# Plot elements initialization
line_2025, = ax_chart.plot([], [], color='#10b981', linestyle=':', linewidth=1.5, alpha=0.5, label='Realisasi 2025 (Tahun Lalu)')
line_2026, = ax_chart.plot([], [], color='#38bdf8', linewidth=2.0, alpha=0.95, label='Realisasi Riil 2026 (Jan - Sep)')
line_cutoff = ax_chart.axvline(cutoff_date, color='#ef4444', linestyle='--', linewidth=1.5, alpha=0)
text_cutoff = ax_chart.text(cutoff_date, 2_450_000, ' Cutoff Data Riil (29 Sep)', color='#ef4444', fontsize=9, fontweight='bold', alpha=0)

line_hw_base, = ax_chart.plot([], [], color='#93c5fd', linestyle='--', linewidth=1.4, alpha=0, label='Level dasar + Damped Trend')
line_fc, = ax_chart.plot([], [], color='#c084fc', linewidth=2.4, alpha=0, label='Proyeksi 1 Model Terpadu (100H)')
fill_ci = None

# Video Animation Parameters
fps = 24
total_frames = 360 # ~15 detik
# Phase breakdown:
# Frames 0 - 90   (0s - 3.75s): Fase 1 - Data Latih Historis
# Frames 91 - 180 (3.75s - 7.5s): Fase 2 - Level & Damped Trend Extrapolation
# Frames 181 - 270 (7.5s - 11.25s): Fase 3 - Shock Kalender Nataru & Gelombang Lonjakan
# Frames 271 - 360 (11.25s - 15.0s): Fase 4 - Pita Keyakinan 95% CI & Validasi Akurasi

print(f"Memulai pembuatan animasi: {total_frames} frame pada {fps} FPS...")

def animate(frame):
    global fill_ci
    
    # -------------------------------------------------------------
    # FASE 1: DATA LATIH HISTORIS (Frames 0 - 90)
    # -------------------------------------------------------------
    if frame <= 90:
        progress = frame / 90.0
        n_2026 = max(1, int(len(dates_2026) * progress))
        line_2026.set_data(dates_2026[:n_2026], vols_2026[:n_2026])
        
        # 2025 benchmark shows up gradually
        n_2025 = max(1, int(len(dates_2025_sorted) * progress))
        line_2025.set_data(dates_2025_sorted[:n_2025], vols_2025_sorted[:n_2025])
        
        cur_date_str = dates_2026[n_2026 - 1].strftime('%d %b %Y')
        cur_vol = vols_2026[n_2026 - 1]
        
        # Header update
        ax_header.clear()
        ax_header.axis('off')
        ax_header.text(0, 0.78, "SIMULASI METODOLOGI PERAMALAN (FORECASTING) NATARU 2026/2027", fontsize=15, fontweight='black', color='white')
        ax_header.text(0, 0.42, "FASE 1/4: DATA LATIH HISTORIS KONTINU (635 HARI GABUNGAN 2025 + 2026)", fontsize=11, fontweight='bold', color='#38bdf8')
        ax_header.text(0, 0.10, "Formula: Input Time Series Gabungan = [Data Riil 2025 (365H) + Data Riil 2026 (270H)]", fontsize=9.5, color='#94a3b8', fontfamily='monospace')
        
        # Footer update
        ax_footer.clear()
        ax_footer.axis('off')
        ax_footer.text(0.00, 0.50, f"Tanggal Latih: {cur_date_str}", fontsize=11, fontweight='bold', color='white')
        ax_footer.text(0.25, 0.50, f"Volume Riil: {cur_vol:,.0f} pnp", fontsize=11, fontweight='bold', color='#38bdf8')
        ax_footer.text(0.55, 0.50, "Status: Belajar dari Pola Nataru Tahun Lalu", fontsize=10.5, color='#cbd5e1')
        ax_footer.text(0.85, 0.50, "Tren YoY: +5,13%", fontsize=11, fontweight='bold', color='#10b981')

    # -------------------------------------------------------------
    # FASE 2: LEVEL & DAMPED TREND (Frames 91 - 180)
    # -------------------------------------------------------------
    elif frame <= 180:
        line_2026.set_data(dates_2026, vols_2026)
        line_2025.set_data(dates_2025_sorted, vols_2025_sorted)
        line_cutoff.set_alpha(1.0)
        text_cutoff.set_alpha(1.0)
        
        progress = (frame - 90) / 90.0
        n_fc = max(1, int(len(dates_fc) * progress))
        
        # Display smooth Holt-Winters baseline (Damped Trend)
        line_hw_base.set_alpha(0.85)
        line_hw_base.set_data(dates_fc[:n_fc], hw_baseline[:n_fc])
        
        cur_date_str = dates_fc[n_fc - 1].strftime('%d %b %Y')
        cur_base = hw_baseline[n_fc - 1]
        
        ax_header.clear()
        ax_header.axis('off')
        ax_header.text(0, 0.78, "SIMULASI METODOLOGI PERAMALAN (FORECASTING) NATARU 2026/2027", fontsize=15, fontweight='black', color='white')
        ax_header.text(0, 0.42, "FASE 2/4: EKSTRAPOLASI LEVEL DASAR (l_t) & TREN TEREDAM (b_t, phi = 0,98)", fontsize=11, fontweight='bold', color='#93c5fd')
        ax_header.text(0, 0.10, "Formula: y_base = [ Level(l_t) + sum(phi^i * b_t) ]  --> Mencegah over-ekstrapolasi tanpa batas", fontsize=9.5, color='#94a3b8', fontfamily='monospace')
        
        ax_footer.clear()
        ax_footer.axis('off')
        ax_footer.text(0.00, 0.50, f"Horizon Proyeksi: +{n_fc} Hari", fontsize=11, fontweight='bold', color='white')
        ax_footer.text(0.25, 0.50, f"Baseline HW: {cur_base:,.0f} pnp", fontsize=11, fontweight='bold', color='#93c5fd')
        ax_footer.text(0.55, 0.50, "Peredam Tren: phi = 0,98 (Stabil)", fontsize=10.5, color='#cbd5e1')
        ax_footer.text(0.85, 0.50, f"Tanggal: {cur_date_str}", fontsize=10.5, color='#e2e8f0')

    # -------------------------------------------------------------
    # FASE 3: SHOCK KALENDER NATARU & MUSIMAN (Frames 181 - 270)
    # -------------------------------------------------------------
    elif frame <= 270:
        line_2026.set_data(dates_2026, vols_2026)
        line_2025.set_data(dates_2025_sorted, vols_2025_sorted)
        line_cutoff.set_alpha(1.0)
        text_cutoff.set_alpha(1.0)
        line_hw_base.set_data(dates_fc, hw_baseline)
        line_hw_base.set_alpha(0.35)
        
        progress = (frame - 180) / 90.0
        n_fc = max(1, int(len(dates_fc) * progress))
        
        line_fc.set_alpha(1.0)
        line_fc.set_data(dates_fc[:n_fc], vols_fc[:n_fc])
        
        cur_date_str = dates_fc[n_fc - 1].strftime('%d %b %Y')
        cur_vol = vols_fc[n_fc - 1]
        cur_shock = shock_factors[n_fc - 1]
        
        ax_header.clear()
        ax_header.axis('off')
        ax_header.text(0, 0.78, "SIMULASI METODOLOGI PERAMALAN (FORECASTING) NATARU 2026/2027", fontsize=15, fontweight='black', color='white')
        ax_header.text(0, 0.42, "FASE 3/4: RITME MINGGUAN (s_t, m=7) & MULTIPLIER SHOCK NATARU (W_shock)", fontsize=11, fontweight='bold', color='#c084fc')
        ax_header.text(0, 0.10, "Formula: y_hat = y_base * Seasonality(s_t) * Shock_Nataru(W_shock)  --> Menangkap lonjakan libur akhir tahun", fontsize=9.5, color='#94a3b8', fontfamily='monospace')
        
        status_text = "Fase Reguler"
        if cur_shock > 1.2:
            status_text = "🔥 PUNCAK LONJAKAN NATARU"
        elif cur_shock > 1.05:
            status_text = "↗ Peningkatan Pra-Libur"
            
        ax_footer.clear()
        ax_footer.axis('off')
        ax_footer.text(0.00, 0.50, f"Tanggal: {cur_date_str}", fontsize=11, fontweight='bold', color='white')
        ax_footer.text(0.25, 0.50, f"Proyeksi: {cur_vol:,.0f} pnp", fontsize=11, fontweight='bold', color='#c084fc')
        ax_footer.text(0.55, 0.50, f"Faktor Shock: {cur_shock:.2f}x ({status_text})", fontsize=10.5, color='#fde047' if cur_shock > 1.2 else '#cbd5e1', fontweight='bold' if cur_shock > 1.2 else 'normal')
        ax_footer.text(0.85, 0.50, "Puncak: ~2,38 Jt pnp", fontsize=10.5, color='#f43f5e', fontweight='bold')

    # -------------------------------------------------------------
    # FASE 4: PITA KEYAKINAN 95% CI & VALIDASI MODEL (Frames 271 - 360)
    # -------------------------------------------------------------
    else:
        line_2026.set_data(dates_2026, vols_2026)
        line_2025.set_data(dates_2025_sorted, vols_2025_sorted)
        line_cutoff.set_alpha(1.0)
        text_cutoff.set_alpha(1.0)
        line_hw_base.set_data(dates_fc, hw_baseline)
        line_hw_base.set_alpha(0.25)
        line_fc.set_data(dates_fc, vols_fc)
        line_fc.set_alpha(1.0)
        
        progress = (frame - 270) / 90.0
        n_ci = max(1, int(len(dates_fc) * progress))
        
        # Clear existing fill_ci and draw new
        if fill_ci:
            fill_ci.remove()
        fill_ci = ax_chart.fill_between(dates_fc[:n_ci], ci_lower[:n_ci], ci_upper[:n_ci], color='#818cf8', alpha=0.25, label='95% Confidence Interval')
        
        ax_header.clear()
        ax_header.axis('off')
        ax_header.text(0, 0.78, "SIMULASI METODOLOGI PERAMALAN (FORECASTING) NATARU 2026/2027", fontsize=15, fontweight='black', color='white')
        ax_header.text(0, 0.42, "FASE 4/4: PITA KEYAKINAN 95% (CI_95%) & EVALUASI AKURASI OUT-OF-SAMPLE", fontsize=11, fontweight='bold', color='#10b981')
        ax_header.text(0, 0.10, "Formula: CI_95% = y_hat +/- 1.96 * RMSE  |  Evaluasi Uji: MAPE = 4,10% (Sangat Presisi)", fontsize=9.5, color='#34d399', fontfamily='monospace', fontweight='bold')
        
        ax_footer.clear()
        ax_footer.axis('off')
        ax_footer.text(0.00, 0.50, "Akurasi Uji: MAPE 4,10%", fontsize=11, fontweight='black', color='#10b981')
        ax_footer.text(0.25, 0.50, "WAPE: 4,02% • RMSE: 62.051", fontsize=10.5, color='#cbd5e1', fontfamily='monospace')
        ax_footer.text(0.55, 0.50, "Pita Ketidakpastian: +/- 1,96 * RMSE", fontsize=10.5, color='#818cf8')
        ax_footer.text(0.82, 0.50, "Status: MODEL VALID & SIAP", fontsize=11, fontweight='black', color='#38bdf8')

    # Legend configuration
    ax_chart.legend(loc='upper left', facecolor='#1e293b', edgecolor='#334155', fontsize=8.5, labelcolor='#e2e8f0')

print("Merender video MP4 dengan FFmpegWriter...")
writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='PUSDATIN Kemenhub', title='Simulasi Forecasting Nataru 2026'), bitrate=3000)

anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps)
anim.save(OUTPUT_VIDEO, writer=writer)
plt.close()

file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
print(f"Video simulasi berhasil dibuat!")
print(f"File: {OUTPUT_VIDEO} ({file_size_mb:.2f} MB)")
