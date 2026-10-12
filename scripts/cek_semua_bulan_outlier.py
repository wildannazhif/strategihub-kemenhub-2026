import json
import pandas as pd
import numpy as np

# Load 2025 data
df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
df25 = df25[['tanggal', 'TOTAL_PENUMPANG']].rename(columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL'})

# Load 2026 data
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)
df26 = pd.DataFrame(bundle['daily_timeline'])[['date', 'TOTAL']]

# Gabungkan seluruh timeline (2025 + 2026)
df = pd.concat([df25, df26], ignore_index=True).drop_duplicates(subset=['date'])
df['date_dt'] = pd.to_datetime(df['date'])
df['year_month'] = df['date_dt'].dt.to_period('M')
df.sort_values('date_dt', inplace=True)

print("=" * 105)
print(f"ANALISIS LENGKAP DETEKSI OUTLIER PER BULAN (SIASATI KEMENHUB)")
print(f"Rentang Data: {df['date'].min()} s.d. {df['date'].max()} (Total {len(df)} Hari / {df['year_month'].nunique()} Bulan)")
print("=" * 105)

results = []

for ym, group in df.groupby('year_month'):
    y = group['TOTAL'].values
    n = len(y)
    q1 = np.percentile(y, 25)
    q3 = np.percentile(y, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    
    outliers_iqr = group[(group['TOTAL'] < lower) | (group['TOTAL'] > upper)]
    
    mean = y.mean()
    std = y.std()
    z = (y - mean) / (std if std > 0 else 1)
    group = group.copy()
    group['z'] = z
    outliers_z25 = group[np.abs(group['z']) > 2.5]
    
    results.append({
        'year_month': str(ym),
        'n_days': n,
        'min': int(y.min()),
        'max': int(y.max()),
        'mean': int(mean),
        'median': int(np.median(y)),
        'std': int(std),
        'q1': int(q1),
        'q3': int(q3),
        'iqr': int(iqr),
        'lower_iqr': int(lower),
        'upper_iqr': int(upper),
        'n_outlier_iqr': len(outliers_iqr),
        'outlier_dates_iqr': [(r['date'], int(r['TOTAL']), 'ATAS (Tinggi)' if r['TOTAL'] > upper else 'BAWAH (Rendah)', r['date_dt'].strftime('%A')) for _, r in outliers_iqr.iterrows()],
        'n_outlier_z25': len(outliers_z25),
        'outlier_dates_z25': [(r['date'], int(r['TOTAL']), f"Z={r['z']:.2f}", r['date_dt'].strftime('%A')) for _, r in outliers_z25.iterrows()]
    })

print(f"{'Bulan':<10} | {'Hari':<4} | {'Rata-rata':<12} | {'Min':<10} | {'Max':<10} | {'Batas Bawah':<11} | {'Batas Atas':<11} | {'Outlier IQR':<14} | {'Outlier Z>2.5'}")
print("-" * 105)

for r in results:
    status_iqr = f"ADA ({r['n_outlier_iqr']} hari)" if r['n_outlier_iqr'] > 0 else "0 (Bersih)"
    status_z = f"ADA ({r['n_outlier_z25']} hari)" if r['n_outlier_z25'] > 0 else "0 (Bersih)"
    print(f"{r['year_month']:<10} | {r['n_days']:<4} | {r['mean']:>12,d} | {r['min']:>10,d} | {r['max']:>10,d} | {r['lower_iqr']:>11,d} | {r['upper_iqr']:>11,d} | {status_iqr:<14} | {status_z}")

print("\n" + "=" * 105)
print("RINCIAN TANGGAL & PENYEBAB OUTLIER:")
print("=" * 105)

for r in results:
    if r['n_outlier_iqr'] > 0 or r['n_outlier_z25'] > 0:
        print(f"\n[*] BULAN {r['year_month']} -> Outlier IQR: {r['n_outlier_iqr']} hari, Outlier Z-Score (|Z|>2.5): {r['n_outlier_z25']} hari")
        for d, val, arah, hari in r['outlier_dates_iqr']:
            print(f"    - [IQR {arah}] {d} ({hari}): {val:,d} penumpang")
        for d, val, zstr, hari in r['outlier_dates_z25']:
            if not any(d == x[0] for x in r['outlier_dates_iqr']):
                print(f"    - [Z-Score {zstr}] {d} ({hari}): {val:,d} penumpang")

print("\n" + "=" * 105)
print("ANALISIS OUTLIER TINGKAT AGREGAT BULANAN (ANTAR-BULAN DALAM SETAHUN):")
print("=" * 105)

monthly_df = df.groupby('year_month')['TOTAL'].agg(['count', 'mean', 'sum']).reset_index()
monthly_df['year'] = monthly_df['year_month'].apply(lambda x: str(x).split('-')[0])

for yr in ['2025', '2026']:
    sub = monthly_df[monthly_df['year'] == yr].copy()
    y_mean = sub['mean'].values
    q1 = np.percentile(y_mean, 25)
    q3 = np.percentile(y_mean, 75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    up = q3 + 1.5 * iqr
    outliers = sub[(sub['mean'] < low) | (sub['mean'] > up)]
    
    print(f"\nTahun {yr} (Berdasarkan Rata-rata Harian Bulanan):")
    print(f"  • Q1 = {q1:,.0f} | Q3 = {q3:,.0f} | IQR = {iqr:,.0f}")
    print(f"  • Batas Bawah = {low:,.0f} | Batas Atas = {up:,.0f}")
    print(f"  • Jumlah Bulan Outlier: {len(outliers)}")
    if len(outliers) == 0:
        print("  • Kesimpulan: TIDAK ADA BULAN YANG MENJADI OUTLIER SECARA AGREGAT.")
    else:
        for _, r_out in outliers.iterrows():
            print(f"  • BULAN OUTLIER: {r_out['year_month']} (Rata-rata: {r_out['mean']:,.0f} pnp/hari)")
