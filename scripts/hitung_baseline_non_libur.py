import json
import pandas as pd
import numpy as np

with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df = pd.DataFrame(bundle['daily_timeline'])
df['date_dt'] = pd.to_datetime(df['date'])

# 1. Definisi Hari Libur Ekstrem:
# - Nataru 2026: 1 Jan s.d. 5 Jan 2026 (5 hari puncak arus balik libur tahun baru)
# - Lebaran 2026: 13 Maret s.d. 29 Maret 2026 (17 hari masa posko resmi H-8 s.d. H+8)
# - Opsi B (Lebaran Extended s.d. libur Paskah): 13 Maret s.d. 5 April 2026 (24 hari)

is_nataru = df['date'].between('2026-01-01', '2026-01-05')
is_lebaran_core = df['date'].between('2026-03-13', '2026-03-29')
is_peak_A = is_nataru | is_lebaran_core
df_reg_A = df[~is_peak_A].copy()

is_lebaran_ext = df['date'].between('2026-03-13', '2026-04-05')
is_peak_B = is_nataru | is_lebaran_ext
df_reg_B = df[~is_peak_B].copy()

modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']

print("=" * 80)
print("ANALISIS BASELINE HARIAN REGULER (EKSKLUSI NATARU & LEBARAN)")
print("=" * 80)
print(f"Total Riwayat Data 2026 : {len(df)} hari (1 Jan s.d. 29 Sep 2026)")

print(f"\n[OPSI 1] Eksklusi Nataru (1-5 Jan) + Posko Lebaran Resmi (13-29 Mar):")
print(f"   • Hari yang Dikeluarkan : {is_peak_A.sum()} hari (Peak Shock)")
print(f"   • Jumlah Hari Reguler   : {len(df_reg_A)} hari ({len(df_reg_A)/len(df)*100:.1f}% dari seluruh data)")
print(f"   • Rata-rata TOTAL       : {df_reg_A['TOTAL'].mean():,.0f} pnp/hari")
print(f"   • Median TOTAL          : {df_reg_A['TOTAL'].median():,.0f} pnp/hari")
print(f"   • Standar Deviasi       : {df_reg_A['TOTAL'].std():,.0f} pnp")
print(f"   • Rentang (Min - Max)   : {df_reg_A['TOTAL'].min():,.0f} s.d. {df_reg_A['TOTAL'].max():,.0f} pnp")
print("   • Rincian Rata-rata Per Moda:")
for m in modes:
    print(f"     - {m:<6}: {df_reg_A[m].mean():,.0f} pnp/hari ({df_reg_A[m].mean()/df_reg_A['TOTAL'].mean()*100:.1f}%)")

print(f"\n[OPSI 2] Eksklusi Nataru (1-5 Jan) + Lebaran Extended s.d. Paskah (13 Mar - 5 Apr):")
print(f"   • Hari yang Dikeluarkan : {is_peak_B.sum()} hari")
print(f"   • Jumlah Hari Reguler   : {len(df_reg_B)} hari ({len(df_reg_B)/len(df)*100:.1f}% dari seluruh data)")
print(f"   • Rata-rata TOTAL       : {df_reg_B['TOTAL'].mean():,.0f} pnp/hari")
print(f"   • Median TOTAL          : {df_reg_B['TOTAL'].median():,.0f} pnp/hari")
print(f"   • Standar Deviasi       : {df_reg_B['TOTAL'].std():,.0f} pnp")
print("   • Rincian Rata-rata Per Moda:")
for m in modes:
    print(f"     - {m:<6}: {df_reg_B[m].mean():,.0f} pnp/hari ({df_reg_B[m].mean()/df_reg_B['TOTAL'].mean()*100:.1f}%)")

feb = df[df['date'].between('2026-02-01', '2026-02-28')]
print("\n" + "=" * 80)
print(f"[KOMPARASI] Dengan Baseline Februari Saja:")
print(f"   • Jumlah Hari           : {len(feb)} hari")
print(f"   • Rata-rata TOTAL       : {feb['TOTAL'].mean():,.0f} pnp/hari")
print(f"   • Median TOTAL          : {feb['TOTAL'].median():,.0f} pnp/hari")
print(f"   • Standar Deviasi       : {feb['TOTAL'].std():,.0f} pnp")
print("=" * 80)
