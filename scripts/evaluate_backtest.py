import json
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. Load combined 2025 + 2026 dataset up to 2026-09-29 cutoff
df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df26 = pd.DataFrame(bundle['daily_timeline'])
# Strict cutoff: up to 2026-09-29
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

# 2. Train-test split for backtesting (Temporal holdout 28 days: 2 Sep 2026 s.d. 29 Sep 2026)
train_df = combined.iloc[:-28]
test_df = combined.iloc[-28:]

train_start = train_df.index[0].strftime('%Y-%m-%d')
train_end = train_df.index[-1].strftime('%Y-%m-%d')
test_start = test_df.index[0].strftime('%Y-%m-%d')
test_end = test_df.index[-1].strftime('%Y-%m-%d')

print("=" * 80)
print("EVALUASI BACKTEST HOLDOUT (28 HARI) - HOLT-WINTERS MULTIPLICATIVE DAMPED TREND")
print("=" * 80)
print(f"Dataset Gabungan Total: {len(combined)} hari ({combined.index[0].strftime('%Y-%m-%d')} s.d. {combined.index[-1].strftime('%Y-%m-%d')})")
print(f"Data Latih (Training) : {len(train_df)} hari ({train_start} s.d. {train_end}) [2025: 365H + 2026: 244H]")
print(f"Data Uji (Holdout)    : {len(test_df)} hari ({test_start} s.d. {test_end})")
print("Model Spec            : Additive Trend + Damped Trend (phi=0.98 fixed) + Multiplicative Seasonal (s=7)")
print("=" * 80)

def fit_hw_model(series):
    """
    Fit Holt-Winters Multiplicative Exponential Smoothing
    + Additive Trend
    + Damped Trend with fixed phi = 0.98
    + Weekly Seasonality s = 7
    """
    return ExponentialSmoothing(
        series.clip(lower=1.0),
        trend='add',
        damped_trend=True,
        seasonal='mul',
        seasonal_periods=7,
        initialization_method='estimated'
    ).fit(
        damping_trend=0.98,
        optimized=True,
        use_brute=True
    )

# 3. Fit Holt-Winters on TOTAL series
print("\n[1/2] Melatih dan mengevaluasi Model TOTAL Multimoda...")
hw_tot = fit_hw_model(train_df['TOTAL'])
pred_test = hw_tot.forecast(28).values
y_true = test_df['TOTAL'].values

mape_tot = float(np.mean(np.abs((y_true - pred_test) / y_true)) * 100)
wape_tot = float(np.sum(np.abs(y_true - pred_test)) / np.sum(y_true) * 100)
rmse_tot = float(np.sqrt(np.mean((y_true - pred_test) ** 2)))
mae_tot = float(np.mean(np.abs(y_true - pred_test)))
mean_vol = float(np.mean(y_true))
rel_error_tot = float((rmse_tot / mean_vol) * 100)

print(f"\nHasil Evaluasi Model Total Multimoda (Uji 28 Hari):")
print(f"  MAPE (Mean Absolute % Error) : {mape_tot:.2f}%")
print(f"  WAPE (Weighted MAPE)         : {wape_tot:.2f}%")
print(f"  RMSE (Root Mean Sq Error)    : {rmse_tot:,.0f} penumpang/hari")
print(f"  MAE  (Mean Absolute Error)   : {mae_tot:,.0f} penumpang/hari")
print(f"  Rata-rata Riil Lapangan      : {mean_vol:,.0f} penumpang/hari")
print(f"  Rasio Error Relatif (RMSE/M) : {rel_error_tot:.2f}%")

# 4. Compute per-mode metrics
print("\n[2/2] Melatih dan mengevaluasi Model Per Moda...")
mode_eval = {}
print("\nHasil Evaluasi Per Moda (Uji 28 Hari):")
print("-" * 88)
print(f"{'Moda':<8} | {'MAPE':<8} | {'WAPE':<8} | {'RMSE (pnp)':<12} | {'MAE (pnp)':<12} | {'Rerata Riil':<12} | {'Rel Err'}")
print("-" * 88)

for m in modes:
    hw_m = fit_hw_model(train_df[m])
    pred_m = hw_m.forecast(28).values
    y_m = test_df[m].values
    
    # Safe mask for MAPE on non-zero days
    mask = y_m > 0
    mape_m = float(np.mean(np.abs((y_m[mask] - pred_m[mask]) / y_m[mask])) * 100) if np.any(mask) else 0.0
    wape_m = float(np.sum(np.abs(y_m - pred_m)) / np.sum(y_m) * 100) if np.sum(y_m) > 0 else 0.0
    rmse_m = float(np.sqrt(np.mean((y_m - pred_m) ** 2)))
    mae_m = float(np.mean(np.abs(y_m - pred_m)))
    mean_m = float(np.mean(y_m))
    rel_m = float((rmse_m / mean_m) * 100) if mean_m > 0 else 0.0
    
    mode_eval[m] = {
        'mape': round(mape_m, 2),
        'wape': round(wape_m, 2),
        'rmse': int(round(rmse_m)),
        'mae': int(round(mae_m)),
        'mean_vol': int(round(mean_m)),
        'rel_error_pct': round(rel_m, 2)
    }
    print(f"{m:<8} | {mape_m:6.2f}%  | {wape_m:6.2f}%  | {rmse_m:12,.0f} | {mae_m:12,.0f} | {mean_m:12,.0f} | {rel_m:6.2f}%")

print("-" * 88)

# 5. Save evaluation metrics into bundle['forecast_nataru']['metrics']
if 'forecast_nataru' not in bundle:
    bundle['forecast_nataru'] = {}

bundle['forecast_nataru']['metrics'] = {
    'test_period': f"{test_start} s.d. {test_end} (28 Hari)",
    'train_period': f"{train_start} s.d. {train_end} ({len(train_df)} Hari)",
    'TOTAL': {
        'mape': round(mape_tot, 2),
        'wape': round(wape_tot, 2),
        'rmse': int(round(rmse_tot)),
        'mae': int(round(mae_tot)),
        'mean_vol': int(round(mean_vol)),
        'rel_error_pct': round(rel_error_tot, 2)
    },
    'modes': mode_eval
}

with open('scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("\nSukses menyimpan metrik evaluasi backtest ke scripts/mobility_data_bundle.json!")
