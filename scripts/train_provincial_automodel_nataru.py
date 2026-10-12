import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import datetime
import time
import numpy as np
import pandas as pd
import warnings

from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import Ridge

warnings.filterwarnings('ignore')

print("=" * 105)
print("SISTEM PRODUKSI AUTO-MODEL FORECASTING NATARU 2026/2027: 11 MODEL PERAMALAN PER PROVINSI")
print("Kementerian Perhubungan RI • Pusat Data dan Informasi (PUSDATIN)")
print("Referensi: Laporan Komparasi Forecasting Nataru 2026 (Dokumen No: PR.2026/STAT-09/HST)")
print("=" * 105)

# 1. LOAD DATASETS
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

dt_df = pd.DataFrame(bundle['daily_timeline']).set_index('date')

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

# Modal share per province in 2026
prov_pnp_mode = df26.groupby(['provinsi', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
nat_pnp_mode = df26.groupby('moda')['total_penumpang'].sum()
share_pnp = prov_pnp_mode.div(nat_pnp_mode, axis=1).fillna(0)

prov_arm_mode = df26.groupby(['provinsi', 'moda'])['total_armada'].sum().unstack(fill_value=0)
nat_arm_mode = df26.groupby('moda')['total_armada'].sum()
share_arm = prov_arm_mode.div(nat_arm_mode, axis=1).fillna(0)

load_factors_base = {
    'UDARA': 112.0,
    'KA': 55.0,
    'BUS': 12.5,
    'ASDP': 140.0,
    'LAUT': 70.0
}

def get_provincial_data(prov):
    if prov == 'ALL':
        s25_df = pd.DataFrame({'date': df25['tanggal'], 'dow': df25['dow'], 'md': df25['md']})
        s25_df.set_index('date', inplace=True)
        for m in modes:
            s25_df[m] = df25.set_index('tanggal')[f'pnp_{m}'].values
            s25_df[f'arm_{m}'] = df25.set_index('tanggal')[f'arm_{m}'].values
        s25_df['TOTAL'] = df25.set_index('tanggal')['TOTAL_PENUMPANG'].values
        s25_df['arm_TOTAL'] = df25.set_index('tanggal')['TOTAL_ARMADA'].values

        s26_pvt = dt_df[modes].copy()
        s26_pvt['TOTAL'] = dt_df['TOTAL'].values
        
        arm26_nat = df26.pivot_table(index='tanggal', columns='moda', values='total_armada', aggfunc='sum', fill_value=0).reindex(index=dates_26, columns=modes, fill_value=0)
        for d in ['2026-09-28', '2026-09-29']:
            for m in modes:
                arm26_nat.loc[d, m] = int(round(s26_pvt.loc[d, m] / max(1.0, load_factors_base[m])))
        arm26_nat['arm_TOTAL'] = arm26_nat[modes].sum(axis=1)

        s_tot_comb = pd.concat([s25_df['TOTAL'], s26_pvt['TOTAL']])
        s_tot_comb.index = pd.to_datetime(s_tot_comb.index)
        s_tot_comb.index.freq = 'D'
        return s25_df, s26_pvt, arm26_nat, s_tot_comb

    sub26 = df26[df26['provinsi'] == prov]
    p26_pvt = sub26.pivot_table(index='tanggal', columns='moda', values='total_penumpang', aggfunc='sum', fill_value=0).reindex(index=dates_26, columns=modes, fill_value=0)
    a26_pvt = sub26.pivot_table(index='tanggal', columns='moda', values='total_armada', aggfunc='sum', fill_value=0).reindex(index=dates_26, columns=modes, fill_value=0)
    
    # Impute 28-29 Sep from national official daily_timeline scaled by province modal share
    for d in ['2026-09-28', '2026-09-29']:
        for m in modes:
            p26_pvt.loc[d, m] = int(round(dt_df.loc[d, m] * share_pnp.loc[prov, m]))
            a26_pvt.loc[d, m] = int(round(p26_pvt.loc[d, m] / max(1.0, load_factors_base[m])))

    p26_pvt['TOTAL'] = p26_pvt[modes].sum(axis=1)
    a26_pvt['arm_TOTAL'] = a26_pvt[modes].sum(axis=1)

    # Reconstructed 2025
    sh_pnp_prov = share_pnp.loc[prov] if prov in share_pnp.index else pd.Series(0.0, index=modes)
    sh_arm_prov = share_arm.loc[prov] if prov in share_arm.index else pd.Series(0.0, index=modes)

    p25_df = pd.DataFrame({'date': df25['tanggal'], 'dow': df25['dow'], 'md': df25['md']})
    p25_df.set_index('date', inplace=True)
    for m in modes:
        p25_df[m] = (df25.set_index('tanggal')[f'pnp_{m}'] * sh_pnp_prov.get(m, 0.0)).round().astype(int)
        p25_df[f'arm_{m}'] = (df25.set_index('tanggal')[f'arm_{m}'] * sh_arm_prov.get(m, 0.0)).round().astype(int)
    p25_df['TOTAL'] = p25_df[modes].sum(axis=1)
    p25_df['arm_TOTAL'] = p25_df[[f'arm_{m}' for m in modes]].sum(axis=1)

    s_tot_comb = pd.concat([p25_df['TOTAL'], p26_pvt['TOTAL']])
    s_tot_comb.index = pd.to_datetime(s_tot_comb.index)
    s_tot_comb.index.freq = 'D'

    return p25_df, p26_pvt, a26_pvt, s_tot_comb

def evaluate_pred(y_true, y_pred, y_last_train):
    mask = y_true > 0
    if not np.any(mask):
        return {'mape': 0.0, 'wape': 0.0, 'rmse': 0.0, 'mae': 0.0, 'dir_acc': 0.0}
    
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    wape = float(np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100) if np.sum(y_true) > 0 else 0.0
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    
    actual_dir = np.sign(np.diff(np.append([y_last_train], y_true)))
    pred_dir = np.sign(np.diff(np.append([y_last_train], y_pred)))
    dir_acc = float(np.mean(actual_dir == pred_dir) * 100)
    
    return {'mape': mape, 'wape': wape, 'rmse': rmse, 'mae': mae, 'dir_acc': dir_acc}

def train_and_eval_11_models(train_s, test_s, s_tot_comb):
    y_train = train_s.values.astype(float)
    y_test = test_s.values.astype(float)
    n_test = len(y_test)
    y_last = y_train[-1]
    mean_tr = train_s.mean()
    
    results = {}
    
    # 1. Holt-Winters Mul Standar
    try:
        m1 = ExponentialSmoothing(train_s.clip(lower=1.0), trend='add', damped_trend=False, seasonal='mul', seasonal_periods=7, initialization_method='estimated').fit(optimized=True, use_brute=True)
        results['Holt-Winters Mul Standar'] = (np.maximum(0, m1.forecast(n_test).values), 'hw_mul_std')
    except Exception: pass

    # 2. Holt-Winters Mul Damped (phi=0.98)
    try:
        m2 = ExponentialSmoothing(train_s.clip(lower=1.0), trend='add', damped_trend=True, seasonal='mul', seasonal_periods=7, initialization_method='estimated').fit(damping_trend=0.98, optimized=True, use_brute=True)
        results['Holt-Winters Mul Damped (phi=0.98)'] = (np.maximum(0, m2.forecast(n_test).values), 'hw_mul_damped')
    except Exception: pass

    # 3. Holt-Winters Add Damped (phi=0.98)
    try:
        m3 = ExponentialSmoothing(train_s.clip(lower=1.0), trend='add', damped_trend=True, seasonal='add', seasonal_periods=7, initialization_method='estimated').fit(damping_trend=0.98, optimized=True, use_brute=True)
        results['Holt-Winters Add Damped (phi=0.98)'] = (np.maximum(0, m3.forecast(n_test).values), 'hw_add_damped')
    except Exception: pass

    # 4. SARIMA (1, 1, 1) x (1, 1, 1, 7)
    try:
        m4 = SARIMAX(train_s, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=50)
        results['SARIMA (1,1,1)x(1,1,1,7)'] = (np.maximum(0, m4.forecast(n_test).values), 'sarima')
    except Exception: pass

    # 5. ARIMA (1, 1, 1) Non-Seasonal
    try:
        m5 = ARIMA(train_s, order=(1, 1, 1)).fit()
        results['ARIMA (1,1,1) Non-Seasonal'] = (np.maximum(0, m5.forecast(n_test).values), 'arima')
    except Exception: pass

    # 6. Holt Linear Trend
    try:
        m6 = Holt(train_s.clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
        results['Holt Linear Trend (No Seasonal)'] = (np.maximum(0, m6.forecast(n_test).values), 'holt_linear')
    except Exception: pass

    # 7. Simple Exp Smoothing (SES)
    try:
        m7 = SimpleExpSmoothing(train_s.clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
        results['Simple Exp Smoothing (SES)'] = (np.maximum(0, m7.forecast(n_test).values), 'ses')
    except Exception: pass

    # 8. Linear / Ridge Regression (Trend + DOW)
    try:
        X_tr = pd.get_dummies(train_s.index.dayofweek, prefix='dow', drop_first=True, dtype=float)
        X_tr['trend'] = np.arange(len(train_s))
        X_te = pd.get_dummies(test_s.index.dayofweek, prefix='dow', drop_first=True, dtype=float)
        X_te['trend'] = np.arange(len(train_s), len(train_s) + len(test_s))
        for col in X_tr.columns:
            if col not in X_te.columns: X_te[col] = 0.0
        X_te = X_te[X_tr.columns]
        m8 = Ridge(alpha=1.0).fit(X_tr, y_train)
        results['Linear Regression (Trend + DOW)'] = (np.maximum(0, m8.predict(X_te)), 'ridge')
    except Exception: pass

    # 9. Seasonal Naive (Lag 7)
    results['Seasonal Naive (Lag 7)'] = (np.array([y_train[-7:][i % 7] for i in range(n_test)]), 'snaive')

    # 10. Naive Random Walk (Lag 1)
    results['Naive Random Walk (Lag 1)'] = (np.full(n_test, y_last), 'naive')

    # 11. 7-Day Moving Average
    results['7-Day Moving Average'] = (np.full(n_test, np.mean(y_train[-7:])), 'ma7')

    benchmarks = []
    for model_name, (pred, code) in results.items():
        if np.any(np.isnan(pred)) or np.any(np.isinf(pred)):
            continue
        ev = evaluate_pred(y_test, pred, y_last)
        
        # Stability check over 100 days
        # A model is stable if test prediction is non-zero and within reasonable bound
        zero_cnt = (pred <= 1).sum()
        is_stable = (pred.mean() >= 0.15 * mean_tr) and (zero_cnt <= 3) if mean_tr > 100 else True

        benchmarks.append({
            'model_name': model_name,
            'model_code': code,
            'mape': round(ev['mape'], 2),
            'wape': round(ev['wape'], 2),
            'rmse': int(round(ev['rmse'])),
            'mae': int(round(ev['mae'])),
            'dir_acc': round(ev['dir_acc'], 1),
            'is_stable': bool(is_stable),
            'pred_mean': int(round(pred.mean()))
        })
    
    # Sort benchmarks by MAPE ascending
    benchmarks.sort(key=lambda x: x['mape'])
    for rank, b in enumerate(benchmarks, 1):
        b['rank'] = rank
    
    # Pick champion: lowest MAPE among stable models
    stable_bench = [b for b in benchmarks if b['is_stable']]
    champion = stable_bench[0] if stable_bench else benchmarks[0]
    return champion, benchmarks

def generate_forecast_with_model(full_s, model_code, forecast_days, future_dates):
    y_full = full_s.values.astype(float)
    y_last = y_full[-1]
    n_fc = forecast_days
    mean_full = full_s.mean()
    
    pred_100 = None
    try:
        if model_code == 'hw_mul_std':
            m = ExponentialSmoothing(full_s.clip(lower=1.0), trend='add', damped_trend=False, seasonal='mul', seasonal_periods=7, initialization_method='estimated').fit(optimized=True, use_brute=True)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'hw_mul_damped':
            m = ExponentialSmoothing(full_s.clip(lower=1.0), trend='add', damped_trend=True, seasonal='mul', seasonal_periods=7, initialization_method='estimated').fit(damping_trend=0.98, optimized=True, use_brute=True)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'hw_add_damped':
            m = ExponentialSmoothing(full_s.clip(lower=1.0), trend='add', damped_trend=True, seasonal='add', seasonal_periods=7, initialization_method='estimated').fit(damping_trend=0.98, optimized=True, use_brute=True)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'sarima':
            m = SARIMAX(full_s, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=60)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'arima':
            m = ARIMA(full_s, order=(1, 1, 1)).fit()
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'holt_linear':
            m = Holt(full_s.clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'ses':
            m = SimpleExpSmoothing(full_s.clip(lower=1.0), initialization_method='estimated').fit(optimized=True)
            pred_100 = m.forecast(n_fc).values
        elif model_code == 'ridge':
            X_tr = pd.get_dummies(full_s.index.dayofweek, prefix='dow', drop_first=True, dtype=float)
            X_tr['trend'] = np.arange(len(full_s))
            future_idx = pd.to_datetime(future_dates)
            X_te = pd.get_dummies(future_idx.dayofweek, prefix='dow', drop_first=True, dtype=float)
            X_te['trend'] = np.arange(len(full_s), len(full_s) + n_fc)
            for col in X_tr.columns:
                if col not in X_te.columns: X_te[col] = 0.0
            X_te = X_te[X_tr.columns]
            m = Ridge(alpha=1.0).fit(X_tr, y_full)
            pred_100 = m.predict(X_te)
        elif model_code == 'snaive':
            pred_100 = np.array([y_full[-7:][i % 7] for i in range(n_fc)])
        elif model_code == 'naive':
            pred_100 = np.full(n_fc, y_last)
        elif model_code == 'ma7':
            pred_100 = np.full(n_fc, np.mean(y_full[-7:]))
    except Exception:
        pass
    
    if pred_100 is None or np.any(np.isnan(pred_100)) or np.any(np.isinf(pred_100)):
        # Fallback to robust HW Add Damped or Naive
        try:
            m = ExponentialSmoothing(full_s.clip(lower=1.0), trend='add', damped_trend=True, seasonal='add', seasonal_periods=7, initialization_method='estimated').fit(damping_trend=0.98, optimized=True, use_brute=False)
            pred_100 = m.forecast(n_fc).values
        except Exception:
            pred_100 = np.full(n_fc, y_last)
    
    # Floor guardrail to prevent unrealistic drop to zero on positive series
    floor = max(0.0, 0.20 * mean_full) if mean_full > 100 else 0.0
    return np.maximum(floor, pred_100)

# Forecast horizons: 30 Sep 2026 s.d. 7 Jan 2027 (100 days)
forecast_start = datetime.date(2026, 9, 30)
forecast_end = datetime.date(2027, 1, 7)
forecast_days = (forecast_end - forecast_start).days + 1
future_dates = [forecast_start + datetime.timedelta(days=i) for i in range(forecast_days)]

scenarios = ['moderat', 'optimis', 'konservatif']
scenario_factors = {'moderat': 1.00, 'optimis': 1.07, 'konservatif': 0.95}

all_provinces_keys = ['ALL'] + std_provinces
by_province_data = {}
automodel_meta_summary = {}

t_start_all = time.time()

for p_idx, prov_key in enumerate(all_provinces_keys):
    t_prov = time.time()
    prov_name = 'Nasional' if prov_key == 'ALL' else prov_key
    p25_df, p26_pvt, a26_pvt, s_tot_comb = get_provincial_data(prov_key)

    # 1. 28-Day Temporal Holdout Backtest
    train_s = s_tot_comb.iloc[:-28]
    test_s = s_tot_comb.iloc[-28:]

    champion, benchmarks = train_and_eval_11_models(train_s, test_s, s_tot_comb)
    
    if prov_key == 'ALL':
        # Champion for national is Holt-Winters Mul Damped as per formal methodology (Laporan PDF)
        hw_damped_entry = next((b for b in benchmarks if b['model_code'] == 'hw_mul_damped'), None)
        if hw_damped_entry:
            champion = hw_damped_entry

    champ_code = champion['model_code']
    champ_name = champion['model_name']
    champ_mape = champion['mape']
    champ_rmse = champion['rmse']
    champ_mae = champion['mae']

    # 2. Fit Champion Model on entire 637 days to get 100-day baseline
    fc_base_tot_100 = generate_forecast_with_model(s_tot_comb, champ_code, forecast_days, future_dates)

    # Individual mode baselines
    fc_base_mode_100 = {}
    for m in modes:
        s_m_comb = pd.concat([p25_df[m], p26_pvt[m]])
        s_m_comb.index = pd.to_datetime(s_m_comb.index)
        s_m_comb.index.freq = 'D'
        if s_m_comb.sum() > 0:
            fc_base_mode_100[m] = generate_forecast_with_model(s_m_comb, champ_code, forecast_days, future_dates)
        else:
            fc_base_mode_100[m] = np.zeros(forecast_days)

    # 3. Benchmark Nataru 2025 (18 Days: 18-31 Des 2025 + 1-4 Jan 2025)
    des25_nat = p25_df.loc[p25_df.index.to_series().between('2025-12-18', '2025-12-31')]
    jan25_nat = p25_df.loc[p25_df.index.to_series().between('2025-01-01', '2025-01-04')]
    df_nat25 = pd.concat([des25_nat, jan25_nat])

    nat25_tot = int(df_nat25['TOTAL'].sum())
    nat25_avg = int(round(df_nat25['TOTAL'].mean())) if len(df_nat25) > 0 else 0
    nat25_arm = int(df_nat25['arm_TOTAL'].sum())

    xmas25_val = int(p25_df.loc['2025-12-24', 'TOTAL']) if '2025-12-24' in p25_df.index else 0
    ny25_val = int(p25_df.loc['2025-01-03', 'TOTAL']) if '2025-01-03' in p25_df.index else 0

    benchmark_2025 = {
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

    # 4. Nataru Calendar Shock computation
    nov25 = p25_df.loc[p25_df.index.to_series().between('2025-11-01', '2025-11-30')]
    nov_mean_tot = nov25.groupby('dow')['TOTAL'].mean().to_dict()
    nov_mean_modes = {m: nov25.groupby('dow')[m].mean().to_dict() for m in modes}
    p25_by_md = p25_df.set_index('md').to_dict(orient='index')

    # 5. Generate 100-day forecast for 3 scenarios
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

            base_tot = fc_base_tot_100[i]
            base_m = {m: fc_base_mode_100[m][i] for m in modes}

            is_nataru_window = ('2026-12-18' <= d_str <= '2027-01-04')
            if is_nataru_window:
                base_ref = max(1.0, nov_mean_tot.get(dow, 1.0))
                shock_tot = float(val25_tot / base_ref)
                pred_total_raw = base_tot * scen_factor * shock_tot

                raw_mode_preds = {}
                for m in modes:
                    m_base_ref = max(1.0, nov_mean_modes[m].get(dow, 1.0))
                    val25_m = rec25.get(m, 0)
                    shock_m = float(val25_m / m_base_ref) if val25_m > 0 else 1.0
                    raw_mode_preds[m] = base_m[m] * scen_factor * shock_m
            else:
                shock_tot = 1.0
                pred_total_raw = base_tot * scen_factor
                raw_mode_preds = {m: base_m[m] * scen_factor for m in modes}

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
                lf = max(1.0, load_factors_base[m])
                arm_preds[f'arm_{m}'] = max(0, int(round(mode_preds[m] / lf)))
            arm_preds['arm_TOTAL'] = sum(arm_preds.values())

            # 95% Confidence Interval
            ci_half = 1.96 * max(100.0, champ_rmse)
            ci_lower = max(0, int(round(pred_total - ci_half)))
            ci_upper = int(round(pred_total + ci_half))

            entry = {
                'date': d_str,
                'dow': dow,
                'day_name': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][dow],
                'is_nataru': is_nataru_window,
                'shock_factor': round(shock_tot, 4),
                'TOTAL': pred_total,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                **mode_preds,
                **arm_preds,
                'TOTAL_2025': val25_tot,
                'arm_2025': arm25_tot,
            }
            prov_fc_scenarios[s].append(entry)

    # 6. Nataru 18-Day Summary (18 Des 2026 s.d. 4 Jan 2027)
    prov_summaries = {}
    for s in scenarios:
        scen_rows = prov_fc_scenarios[s]
        nataru_rows = [r for r in scen_rows if '2026-12-18' <= r['date'] <= '2027-01-04']

        s_tot_pnp = sum(r['TOTAL'] for r in nataru_rows)
        s_avg_pnp = int(round(s_tot_pnp / len(nataru_rows))) if nataru_rows else 0
        s_tot_arm = sum(r['arm_TOTAL'] for r in nataru_rows)

        diff_pnp = s_tot_pnp - nat25_tot
        yoy_tot_pct = round(float((s_tot_pnp / nat25_tot - 1.0) * 100), 1) if nat25_tot > 0 else 0.0
        yoy_avg_pct = round(float((s_avg_pnp / nat25_avg - 1.0) * 100), 1) if nat25_avg > 0 else 0.0
        yoy_arm_pct = round(float((s_tot_arm / nat25_arm - 1.0) * 100), 1) if nat25_arm > 0 else 0.0

        all_time_peak = max(nataru_rows, key=lambda r: r['TOTAL']) if nataru_rows else {}
        xmas_row = next((r for r in nataru_rows if r['date'] == '2026-12-24'), nataru_rows[0] if nataru_rows else {})
        ny_row = next((r for r in nataru_rows if r['date'] == '2027-01-03'), nataru_rows[0] if nataru_rows else {})

        xmas_yoy = round(float((xmas_row.get('TOTAL', 0) / xmas25_val - 1.0) * 100), 1) if xmas25_val > 0 else 0.0
        ny_yoy = round(float((ny_row.get('TOTAL', 0) / ny25_val - 1.0) * 100), 1) if ny25_val > 0 else 0.0
        peak_yoy = round(float((all_time_peak.get('TOTAL', 0) / max(1, all_time_peak.get('TOTAL_2025', 1)) - 1.0) * 100), 1)

        # Mode breakdown
        mode_bd = {}
        for m in modes:
            m_pnp_26 = sum(r[m] for r in nataru_rows)
            m_arm_26 = sum(r[f'arm_{m}'] for r in nataru_rows)
            m_pnp_25 = benchmark_2025['modes'][m]['passengers']
            m_arm_25 = benchmark_2025['modes'][m]['armada']

            m_diff = m_pnp_26 - m_pnp_25
            m_yoy = round(float((m_pnp_26 / m_pnp_25 - 1.0) * 100), 1) if m_pnp_25 > 0 else 0.0
            m_share_26 = round(float(m_pnp_26 / s_tot_pnp * 100), 1) if s_tot_pnp > 0 else 0.0
            m_share_25 = benchmark_2025['modes'][m]['share_pct']

            mode_bd[m] = {
                'passengers_2026': m_pnp_26,
                'passengers_2025': m_pnp_25,
                'diff': m_diff,
                'yoy_pct': m_yoy,
                'share_pct_2026': m_share_26,
                'share_pct_2025': m_share_25,
                'armada_2026': m_arm_26,
                'armada_2025': m_arm_25
            }

        prov_summaries[s] = {
            'total_passengers': s_tot_pnp,
            'total_passengers_2025': nat25_tot,
            'diff_passengers': diff_pnp,
            'yoy_total_pct': yoy_tot_pct,
            'avg_daily_passengers': s_avg_pnp,
            'avg_daily_passengers_2025': nat25_avg,
            'yoy_avg_pct': yoy_avg_pct,
            'total_armada': s_tot_arm,
            'total_armada_2025': nat25_arm,
            'yoy_armada_pct': yoy_arm_pct,
            'all_time_peak_date': all_time_peak.get('date', ''),
            'all_time_peak_val': all_time_peak.get('TOTAL', 0),
            'all_time_peak_yoy': peak_yoy,
            'xmas_peak_date': xmas_row.get('date', ''),
            'xmas_peak_val': xmas_row.get('TOTAL', 0),
            'xmas_peak_val_2025': xmas25_val,
            'xmas_peak_yoy': xmas_yoy,
            'ny_peak_date': ny_row.get('date', ''),
            'ny_peak_val': ny_row.get('TOTAL', 0),
            'ny_peak_val_2025': ny25_val,
            'ny_peak_yoy': ny_yoy,
            'mode_breakdown': mode_bd
        }

    # 7. Compact history for chart rendering
    compact_hist_26 = {
        'dates': dates_26,
        'TOTAL': [int(v) for v in p26_pvt['TOTAL'].values],
        **{m: [int(v) for v in p26_pvt[m].values] for m in modes}
    }
    compact_hist_25 = {
        d.strftime('%m-%d'): int(p25_df.loc[d_str, 'TOTAL']) for d_str, d in zip(p25_df.index, pd.to_datetime(p25_df.index))
    }

    prov_pack = {
        'champion_model': {
            'name': champ_name,
            'code': champ_code,
            'mape': champ_mape,
            'rmse': champ_rmse,
            'mae': champ_mae,
            'wape': champion['wape'],
            'dir_acc': champion['dir_acc']
        },
        'benchmarks': benchmarks,
        'metrics': {
            'TOTAL': {
                'model_name': champ_name,
                'model_code': champ_code,
                'mape': champ_mape,
                'rmse': champ_rmse,
                'mae': champ_mae,
                'wape': champion['wape'],
                'dir_acc': champion['dir_acc']
            }
        },
        'benchmark_2025': benchmark_2025,
        'summaries': prov_summaries,
        'scenarios': prov_fc_scenarios,
        'history_2026': compact_hist_26,
        'history_2025_md': compact_hist_25
    }

    if prov_key == 'ALL':
        bundle['forecast_nataru']['champion_model'] = prov_pack['champion_model']
        bundle['forecast_nataru']['benchmarks'] = prov_pack['benchmarks']
        bundle['forecast_nataru']['metrics'] = prov_pack['metrics']
        bundle['forecast_nataru']['benchmark_2025'] = prov_pack['benchmark_2025']
        bundle['forecast_nataru']['summaries'] = prov_pack['summaries']
        bundle['forecast_nataru']['scenarios'] = prov_pack['scenarios']
    else:
        by_province_data[prov_key] = prov_pack
        automodel_meta_summary[prov_key] = {
            'winner': champ_name,
            'mape': champ_mape,
            'rmse': champ_rmse,
            'top3': [f"{b['model_name']} ({b['mape']}%)" for b in benchmarks[:3]]
        }

    dur_prov = time.time() - t_prov
    print(f"[{p_idx+1:2d}/39] {prov_name:28s} -> Champion: {champ_name[:28]:28s} | MAPE: {champ_mape:5.2f}% | Nataru: {prov_summaries['moderat']['total_passengers']:,} pnp ({dur_prov:.1f}s)")

bundle['forecast_nataru']['by_province'] = by_province_data
bundle['forecast_nataru']['automodel_meta_summary'] = automodel_meta_summary

def json_serialize(obj):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)

# Save updated bundle safely
print("\nMenyimpan pembaruan bundle dengan Auto-Model Selection ke scripts/mobility_data_bundle.json...")
temp_file = 'scripts/mobility_data_bundle_temp.json'
with open(temp_file, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False, default=json_serialize)

import shutil
shutil.move(temp_file, 'scripts/mobility_data_bundle.json')

total_dur = time.time() - t_start_all
print(f"SUKSES! Bundle diperbarui dalam {total_dur:.1f} detik.")
print("=" * 105)
