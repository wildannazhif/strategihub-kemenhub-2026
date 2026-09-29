import os
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026_raw.csv"
print("Memuat dataset mentah...")
df = pd.read_csv(raw_csv, low_memory=False)

# Identifikasi kondisi koordinat
# 1. Kosong / Blank / NaN
is_na_lat = df['lat'].isna() | (df['lat'].astype(str).str.strip() == '')
is_na_lon = df['lon'].isna() | (df['lon'].astype(str).str.strip() == '')
is_empty = is_na_lat | is_na_lon

# 2. Nilai 0,0 (Null Island)
lat_num = pd.to_numeric(df['lat'], errors='coerce')
lon_num = pd.to_numeric(df['lon'], errors='coerce')
is_zero = (lat_num == 0) & (lon_num == 0)

# 3. Nilai tertukar (Maluku Lat > 50, Lon < 0)
is_swapped = (lat_num > 50) & (lon_num < 0)

# =========================================================================
# FILE 1: SELURUH BARIS TRANSAKSI HARIAN DENGAN LAT/LON KOSONG
# =========================================================================
df_empty_tx = df[is_empty].copy()
out_csv_tx = r"c:\Users\USER\Documents\PUSDATIN\data_lat_lon_kosong_transaksi.csv"
df_empty_tx.to_csv(out_csv_tx, index=False)
print(f"1. Berhasil membuat CSV Transaksi Harian Lat/Lon Kosong:")
print(f"   -> {out_csv_tx} ({len(df_empty_tx):,} baris, {os.path.getsize(out_csv_tx)/1024:.1f} KB)")

# =========================================================================
# FILE 2: DAFTAR PRASARANA / SIMPUL UNIK YANG KOORDINATNYA KOSONG
# =========================================================================
grp_empty = df_empty_tx.groupby(['moda', 'id_prasarana', 'nama_prasarana', 'provinsi']).agg(
    tipe=('tipe', 'first'),
    jumlah_hari_lapor=('tanggal', 'count'),
    total_penumpang=('total_penumpang_raw', 'sum'),
    total_armada=('total_armada_raw', 'sum'),
    caturwulan_muncul=('caturwulan', lambda s: ', '.join(sorted(s.unique())))
).reset_index().sort_values(by=['moda', 'total_penumpang'], ascending=[True, False])

grp_empty['status_koordinat'] = 'KOSONG / BELUM TERSEDIA'

out_csv_unique = r"c:\Users\USER\Documents\PUSDATIN\daftar_prasarana_lat_lon_kosong.csv"
grp_empty.to_csv(out_csv_unique, index=False)
print(f"2. Berhasil membuat CSV Daftar Simpul Prasarana Unik Lat/Lon Kosong:")
print(f"   -> {out_csv_unique} ({len(grp_empty):,} simpul unik)")

# =========================================================================
# FILE 3: MASTER KOMPREHENSIF ANOMALI KOORDINAT (KOSONG + NOL + TERTUKAR)
# =========================================================================
df_all_anom = df[is_empty | is_zero | is_swapped].copy()

def flag_status(row):
    lat_val = pd.to_numeric(row['lat'], errors='coerce')
    lon_val = pd.to_numeric(row['lon'], errors='coerce')
    
    if pd.isna(row['lat']) or str(row['lat']).strip() == '' or pd.isna(row['lon']) or str(row['lon']).strip() == '':
        return 'KOSONG (Blank / NaN)'
    elif lat_val == 0 and lon_val == 0:
        return 'NULL ISLAND (0.0, 0.0) Samudera Atlantik'
    elif lat_val > 50 and lon_val < 0:
        return 'TERTUKAR (Lat dan Lon Terbalik ke Kutub Utara)'
    return 'LAINNYA'

df_all_anom['kategori_anomali_spasial'] = df_all_anom.apply(flag_status, axis=1)
out_csv_all = r"c:\Users\USER\Documents\PUSDATIN\data_lat_lon_anomali_lengkap.csv"
df_all_anom.to_csv(out_csv_all, index=False)
print(f"3. Berhasil membuat CSV Master Anomali Koordinat Lengkap (Kosong, 0,0, dan Tertukar):")
print(f"   -> {out_csv_all} ({len(df_all_anom):,} baris, {os.path.getsize(out_csv_all)/1024:.1f} KB)")

print("\n--- RINGKASAN REKAPITULASI ---")
print(df_all_anom['kategori_anomali_spasial'].value_counts())
print("\nBreakdown Simpul Unik Kosong per Moda:")
print(grp_empty['moda'].value_counts())
