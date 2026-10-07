import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

# Set style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# Load benchmark data and predictions
print("Memuat hasil benchmark...")
with open('scripts/benchmark_forecast_results.json', 'r', encoding='utf-8') as f:
    bench_data = json.load(f)

# Re-run predictions for top 5 comparison curves
df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df26 = pd.DataFrame(bundle['daily_timeline'])
df26 = df26[df26['date'] <= '2026-09-29'].copy()

modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
s25 = df25[['tanggal', 'TOTAL_PENUMPANG'] + [f'pnp_{m}' for m in modes]].rename(
    columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL', **{f'pnp_{m}': m for m in modes}}
)
s26 = df26[['date', 'TOTAL'] + modes]

combined = pd.concat([s25, s26], ignore_index=True)
combined['date_dt'] = pd.to_datetime(combined['date'])
combined.set_index('date_dt', inplace=True)
combined.index.freq = 'D'

train_df = combined.iloc[:-28]
test_df = combined.iloc[-28:]
dates_test = test_df.index
y_true = test_df['TOTAL'].values

from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA

# Generate predictions
pred_hw_damped = ExponentialSmoothing(
    train_df['TOTAL'].clip(lower=1.0),
    trend='add', damped_trend=True, seasonal='mul', seasonal_periods=7
).fit(damping_trend=0.98, optimized=True, use_brute=True).forecast(28).values

pred_sarima = SARIMAX(
    train_df['TOTAL'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 7),
    enforce_stationarity=False, enforce_invertibility=False
).fit(disp=False).forecast(28).values

pred_arima = ARIMA(train_df['TOTAL'], order=(1, 1, 1)).fit().forecast(28).values
pred_ses = SimpleExpSmoothing(train_df['TOTAL'].clip(lower=1.0), initialization_method='estimated').fit(optimized=True).forecast(28).values
pred_snaive = train_df['TOTAL'].values[-28:]

# Create Figure
fig = plt.figure(figsize=(16, 10), dpi=300, facecolor='#ffffff')
gs = GridSpec(2, 2, height_ratios=[1.3, 1.0], width_ratios=[1.2, 0.8], hspace=0.32, wspace=0.22)

# --- PANEL 1: KURVA PREDIKSI OUT-OF-SAMPLE (28 HARI) ---
ax_curves = fig.add_subplot(gs[0, :])
ax_curves.set_facecolor('#f8fafc')
ax_curves.grid(True, linestyle=':', alpha=0.7, color='#cbd5e1')

ax_curves.plot(dates_test, y_true, color='#0f172a', linewidth=2.8, label='Data Aktual Riil (Ground Truth)', zorder=10)
ax_curves.plot(dates_test, pred_hw_damped, color='#10b981', linewidth=2.4, linestyle='-', label='Holt-Winters Mul Damped (Pilihan, MAPE 4,06%)', zorder=9)
ax_curves.plot(dates_test, pred_sarima, color='#f59e0b', linewidth=1.8, linestyle='--', label='SARIMA (1,1,1)x(1,1,1)7 (MAPE 5,87%)', zorder=8)
ax_curves.plot(dates_test, pred_ses, color='#8b5cf6', linewidth=1.5, linestyle=':', label='Simple Exp Smoothing (SES, MAPE 6,15%)', zorder=6)
ax_curves.plot(dates_test, pred_arima, color='#ef4444', linewidth=1.5, linestyle='-.', label='ARIMA (1,1,1) Non-Seasonal (MAPE 11,17%)', zorder=5)
ax_curves.plot(dates_test, pred_snaive, color='#94a3b8', linewidth=1.2, linestyle='--', alpha=0.7, label='Seasonal Naive Lag-7 (MAPE 13,51%)', zorder=4)

ax_curves.set_title('UJI EMPIRIS OUT-OF-SAMPLE (28 HARI): AKTUAL VS PERAMALAN MODEL', fontsize=13, fontweight='bold', color='#0f172a', loc='left')
ax_curves.set_ylabel('Volume Penumpang Multimoda', fontsize=11, fontweight='bold', color='#334155')
ax_curves.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
ax_curves.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax_curves.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v*1e-6:.2f}M' if v >= 1e6 else f'{v*1e-3:.0f}k'))
ax_curves.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9.5)

# Annotation callout
ax_curves.annotate('Holt-Winters mereplikasi puncak\nakhir pekan & lembah hari kerja\ndengan deviasi terendah!',
                   xy=(dates_test[12], pred_hw_damped[12]), xytext=(dates_test[4], 1_420_000),
                   arrowprops=dict(arrowstyle='->', color='#10b981', lw=1.5),
                   fontsize=9.5, fontweight='bold', color='#047857',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#ecfdf5', edgecolor='#10b981', lw=1))

# --- PANEL 2: BAR CHART PERINGKAT MAPE (%) ---
ax_mape = fig.add_subplot(gs[1, 0])
ax_mape.set_facecolor('#ffffff')
ax_mape.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1', axis='x')

# Prepare ranking df
models_clean = [
    ('HW Mul Standar', 3.34, '#10b981'),
    ('HW Mul Damped (Pilihan)', 4.06, '#059669'),
    ('HW Additive Damped', 4.63, '#34d399'),
    ('SARIMA (1,1,1)x(1,1,1)7', 5.87, '#f59e0b'),
    ('Simple Exp Smoothing', 6.15, '#fbbf24'),
    ('Holt Linear Trend', 6.24, '#f97316'),
    ('Naive Random Walk', 7.10, '#ea580c'),
    ('7-Day Moving Average', 10.55, '#ef4444'),
    ('ARIMA Non-Seasonal', 11.17, '#dc2626'),
    ('Seasonal Naive Lag-7', 13.51, '#b91c1c'),
    ('Linear Regression (DOW)', 16.76, '#991b1b')
]
models_clean.reverse()

names = [m[0] for m in models_clean]
mapes = [m[1] for m in models_clean]
colors = [m[2] for m in models_clean]

bars = ax_mape.barh(names, mapes, color=colors, height=0.68, edgecolor='none')
ax_mape.set_xlabel('MAPE (%) - Semakin Kecil Semakin Akurat', fontsize=10.5, fontweight='bold', color='#334155')
ax_mape.set_title('Peringkat Akurasi Model: MAPE (%)', fontsize=12, fontweight='bold', color='#0f172a', loc='left')
ax_mape.axvline(10.0, color='#dc2626', linestyle='--', linewidth=1.2, label='Batas Standar Internasional (<10% = Akurasi Tinggi)')

for bar, val in zip(bars, mapes):
    ax_mape.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.2f}%', va='center', fontsize=9, fontweight='bold', color='#0f172a')

ax_mape.set_xlim(0, 20)
ax_mape.legend(loc='lower right', fontsize=8.5, frameon=True, facecolor='#ffffff')

# --- PANEL 3: DIRECTIONAL ACCURACY & RMSE METRICS ---
ax_dir = fig.add_subplot(gs[1, 1])
ax_dir.set_facecolor('#ffffff')
ax_dir.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1', axis='x')

dir_data = [
    ('HW Mul Damped', 89.3, 60232, '#059669'),
    ('SARIMA (1,1,1)7', 57.1, 83614, '#f59e0b'),
    ('Holt Linear', 50.0, 103284, '#f97316'),
    ('ARIMA (1,1,1)', 53.6, 151818, '#dc2626'),
    ('Simple Exp (SES)', 3.6, 100170, '#fbbf24'),
    ('Naive Lag-1', 0.0, 118759, '#ea580c')
]
dir_data.reverse()

d_names = [d[0] for d in dir_data]
d_accs = [d[1] for d in dir_data]
d_colors = [d[3] for d in dir_data]

bars_d = ax_dir.barh(d_names, d_accs, color=d_colors, height=0.65, edgecolor='none')
ax_dir.set_xlabel('Directional Accuracy (%) - Kemampuan Prediksi Arah Naik/Turun', fontsize=10, fontweight='bold', color='#334155')
ax_dir.set_title('Ketepatan Pola Siklus Mingguan: Hit Rate (%)', fontsize=12, fontweight='bold', color='#0f172a', loc='left')
ax_dir.set_xlim(0, 105)

for bar, val, item in zip(bars_d, d_accs, dir_data):
    rmse_str = f"RMSE: {item[2]:,}"
    ax_dir.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val:.1f}% ({rmse_str})', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')

# Main Header
fig.suptitle('BUKTI EMPIRIS PERBANDINGAN 11 MODEL PERAMALAN MOBILITAS NASIONAL 2026', fontsize=16, fontweight='black', color='#0f172a', y=0.98)

output_img = 'benchmark_perbandingan_model_forecasting.png'
plt.savefig(output_img, dpi=300, bbox_inches='tight')
plt.close()
print(f"Gambar perbandingan model berhasil dibuat: {output_img}")
