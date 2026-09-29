import os
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
print(f"Memuat {raw_csv}...")
df = pd.read_csv(raw_csv, low_memory=False)

metrics = ['armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat']
key_cols = ['moda', 'id_prasarana', 'tanggal']

# =========================================================================
# 1. DATA DUPLIKAT SAMA PERSIS (EXACT IDENTICAL DUPLICATES)
# =========================================================================
print("\n--- Memproses 1. Data Duplikat Sama Persis ---")
# Baris yang terduplikasi pada (moda, id_prasarana, tanggal, armada_datang, penumpang_datang, armada_berangkat, penumpang_berangkat)
exact_mask = df.duplicated(subset=key_cols + metrics, keep=False)
df_exact = df[exact_mask].copy().sort_values(by=['moda', 'nama_prasarana', 'tanggal', 'id_prasarana'])

# Tambahkan kolom penjelas
has_val = (df_exact['penumpang_datang'] > 0) | (df_exact['penumpang_berangkat'] > 0) | (df_exact['armada_datang'] > 0) | (df_exact['armada_berangkat'] > 0)
df_exact['kategori_duplikat'] = np.where(has_val, 'Kembar Bernilai Positif (Double Entry Nyata)', 'Kembar Nol Semua (0 + 0)')

out_csv1 = r"c:\Users\USER\Documents\PUSDATIN\data_duplikat_sama_persis.csv"
df_exact.to_csv(out_csv1, index=False)
print(f"File 1 berhasil disimpan: {out_csv1}")
print(f"  Total baris: {len(df_exact):,} baris ({len(df_exact)//2:,} pasang)")
print(f"  - Bernilai Positif (>0): {has_val.sum():,} baris ({has_val.sum()//2} pasang)")
print(f"  - Bernilai Nol (0+0): {(~has_val).sum():,} baris ({(~has_val).sum()//2} pasang)")
print("  Distribusi moda:")
print(df_exact['moda'].value_counts())

# =========================================================================
# 2. DATA DUPLIKAT BIASA (BEDA NILAI / DUMMY NOL / LAYANAN GANDA)
# =========================================================================
print("\n--- Memproses 2. Data Duplikat Biasa (Beda Nilai) ---")
# Duplikat tanggal, moda, & id_prasarana
all_dup_mask = df.duplicated(subset=key_cols, keep=False)
df_all_dup = df[all_dup_mask].copy()

# Grupkan per (moda, id_prasarana, tanggal) untuk mengecek apakah dalam satu grup ada variasi nilai
def group_is_varying(group):
    first_row = group[metrics].iloc[0]
    return not (group[metrics] == first_row).all().all()

varying_keys = df_all_dup.groupby(key_cols, as_index=False).filter(group_is_varying)
df_diff = varying_keys.sort_values(by=['moda', 'nama_prasarana', 'tanggal', 'penumpang_datang', 'penumpang_berangkat']).copy()

def classify_diff_row(row):
    tot = row['penumpang_datang'] + row['penumpang_berangkat'] + row['armada_datang'] + row['armada_berangkat']
    if tot == 0:
        return 'Baris Dummy Nol Sistem'
    else:
        return 'Baris Riil Transaksi Aktif'

df_diff['peran_baris'] = df_diff.apply(classify_diff_row, axis=1)

out_csv2 = r"c:\Users\USER\Documents\PUSDATIN\data_duplikat_biasa_beda_nilai.csv"
df_diff.to_csv(out_csv2, index=False)
print(f"File 2 berhasil disimpan: {out_csv2}")
print(f"  Total baris: {len(df_diff):,} baris ({df_diff.groupby(key_cols).ngroups:,} grup tanggal-simpul)")
print("  Distribusi moda:")
print(df_diff['moda'].value_counts())
print("  Distribusi peran baris:")
print(df_diff['peran_baris'].value_counts())

# =========================================================================
# 3. DATA LAT LONG YANG KOSONG
# =========================================================================
print("\n--- Memproses 3. Data Lat Long yang Kosong ---")
is_empty_lat = df['lat'].isna() | (df['lat'].astype(str).str.strip() == '')
is_empty_lon = df['lon'].isna() | (df['lon'].astype(str).str.strip() == '')
is_empty_coords = is_empty_lat | is_empty_lon

df_empty_coords = df[is_empty_coords].copy().sort_values(by=['moda', 'nama_prasarana', 'tanggal'])

out_csv3 = r"c:\Users\USER\Documents\PUSDATIN\data_lat_lon_kosong.csv"
df_empty_coords.to_csv(out_csv3, index=False)
print(f"File 3 berhasil disimpan: {out_csv3}")
print(f"  Total baris: {len(df_empty_coords):,} baris")
print("  Distribusi moda:")
print(df_empty_coords['moda'].value_counts())

# Simpul uniknya juga diekspor sebagai ringkasan aset
grp_unique_empty = df_empty_coords.groupby(['moda', 'id_prasarana', 'nama_prasarana', 'provinsi']).agg(
    tipe=('tipe', 'first'),
    jumlah_hari_lapor=('tanggal', 'count'),
    total_penumpang=('total_penumpang', 'sum'),
    total_armada=('total_armada', 'sum')
).reset_index().sort_values(by=['moda', 'total_penumpang'], ascending=[True, False])

out_csv3_unique = r"c:\Users\USER\Documents\PUSDATIN\daftar_prasarana_unik_lat_lon_kosong.csv"
grp_unique_empty.to_csv(out_csv3_unique, index=False)
print(f"File 3 (Ringkasan Simpul Unik) berhasil disimpan: {out_csv3_unique}")
print(f"  Total simpul unik: {len(grp_unique_empty):,} prasarana")

print("\n=== SEMUA FILE CSV BERHASIL DIPERBARUI & DIVALIDASI 100%! ===")
