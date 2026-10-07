import json
import time
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import Ridge

# 1. Load data
print("Memuat dataset gabungan 2025 + 2026...")
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

# 2. Train-test split (28-day holdout: 2 Sep - 29 Sep 2026)
train_df = combined.iloc[:-28]
test_df = combined.iloc[-28:]

y_train = train_df['TOTAL'].values
y_test = test_df['TOTAL'].values
n_test = len(y_test)

print(f"Total data: {len(combined)} hari | Train: {len(train_df)} hari | Test: {len(test_df)} hari\n")

models_benchmark = {}

def evaluate(name, y_pred, elapsed_sec):
    mape = float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100)
    wape = float(np.sum(np.abs(y_test - y_pred)) / np.sum(y_test) * 100)
    rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_test - y_pred)))
    max_err = float(np.max(np.abs(y_test - y_pred)))
    
    # Directional Accuracy (Direction of daily change)
    actual_dir = np.sign(np.diff(np.append([y_train[-1]], y_test)))
    pred_dir = np.sign(np.diff(np.append([y_train[-1]], y_pred)))
    dir_acc = float(np.mean(actual_dir == pred_dir) * 100)
    
    models_benchmark[name] = {
        'MAPE (%)': round(mape, 2),
        'WAPE (%)': round(wape, 2),
        'RMSE': int(round(rmse)),
        'MAE': int(round(mae)),
        'Max Error': int(round(max_err)),
        'Direction Acc (%)': round(dir_acc, 1),
        'Waktu (dtk)': round(elapsed_sec, 3),
        'y_pred': y_pred
    }
    print(f"[{name}] MAPE: {mape:.2f}% | WAPE: {wape:.2f}% | RMSE: {rmse:,.0f} | MAE: {mae:,.0f} | DirAcc: {dir_acc:.1f}% ({elapsed_sec:.2f}s)")

# MODEL 1: Holt-Winters Multiplicative Damped (Model Terpilih)
t0 = time.time()
hw_damped = ExponentialSmoothing(
    train_df['TOTAL'].clip(lower=1.0),
    trend='add',
    damped_trend=True,
    seasonal='mul',
    seasonal_periods=7,
    initialization_method='estimated'
).fit(damping_trend=0.98, optimized=True, use_brute=True)
pred_hw_damped = hw_damped.forecast(n_test).values
evaluate("1. Holt-Winters Mul Damped (Model Terpilih)", pred_hw_damped, time.time() - t0)

# MODEL 2: Holt-Winters Multiplicative Standard (Tanpa Damped)
t0 = time.time()
hw_mul = ExponentialSmoothing(
    train_df['TOTAL'].clip(lower=1.0),
    trend='add',
    damped_trend=False,
    seasonal='mul',
    seasonal_periods=7,
    initialization_method='estimated'
).fit(optimized=True, use_brute=True)
pred_hw_mul = hw_mul.forecast(n_test).values
evaluate("2. Holt-Winters Mul Standar (No Damping)", pred_hw_mul, time.time() - t0)

# MODEL 3: Holt-Winters Additive Seasonal
t0 = time.time()
hw_add = ExponentialSmoothing(
    train_df['TOTAL'].clip(lower=1.0),
    trend='add',
    damped_trend=True,
    seasonal='add',
    seasonal_periods=7,
    initialization_method='estimated'
).fit(damping_trend=0.98, optimized=True, use_brute=True)
pred_hw_add = hw_add.forecast(n_test).values
evaluate("3. Holt-Winters Additive Damped", pred_hw_add, time.time() - t0)

# MODEL 4: SARIMA(1, 1, 1) x (1, 1, 1, 7)
t0 = time.time()
sarima_mod = SARIMAX(
    train_df['TOTAL'],
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 7),
    enforce_stationarity=False,
    enforce_invertibility=False
).fit(disp=False)
pred_sarima = sarima_mod.forecast(n_test).values
evaluate("4. SARIMA (1,1,1)x(1,1,1,7)", pred_sarima, time.time() - t0)

# MODEL 5: ARIMA(1, 1, 1) Non-Seasonal
t0 = time.time()
arima_mod = ARIMA(train_df['TOTAL'], order=(1, 1, 1)).fit()
pred_arima = arima_mod.forecast(n_test).values
evaluate("5. ARIMA (1,1,1) Non-Seasonal", pred_arima, time.time() - t0)

# MODEL 6: Holt's Linear Trend (Double Exponential Smoothing - No Seasonality)
t0 = time.time()
holt_mod = Holt(train_df['TOTAL'].clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
pred_holt = holt_mod.forecast(n_test).values
evaluate("6. Holt's Linear Trend (No Seasonal)", pred_holt, time.time() - t0)

# MODEL 7: Simple Exponential Smoothing (SES - Flat Level)
t0 = time.time()
ses_mod = SimpleExpSmoothing(train_df['TOTAL'].clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
pred_ses = ses_mod.forecast(n_test).values
evaluate("7. Simple Exp Smoothing (SES)", pred_ses, time.time() - t0)

# MODEL 8: Regresi Ridge dengan Trend + Day-of-Week Dummies
t0 = time.time()
X_train = pd.get_dummies(train_df.index.dayofweek, prefix='dow', drop_first=True, dtype=float)
X_train['trend'] = np.arange(len(train_df))
X_test = pd.get_dummies(test_df.index.dayofweek, prefix='dow', drop_first=True, dtype=float)
X_test['trend'] = np.arange(len(train_df), len(train_df) + len(test_df))
ridge = Ridge(alpha=1.0).fit(X_train, y_train)
pred_ridge = ridge.predict(X_test)
evaluate("8. Linear Regression (Trend + DOW)", pred_ridge, time.time() - t0)

# MODEL 9: Seasonal Naive (Lag 7 Baseline)
t0 = time.time()
pred_snaive = y_train[-28:] # 28 days cycle from end of training
evaluate("9. Seasonal Naive (Lag 7)", pred_snaive, time.time() - t0)

# MODEL 10: Naive Random Walk (Lag 1 Baseline)
t0 = time.time()
pred_naive = np.full(n_test, y_train[-1])
evaluate("10. Naive / Random Walk (Lag 1)", pred_naive, time.time() - t0)

# MODEL 11: 7-Day Rolling Moving Average (Flat)
t0 = time.time()
pred_ma7 = np.full(n_test, np.mean(y_train[-7:]))
evaluate("11. 7-Day Moving Average", pred_ma7, time.time() - t0)

# SUMMARY RANKING TABLE
print("\n" + "=" * 95)
print("TABEL PERINGKAT EVALUASI BENCHMARK MODEL PERAMALAN (DATA UJI 28 HARI)")
print("=" * 95)

records = []
for name, data in models_benchmark.items():
    records.append({
        'Model': name,
        'MAPE (%)': data['MAPE (%)'],
        'WAPE (%)': data['WAPE (%)'],
        'RMSE': data['RMSE'],
        'MAE': data['MAE'],
        'Max Error': data['Max Error'],
        'Dir Acc (%)': data['Direction Acc (%)'],
        'Waktu (s)': data['Waktu (dtk)']
    })

df_res = pd.DataFrame(records).sort_values(by='MAPE (%)').reset_index(drop=True)
df_res.index = df_res.index + 1
print(df_res.to_string())

# Save results to json for charting/report
output_json = 'scripts/benchmark_forecast_results.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump({k: {k2: v2 for k2, v2 in v.items() if k2 != 'y_pred'} for k, v in models_benchmark.items()}, f, indent=2)
print(f"\nHasil benchmark tersimpan di: {output_json}")
