import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

data_dir = r"c:\Users\USER\Documents\PUSDATIN\data_clean"
plots_dir = r"c:\Users\USER\Documents\PUSDATIN\analysis_plots"
os.makedirs(plots_dir, exist_ok=True)

# Warna khas per moda
mode_colors = {
    'UDARA': '#0284c7',   # Biru Langit
    'ASDP': '#10b981',    # Hijau Emerald
    'BUS': '#f59e0b',     # Amber / Oranye
    'LAUT': '#0f766e',    # Teal Laut
    'KA': '#8b5cf6'       # Ungu Modern
}

print("=== MEMUAT DATASET UNTUK ANALISIS DESKRIPTIF ===")
df_clean = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_2026_clean.csv"))
df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'])
df_daily = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_daily.csv"))
df_daily['tanggal'] = pd.to_datetime(df_daily['tanggal'])
df_monthly = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_monthly.csv"))
df_dow = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_summary_dow.csv"))
df_top = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_top_prasarana.csv"))
df_prov = pd.read_csv(os.path.join(data_dir, "siasati_multimoda_provinsi.csv"))

print(f"Data harian: {len(df_daily):,} baris")

# -------------------------------------------------------------
# 1. PERHITUNGAN STATISTIK DESKRIPTIF DETAIL
# -------------------------------------------------------------
print("\nMenghitung statistik deskriptif detail per moda...")

stats_records = []
for mode in ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA']:
    sub = df_clean[df_clean['moda'] == mode]
    p_tot = sub['total_penumpang']
    a_tot = sub['total_armada']
    p_dat = sub['penumpang_datang']
    p_brg = sub['penumpang_berangkat']
    
    stats_records.append({
        'Moda': mode,
        'Jumlah_Observasi': len(sub),
        'Total_Penumpang': int(p_tot.sum()),
        'Total_Penumpang_Datang': int(p_dat.sum()),
        'Total_Penumpang_Berangkat': int(p_brg.sum()),
        'Total_Armada': int(a_tot.sum()),
        'Rata_Penumpang_per_Simpul_Hari': round(float(p_tot.mean()), 2),
        'Median_Penumpang': float(p_tot.median()),
        'Std_Penumpang': round(float(p_tot.std()), 2),
        'IQR_Penumpang': float(p_tot.quantile(0.75) - p_tot.quantile(0.25)),
        'Min_Penumpang': float(p_tot.min()),
        'Max_Penumpang': float(p_tot.max()),
        'Skewness_Penumpang': round(float(p_tot.skew()), 2),
        'Rata_Armada_per_Hari': round(float(a_tot.mean()), 2),
        'Rasio_Penumpang_per_Armada': round(float(p_tot.sum() / a_tot.sum()), 2) if a_tot.sum() > 0 else 0
    })

df_stats = pd.DataFrame(stats_records)
df_stats.to_csv(os.path.join(data_dir, "descriptive_statistics_table.csv"), index=False)
print("  -> Saved: descriptive_statistics_table.csv")
print(df_stats[['Moda', 'Total_Penumpang', 'Total_Armada', 'Rata_Penumpang_per_Simpul_Hari', 'Rasio_Penumpang_per_Armada']])

# Ekspor JSON Ringkasan untuk Dashboard
total_nasional_penumpang = int(df_stats['Total_Penumpang'].sum())
total_nasional_armada = int(df_stats['Total_Armada'].sum())

summary_json = {
    'total_penumpang': total_nasional_penumpang,
    'total_armada': total_nasional_armada,
    'rentang_tanggal': '01 Jan 2026 s/d 25 Sep 2026',
    'total_hari': int(df_clean['tanggal'].nunique()),
    'total_simpul_aktif': int(df_clean['nama_prasarana'].nunique()),
    'moda_breakdown': df_stats.to_dict(orient='records')
}
with open(os.path.join(data_dir, "descriptive_summary.json"), 'w', encoding='utf-8') as f:
    json.dump(summary_json, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------
# PLOT 1: PANGSA PASAR PENUMPANG (MODAL SPLIT)
# -------------------------------------------------------------
print("\nMembuat Plot 1: Modal Split Share...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Donut chart
labels = df_stats['Moda'].tolist()
sizes = df_stats['Total_Penumpang'].tolist()
colors = [mode_colors[m] for m in labels]

wedges, texts, autotexts = ax1.pie(
    sizes, 
    labels=labels, 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=colors,
    pctdistance=0.75,
    textprops={'fontsize': 11, 'weight': 'bold'},
    wedgeprops={'width': 0.45, 'edgecolor': 'white', 'linewidth': 2}
)
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10)
ax1.set_title("Pangsa Pasar Volume Penumpang (Jan–Sep 2026)\nTotal: 370,4 Juta Pergerakan", fontsize=13, weight='bold', pad=15)

# Bar chart
y_pos = np.arange(len(labels))
bars = ax2.barh(y_pos, [s / 1e6 for s in sizes], color=colors, height=0.6)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(labels, fontsize=11, weight='bold')
ax2.invert_yaxis()
ax2.set_xlabel("Volume Penumpang (Juta Orang)", fontsize=11)
ax2.set_title("Volume Penumpang Kumulatif per Moda", fontsize=13, weight='bold', pad=15)
for bar in bars:
    w = bar.get_width()
    ax2.text(w + 1.5, bar.get_y() + bar.get_height()/2, f'{w:.1f} Juta', va='center', ha='left', fontsize=10, weight='bold', color='#1e293b')
ax2.set_xlim(0, max(sizes)/1e6 * 1.18)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "01_modal_split_share.png"), dpi=200)
plt.close()
print("  -> Saved: 01_modal_split_share.png")

# -------------------------------------------------------------
# PLOT 2: TREN HARIAN MULTIMODA (TIME-SERIES)
# -------------------------------------------------------------
print("Membuat Plot 2: Tren Harian Multimoda...")
fig, ax = plt.subplots(figsize=(15, 6.5))

pivot_daily = df_daily.pivot(index='tanggal', columns='moda', values='total_penumpang').fillna(0)
for mode in ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA']:
    if mode in pivot_daily.columns:
        ax.plot(pivot_daily.index, pivot_daily[mode] / 1e3, label=f"Moda {mode}", color=mode_colors[mode], linewidth=1.7, alpha=0.9)

# Anotasi Musim Mudik Lebaran 2026 (sekitar April 2026)
ax.axvspan(pd.to_datetime('2026-04-15'), pd.to_datetime('2026-04-28'), color='#fef08a', alpha=0.35, label='Puncak Mudik & Balik Lebaran')
ax.annotate('Puncak Arus Mudik\n(19-23 April 2026)', 
            xy=(pd.to_datetime('2026-04-21'), 950),
            xytext=(pd.to_datetime('2026-02-15'), 1100),
            arrowprops=dict(facecolor='#b45309', shrink=0.08, width=1.5, headwidth=7),
            fontsize=10, weight='bold', color='#b45309',
            bbox=dict(boxstyle="round,pad=0.3", fc="#fef3c7", ec="#f59e0b", lw=1))

# Anotasi Libur Sekolah (Juni-Juli)
ax.axvspan(pd.to_datetime('2026-06-20'), pd.to_datetime('2026-07-15'), color='#e0f2fe', alpha=0.4, label='Liburan Sekolah (Jun-Jul)')

ax.set_title("Dinamika Fluktuasi Harian Penumpang Antarmoda Transportasi Nasional 2026", fontsize=14, weight='bold', pad=15)
ax.set_xlabel("Tanggal Operasional (Januari – September 2026)", fontsize=11)
ax.set_ylabel("Volume Penumpang Harian (Ribu Orang)", fontsize=11)
ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=10)
ax.set_ylim(0, pivot_daily.values.max() / 1e3 * 1.15)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "02_tren_harian_multimoda.png"), dpi=200)
plt.close()
print("  -> Saved: 02_tren_harian_multimoda.png")

# -------------------------------------------------------------
# PLOT 3: HEATMAP BULANAN VOLUME PENUMPANG
# -------------------------------------------------------------
print("Membuat Plot 3: Heatmap Bulanan...")
pivot_monthly = df_monthly.pivot(index='moda', columns='nama_bulan', values='total_penumpang')
# Urutkan bulan
bulan_order = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September"]
pivot_monthly = pivot_monthly.reindex(columns=[b for b in bulan_order if b in pivot_monthly.columns])
pivot_monthly = pivot_monthly.reindex(index=['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA'])

fig, ax = plt.subplots(figsize=(13, 5.5))
sns.heatmap(pivot_monthly / 1e6, cmap="YlGnBu", annot=True, fmt=".2f", cbar_kws={'label': 'Volume Penumpang (Juta Orang)'}, ax=ax, linewidths=1, linecolor='white')
ax.set_title("Heatmap Intensitas Penumpang per Moda per Bulan (Juta Orang)", fontsize=13, weight='bold', pad=15)
ax.set_xlabel("Bulan (Tahun 2026)", fontsize=11, labelpad=10)
ax.set_ylabel("Moda Transportasi", fontsize=11, labelpad=10)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "03_heatmap_bulanan_moda.png"), dpi=200)
plt.close()
print("  -> Saved: 03_heatmap_bulanan_moda.png")

# -------------------------------------------------------------
# PLOT 4: POLA HARI DALAM SEMINGGU (DAY OF WEEK)
# -------------------------------------------------------------
print("Membuat Plot 4: Pola Hari Mingguan...")
hari_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
pivot_dow = df_dow.pivot(index='hari', columns='moda', values='total_penumpang').reindex(hari_order) / 1e6

fig, ax = plt.subplots(figsize=(13, 6))
pivot_dow.plot(kind='bar', ax=ax, color=[mode_colors.get(c, '#64748b') for c in pivot_dow.columns], width=0.8, edgecolor='white')
ax.set_title("Distribusi Total Volume Penumpang Berdasarkan Hari dalam Seminggu", fontsize=13, weight='bold', pad=15)
ax.set_xlabel("Hari Operasional", fontsize=11)
ax.set_ylabel("Total Penumpang (Juta Orang)", fontsize=11)
ax.set_xticklabels(hari_order, rotation=0, fontsize=10, weight='bold')
ax.legend(title='Moda', frameon=True, facecolor='white', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "04_pola_hari_mingguan.png"), dpi=200)
plt.close()
print("  -> Saved: 04_pola_hari_mingguan.png")

# -------------------------------------------------------------
# PLOT 5: TOP 10 SIMPUL PRASARANA PER MODA
# -------------------------------------------------------------
print("Membuat Plot 5: Top Simpul Prasarana...")
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
axes_flat = axes.flatten()

modes_list = ['UDARA', 'ASDP', 'BUS', 'LAUT', 'KA']
titles = {
    'UDARA': 'Top 10 Bandara Udara',
    'ASDP': 'Top 10 Pelabuhan ASDP',
    'BUS': 'Top 10 Terminal Bus',
    'LAUT': 'Top 10 Pelabuhan Laut',
    'KA': 'Top 10 Stasiun Kereta Api'
}

for idx, mode in enumerate(modes_list):
    ax = axes_flat[idx]
    top_sub = df_top[df_top['moda'] == mode].head(10).copy()
    top_sub.sort_values(by='total_penumpang', ascending=True, inplace=True)
    
    y_pos = np.arange(len(top_sub))
    names = top_sub['nama_prasarana'].tolist()
    vals = (top_sub['total_penumpang'] / 1e6).tolist()
    
    bars = ax.barh(y_pos, vals, color=mode_colors[mode], height=0.65, edgecolor='none')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_title(titles[mode], fontsize=11.5, weight='bold', color='#0f172a')
    ax.set_xlabel("Juta Penumpang", fontsize=9.5)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(vals)*0.02, bar.get_y() + bar.get_height()/2, f'{w:.2f}M', va='center', ha='left', fontsize=8.5, weight='bold', color='#334155')
    ax.set_xlim(0, max(vals) * 1.25)

# Sembunyikan axis ke-6
axes_flat[5].axis('off')
fig.suptitle("Peringkat 10 Simpul Prasarana Terpadat per Moda Transportasi (Jan–Sep 2026)", fontsize=15, weight='bold', y=0.99)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "05_top10_simpul_per_moda.png"), dpi=200)
plt.close()
print("  -> Saved: 05_top10_simpul_per_moda.png")

# -------------------------------------------------------------
# PLOT 6: SEBARAN PROVINSI TERPADAT
# -------------------------------------------------------------
print("Membuat Plot 6: Sebaran Provinsi Terpadat...")
top_prov = df_prov.groupby('provinsi')['total_penumpang'].sum().reset_index().sort_values(by='total_penumpang', ascending=False).head(12)
top_prov.sort_values(by='total_penumpang', ascending=True, inplace=True)

fig, ax = plt.subplots(figsize=(12, 6.5))
y_pos = np.arange(len(top_prov))
vals = top_prov['total_penumpang'] / 1e6
bars = ax.barh(y_pos, vals, color='#0284c7', height=0.65, edgecolor='none')
ax.set_yticks(y_pos)
ax.set_yticklabels(top_prov['provinsi'], fontsize=10.5, weight='bold')
ax.set_title("Peringkat 12 Provinsi dengan Beban Pergerakan Penumpang Tertinggi (Semua Moda)", fontsize=13, weight='bold', pad=15)
ax.set_xlabel("Akumulasi Penumpang (Juta Orang)", fontsize=11)

for bar in bars:
    w = bar.get_width()
    ax.text(w + max(vals)*0.015, bar.get_y() + bar.get_height()/2, f'{w:.1f} Juta', va='center', ha='left', fontsize=9.5, weight='bold', color='#0f172a')
ax.set_xlim(0, max(vals) * 1.15)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "06_sebaran_provinsi_terpadat.png"), dpi=200)
plt.close()
print("  -> Saved: 06_sebaran_provinsi_terpadat.png")

# -------------------------------------------------------------
# PLOT 7: RASIO PENUMPANG PER ARMADA
# -------------------------------------------------------------
print("Membuat Plot 7: Rasio Penumpang per Armada...")
fig, ax = plt.subplots(figsize=(10, 5))
sub_ratio = df_stats.sort_values(by='Rasio_Penumpang_per_Armada', ascending=True)
y_pos = np.arange(len(sub_ratio))
bars = ax.barh(y_pos, sub_ratio['Rasio_Penumpang_per_Armada'], color=[mode_colors[m] for m in sub_ratio['Moda']], height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(sub_ratio['Moda'], fontsize=11, weight='bold')
ax.set_title("Rasio Rata-rata Penumpang per Pergerakan Armada (Load Proxy per Trip)", fontsize=13, weight='bold', pad=15)
ax.set_xlabel("Rata-rata Penumpang per Armada", fontsize=11)

for bar in bars:
    w = bar.get_width()
    ax.text(w + max(sub_ratio['Rasio_Penumpang_per_Armada'])*0.02, bar.get_y() + bar.get_height()/2, f'{w:.1f} org/armada', va='center', ha='left', fontsize=10, weight='bold', color='#1e293b')
ax.set_xlim(0, max(sub_ratio['Rasio_Penumpang_per_Armada']) * 1.22)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "07_rasio_penumpang_per_armada.png"), dpi=200)
plt.close()
print("  -> Saved: 07_rasio_penumpang_per_armada.png")

# -------------------------------------------------------------
# PLOT 8: KESEIMBANGAN KEDATANGAN VS KEBERANGKATAN
# -------------------------------------------------------------
print("Membuat Plot 8: Keseimbangan Kedatangan vs Keberangkatan...")
fig, ax = plt.subplots(figsize=(12, 5.5))
x = np.arange(len(df_stats))
width = 0.35

ax.bar(x - width/2, df_stats['Total_Penumpang_Datang'] / 1e6, width, label='Penumpang Datang', color='#0ea5e9')
ax.bar(x + width/2, df_stats['Total_Penumpang_Berangkat'] / 1e6, width, label='Penumpang Berangkat', color='#f97316')

ax.set_title("Komparasi Volume Penumpang Datang vs Berangkat per Moda", fontsize=13, weight='bold', pad=15)
ax.set_xlabel("Moda Transportasi", fontsize=11)
ax.set_ylabel("Volume Penumpang (Juta Orang)", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(df_stats['Moda'], fontsize=11, weight='bold')
ax.legend(frameon=True, facecolor='white', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "08_distribusi_kedatangan_keberangkatan.png"), dpi=200)
plt.close()
print("  -> Saved: 08_distribusi_kedatangan_keberangkatan.png")

print("\n[SELESAI] Seluruh 8 plot visualisasi deskriptif berhasil dibuat!")
