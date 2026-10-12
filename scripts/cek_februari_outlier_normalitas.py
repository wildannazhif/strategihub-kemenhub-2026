r"""
UJI OUTLIER DAN NORMALITAS DATA BULAN FEBRUARI 2026
Jalankan file ini untuk melihat hasil uji outlier dan uji normalitas data Februari 2026.
"""

import json
import pandas as pd
import numpy as np
from scipy import stats

with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df = pd.DataFrame(bundle['daily_timeline'])
df['date_dt'] = pd.to_datetime(df['date'])
feb = df[df['date'].between('2026-02-01', '2026-02-28')].copy()
feb.sort_values('date_dt', inplace=True)

y = feb['TOTAL'].values

print("=" * 80)
print("ANALISIS DESKRIPTIF DATA BULAN FEBRUARI 2026 (28 HARI)")
print("=" * 80)
print(f"Jumlah Hari  : {len(y)} Hari (Tepat 4 Minggu: 1 Feb - 28 Feb 2026)")
print(f"Nilai Min    : {y.min():,} penumpang")
print(f"Nilai Max    : {y.max():,} penumpang")
print(f"Rata-rata    : {y.mean():,.0f} penumpang/hari")
print(f"Median       : {np.median(y):,.0f} penumpang/hari")
print(f"Standar Dev  : {y.std():,.0f} penumpang")

# 1. UJI OUTLIER DENGAN METODE IQR (Interquartile Range)
print("\n" + "=" * 80)
print("[1] UJI DETEKSI OUTLIER DENGAN METODE IQR (Boxplot Standard)")
print("=" * 80)
q1 = np.percentile(y, 25)
q3 = np.percentile(y, 75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

print(f"Kuartil 1 (Q1, 25%)      : {q1:,.0f} pnp")
print(f"Kuartil 3 (Q3, 75%)      : {q3:,.0f} pnp")
print(f"Rentang Antar Kuartil (IQR): {iqr:,.0f} pnp")
print(f"Batas Bawah Outlier (Q1 - 1.5*IQR) : {lower_bound:,.0f} pnp")
print(f"Batas Atas Outlier (Q3 + 1.5*IQR)  : {upper_bound:,.0f} pnp")

outliers_iqr = feb[(feb['TOTAL'] < lower_bound) | (feb['TOTAL'] > upper_bound)]
print(f"\nJumlah Titik Outlier (Metode IQR) : {len(outliers_iqr)}")
if len(outliers_iqr) == 0:
    print("[OK] KESIMPULAN: TIDAK ADA OUTLIER PADA METODE IQR!")
else:
    print("Daftar Outlier:")
    for _, r in outliers_iqr.iterrows():
        print(f"  • {r['date']} ({r['date_dt'].strftime('%A')}): {r['TOTAL']:,} pnp")

# 2. UJI OUTLIER DENGAN METODE Z-SCORE
print("\n" + "=" * 80)
print("[2] UJI DETEKSI OUTLIER DENGAN METODE Z-SCORE (|Z| > 2.5 dan |Z| > 3.0)")
print("=" * 80)
z_scores = (y - np.mean(y)) / np.std(y)
feb['z_score'] = z_scores

outliers_z25 = feb[np.abs(feb['z_score']) > 2.5]
outliers_z30 = feb[np.abs(feb['z_score']) > 3.0]
print(f"Nilai Z-Score Min : {z_scores.min():.2f}")
print(f"Nilai Z-Score Max : {z_scores.max():.2f}")
print(f"Jumlah Outlier (|Z| > 2.5) : {len(outliers_z25)}")
print(f"Jumlah Outlier (|Z| > 3.0) : {len(outliers_z30)}")
if len(outliers_z25) == 0:
    print("[OK] KESIMPULAN: TIDAK ADA OUTLIER PADA METODE Z-SCORE (Semua data dalam batas wajar)!")

# 3. UJI NORMALITAS
print("\n" + "=" * 80)
print("[3] UJI DISTRIBUSI NORMALITAS DATA BULAN FEBRUARI 2026")
print("=" * 80)
skew = stats.skew(y)
kurt = stats.kurtosis(y)
print(f"Skewness (Kemencengan) : {skew:.4f}  (Dekat 0 = Simetris)")
print(f"Kurtosis (Keruncingan) : {kurt:.4f}  (Dekat 0 = Mesokurtik / Normal)")

# Uji Shapiro-Wilk (Standar terbaik untuk N = 28)
sw_stat, sw_p = stats.shapiro(y)
print(f"\n1. Uji Shapiro-Wilk : W = {sw_stat:.4f}, p-value = {sw_p:.4f}")
if sw_p > 0.05:
    print("   [OK] HASIL: DATA FEBRUARI BERDISTRIBUSI NORMAL! (p-value > 0.05, H0 Diterima)")
else:
    print("   [GAGAL] HASIL: Data Tidak Berdistribusi Normal (p-value <= 0.05)")

# Uji Jarque-Bera
jb_stat, jb_p = stats.jarque_bera(y)
print(f"2. Uji Jarque-Bera  : JB = {jb_stat:.4f}, p-value = {jb_p:.4f}")
if jb_p > 0.05:
    print("   [OK] HASIL: DATA FEBRUARI BERDISTRIBUSI NORMAL! (p-value > 0.05, H0 Diterima)")
else:
    print("   [GAGAL] HASIL: Data Tidak Berdistribusi Normal (p-value <= 0.05)")

# Uji D'Agostino-Pearson
dag_stat, dag_p = stats.normaltest(y)
print(f"3. Uji D'Agostino   : K2 = {dag_stat:.4f}, p-value = {dag_p:.4f}")
if dag_p > 0.05:
    print("   [OK] HASIL: DATA FEBRUARI BERDISTRIBUSI NORMAL! (p-value > 0.05, H0 Diterima)")
else:
    print("   [GAGAL] HASIL: Data Tidak Berdistribusi Normal (p-value <= 0.05)")

print("=" * 80)
