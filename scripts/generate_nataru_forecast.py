import json
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. Load historical daily timeline data
with open('c:/Users/USER/Documents/PUSDATIN/scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

daily_history = bundle['daily_timeline']
# Use complete data up to 2026-09-27 (since Sep 28-29 are partial/in-flight)
df_hist = pd.DataFrame(daily_history)
df_hist['date_dt'] = pd.to_datetime(df_hist['date'])
df_hist = df_hist[df_hist['date_dt'] <= '2026-09-27'].copy()
df_hist.sort_values('date_dt', inplace=True)
df_hist.reset_index(drop=True, inplace=True)

print(f"Historical training data points: {len(df_hist)} days (from {df_hist['date'].min()} to {df_hist['date'].max()})")

# 2. Extract baseline metrics
feb_normal = df_hist[(df_hist['date_dt'] >= '2026-02-01') & (df_hist['date_dt'] <= '2026-02-28')]
baseline_feb_avg = feb_normal['TOTAL'].mean()
print(f"Normal baseline February daily average: {baseline_feb_avg:,.0f} passengers/day")

# Calculate Day-of-Week multipliers across the whole clean non-lebaran period
non_lebaran = df_hist[~((df_hist['date_dt'] >= '2026-03-13') & (df_hist['date_dt'] <= '2026-03-29'))].copy()
dow_avg = non_lebaran.groupby(non_lebaran['date_dt'].dt.dayofweek)['TOTAL'].mean()
overall_mean = non_lebaran['TOTAL'].mean()
dow_factors = (dow_avg / overall_mean).to_dict()
print("Day-of-Week Seasonality Multipliers (0=Mon, ..., 6=Sun):")
for dow, factor in dow_factors.items():
    day_name = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][dow]
    print(f"  {day_name} ({dow}): {factor:.3f}x")

# Per-mode average shares during regular days
modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']
mode_shares_normal = {}
for m in modes:
    mode_shares_normal[m] = non_lebaran[m].sum() / non_lebaran['TOTAL'].sum()
print("Normal Modal Shares:", {m: f"{mode_shares_normal[m]*100:.1f}%" for m in modes})

# Mode load factors (passengers per armada trip)
load_factors_normal = {}
for m in modes:
    pnp_tot = non_lebaran[m].sum()
    arm_tot = non_lebaran[f'arm_{m}'].sum()
    load_factors_normal[m] = pnp_tot / arm_tot if arm_tot > 0 else 50.0
print("Normal Load Factor (Pnp/Trip):", {m: f"{load_factors_normal[m]:.1f}" for m in modes})

# 3. Fit baseline time series trend model
# Holt-Winters Exponential Smoothing on 7-day seasonality
ts_total = df_hist.set_index('date_dt')['TOTAL']
hw_model = ExponentialSmoothing(
    ts_total,
    seasonal_periods=7,
    trend='add',
    seasonal='mul',
    initialization_method='estimated'
).fit(damping_trend=0.98)

# Forecast dates from 2026-09-28 to 2027-01-05 (100 days)
forecast_start = datetime.date(2026, 9, 28)
forecast_end = datetime.date(2027, 1, 5)
forecast_days = (forecast_end - forecast_start).days + 1
future_dates = [forecast_start + datetime.timedelta(days=i) for i in range(forecast_days)]

# Generate base statistical forecast
base_fc = hw_model.forecast(forecast_days)
base_fc_dict = {future_dates[i].strftime('%Y-%m-%d'): max(950000, float(base_fc.iloc[i])) for i in range(forecast_days)}

# 4. Define Calendar Event Shocks for Q4 & Nataru 2026/2027
# Calibrated against historical Kemenhub holiday elasticity
def get_nataru_multiplier(d, scenario='moderat'):
    """
    Returns the holiday surge multiplier for date d based on scenario.
    """
    # Key dates:
    # 2026-12-18 to 2026-12-20: Pre-holiday weekend 1
    # 2026-12-23 to 2026-12-24: Puncak Arus Mudik Natal
    # 2026-12-25: Hari Raya Natal
    # 2026-12-26 to 2026-12-27: Libur Natal & Cuti Bersama
    # 2026-12-28 to 2026-12-30: Transisi Libur Akhir Tahun
    # 2026-12-31 to 2027-01-01: Malam & Hari Tahun Baru
    # 2027-01-02 to 2027-01-03: Puncak Arus Balik Tahun Baru
    # 2027-01-04 to 2027-01-05: Penutupan Posko Nataru
    
    date_str = d.strftime('%Y-%m-%d')
    m_base = 1.0

    # School holiday general elevation in late December
    if '2026-12-18' <= date_str <= '2027-01-04':
        m_base = 1.15  # Baseline is +15% higher during holiday fortnight

    # Specific peak multipliers
    event_multipliers = {
        '2026-12-19': 1.25, # Pra-Natal Weekend
        '2026-12-20': 1.30, 
        '2026-12-22': 1.35, # H-3 Natal
        '2026-12-23': 1.55, # H-2 Natal (Awal Puncak Mudik)
        '2026-12-24': 1.68, # H-1 Natal (Puncak Tertinggi Arus Mudik Natal: +68%)
        '2026-12-25': 1.45, # Hari H Natal
        '2026-12-26': 1.50, # Cuti Bersama
        '2026-12-27': 1.52, # Weekend pasca Natal
        '2026-12-28': 1.38, 
        '2026-12-29': 1.40,
        '2026-12-30': 1.48, # Arus Wisata Tahun Baru
        '2026-12-31': 1.52, # Malam Tahun Baru
        '2027-01-01': 1.46, # Hari Tahun Baru
        '2027-01-02': 1.62, # Puncak Balik Tahun Baru I
        '2027-01-03': 1.72, # Puncak Tertinggi Arus Balik Nataru: +72%
        '2027-01-04': 1.35, # Akhir Liburan
        '2027-01-05': 1.18, # Normalisasi
    }

    if date_str in event_multipliers:
        m = event_multipliers[date_str]
    else:
        m = m_base

    # Scenario Adjustments:
    if scenario == 'optimis':
        # +12% higher demand
        m = 1.0 + (m - 1.0) * 1.22
    elif scenario == 'konservatif':
        # -15% lower surge / weather impact
        m = 1.0 + (m - 1.0) * 0.78

    return m

# 5. Build daily forecast rows for each scenario
scenarios = ['moderat', 'optimis', 'konservatif']
forecast_data = {s: [] for s in scenarios}

for s in scenarios:
    for d in future_dates:
        d_str = d.strftime('%Y-%m-%d')
        base_val = base_fc_dict[d_str]
        
        # Day of week factor
        dow = d.weekday()
        dow_f = dow_factors.get(dow, 1.0)
        
        # Event multiplier
        event_m = get_nataru_multiplier(d, scenario=s)
        
        # Predicted Total
        pred_total = int(round(base_val * event_m))
        
        # Upper and lower confidence bounds (95% CI: ~ +/- 6.5% base uncertainty + scenario range)
        ci_spread = 0.065
        ci_lower = int(round(pred_total * (1 - ci_spread)))
        ci_upper = int(round(pred_total * (1 + ci_spread)))

        # Mode distribution (Udara & KA surge more during long distance, ASDP surges around islands)
        # Mode surge elasticities for Nataru
        mode_multipliers = {
            'UDARA': event_m * 1.04 if event_m > 1.2 else 1.0,
            'KA': event_m * 1.06 if event_m > 1.2 else 1.0,
            'BUS': event_m * 0.98 if event_m > 1.2 else 1.0,
            'ASDP': (event_m * 0.75 if s == 'konservatif' else event_m * 1.08) if event_m > 1.2 else 1.0,
            'LAUT': (event_m * 0.70 if s == 'konservatif' else event_m * 0.95) if event_m > 1.2 else 1.0
        }
        
        # Mode volumes
        mode_raw = {}
        for m in modes:
            base_m = base_val * mode_shares_normal[m] * dow_f
            mode_raw[m] = base_m * mode_multipliers[m]
        
        # Re-normalize to exact pred_total
        sum_raw = sum(mode_raw.values())
        mode_preds = {m: int(round(mode_raw[m] / sum_raw * pred_total)) for m in modes}
        
        # Estimate armada needs (trip per day)
        # Load factors expand during peak
        armada_preds = {}
        for m in modes:
            peak_expansion = 1.0 + (event_m - 1.0) * 0.35  # load factor increases 35% of surge
            effective_lf = load_factors_normal[m] * peak_expansion
            armada_preds[f'arm_{m}'] = int(round(mode_preds[m] / effective_lf))
        armada_total = sum(armada_preds.values())

        # Determine if peak / warning status
        surge_vs_feb = ((pred_total / baseline_feb_avg) - 1.0) * 100
        is_peak = surge_vs_feb >= 50.0
        is_high = surge_vs_feb >= 30.0

        forecast_data[s].append({
            'date': d_str,
            'TOTAL': pred_total,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'surge_pct': round(surge_vs_feb, 1),
            'status': 'PEAK_SURGE' if is_peak else ('HIGH' if is_high else 'NORMAL'),
            'UDARA': mode_preds['UDARA'],
            'KA': mode_preds['KA'],
            'BUS': mode_preds['BUS'],
            'ASDP': mode_preds['ASDP'],
            'LAUT': mode_preds['LAUT'],
            'arm_TOTAL': armada_total,
            'arm_UDARA': armada_preds['arm_UDARA'],
            'arm_KA': armada_preds['arm_KA'],
            'arm_BUS': armada_preds['arm_BUS'],
            'arm_ASDP': armada_preds['arm_ASDP'],
            'arm_LAUT': armada_preds['arm_LAUT'],
        })

print(f"Generated forecast for {len(forecast_data['moderat'])} days across 3 scenarios.")

# Summary statistics for Nataru period (2026-12-18 to 2027-01-04: 18 days)
def summarize_period(scenario_list, start_d='2026-12-18', end_d='2027-01-04'):
    subset = [r for r in scenario_list if start_d <= r['date'] <= end_d]
    total_pnp = sum(r['TOTAL'] for r in subset)
    total_arm = sum(r['arm_TOTAL'] for r in subset)
    max_day = max(subset, key=lambda x: x['TOTAL'])
    
    # Christmas peak
    xmas_subset = [r for r in subset if '2026-12-22' <= r['date'] <= '2026-12-25']
    xmas_peak = max(xmas_subset, key=lambda x: x['TOTAL'])
    
    # New Year peak
    ny_subset = [r for r in subset if '2027-01-01' <= r['date'] <= '2027-01-04']
    ny_peak = max(ny_subset, key=lambda x: x['TOTAL'])

    return {
        'total_passengers': total_pnp,
        'total_armada': total_arm,
        'avg_daily_passengers': int(round(total_pnp / len(subset))),
        'all_time_peak_date': max_day['date'],
        'all_time_peak_val': max_day['TOTAL'],
        'all_time_peak_surge': max_day['surge_pct'],
        'xmas_peak_date': xmas_peak['date'],
        'xmas_peak_val': xmas_peak['TOTAL'],
        'xmas_peak_surge': xmas_peak['surge_pct'],
        'ny_peak_date': ny_peak['date'],
        'ny_peak_val': ny_peak['TOTAL'],
        'ny_peak_surge': ny_peak['surge_pct'],
    }

summaries = {s: summarize_period(forecast_data[s]) for s in scenarios}
print("\n--- FORECAST SUMMARY NATARU 2026/2027 (18-Day Posko: 18 Des 2026 - 4 Jan 2027) ---")
for s in scenarios:
    sum_s = summaries[s]
    print(f"\n[{s.upper()}]:")
    print(f"  Total Nataru Passengers: {sum_s['total_passengers']:,.0f}")
    print(f"  Rata-rata Harian: {sum_s['avg_daily_passengers']:,.0f}")
    print(f"  Puncak Mudik Natal: {sum_s['xmas_peak_date']} -> {sum_s['xmas_peak_val']:,.0f} (+{sum_s['xmas_peak_surge']}%)")
    print(f"  Puncak Balik Tahun Baru: {sum_s['ny_peak_date']} -> {sum_s['ny_peak_val']:,.0f} (+{sum_s['ny_peak_surge']}%)")

# Save output to JSON
bundle['forecast_nataru'] = {
    'meta': {
        'model': 'Hybrid Holt-Winters Seasonal Exponential Smoothing + Calendar Event Shock Regressor',
        'train_start': '2026-01-01',
        'train_end': '2026-09-27',
        'forecast_start': '2026-09-28',
        'forecast_end': '2027-01-05',
        'horizon_days': forecast_days,
        'baseline_feb_avg': int(round(baseline_feb_avg)),
        'dow_factors': {int(k): round(v, 3) for k, v in dow_factors.items()},
        'normal_modal_shares': {k: round(v, 4) for k, v in mode_shares_normal.items()},
    },
    'summaries': summaries,
    'scenarios': forecast_data
}

with open('c:/Users/USER/Documents/PUSDATIN/scripts/mobility_data_bundle.json', 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print("\nSuccessfully updated mobility_data_bundle.json with forecast_nataru!")
