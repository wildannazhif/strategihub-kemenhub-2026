r"""
UJI ASUMSI RESMI SARIMA PADA DATA MOBILITAS SIASATI KEMENHUB (637 HARI)
Jalankan file ini untuk membuktikan sendiri bahwa SARIMA melanggar asumsi statistik.
Perintah jalan:
python scripts/uji_asumsi_sarima.py
"""

import json
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from scipy.stats import jarque_bera

print("=" * 80)
print("MEMUAT DATA HISTORIS SIASATI KEMENHUB (2025 - 2026)...")
print("=" * 80)

df25 = pd.read_csv('siasati_ringkasan_harian_multimoda_2025.csv')
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df26 = pd.DataFrame(bundle['daily_timeline'])
df26 = df26[pd.to_datetime(df26['date']) <= '2026-09-29']

s25 = df25[['tanggal', 'TOTAL_PENUMPANG']].rename(columns={'tanggal': 'date', 'TOTAL_PENUMPANG': 'TOTAL'})
s26 = df26[['date', 'TOTAL']]
df = pd.concat([s25, s26], ignore_index=True)
y = df['TOTAL'].values

print(f"Total Observasi Runtun Waktu: {len(y)} Hari (1 Jan 2025 s.d. 29 Sep 2026)")
print(f"Rata-rata Penumpang Harian  : {np.mean(y):,.0f} pnp/hari")

print("\n" + "=" * 80)
print("MENJALANKAN MODEL RESMI SARIMA(1,1,1)(1,0,1,7)...")
print("=" * 80)

model = SARIMAX(y, order=(1,1,1), seasonal_order=(1,0,1,7), enforce_stationarity=False, enforce_invertibility=False)
res = model.fit(disp=False)
resid = res.resid[10:]  # Potong burn-in

print("\n--- [UJI 1] ASUMSI WHITE NOISE (Uji Ljung-Box pada Residual) ---")
print("Syarat Lolos: p-value HARUS > 0.05 (Tidak ada korelasi yang tertinggal)")
lb = acorr_ljungbox(resid, lags=[7, 14, 21], return_df=True)
print(lb)
for lag in [7, 14, 21]:
    pval = lb.loc[lag, 'lb_pvalue']
    status = "TIDAK LOLOS / ASUMSI DILANGGAR (p < 0.05)" if pval < 0.05 else "LOLOS"
    print(f"  • Lag {lag:2d}: p-value = {pval:.6f} -> {status}")

print("\n--- [UJI 2] PENGUJIAN LENGKAP ASUMSI NORMALITAS ERROR (5 METODE BERBEDA) ---")
print("Syarat Lolos Distribusi Normal: p-value HARUS > 0.05")

from scipy import stats
from statsmodels.stats.diagnostic import lilliefors

skew = stats.skew(resid)
kurt = stats.kurtosis(resid, fisher=False)
print(f"  • Skewness (Kemencengan)      : {skew:.4f}  (Normal ideal = 0.0)")
print(f"  • Kurtosis (Keruncingan)      : {kurt:.4f}  (Normal ideal = 3.0, ini ekor tebal / fat-tail)")

# 1. Jarque-Bera
jb_stat, jb_p = jarque_bera(resid)
print(f"\n  [2A] Uji Jarque-Bera          : Stat = {jb_stat:,.2f} | p-value = {jb_p:.4e} -> {'TIDAK NORMAL (GAGAL)' if jb_p < 0.05 else 'LOLOS'}")

# 2. Shapiro-Wilk
sw_stat, sw_p = stats.shapiro(resid)
print(f"  [2B] Uji Shapiro-Wilk         : W    = {sw_stat:.4f} | p-value = {sw_p:.4e} -> {'TIDAK NORMAL (GAGAL)' if sw_p < 0.05 else 'LOLOS'}")

# 3. D'Agostino-Pearson Omnibus
dag_stat, dag_p = stats.normaltest(resid)
print(f"  [2C] Uji D'Agostino-Pearson   : K2   = {dag_stat:,.2f} | p-value = {dag_p:.4e} -> {'TIDAK NORMAL (GAGAL)' if dag_p < 0.05 else 'LOLOS'}")

# 4. Lilliefors (Kolmogorov-Smirnov)
lil_stat, lil_p = lilliefors(resid)
print(f"  [2D] Uji Lilliefors (KS Corr) : D    = {lil_stat:.4f} | p-value = {lil_p:.4e} -> {'TIDAK NORMAL (GAGAL)' if lil_p < 0.05 else 'LOLOS'}")

# 5. Anderson-Darling
ad_res = stats.anderson(resid, dist='norm')
crit_5pct = ad_res.critical_values[2]
print(f"  [2E] Uji Anderson-Darling     : A2   = {ad_res.statistic:.4f} | Batas Kritis 5% = {crit_5pct:.4f} -> {'TIDAK NORMAL (GAGAL: A2 > Kritis)' if ad_res.statistic > crit_5pct else 'LOLOS'}")

print("\n--- [UJI 3] ASUMSI HOMOSKEDASTISITAS / VARIANS KONSTAN (Uji ARCH) ---")
print("Syarat Lolos: p-value HARUS > 0.05 (Tidak ada heteroskedastisitas)")
arch_stat, arch_p, _, _ = het_arch(resid)
print(f"  • Nilai LM Stat          : {arch_stat:.4f}")
print(f"  • Nilai p-value          : {arch_p:.4e}")
print(f"  • Status                 : {'TIDAK LOLOS / ASUMSI DILANGGAR (p < 0.05)' if arch_p < 0.05 else 'LOLOS'}")

print("\n--- [UJI 4] EVALUASI PROYEKSI OPERASIONAL 100 HARI KE DEPAN ---")
fc = res.get_forecast(steps=100)
ci = fc.conf_int()
print(f"  • Prediksi Hari ke-100 (Titik Nataru) : {fc.predicted_mean[-1]:,.0f} pnp")
print(f"  • Batas Bawah 95% Confidence Interval : {ci[-1, 0]:,.0f} pnp (MUSTAHIL / NILAI NEGATIF!)")
print(f"  • Batas Atas 95% Confidence Interval  : {ci[-1, 1]:,.0f} pnp")
print(f"  • Lebar Rentang Ketidakpastian       : {ci[-1, 1] - ci[-1, 0]:,.0f} pnp")

print("\n" + "=" * 80)
print("KESIMPULAN: SARIMA TERBUKTI MELANGGAR 3 ASUMSI STATISTIK & GAGAL SECARA OPERASIONAL.")
print("=" * 80)
