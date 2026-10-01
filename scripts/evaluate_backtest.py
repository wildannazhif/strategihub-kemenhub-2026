import json
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. Load combined 2025 + 2026 dataset
df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)
df26 = pd.DataFrame(bundle['daily_timeline'])
df26 = df26[df26['date'] <= '2026-09-27'].copy()

modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
s25 = df25[['tanggal', 'TOTAL_PENUMPANG'] + [f'pnp_{m}' for m in modes]].rename(
    columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL', **{f'pnp_{m}': m for m in modes}}
)
s26 = df26[['date', 'TOTAL'] + modes]

combined = pd.concat([s25, s26], ignore_index=True)
combined['date_dt'] = pd.to_datetime(combined['date'])
combined.set_index('date_dt', inplace=True)

# 2. Train-test split for backtesting (last 28 days: 31 Aug 2026 - 27 Sep 2026 as test set)
train_df = combined.iloc[:-28]
test_df = combined.iloc[-28:]

train_start = train_df.index[0].strftime('%Y-%m-%d')
train_end = train_df.index[-1].strftime('%Y-%m-%d')
test_start = test_df.index[0].strftime('%Y-%m-%d')
test_end = test_df.index[-1].strftime('%Y-%m-%d')

print(f"Data Latih (Training): {len(train_df)} hari ({train_start} s.d. {train_end}) [2025: 365H + 2026: 242H]")
print(f"Data Uji (Testing/Backtest): {len(test_df)} hari ({test_start} s.d. {test_end})")

# 3. Fit Holt-Winters (s=7, Damped Trend) on total series
hw = ExponentialSmoothing(
    train_df['TOTAL'],
    seasonal_periods=7,
    trend='add',
    damped_trend=True,
    seasonal='mul',
    initialization_method='estimated'
).fit()

pred_test = hw.forecast(28).values
y_true = test_df['TOTAL'].values

mape = float(np.mean(np.abs((y_true - pred_test) / y_true)) * 100)
rmse = float(np.sqrt(np.mean((y_true - pred_test) ** 2)))
mae = float(np.mean(np.abs(y_true - pred_test)))
mean_vol = float(np.mean(y_true))

print(f"\nEvaluasi Model Total Multimoda (Uji 28 Hari):")
print(f"  MAPE: {mape:.2f}%")
print(f"  RMSE: {rmse:,.0f} penumpang/hari")
print(f"  MAE:  {mae:,.0f} penumpang/hari")
print(f"  Rata-rata Riil: {mean_vol:,.0f} penumpang/hari")
print(f"  Rasio Error (RMSE / Mean): {(rmse / mean_vol) * 100:.2f}%")

# 4. Compute per-mode metrics
mode_eval = {}
print("\nEvaluasi Per Moda (Uji 28 Hari):")
for m in modes:
    hw_m = ExponentialSmoothing(
        train_df[m],
        seasonal_periods=7,
        trend='add',
        damped_trend=True,
        seasonal='mul',
        initialization_method='estimated'
    ).fit()
    
    pred_m = hw_m.forecast(28).values
    y_m = test_df[m].values
    mape_m = float(np.mean(np.abs((y_m - pred_m) / y_m)) * 100)
    rmse_m = float(np.sqrt(np.mean((y_m - pred_m) ** 2)))
    mae_m = float(np.mean(np.abs(y_m - pred_m)))
    mean_m = float(np.mean(y_m))
    
    mode_eval[m] = {
        'mape': round(mape_m, 2),
        'rmse': int(round(rmse_m)),
        'mae': int(round(mae_m)),
        'mean_vol': int(round(mean_m)),
        'rel_error_pct': round((rmse_m / mean_m) * 100, 2)
    }
    print(f"  {m:5s} -> MAPE: {mape_m:5.2f}% | RMSE: {rmse_m:8,.0f} pnp | Rerata: {mean_m:8,.0f} pnp | Rel: {mode_eval[m]['rel_error_pct']}%")

# Save evaluation metrics into bundle['forecast_nataru']['metrics']
bundle['forecast_nataru']['metrics'] = {
    'test_period': f"{test_start} s.d. {test_end} (28 Hari)",
    'train_period': f"{train_start} s.d. {train_end} ({len(train_df)} Hari)",
    'TOTAL': {
        'mape': round(mape, 2),
        'rmse': int(round(rmse)),
        'mae': int(round(mae)),
        'mean_vol': int(round(mean_vol)),
        'rel_error_pct': round((rmse / mean_vol) * 100, 2)
    },
    'modes': mode_eval
}

with open('scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("\nSaved evaluation metrics to mobility_data_bundle.json successfully!")
