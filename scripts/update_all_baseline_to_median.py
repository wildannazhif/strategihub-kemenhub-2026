import json
import re
import pandas as pd

if __package__:
    from .generate_simpul_recommendations import build_recommendations
else:
    from generate_simpul_recommendations import build_recommendations

print("=" * 80)
print("MEMULAI PEMBARUAN BASELINE MENJADI NILAI MEDIAN PADA SELURUH SISTEM")
print("=" * 80)

# 1. Load siasati_multimoda_2026.csv
raw_csv = "siasati_multimoda_2026.csv"
print(f"1. Membaca dataset mentah: {raw_csv}...")
df_source = pd.read_csv(raw_csv, low_memory=False)
# 2. Load bundle JSON
bundle_path = "scripts/mobility_data_bundle.json"
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df_daily = pd.DataFrame(bundle['daily_timeline'])
modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']

# ==============================================================================
# A. HITUNG METRIK BASELINE MEDIAN HARIAN 2026 (NASIONAL & PER MODA)
# ==============================================================================
med_pnp = {m: int(df_daily[m].median()) for m in modes}
med_tot_pnp = int(df_daily['TOTAL'].median())

med_arm = {m: int(df_daily[f'arm_{m}'].median()) for m in modes}
med_tot_arm = int(df_daily['arm_TOTAL'].median())

print(f"Baseline Median Total Penumpang : {med_tot_pnp:,} pnp/hari (N = {len(df_daily)} hari)")
print(f"Baseline Median Per Moda Penumpang: {med_pnp}")
print(f"Baseline Median Per Moda Armada   : {med_arm}")

# ==============================================================================
# B. UPDATE SURGE SUMMARY BERDASARKAN MEDIAN
# ==============================================================================
# Tanggal puncak Lebaran: Mudik 18 Mar, Balik 1 24 Mar, Balik 2 29 Mar
d_mudik = df_daily[df_daily['date'] == '2026-03-18'].iloc[0]
d_balik1 = df_daily[df_daily['date'] == '2026-03-24'].iloc[0]
d_balik2 = df_daily[df_daily['date'] == '2026-03-29'].iloc[0]

new_surge_summary = {}
for m in modes:
    base = med_pnp[m]
    vm = int(d_mudik[m])
    vb1 = int(d_balik1[m])
    vb2 = int(d_balik2[m])
    new_surge_summary[m] = {
        'baseline': base,
        'peak_mudik': vm,
        'surge_mudik_pct': round((vm - base) / base * 100, 1),
        'peak_balik1': vb1,
        'surge_balik1_pct': round((vb1 - base) / base * 100, 1),
        'peak_balik2': vb2,
        'surge_balik2_pct': round((vb2 - base) / base * 100, 1)
    }

new_surge_summary['TOTAL'] = {
    'baseline': med_tot_pnp,
    'peak_mudik': int(d_mudik['TOTAL']),
    'surge_mudik_pct': round((d_mudik['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1),
    'peak_balik1': int(d_balik1['TOTAL']),
    'surge_balik1_pct': round((d_balik1['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1),
    'peak_balik2': int(d_balik2['TOTAL']),
    'surge_balik2_pct': round((d_balik2['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1)
}

bundle['surge_summary'] = new_surge_summary
print("2. surge_summary berhasil diperbarui dengan baseline median.")

# ==============================================================================
# C. UPDATE LOAD FACTOR STATS BERDASARKAN MEDIAN
# ==============================================================================
new_load_factor_stats = {}
for m in modes:
    lf_base = round(med_pnp[m] / med_arm[m], 1) if med_arm[m] > 0 else 0
    p_mud = float(d_mudik[m])
    a_mud = float(d_mudik[f'arm_{m}'])
    lf_mud = round(p_mud / a_mud, 1) if a_mud > 0 else 0
    
    p_bal = float(d_balik1[m])
    a_bal = float(d_balik1[f'arm_{m}'])
    lf_bal = round(p_bal / a_bal, 1) if a_bal > 0 else 0
    
    peak_lf = max(lf_mud, lf_bal)
    surge_lf_pct = round((peak_lf - lf_base) / lf_base * 100, 1) if lf_base > 0 else 0
    
    new_load_factor_stats[m] = {
        'baseline_lf': lf_base,
        'mudik_lf': lf_mud,
        'balik_lf': lf_bal,
        'peak_lf': peak_lf,
        'surge_lf_pct': surge_lf_pct
    }

bundle['load_factor_stats'] = new_load_factor_stats
print("3. load_factor_stats berhasil diperbarui dengan baseline median.")

# ==============================================================================
# D. UPDATE SKENARIO NORMAL RATIO HISTORIS (BASELINE 1 JAN - 12 MAR)
# ==============================================================================
simpul_items, scenario_metadata = build_recommendations(
    df_source, bundle.get('simpul_recommendations', [])
)
bundle['simpul_recommendations'] = simpul_items
bundle['simpul_scenario_metadata'] = scenario_metadata
print(f"5. Skenario simpul ({len(simpul_items)} simpul) berhasil diperbarui.")

# Simpan kembali ke bundle
with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)
print(f"6. File {bundle_path} berhasil disimpan!")

# ==============================================================================
# E. UPDATE INDEX.HTML DAN DASHBOARD_MOBILITAS_NASIONAL_2026.HTML
# ==============================================================================
print("7. Memperbarui index.html dan Dashboard_Mobilitas_Nasional_2026.html...")

bundle_str = json.dumps(bundle, ensure_ascii=False)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update const DATA = ...
data_pattern = re.compile(r'const DATA = \{.*?\};\n', re.DOTALL)
html = data_pattern.sub(f"const DATA = {bundle_str};\n", html, count=1)

# 2. Update modal rumus / methodology text
html = html.replace(
    'A. Baseline Normal (Februari 2026):',
    'A. Baseline Normal Operasional (Median 2026):'
)
html = html.replace(
    'P̃_Feb = (∑ P_Februari) / 28 Hari = 1.188.888 pnp/hari',
    'P̃_Median = Median(P_Harian 2026) = 1.321.644 pnp/hari'
)
html = html.replace(
    'Bulan Februari digunakan sebagai acuan normal karena bebas libur panjang nasional.',
    'Nilai Median harian dari seluruh 272 hari (Jan–Sep 2026) digunakan sebagai acuan normal sesuai metodologi robust Google Mobility & Van Lint (2005) agar kebal terhadap lonjakan ekstrem mudik.'
)

# 3. Update Tab 2 (Puncak Lebaran)
html = html.replace(
    'Persentase Lonjakan (%) terhadap Rata-rata Normal Februari',
    'Persentase Lonjakan (%) terhadap Baseline Normal (Median 2026)'
)
html = html.replace(
    'Perbandingan baseline harian Februari dengan volume puncak arus mudik dan arus balik',
    'Perbandingan baseline harian normal (Median 2026) dengan volume puncak arus mudik dan arus balik'
)
html = html.replace(
    'Baseline Normal (Feb)',
    'Baseline Normal (Median)'
)

# 4. Update Tab 3 (Modal Share)
html = html.replace(
    'Februari (Normal)',
    'Periode Normal (Median)'
)
html = html.replace(
    'antara periode normal (Februari) dan puncak arus mudik Lebaran (Maret)',
    'antara periode normal (Median 2026) dan puncak arus mudik Lebaran (Maret)'
)

# 5. Dropdown filter di Tab 1 (jika ada opsi Februari Baseline Normal)
html = html.replace(
    '<option value="2">Februari 2026 (Baseline Normal)</option>',
    '<option value="2">Februari 2026 (Kondisi Reguler)</option>'
)

# Simpan ke index.html dan Dashboard_Mobilitas_Nasional_2026.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('Dashboard_Mobilitas_Nasional_2026.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("=" * 80)
print("SUKSES PENUH! Seluruh dashboard, JSON bundle, dan HTML telah beralih ke BASELINE MEDIAN!")
print("=" * 80)
