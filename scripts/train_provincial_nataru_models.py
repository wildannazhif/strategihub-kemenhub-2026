import json
import datetime
import numpy as np
import pandas as pd
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings('ignore')

print("=" * 80)
print("TRAINING SISTEM FORECASTING NATARU 2026/2027 PER PROVINSI (38 PROVINSI)")
print("Model: Holt-Winters Multiplicative Exponential Smoothing + Additive Trend")
print("       + Damped Trend (phi=0.98) + Weekly Seasonality (s=7) + Nataru Calendar Shock")
print("=" * 80)

# 1. LOAD DATASETS
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
df25['tanggal_dt'] = pd.to_datetime(df25['tanggal'])
df25['dow'] = df25['tanggal_dt'].dt.dayofweek
df25['md'] = df25['tanggal'].str[5:]
dates_25 = sorted(df25['tanggal'].unique())

df26 = pd.read_csv('siasati_multimoda_2026.csv', low_memory=False)
df26['provinsi'] = df26['provinsi'].replace({'D.I. Yogyakarta': 'D.I Yogyakarta', 'SULAWESI SELATAN': 'Sulawesi Selatan'})
df26['tanggal_dt'] = pd.to_datetime(df26['tanggal'])
df26 = df26[df26['tanggal_dt'] <= '2026-09-29'].copy()
dates_26 = sorted(df26['tanggal'].unique())

modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
std_provinces = sorted(bundle['province_monthly_data']['pnp_tot']['provinces'])

print(f"Total Provinsi Terdaftar : {len(std_provinces)}")
print(f"Data Historis 2025       : {len(dates_25)} hari ({dates_25[0]} s.d. {dates_25[-1]})")
print(f"Data Historis 2026       : {len(dates_26)} hari ({dates_26[0]} s.d. {dates_26[-1]})")
print(f"Total Hari Pelatihan     : {len(dates_25) + len(dates_26)} hari (1 Jan 2025 - 29 Sep 2026)")
print("=" * 80)

# Calculate modal share for each province in 2026
prov_pnp_mode = df26.groupby(['provinsi', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
nat_pnp_mode = df26.groupby('moda')['total_penumpang'].sum()
share_pnp = prov_pnp_mode.div(nat_pnp_mode, axis=1).fillna(0)

prov_arm_mode = df26.groupby(['provinsi', 'moda'])['total_armada'].sum().unstack(fill_value=0)
nat_arm_mode = df26.groupby('moda')['total_armada'].sum()
share_arm = prov_arm_mode.div(nat_arm_mode, axis=1).fillna(0)

def fit_hw_robust(series):
    s = series.astype(float).clip(lower=1.0)
    try:
        model = ExponentialSmoothing(
            s,
            trend='add',
            damped_trend=True,
            seasonal='mul',
            seasonal_periods=7,
            initialization_method='estimated'
        ).fit(damping_trend=0.98, optimized=True, use_brute=False)
        return model
    except Exception:
        pass
    try:
        model = ExponentialSmoothing(
            s,
            trend='add',
            damped_trend=True,
            seasonal='add',
            seasonal_periods=7,
            initialization_method='estimated'
        ).fit(damping_trend=0.98, optimized=True, use_brute=False)
        return model
    except Exception:
        return ExponentialSmoothing(
            s,
            trend='add',
            damped_trend=True,
            initialization_method='estimated'
        ).fit(damping_trend=0.98, optimized=True, use_brute=False)

# Dates for 100-day forecast: 2026-09-30 to 2027-01-07
forecast_start = datetime.date(2026, 9, 30)
forecast_end = datetime.date(2027, 1, 7)
forecast_days = (forecast_end - forecast_start).days + 1
future_dates = [forecast_start + datetime.timedelta(days=i) for i in range(forecast_days)]

scenarios = ['moderat', 'optimis', 'konservatif']
scenario_factors = {'moderat': 1.00, 'optimis': 1.07, 'konservatif': 0.95}

load_factors_base = {
    'UDARA': 112.0,
    'KA': 55.0,
    'BUS': 12.5,
    'ASDP': 140.0,
    'LAUT': 70.0
}

by_province_data = {}

for p_idx, prov in enumerate(std_provinces):
    # 1. Actual 2026 daily data for this province
    sub26 = df26[df26['provinsi'] == prov]
    p26_pvt = sub26.pivot_table(index='tanggal', columns='moda', values='total_penumpang', aggfunc='sum', fill_value=0).reindex(index=dates_26, columns=modes, fill_value=0)
    a26_pvt = sub26.pivot_table(index='tanggal', columns='moda', values='total_armada', aggfunc='sum', fill_value=0).reindex(index=dates_26, columns=modes, fill_value=0)
    p26_pvt['TOTAL'] = p26_pvt[modes].sum(axis=1)
    a26_pvt['arm_TOTAL'] = a26_pvt[modes].sum(axis=1)

    # 2. Reconstructed 2025 daily series for this province
    sh_pnp_prov = share_pnp.loc[prov] if prov in share_pnp.index else pd.Series(0.0, index=modes)
    sh_arm_prov = share_arm.loc[prov] if prov in share_arm.index else pd.Series(0.0, index=modes)

    p25_df = pd.DataFrame({'date': df25['tanggal'], 'dow': df25['dow'], 'md': df25['md']})
    p25_df.set_index('date', inplace=True)
    for m in modes:
        p25_df[m] = (df25.set_index('tanggal')[f'pnp_{m}'] * sh_pnp_prov.get(m, 0.0)).round().astype(int)
        p25_df[f'arm_{m}'] = (df25.set_index('tanggal')[f'arm_{m}'] * sh_arm_prov.get(m, 0.0)).round().astype(int)
    p25_df['TOTAL'] = p25_df[modes].sum(axis=1)
    p25_df['arm_TOTAL'] = p25_df[[f'arm_{m}' for m in modes]].sum(axis=1)

    # Combine 2025 (365d) + 2026 (272d) = 637 days
    s_tot_comb = pd.concat([p25_df['TOTAL'], p26_pvt['TOTAL']])
    s_tot_comb.index = pd.to_datetime(s_tot_comb.index)
    s_tot_comb.index.freq = 'D'

    # 3. Backtest 28-Day Temporal Holdout (2 Sep - 29 Sep 2026)
    train_split = s_tot_comb.iloc[:-28]
    test_split = s_tot_comb.iloc[-28:]
    y_test = test_split.values

    hw_test = fit_hw_robust(train_split)
    pred_test = np.maximum(0, hw_test.forecast(28).values)

    mask = y_test > 0
    mape = float(np.mean(np.abs((y_test[mask] - pred_test[mask]) / y_test[mask])) * 100) if np.any(mask) else 0.0
    wape = float(np.sum(np.abs(y_test - pred_test)) / np.sum(y_test) * 100) if np.sum(y_test) > 0 else 0.0
    rmse = float(np.sqrt(np.mean((y_test - pred_test) ** 2)))
    mae = float(np.mean(np.abs(y_test - pred_test)))
    mean_vol = float(np.mean(y_test))
    rel_err = float((rmse / mean_vol) * 100) if mean_vol > 0 else 0.0

    # 4. Fit Full Holt-Winters on entire 637 days
    hw_full_tot = fit_hw_robust(s_tot_comb)
    hw_base_tot_100 = np.maximum(0, hw_full_tot.forecast(forecast_days).values)

    hw_full_modes = {}
    hw_base_mode_100 = {}
    for m in modes:
        s_m_comb = pd.concat([p25_df[m], p26_pvt[m]])
        s_m_comb.index = pd.to_datetime(s_m_comb.index)
        s_m_comb.index.freq = 'D'
        if s_m_comb.sum() > 0:
            hw_m = fit_hw_robust(s_m_comb)
            hw_full_modes[m] = hw_m
            hw_base_mode_100[m] = np.maximum(0, hw_m.forecast(forecast_days).values)
        else:
            hw_full_modes[m] = None
            hw_base_mode_100[m] = np.zeros(forecast_days)

    # 5. Benchmark Nataru 2025 (18 Days: 18-31 Des 2025 + 1-4 Jan 2025)
    des25_nat = p25_df.loc[p25_df.index.to_series().between('2025-12-18', '2025-12-31')]
    jan25_nat = p25_df.loc[p25_df.index.to_series().between('2025-01-01', '2025-01-04')]
    df_nat25 = pd.concat([des25_nat, jan25_nat])

    nat25_tot = int(df_nat25['TOTAL'].sum())
    nat25_avg = int(round(df_nat25['TOTAL'].mean())) if len(df_nat25) > 0 else 0
    nat25_arm = int(df_nat25['arm_TOTAL'].sum())

    xmas25_val = int(p25_df.loc['2025-12-24', 'TOTAL']) if '2025-12-24' in p25_df.index else 0
    ny25_val = int(p25_df.loc['2025-01-03', 'TOTAL']) if '2025-01-03' in p25_df.index else 0

    benchmark_2025_prov = {
        'total_passengers': nat25_tot,
        'avg_daily_passengers': nat25_avg,
        'total_armada': nat25_arm,
        'xmas_peak_val': xmas25_val,
        'ny_peak_val': ny25_val,
        'modes': {
            m: {
                'passengers': int(df_nat25[m].sum()),
                'armada': int(df_nat25[f'arm_{m}'].sum()),
                'share_pct': round(float(df_nat25[m].sum() / nat25_tot * 100), 1) if nat25_tot > 0 else 0.0,
            } for m in modes
        }
    }

    # 6. Nataru Calendar Shock computation
    nov25_prov = p25_df.loc[p25_df.index.to_series().between('2025-11-01', '2025-11-30')]
    nov_mean_tot = nov25_prov.groupby('dow')['TOTAL'].mean().to_dict()
    nov_mean_modes = {m: nov25_prov.groupby('dow')[m].mean().to_dict() for m in modes}
    p25_by_md = p25_df.set_index('md').to_dict(orient='index')

    # 7. Generate 100-day forecast for 3 scenarios
    prov_fc_scenarios = {s: [] for s in scenarios}

    for s in scenarios:
        scen_factor = scenario_factors[s]
        for i, d in enumerate(future_dates):
            d_str = d.strftime('%Y-%m-%d')
            md = d.strftime('%m-%d')
            dow = d.weekday()

            rec25 = p25_by_md.get(md, {'TOTAL': 1, 'arm_TOTAL': 1, **{m: 0 for m in modes}, **{f'arm_{m}': 0 for m in modes}})
            val25_tot = max(1, rec25['TOTAL'])
            arm25_tot = max(1, rec25['arm_TOTAL'])

            hw_base_tot = hw_base_tot_100[i]
            hw_base_m = {m: hw_base_mode_100[m][i] for m in modes}

            is_nataru_window = ('2026-12-18' <= d_str <= '2027-01-04')
            if is_nataru_window:
                base_ref = max(1.0, nov_mean_tot.get(dow, 1.0))
                shock_tot = float(val25_tot / base_ref)
                pred_total_raw = hw_base_tot * scen_factor * shock_tot

                raw_mode_preds = {}
                for m in modes:
                    m_base_ref = max(1.0, nov_mean_modes[m].get(dow, 1.0))
                    val25_m = rec25.get(m, 0)
                    shock_m = float(val25_m / m_base_ref) if val25_m > 0 else 1.0
                    raw_mode_preds[m] = hw_base_m[m] * scen_factor * shock_m
            else:
                shock_tot = 1.0
                pred_total_raw = hw_base_tot * scen_factor
                raw_mode_preds = {m: hw_base_m[m] * scen_factor for m in modes}

            pred_total = max(0, int(round(pred_total_raw)))

            sum_raw_modes = sum(raw_mode_preds.values())
            if sum_raw_modes > 0:
                scale = pred_total / sum_raw_modes
                mode_preds = {m: max(0, int(round(raw_mode_preds[m] * scale))) for m in modes}
                diff_round = pred_total - sum(mode_preds.values())
                highest_m = max(mode_preds, key=mode_preds.get)
                mode_preds[highest_m] = max(0, mode_preds[highest_m] + diff_round)
            else:
                mode_preds = {m: 0 for m in modes}

            # Armada
            arm_preds = {}
            for m in modes:
                lf = load_factors_base[m]
                if is_nataru_window:
                    lf *= 1.10
                arm_preds[f'arm_{m}'] = int(round(mode_preds[m] / lf)) if mode_preds[m] > 0 else 0
            arm_total = sum(arm_preds.values())

            ci_lower = max(0, int(round(pred_total - 1.96 * rmse)))
            ci_upper = int(round(pred_total + 1.96 * rmse))

            yoy_pct = round(((pred_total / val25_tot) - 1.0) * 100, 1) if val25_tot > 0 else 0.0

            prov_fc_scenarios[s].append({
                'date': d_str,
                'TOTAL': pred_total,
                'hw_baseline': int(round(hw_base_tot)),
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'pnp_2025': val25_tot,
                'yoy_pct': yoy_pct,
                'status': 'PEAK_SURGE' if is_nataru_window and pred_total >= int(1.15 * mean_vol) else ('HIGH' if pred_total >= int(1.05 * mean_vol) else 'NORMAL'),
                'UDARA': mode_preds['UDARA'],
                'KA': mode_preds['KA'],
                'BUS': mode_preds['BUS'],
                'ASDP': mode_preds['ASDP'],
                'LAUT': mode_preds['LAUT'],
                'arm_TOTAL': arm_total,
                'arm_2025': arm25_tot,
                'arm_UDARA': arm_preds['arm_UDARA'],
                'arm_KA': arm_preds['arm_KA'],
                'arm_BUS': arm_preds['arm_BUS'],
                'arm_ASDP': arm_preds['arm_ASDP'],
                'arm_LAUT': arm_preds['arm_LAUT'],
            })

    # 8. Summarize Nataru period (18 Days: 18 Des - 4 Jan)
    prov_summaries = {}
    for s in scenarios:
        sub = [r for r in prov_fc_scenarios[s] if '2026-12-18' <= r['date'] <= '2027-01-04']
        tot_p = sum(r['TOTAL'] for r in sub)
        tot_a = sum(r['arm_TOTAL'] for r in sub)
        avg_d = int(round(tot_p / len(sub))) if len(sub) > 0 else 0
        max_d = max(sub, key=lambda x: x['TOTAL']) if len(sub) > 0 else sub[0]

        xmas_d = [r for r in sub if r['date'] == '2026-12-24'][0]
        ny_d = [r for r in sub if r['date'] == '2027-01-03'][0]

        mode_sums = {}
        for m in modes:
            p_sum = sum(r[m] for r in sub)
            p25_sum = benchmark_2025_prov['modes'][m]['passengers']
            yoy_m = round(((p_sum / p25_sum) - 1.0) * 100, 1) if p25_sum > 0 else 0.0
            mode_sums[m] = {
                'passengers_2026': p_sum,
                'passengers_2025': p25_sum,
                'diff': p_sum - p25_sum,
                'yoy_pct': yoy_m,
                'share_pct_2026': round(p_sum / tot_p * 100, 1) if tot_p > 0 else 0.0,
                'share_pct_2025': benchmark_2025_prov['modes'][m]['share_pct'],
            }

        prov_summaries[s] = {
            'total_passengers': tot_p,
            'total_passengers_2025': nat25_tot,
            'diff_passengers': tot_p - nat25_tot,
            'yoy_total_pct': round(((tot_p / nat25_tot) - 1.0) * 100, 1) if nat25_tot > 0 else 0.0,
            'avg_daily_passengers': avg_d,
            'avg_daily_passengers_2025': nat25_avg,
            'yoy_avg_pct': round(((avg_d / nat25_avg) - 1.0) * 100, 1) if nat25_avg > 0 else 0.0,
            'total_armada': tot_a,
            'total_armada_2025': nat25_arm,
            'yoy_armada_pct': round(((tot_a / nat25_arm) - 1.0) * 100, 1) if nat25_arm > 0 else 0.0,
            'all_time_peak_date': max_d['date'],
            'all_time_peak_val': max_d['TOTAL'],
            'all_time_peak_yoy': max_d['yoy_pct'],
            'xmas_peak_date': xmas_d['date'],
            'xmas_peak_val': xmas_d['TOTAL'],
            'xmas_peak_val_2025': xmas25_val,
            'xmas_peak_yoy': xmas_d['yoy_pct'],
            'ny_peak_date': ny_d['date'],
            'ny_peak_val': ny_d['TOTAL'],
            'ny_peak_val_2025': ny25_val,
            'ny_peak_yoy': ny_d['yoy_pct'],
            'mode_breakdown': mode_sums
        }

    # 9. Extract compact historical curves for chart
    # history_2026: dict of mode/metric -> list of 272 numbers
    hist_2026_dict = {
        'TOTAL': [int(v) for v in p26_pvt['TOTAL']],
        'arm_TOTAL': [int(v) for v in a26_pvt['arm_TOTAL']],
    }
    for m in modes:
        hist_2026_dict[m] = [int(v) for v in p26_pvt[m]]
        hist_2026_dict[f'arm_{m}'] = [int(v) for v in a26_pvt[m]]

    # history_2025_md: dict of md ('01-01', ...) -> metric dict
    hist_2025_md_dict = {}
    for md, sub_p25 in p25_df.groupby('md'):
        row_first = sub_p25.iloc[0]
        hist_2025_md_dict[md] = {
            'TOTAL': int(row_first['TOTAL']),
            'arm_TOTAL': int(row_first['arm_TOTAL']),
            **{m: int(row_first[m]) for m in modes},
            **{f'arm_{m}': int(row_first[f'arm_{m}']) for m in modes}
        }

    by_province_data[prov] = {
        'metrics': {
            'TOTAL': {
                'mape': round(mape, 2),
                'wape': round(wape, 2),
                'rmse': int(round(rmse)),
                'mae': int(round(mae)),
                'mean_vol': int(round(mean_vol)),
                'rel_error_pct': round(rel_err, 2)
            }
        },
        'summaries': prov_summaries,
        'scenarios': prov_fc_scenarios,
        'history_2026': hist_2026_dict,
        'history_2025_md': hist_2025_md_dict
    }

    print(f"[{p_idx+1:02d}/38] {prov:<25} -> Backtest MAPE: {mape:5.2f}% | RMSE: {int(rmse):6,d} pnp | Nataru Total: {prov_summaries['moderat']['total_passengers']:9,d} pnp (YoY: {prov_summaries['moderat']['yoy_total_pct']:+5.1f}%)")

print("=" * 80)
print("TRAINING SELESAI UNTUK SELURUH 38 PROVINSI.")

# Save into bundle
bundle['forecast_nataru']['provinces'] = std_provinces
bundle['forecast_nataru']['by_province'] = by_province_data

with open('scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("Berhasil memperbarui scripts/mobility_data_bundle.json dengan data forecasting 38 provinsi!")
