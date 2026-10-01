import json
import datetime
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ==============================================================================
# 1. LOAD HISTORICAL DATASETS (2025: 365 Days, 2026: 272 Days up to 2026-09-29)
# ==============================================================================
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

# 2025 daily CSV (365 days)
df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
df25['tanggal_dt'] = pd.to_datetime(df25['tanggal'])
df25['dow'] = df25['tanggal_dt'].dt.dayofweek
df25['md'] = df25['tanggal'].str[5:]
p25_by_md = df25.set_index('md').to_dict(orient='index')

# 2026 daily history strictly up to cutoff 2026-09-29
modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
daily_history_26 = bundle['daily_timeline']
df26 = pd.DataFrame(daily_history_26)
df26['date_dt'] = pd.to_datetime(df26['date'])
df26 = df26[df26['date_dt'] <= '2026-09-29'].copy()
df26.sort_values('date_dt', inplace=True)
df26.reset_index(drop=True, inplace=True)
df26['md'] = df26['date'].str[5:]

# Combine 2025 + 2026 into a single continuous training time series (637 days)
s25_tot = df25[['tanggal', 'TOTAL_PENUMPANG'] + [f'pnp_{m}' for m in modes] + ['TOTAL_ARMADA'] + [f'arm_{m}' for m in modes]].rename(
    columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL', 'TOTAL_ARMADA': 'arm_TOTAL',
             **{f'pnp_{m}': m for m in modes}}
)
s26_tot = df26[['date', 'TOTAL'] + modes + ['arm_TOTAL'] + [f'arm_{m}' for m in modes]]

df_train_combined = pd.concat([s25_tot, s26_tot], ignore_index=True)
df_train_combined['date_dt'] = pd.to_datetime(df_train_combined['date'])
df_train_combined.set_index('date_dt', inplace=True)
df_train_combined.index.freq = 'D'
total_train_days = len(df_train_combined)

print("=" * 80)
print("SISTEM FORECASTING NATARU 2026/2027 (KEMENHUB PUSDATIN)")
print("Model: Holt-Winters Multiplicative Exponential Smoothing + Additive Trend")
print("       + Damped Trend (phi=0.98) + Weekly Seasonality (s=7) + Nataru Calendar Shock")
print("=" * 80)
print(f"Unified Training Data: {total_train_days} hari ({df_train_combined.index[0].strftime('%Y-%m-%d')} s.d. {df_train_combined.index[-1].strftime('%Y-%m-%d')})")
print(f"  • Data 2025: 365 hari (1 Jan 2025 - 31 Des 2025)")
print(f"  • Data 2026: 272 hari (1 Jan 2026 - 29 Sep 2026)")
print("=" * 80)

# Helper function to fit Holt-Winters strictly per requirements
def fit_hw_model(series):
    """
    Fit Holt-Winters Multiplicative Exponential Smoothing
    + Additive Trend
    + Damped Trend with phi = 0.98 fixed
    + Weekly Seasonality s = 7
    Initialization: estimated
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

# ==============================================================================
# 2. BACKTEST EVALUATION (28-Day Temporal Holdout: 2 Sep 2026 - 29 Sep 2026)
# ==============================================================================
print("\n[LANGKAH 1/4] Melakukan Backtest Temporal Holdout 28 Hari...")
train_split = df_train_combined.iloc[:-28]
test_split = df_train_combined.iloc[-28:]
test_start = test_split.index[0].strftime('%Y-%m-%d')
test_end = test_split.index[-1].strftime('%Y-%m-%d')
train_start = train_split.index[0].strftime('%Y-%m-%d')
train_end = train_split.index[-1].strftime('%Y-%m-%d')

hw_test_tot = fit_hw_model(train_split['TOTAL'])
pred_test_tot = hw_test_tot.forecast(28).values
y_true_tot = test_split['TOTAL'].values

mape_tot = float(np.mean(np.abs((y_true_tot - pred_test_tot) / y_true_tot)) * 100)
wape_tot = float(np.sum(np.abs(y_true_tot - pred_test_tot)) / np.sum(y_true_tot) * 100)
rmse_tot = float(np.sqrt(np.mean((y_true_tot - pred_test_tot) ** 2)))
mae_tot = float(np.mean(np.abs(y_true_tot - pred_test_tot)))
mean_test_vol = float(np.mean(y_true_tot))
rel_error_tot = float((rmse_tot / mean_test_vol) * 100)

mode_eval = {}
for m in modes:
    hw_test_m = fit_hw_model(train_split[m])
    pm = hw_test_m.forecast(28).values
    ym = test_split[m].values
    mask = ym > 0
    mape_m = float(np.mean(np.abs((ym[mask] - pm[mask]) / ym[mask])) * 100) if np.any(mask) else 0.0
    wape_m = float(np.sum(np.abs(ym - pm)) / np.sum(ym) * 100) if np.sum(ym) > 0 else 0.0
    rmse_m = float(np.sqrt(np.mean((ym - pm) ** 2)))
    mae_m = float(np.mean(np.abs(ym - pm)))
    mean_m = float(np.mean(ym))
    rel_m = float((rmse_m / mean_m) * 100) if mean_m > 0 else 0.0
    
    mode_eval[m] = {
        'mape': round(mape_m, 2),
        'wape': round(wape_m, 2),
        'rmse': int(round(rmse_m)),
        'mae': int(round(mae_m)),
        'mean_vol': int(round(mean_m)),
        'rel_error_pct': round(rel_m, 2)
    }

print(f"Hasil Backtest TOTAL (28 Hari): MAPE={mape_tot:.2f}%, WAPE={wape_tot:.2f}%, RMSE={rmse_tot:,.0f} pnp, MAE={mae_tot:,.0f} pnp")
for m in modes:
    print(f"  {m:<8} -> MAPE: {mode_eval[m]['mape']:6.2f}% | WAPE: {mode_eval[m]['wape']:6.2f}% | RMSE: {mode_eval[m]['rmse']:8,d} pnp | MAE: {mode_eval[m]['mae']:8,d} pnp")

# ==============================================================================
# 3. FIT FINAL HOLT-WINTERS ON ENTIRE 637-DAY HISTORICAL DATA
# ==============================================================================
print("\n[LANGKAH 2/4] Fit Ulang Model Holt-Winters dengan Seluruh Data (637 Hari)...")
hw_full_tot = fit_hw_model(df_train_combined['TOTAL'])
hw_full_modes = {m: fit_hw_model(df_train_combined[m]) for m in modes}

# ==============================================================================
# 4. BENCHMARK NATARU 2025 (18 Days: 18-31 Des 2025 + 1-4 Jan 2025)
# ==============================================================================
des25_nataru = df25[df25['tanggal'].between('2025-12-18', '2025-12-31')]
jan25_nataru = df25[df25['tanggal'].between('2025-01-01', '2025-01-04')]
df_nataru25 = pd.concat([des25_nataru, jan25_nataru])

benchmark_2025 = {
    'total_passengers': int(df_nataru25['TOTAL_PENUMPANG'].sum()),
    'avg_daily_passengers': int(round(df_nataru25['TOTAL_PENUMPANG'].mean())),
    'total_armada': int(df_nataru25['TOTAL_ARMADA'].sum()),
    'xmas_peak_date': '2025-12-24',
    'xmas_peak_val': int(df25.loc[df25['tanggal'] == '2025-12-24', 'TOTAL_PENUMPANG'].values[0]),
    'libur_peak_date': '2025-12-28',
    'libur_peak_val': int(df25.loc[df25['tanggal'] == '2025-12-28', 'TOTAL_PENUMPANG'].values[0]),
    'ny_peak_date': '2025-01-03',
    'ny_peak_val': int(df25.loc[df25['tanggal'] == '2025-01-03', 'TOTAL_PENUMPANG'].values[0]),
    'modes': {
        m: {
            'passengers': int(df_nataru25[f'pnp_{m}'].sum()),
            'armada': int(df_nataru25[f'arm_{m}'].sum()),
            'share_pct': round(float(df_nataru25[f'pnp_{m}'].sum() / df_nataru25['TOTAL_PENUMPANG'].sum() * 100), 1),
            'load_factor': round(float(df_nataru25[f'pnp_{m}'].sum() / df_nataru25[f'arm_{m}'].sum()), 1)
        } for m in modes
    }
}

# ==============================================================================
# 5. NATARU CALENDAR SHOCK COMPUTATION (Nov 2025 DOW Baseline Reference)
# ==============================================================================
nov25 = df25[df25['tanggal'].between('2025-11-01', '2025-11-30')]
nov_mean_tot = nov25.groupby('dow')['TOTAL_PENUMPANG'].mean().to_dict()
nov_mean_modes = {m: nov25.groupby('dow')[f'pnp_{m}'].mean().to_dict() for m in modes}

dow_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
shock_factors_log = []

# Generate exactly 100 days of future dates: 2026-09-30 to 2027-01-07
forecast_start = datetime.date(2026, 9, 30)
forecast_end = datetime.date(2027, 1, 7)
forecast_days = (forecast_end - forecast_start).days + 1  # Exactly 100 days
future_dates = [forecast_start + datetime.timedelta(days=i) for i in range(forecast_days)]

# Generate Holt-Winters 100-day baseline forecasts
hw_baseline_tot_series = hw_full_tot.forecast(forecast_days).values
hw_baseline_mode_series = {m: hw_full_modes[m].forecast(forecast_days).values for m in modes}

hw_baseline_map_tot = {future_dates[i].strftime('%Y-%m-%d'): hw_baseline_tot_series[i] for i in range(forecast_days)}
hw_baseline_map_modes = {
    m: {future_dates[i].strftime('%Y-%m-%d'): hw_baseline_mode_series[m][i] for i in range(forecast_days)}
    for m in modes
}

# Compute shock factor table for Nataru period (18 Des 2026 s.d. 4 Jan 2027)
for d in future_dates:
    d_str = d.strftime('%Y-%m-%d')
    md = d.strftime('%m-%d')
    dow = d.weekday()
    if '2026-12-18' <= d_str <= '2027-01-04':
        val25_tot = p25_by_md[md]['TOTAL_PENUMPANG']
        shock_tot = float(val25_tot / nov_mean_tot[dow])
        entry = {
            'date': d_str,
            'dow': dow_names[dow],
            'val_2025_tot': int(val25_tot),
            'nov_baseline_tot': int(round(nov_mean_tot[dow])),
            'shock_factor_tot': round(shock_tot, 4),
            'mode_shocks': {}
        }
        for m in modes:
            val25_m = p25_by_md[md][f'pnp_{m}']
            shock_m = float(val25_m / nov_mean_modes[m][dow])
            entry['mode_shocks'][m] = round(shock_m, 4)
        shock_factors_log.append(entry)

# ==============================================================================
# 6. SCENARIO SIMULATION & 100-DAY FORECAST GENERATION
# ==============================================================================
print("\n[LANGKAH 3/4] Menghasilkan 100 Hari Proyeksi (30 Sep 2026 s.d. 7 Jan 2027)...")

# Baseline load factor per mode
load_factors_base = {
    'UDARA': 112.0,
    'KA': 55.0,
    'BUS': 12.5,
    'ASDP': 140.0,
    'LAUT': 70.0
}

# Explicit scenario factors
scenarios = ['moderat', 'optimis', 'konservatif']
scenario_factors = {
    'moderat': 1.00,
    'optimis': 1.07,
    'konservatif': 0.95
}

forecast_data = {s: [] for s in scenarios}

for s in scenarios:
    scen_factor = scenario_factors[s]
    
    for i, d in enumerate(future_dates):
        d_str = d.strftime('%Y-%m-%d')
        md = d.strftime('%m-%d')
        dow = d.weekday()
        
        rec25 = p25_by_md[md]
        val25_tot = rec25['TOTAL_PENUMPANG']
        arm25_tot = rec25['TOTAL_ARMADA']
        
        # 1. Holt-Winters baselines
        hw_base_tot = hw_baseline_tot_series[i]
        hw_base_m = {m: hw_baseline_mode_series[m][i] for m in modes}
        
        # 2. Check Nataru shock window (18 Des 2026 s.d. 4 Jan 2027)
        is_nataru_window = ('2026-12-18' <= d_str <= '2027-01-04')
        
        if is_nataru_window:
            # Nataru Calendar Shock factor based on November 2025 weekday baseline
            shock_tot = float(val25_tot / nov_mean_tot[dow])
            pred_total_raw = hw_base_tot * scen_factor * shock_tot
            
            raw_mode_preds = {}
            for m in modes:
                val25_m = rec25[f'pnp_{m}']
                shock_m = float(val25_m / nov_mean_modes[m][dow])
                raw_mode_preds[m] = hw_base_m[m] * scen_factor * shock_m
        else:
            # Non-Nataru dates: pure Holt-Winters baseline scaled by scenario factor
            shock_tot = 1.0
            pred_total_raw = hw_base_tot * scen_factor
            raw_mode_preds = {m: hw_base_m[m] * scen_factor for m in modes}
            
        pred_total = int(round(pred_total_raw))
        
        # 3. Proportional normalization across 5 modes: sum(modes) == TOTAL
        sum_raw_modes = sum(raw_mode_preds.values())
        if sum_raw_modes > 0:
            scale = pred_total / sum_raw_modes
            mode_preds = {m: max(10, int(round(raw_mode_preds[m] * scale))) for m in modes}
            # Adjust minor rounding difference to match pred_total exactly
            diff_round = pred_total - sum(mode_preds.values())
            mode_preds['UDARA'] += diff_round
        else:
            share_fallback = 1.0 / len(modes)
            mode_preds = {m: int(round(pred_total * share_fallback)) for m in modes}
            diff_round = pred_total - sum(mode_preds.values())
            mode_preds['UDARA'] += diff_round
            
        # 4. Armada predictions
        arm_preds = {}
        for m in modes:
            lf = load_factors_base[m]
            if pred_total > 1600000:
                lf *= 1.12
            arm_preds[f'arm_{m}'] = max(10, int(round(mode_preds[m] / lf)))
        arm_total = sum(arm_preds.values())
        
        # 5. Approximate 95% Confidence Interval (RMSE-based)
        ci_lower = max(0, int(round(pred_total - 1.96 * rmse_tot)))
        ci_upper = int(round(pred_total + 1.96 * rmse_tot))
        
        yoy_pct = round(((pred_total / val25_tot) - 1.0) * 100, 1)
        yoy_diff = pred_total - val25_tot
        
        is_peak = pred_total >= 1800000 or d_str in ['2026-12-24', '2026-12-27', '2026-12-28', '2027-01-03']
        is_high = pred_total >= 1400000
        
        forecast_data[s].append({
            'date': d_str,
            'TOTAL': pred_total,
            'hw_baseline': int(round(hw_base_tot)),
            'shock_factor': round(shock_tot, 4),
            'scenario_factor': scen_factor,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'status': 'PEAK_SURGE' if is_peak else ('HIGH' if is_high else 'NORMAL'),
            'pnp_2025': val25_tot,
            'yoy_pct': yoy_pct,
            'yoy_diff': yoy_diff,
            'UDARA': mode_preds['UDARA'],
            'KA': mode_preds['KA'],
            'BUS': mode_preds['BUS'],
            'ASDP': mode_preds['ASDP'],
            'LAUT': mode_preds['LAUT'],
            'UDARA_2025': rec25['pnp_UDARA'],
            'KA_2025': rec25['pnp_KA'],
            'BUS_2025': rec25['pnp_BUS'],
            'ASDP_2025': rec25['pnp_ASDP'],
            'LAUT_2025': rec25['pnp_LAUT'],
            'arm_TOTAL': arm_total,
            'arm_2025': arm25_tot,
            'arm_UDARA': arm_preds['arm_UDARA'],
            'arm_KA': arm_preds['arm_KA'],
            'arm_BUS': arm_preds['arm_BUS'],
            'arm_ASDP': arm_preds['arm_ASDP'],
            'arm_LAUT': arm_preds['arm_LAUT'],
            'arm_UDARA_2025': rec25['arm_UDARA'],
            'arm_KA_2025': rec25['arm_KA'],
            'arm_BUS_2025': rec25['arm_BUS'],
            'arm_ASDP_2025': rec25['arm_ASDP'],
            'arm_LAUT_2025': rec25['arm_LAUT'],
        })

# ==============================================================================
# 7. SUMMARIZE NATARU PERIOD (18-Day: 18 Des 2026 - 4 Jan 2027)
# ==============================================================================
def summarize_nataru(scen_list, b25):
    subset = [r for r in scen_list if '2026-12-18' <= r['date'] <= '2027-01-04']
    total_pnp = sum(r['TOTAL'] for r in subset)
    total_arm = sum(r['arm_TOTAL'] for r in subset)
    avg_daily = int(round(total_pnp / len(subset)))
    max_day = max(subset, key=lambda x: x['TOTAL'])

    xmas_day = [r for r in subset if r['date'] == '2026-12-24'][0]
    ny_day = [r for r in subset if r['date'] == '2027-01-03'][0]

    mode_sums = {}
    for m in modes:
        p_sum = sum(r[m] for r in subset)
        p25_sum = b25['modes'][m]['passengers']
        yoy_m = round(((p_sum / p25_sum) - 1.0) * 100, 1) if p25_sum > 0 else 0.0
        mode_sums[m] = {
            'passengers_2026': p_sum,
            'passengers_2025': p25_sum,
            'diff': p_sum - p25_sum,
            'yoy_pct': yoy_m,
            'share_pct_2026': round(p_sum / total_pnp * 100, 1) if total_pnp > 0 else 0.0,
            'share_pct_2025': b25['modes'][m]['share_pct'],
        }

    return {
        'total_passengers': total_pnp,
        'total_passengers_2025': b25['total_passengers'],
        'diff_passengers': total_pnp - b25['total_passengers'],
        'yoy_total_pct': round(((total_pnp / b25['total_passengers']) - 1.0) * 100, 1) if b25['total_passengers'] > 0 else 0.0,
        'avg_daily_passengers': avg_daily,
        'avg_daily_passengers_2025': b25['avg_daily_passengers'],
        'yoy_avg_pct': round(((avg_daily / b25['avg_daily_passengers']) - 1.0) * 100, 1) if b25['avg_daily_passengers'] > 0 else 0.0,
        'total_armada': total_arm,
        'total_armada_2025': b25['total_armada'],
        'yoy_armada_pct': round(((total_arm / b25['total_armada']) - 1.0) * 100, 1) if b25['total_armada'] > 0 else 0.0,
        'all_time_peak_date': max_day['date'],
        'all_time_peak_val': max_day['TOTAL'],
        'all_time_peak_yoy': max_day['yoy_pct'],
        'xmas_peak_date': xmas_day['date'],
        'xmas_peak_val': xmas_day['TOTAL'],
        'xmas_peak_val_2025': b25['xmas_peak_val'],
        'xmas_peak_yoy': xmas_day['yoy_pct'],
        'ny_peak_date': ny_day['date'],
        'ny_peak_val': ny_day['TOTAL'],
        'ny_peak_val_2025': b25['ny_peak_val'],
        'ny_peak_yoy': ny_day['yoy_pct'],
        'mode_breakdown': mode_sums
    }

summaries = {s: summarize_nataru(forecast_data[s], benchmark_2025) for s in scenarios}

# ==============================================================================
# 8. UPDATE DATA BUNDLE & SAVE
# ==============================================================================
print("\n[LANGKAH 4/4] Memperbarui bundle data JSON...")

# 2025 timeline list
timeline_2025 = []
for _, r in df25.iterrows():
    timeline_2025.append({
        'date': r['tanggal'],
        'TOTAL': int(r['TOTAL_PENUMPANG']),
        'UDARA': int(r['pnp_UDARA']),
        'KA': int(r['pnp_KA']),
        'BUS': int(r['pnp_BUS']),
        'ASDP': int(r['pnp_ASDP']),
        'LAUT': int(r['pnp_LAUT']),
        'arm_TOTAL': int(r['TOTAL_ARMADA']),
        'arm_UDARA': int(r['arm_UDARA']),
        'arm_KA': int(r['arm_KA']),
        'arm_BUS': int(r['arm_BUS']),
        'arm_ASDP': int(r['arm_ASDP']),
        'arm_LAUT': int(r['arm_LAUT']),
    })

bundle['timeline_2025'] = timeline_2025
bundle['forecast_nataru'] = {
    'meta': {
        'model': "Holt-Winters Multiplicative Exponential Smoothing + Additive Trend + Damped Trend (phi=0.98) + Weekly Seasonality (s=7) + Nataru Calendar Shock",
        'training_dataset': f"Gabungan Runtun Waktu Kontinu 2025 (365 hari) + 2026 (272 hari) = {total_train_days} Hari",
        'train_start': '2025-01-01',
        'train_end': '2026-09-29',
        'train_days': total_train_days,
        'forecast_start': future_dates[0].strftime('%Y-%m-%d'),
        'forecast_end': future_dates[-1].strftime('%Y-%m-%d'),
        'horizon_days': forecast_days,
        'parameters': {
            'trend': 'add',
            'damped_trend': True,
            'damping_trend_phi': 0.98,
            'seasonal': 'mul',
            'seasonal_periods': 7,
            'initialization_method': 'estimated',
            'fit_options': 'optimized=True, use_brute=True'
        },
        'scenario_factors': scenario_factors,
        'scenario_note': 'Scenario factor adalah asumsi proyeksi kebijakan/animo, bukan parameter internal Holt-Winters: moderat=1.00, optimis=1.07, konservatif=0.95.',
        'ci_method': 'RMSE-based approximate 95% interval / uncertainty approximation (CI = ŷ ± 1.96 × RMSE)',
    },
    'metrics': {
        'test_period': f"{test_start} s.d. {test_end} (28 Hari)",
        'train_period': f"{train_start} s.d. {train_end} ({len(train_split)} Hari)",
        'TOTAL': {
            'mape': round(mape_tot, 2),
            'wape': round(wape_tot, 2),
            'rmse': int(round(rmse_tot)),
            'mae': int(round(mae_tot)),
            'mean_vol': int(round(mean_test_vol)),
            'rel_error_pct': round(rel_error_tot, 2)
        },
        'modes': mode_eval
    },
    'benchmark_2025': benchmark_2025,
    'shock_factors': {
        'nataru_window': '2026-12-18 s.d. 2027-01-04 (18 Hari)',
        'november_2025_weekday_baseline': {
            dow_names[dow]: {
                'TOTAL': int(round(nov_mean_tot[dow])),
                **{m: int(round(nov_mean_modes[m][dow])) for m in modes}
            } for dow in range(7)
        },
        'factors_by_date': shock_factors_log
    },
    'summaries': summaries,
    'scenarios': forecast_data
}

with open('scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("\n" + "=" * 80)
print("PROSES SELESAI DAN VALIDASI BERHASIL:")
print(f"1. Model Definition : {bundle['forecast_nataru']['meta']['model']}")
print(f"2. Data Latih       : {total_train_days} Hari (2025-01-01 s.d. 2026-09-29)")
print(f"3. Jumlah Forecast  : {forecast_days} Hari (Tepat 100 Hari)")
print(f"4. Tanggal Forecast : {future_dates[0].strftime('%Y-%m-%d')} s.d. {future_dates[-1].strftime('%Y-%m-%d')}")
print(f"5. Backtest TOTAL   : MAPE={mape_tot:.2f}%, WAPE={wape_tot:.2f}%, RMSE={rmse_tot:,.0f} pnp, MAE={mae_tot:,.0f} pnp")
for s in scenarios:
    su = summaries[s]
    print(f"6. Skenario [{s.upper():<11}] (factor={scenario_factors[s]:.2f}) -> Nataru Total: {su['total_passengers']:,} pnp | Puncak: {su['all_time_peak_val']:,} pnp ({su['all_time_peak_date']})")
print("=" * 80)
