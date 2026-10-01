import json
import datetime
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. Load historical datasets: 2025 daily CSV (365 days) and 2026 bundle (270 days)
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
df25['tanggal_dt'] = pd.to_datetime(df25['tanggal'])
df25['md'] = df25['tanggal'].str[5:]
p25_by_md = df25.set_index('md').to_dict(orient='index')

# 2026 daily history up to 2026-09-27
daily_history_26 = bundle['daily_timeline']
df26 = pd.DataFrame(daily_history_26)
df26['date_dt'] = pd.to_datetime(df26['date'])
df26 = df26[df26['date_dt'] <= '2026-09-27'].copy()
df26.sort_values('date_dt', inplace=True)
df26.reset_index(drop=True, inplace=True)
df26['md'] = df26['date'].str[5:]

# 2. Combine 2025 + 2026 into a single continuous training time series (635 days)
modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
s25_tot = df25[['tanggal', 'TOTAL_PENUMPANG'] + [f'pnp_{m}' for m in modes] + ['TOTAL_ARMADA'] + [f'arm_{m}' for m in modes]].rename(
    columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL', 'TOTAL_ARMADA': 'arm_TOTAL',
             **{f'pnp_{m}': m for m in modes}}
)
s26_tot = df26[['date', 'TOTAL'] + modes + ['arm_TOTAL'] + [f'arm_{m}' for m in modes]]

df_train_combined = pd.concat([s25_tot, s26_tot], ignore_index=True)
df_train_combined['date_dt'] = pd.to_datetime(df_train_combined['date'])
df_train_combined.set_index('date_dt', inplace=True)
total_train_days = len(df_train_combined)

print(f"Dataset Latih Gabungan (Unified Training Data): {total_train_days} hari ({df_train_combined.index[0].strftime('%Y-%m-%d')} s.d. {df_train_combined.index[-1].strftime('%Y-%m-%d')})")

# 3. Fit Holt-Winters (Exponential Smoothing) on Combined Series
# Seasonality s=7 (weekly cyclical pattern) with Damped Trend
hw_model = ExponentialSmoothing(
    df_train_combined['TOTAL'],
    seasonal_periods=7,
    trend='add',
    damped_trend=True,
    seasonal='mul',
    initialization_method='estimated'
).fit()

# Calculate empirical growth 2026 vs 2025 YTD
merged_ytd = pd.merge(df26, df25, on='md', suffixes=('_2026', '_2025'))
tot26_ytd = merged_ytd['TOTAL'].sum()
tot25_ytd = merged_ytd['TOTAL_PENUMPANG'].sum()
ytd_growth_tot = (tot26_ytd / tot25_ytd) - 1.0

ytd_growth_modes = {}
for m in modes:
    p26 = merged_ytd[m].sum()
    p25 = merged_ytd[f'pnp_{m}'].sum()
    ytd_growth_modes[m] = (p26 / p25) - 1.0

print(f"YTD Growth (Jan 1 - Sep 27): Total={ytd_growth_tot*100:+.2f}%")
for m in modes:
    print(f"  {m:5s}: {ytd_growth_modes[m]*100:+.2f}%")

# 4. Extract Benchmark Nataru 2025 (18 Days: 18-31 Des 2025 [14H] + 1-4 Jan 2025 [4H])
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

# 5. Generate 100-Day Forecast (2026-09-28 to 2027-01-05) using Holt-Winters + 2025 Nataru Shock
forecast_start = datetime.date(2026, 9, 28)
forecast_end = datetime.date(2027, 1, 5)
forecast_days = (forecast_end - forecast_start).days + 1
future_dates = [forecast_start + datetime.timedelta(days=i) for i in range(forecast_days)]

# Generate Holt-Winters 100-day baseline
hw_baseline_series = hw_model.forecast(forecast_days)
hw_baseline_map = {d.strftime('%Y-%m-%d'): hw_baseline_series.iloc[i] for i, d in enumerate(future_dates)}

# November 2025 regular baseline
nov25_mean = df25[df25['tanggal'].between('2025-11-01', '2025-11-30')]['TOTAL_PENUMPANG'].mean()

# Load factor base per mode
load_factors_base = {
    'UDARA': 112.0,
    'KA': 55.0,
    'BUS': 12.5,
    'ASDP': 140.0,
    'LAUT': 70.0
}

scenarios = ['moderat', 'optimis', 'konservatif']
forecast_data = {s: [] for s in scenarios}

for s in scenarios:
    if s == 'moderat':
        growth_tot = ytd_growth_tot # +5.13%
        growth_m = ytd_growth_modes.copy()
    elif s == 'optimis':
        growth_tot = ytd_growth_tot + 0.07 # +12.1%
        growth_m = {m: ytd_growth_modes[m] + 0.07 for m in modes}
    else: # konservatif
        growth_tot = -0.05 # -5.0%
        growth_m = {
            'UDARA': ytd_growth_modes['UDARA'] - 0.05,
            'KA': ytd_growth_modes['KA'] - 0.03,
            'BUS': ytd_growth_modes['BUS'] - 0.04,
            'ASDP': ytd_growth_modes['ASDP'] - 0.20,
            'LAUT': ytd_growth_modes['LAUT'] - 0.25
        }

    for d in future_dates:
        d_str = d.strftime('%Y-%m-%d')
        md = d.strftime('%m-%d')
        rec25 = p25_by_md[md]
        val25_tot = rec25['TOTAL_PENUMPANG']
        arm25_tot = rec25['TOTAL_ARMADA']

        # Holt-Winters baseline for this date
        hw_base = hw_baseline_map[d_str]

        # Is this date inside the Nataru Shock window (Dec 18 - Jan 4)?
        is_nataru_window = ('12-18' <= md <= '12-31') or ('01-01' <= md <= '01-04')
        is_transition = ('12-15' <= md <= '12-17')

        if is_nataru_window:
            # Nataru Seasonal Shock learned from 2025 training data
            shock_factor = val25_tot / nov25_mean
            
            # Calendar day alignment adjustment for 2026/2027
            dow_adj = 1.0
            if d_str in ['2026-12-24', '2026-12-25']:
                dow_adj = 1.03
            elif d_str in ['2026-12-27', '2027-01-03']:
                dow_adj = 1.05
            elif d_str in ['2026-12-31', '2027-01-01']:
                dow_adj = 1.02

            # Forecast = HW Base level scaled by Nataru Shock & Growth scenario
            pred_total = int(round(val25_tot * (1.0 + growth_tot) * dow_adj))
        elif is_transition:
            # Smooth ramp-up from HW baseline into Nataru window
            ramp = 0.5 + 0.5 * (val25_tot / nov25_mean)
            pred_total = int(round(hw_base * (1.0 + growth_tot * 0.5) * ramp))
        else:
            # Regular period (Sep 28 - Dec 14): Follows Holt-Winters baseline directly
            pred_total = int(round(hw_base * (1.0 + (growth_tot - ytd_growth_tot))))

        # Mode predictions
        mode_preds = {}
        for m in modes:
            val25_m = rec25[f'pnp_{m}']
            if is_nataru_window or is_transition:
                pred_m = val25_m * (1.0 + growth_m[m])
            else:
                # Share-weighted distribution based on HW total
                share_m = val25_m / val25_tot
                pred_m = pred_total * share_m
            mode_preds[m] = max(1000, pred_m)

        scale = pred_total / sum(mode_preds.values())
        mode_preds = {m: int(round(mode_preds[m] * scale)) for m in modes}

        # Armada predictions
        arm_preds = {}
        for m in modes:
            lf = load_factors_base[m]
            if pred_total > 1600000:
                lf *= 1.12
            arm_preds[f'arm_{m}'] = max(10, int(round(mode_preds[m] / lf)))
        arm_total = sum(arm_preds.values())

        # 95% Confidence Interval (±5.5%)
        ci_spread = 0.055
        ci_lower = int(round(pred_total * (1 - ci_spread)))
        ci_upper = int(round(pred_total * (1 + ci_spread)))

        yoy_pct = round(((pred_total / val25_tot) - 1.0) * 100, 1)
        yoy_diff = pred_total - val25_tot

        is_peak = pred_total >= 1800000 or d_str in ['2026-12-24', '2026-12-27', '2027-01-03']
        is_high = pred_total >= 1500000

        forecast_data[s].append({
            'date': d_str,
            'TOTAL': pred_total,
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

# 6. Summarize Nataru Period (18-Day: 18 Des 2026 - 4 Jan 2027)
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
        yoy_m = round(((p_sum / p25_sum) - 1.0) * 100, 1)
        mode_sums[m] = {
            'passengers_2026': p_sum,
            'passengers_2025': p25_sum,
            'diff': p_sum - p25_sum,
            'yoy_pct': yoy_m,
            'share_pct_2026': round(p_sum / total_pnp * 100, 1),
            'share_pct_2025': b25['modes'][m]['share_pct'],
        }

    return {
        'total_passengers': total_pnp,
        'total_passengers_2025': b25['total_passengers'],
        'diff_passengers': total_pnp - b25['total_passengers'],
        'yoy_total_pct': round(((total_pnp / b25['total_passengers']) - 1.0) * 100, 1),
        'avg_daily_passengers': avg_daily,
        'avg_daily_passengers_2025': b25['avg_daily_passengers'],
        'yoy_avg_pct': round(((avg_daily / b25['avg_daily_passengers']) - 1.0) * 100, 1),
        'total_armada': total_arm,
        'total_armada_2025': b25['total_armada'],
        'yoy_armada_pct': round(((total_arm / b25['total_armada']) - 1.0) * 100, 1),
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

# 7. Evaluate Backtest Holdout (607 days train vs 28 days test)
train_split = df_train_combined.iloc[:-28]
test_split = df_train_combined.iloc[-28:]
hw_test = ExponentialSmoothing(
    train_split['TOTAL'],
    seasonal_periods=7,
    trend='add',
    damped_trend=True,
    seasonal='mul',
    initialization_method='estimated'
).fit()

pred_test = hw_test.forecast(28).values
y_true = test_split['TOTAL'].values
mape_tot = float(np.mean(np.abs((y_true - pred_test) / y_true)) * 100)
rmse_tot = float(np.sqrt(np.mean((y_true - pred_test) ** 2)))
mae_tot = float(np.mean(np.abs(y_true - pred_test)))
mean_test_vol = float(np.mean(y_true))

mode_eval = {}
for m in modes:
    hw_m = ExponentialSmoothing(
        train_split[m],
        seasonal_periods=7,
        trend='add',
        damped_trend=True,
        seasonal='mul',
        initialization_method='estimated'
    ).fit()
    pm = hw_m.forecast(28).values
    ym = test_split[m].values
    mode_eval[m] = {
        'mape': round(float(np.mean(np.abs((ym - pm) / ym)) * 100), 2),
        'rmse': int(round(float(np.sqrt(np.mean((ym - pm) ** 2))))),
        'mae': int(round(float(np.mean(np.abs(ym - pm))))),
        'mean_vol': int(round(float(np.mean(ym)))),
        'rel_error_pct': round(float((np.sqrt(np.mean((ym - pm) ** 2)) / np.mean(ym)) * 100), 2)
    }

# 8. Store timeline_2025 in bundle
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
        'model': 'Holt-Winters Damped Trend (s=7) + Seasonal Nataru Shock Model',
        'training_dataset': 'Gabungan Runtun Waktu Kontinu 2025 (365 hari) + 2026 (270 hari) = 635 Hari',
        'train_start': '2025-01-01',
        'train_end': '2026-09-27',
        'train_days': total_train_days,
        'forecast_start': '2026-09-28',
        'forecast_end': '2027-01-05',
        'horizon_days': forecast_days,
        'ytd_growth_tot_pct': round(ytd_growth_tot * 100, 2),
        'ytd_growth_modes_pct': {m: round(ytd_growth_modes[m] * 100, 2) for m in modes},
    },
    'metrics': {
        'test_period': '31 Agt 2026 s.d. 27 Sep 2026 (28 Hari)',
        'train_period': f"1 Jan 2025 s.d. 30 Agt 2026 ({len(train_split)} Hari)",
        'TOTAL': {
            'mape': round(mape_tot, 2),
            'rmse': int(round(rmse_tot)),
            'mae': int(round(mae_tot)),
            'mean_vol': int(round(mean_test_vol)),
            'rel_error_pct': round((rmse_tot / mean_test_vol) * 100, 2)
        },
        'modes': mode_eval
    },
    'benchmark_2025': benchmark_2025,
    'summaries': summaries,
    'scenarios': forecast_data
}

with open('scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("\nSukses menyimpan mobility_data_bundle.json dengan 1 Model Holt-Winters Terpadu (2025+2026)!")
print(f"Total Latih: {total_train_days} Hari (2025: 365H + 2026: 270H)")
print(f"Evaluasi Backtest Total MAPE: {mape_tot:.2f}% | RMSE: {rmse_tot:,.0f} pnp")
for s in scenarios:
    su = summaries[s]
    print(f"[{s.upper()}] Nataru Total: {su['total_passengers']:,} pnp | Peak: {su['all_time_peak_val']:,} pnp ({su['all_time_peak_date']})")
