import urllib.request
import json
import ssl
import sys
import os
import pandas as pd
import numpy as np

print("=== MEMULAI PEMUTAKHIRAN DATA MULTIMODA SIASATI S.D. 13 OKTOBER 2026 ===")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data_raw_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

endpoints = [
    ('BUS', 'T1', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_bus_2026_T1?&format=json'),
    ('BUS', 'T2', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_bus_2026_T2?&format=json'),
    ('BUS', 'T3', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_bus_2026_T3?&format=json'),
    ('ASDP', 'T1', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_asdp_2026_T1?&format=json'),
    ('ASDP', 'T2', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_asdp_2026_T2?&format=json'),
    ('ASDP', 'T3', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_asdp_2026_T3?&format=json'),
    ('UDARA', 'T1', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_udara_2026_T1?&format=json'),
    ('UDARA', 'T2', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_udara_2026_T2?&format=json'),
    ('UDARA', 'T3', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_udara_2026_T3?&format=json'),
    ('LAUT', 'T1', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_laut_2026_T1?&format=json'),
    ('LAUT', 'T2', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_laut_2026_T2?&format=json'),
    ('LAUT', 'T3', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_laut_2026_T3?&format=json'),
    ('KA', 'T1', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_ka_2026_T1?&format=json'),
    ('KA', 'T2', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_ka_2026_T2?&format=json'),
    ('KA', 'T3', 'https://hubnet.kemenhub.go.id/dataset/get-data-api/siasati/dm_ka_2026_T3?&format=json'),
]

# 1. DOWNLOAD ATAU BACA DARI CACHE
dfs = []
for moda, term, url in endpoints:
    cache_file = os.path.join(CACHE_DIR, f"{moda}_{term}.json")
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1000:
        print(f"Membaca dari cache: {moda} {term}...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print(f"Mengunduh dari API: {moda} {term} ({url})...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            
    df = pd.DataFrame(data)
    df['moda'] = moda
    df['caturwulan'] = term
    dfs.append((moda, term, df))
    print(f"  -> {moda} {term}: {len(df):,} baris")

# 2. STANDARISASI KOLOM
standard_dfs = []
for moda, term, df in dfs:
    # Cari nama kolom yang tepat
    p_dat_col = [c for c in df.columns if 'penumpang' in c and 'datang' in c][0]
    p_brg_col = [c for c in df.columns if 'penumpang' in c and 'berangkat' in c][0]
    a_dat_col = [c for c in df.columns if ('bus' in c or 'kapal' in c or 'pesawat' in c or 'kereta' in c) and 'datang' in c][0]
    a_brg_col = [c for c in df.columns if ('bus' in c or 'kapal' in c or 'pesawat' in c or 'kereta' in c) and 'berangkat' in c][0]
    nama_col = [c for c in df.columns if 'nama' in c][0]
    prov_col = [c for c in df.columns if 'prov' in c][0]
    
    sub = pd.DataFrame()
    sub['tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%Y-%m-%d')
    sub['caturwulan'] = term
    sub['moda'] = moda
    sub['id_prasarana'] = df['id_prasarana'].astype(str)
    sub['nama_prasarana'] = df[nama_col].astype(str).str.strip()
    sub['provinsi'] = df[prov_col].astype(str).str.strip()
    sub['lat'] = df.get('lat', np.nan)
    sub['lon'] = df.get('lon', np.nan)
    sub['tipe'] = df.get('tipe', '-').astype(str).str.strip()
    
    sub['penumpang_datang'] = pd.to_numeric(df[p_dat_col], errors='coerce').fillna(0).clip(lower=0)
    sub['penumpang_berangkat'] = pd.to_numeric(df[p_brg_col], errors='coerce').fillna(0).clip(lower=0)
    sub['armada_datang'] = pd.to_numeric(df[a_dat_col], errors='coerce').fillna(0).clip(lower=0)
    sub['armada_berangkat'] = pd.to_numeric(df[a_brg_col], errors='coerce').fillna(0).clip(lower=0)
    
    standard_dfs.append(sub)

df_all = pd.concat(standard_dfs, ignore_index=True)
print(f"\nTotal baris mentah gabungan 15 endpoint: {len(df_all):,}")
print(f"Rentang tanggal awal mentah: {df_all['tanggal'].min()} s.d. {df_all['tanggal'].max()}")

# 3. FILTER TANGGAL MUTLAK <= 2026-10-13 (KARENA 14-15 OKTOBER LAG/TIDAK LENGKAP)
df_all = df_all[df_all['tanggal'] <= '2026-10-13'].copy()
print(f"Baris setelah filter <= 2026-10-13: {len(df_all):,}")
print(f"Rentang tanggal setelah filter: {df_all['tanggal'].min()} s.d. {df_all['tanggal'].max()} ({df_all['tanggal'].nunique()} hari)")

# 4. STANDARISASI PROVINSI
def clean_province(prov):
    if not isinstance(prov, str) or not prov.strip() or prov == 'nan' or prov == '-':
        return "Tidak Terdefinisi"
    prov = prov.strip().title()
    prov_map = {
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "D.I. Yogyakarta",
        "D.I Yogyakarta": "D.I. Yogyakarta",
        "D.I. Yogyakarta": "D.I. Yogyakarta",
        "D. I. Yogyakarta": "D.I. Yogyakarta",
        "Diy": "D.I. Yogyakarta",
        "Kepulauan Bangka Belitung": "Bangka Belitung",
        "Bangka Belitung": "Bangka Belitung",
        "Kepulauan Riau": "Kepulauan Riau",
        "Kep. Riau": "Kepulauan Riau",
        "Nusa Tenggara Barat": "NTB",
        "Nusa Tenggara Timur": "NTT",
        "Sulawesi Selatan": "Sulawesi Selatan",
        "Papua Barat Daya": "Papua Barat Daya",
        "Papua Selatan": "Papua Selatan",
        "Papua Pegunungan": "Papua Pegunungan",
        "Papua Tengah": "Papua Tengah"
    }
    return prov_map.get(prov, prov)

df_all['provinsi'] = df_all['provinsi'].apply(clean_province)

# 5. IMPUTASI KOORDINAT
df_all['lat'] = pd.to_numeric(df_all['lat'], errors='coerce')
df_all['lon'] = pd.to_numeric(df_all['lon'], errors='coerce')

valid_coords = df_all[df_all['lat'].notna() & df_all['lon'].notna()].groupby(['moda', 'nama_prasarana'])[['lat', 'lon']].first().reset_index()
coords_dict = {(r['moda'], r['nama_prasarana']): (r['lat'], r['lon']) for _, r in valid_coords.iterrows()}

def fill_lat(row):
    if pd.isna(row['lat']):
        val = coords_dict.get((row['moda'], row['nama_prasarana']))
        return val[0] if val else np.nan
    return row['lat']
    
def fill_lon(row):
    if pd.isna(row['lon']):
        val = coords_dict.get((row['moda'], row['nama_prasarana']))
        return val[1] if val else np.nan
    return row['lon']

df_all['lat'] = df_all.apply(fill_lat, axis=1)
df_all['lon'] = df_all.apply(fill_lon, axis=1)

# 6. DEDUPLIKASI & AGREGASI
# A. Drop duplikat sama persis
df_dedup = df_all.drop_duplicates(keep='first').copy()
print(f"Baris setelah drop duplikat sama persis: {len(df_dedup):,}")

# B. Agregat SUM untuk duplikat (pada tanggal, moda, id_prasarana yang sama)
key_cols = ['tanggal', 'moda', 'id_prasarana']
meta_cols = ['nama_prasarana', 'provinsi', 'lat', 'lon', 'tipe', 'caturwulan']
metrics = ['penumpang_datang', 'penumpang_berangkat', 'armada_datang', 'armada_berangkat']

agg_dict = {m: 'sum' for m in metrics}
for c in meta_cols:
    agg_dict[c] = 'first'

df_clean = df_dedup.groupby(key_cols, as_index=False, dropna=False).agg(agg_dict)
df_clean['total_penumpang'] = df_clean['penumpang_datang'] + df_clean['penumpang_berangkat']
df_clean['total_armada'] = df_clean['armada_datang'] + df_clean['armada_berangkat']

total_clean_rows = len(df_clean)
total_passengers_ytd = int(df_clean['total_penumpang'].sum())
total_pnp_dat_ytd = int(df_clean['penumpang_datang'].sum())
total_pnp_brg_ytd = int(df_clean['penumpang_berangkat'].sum())

total_armada_ytd = int(df_clean['total_armada'].sum())
total_arm_dat_ytd = int(df_clean['armada_datang'].sum())
total_arm_brg_ytd = int(df_clean['armada_berangkat'].sum())

date_min = df_clean['tanggal'].min()
date_max = df_clean['tanggal'].max()
days_count = df_clean['tanggal'].nunique()

print("\n--- RINGKASAN DATA BERSIH S.D. 13 OKTOBER 2026 ---")
print(f"Total baris bersih teragregasi: {total_clean_rows:,}")
print(f"Total Mobilitas Penumpang YTD: {total_passengers_ytd:,} (Datang: {total_pnp_dat_ytd:,}, Berangkat: {total_pnp_brg_ytd:,})")
print(f"Total Armada Beroperasi YTD: {total_armada_ytd:,} (Datang: {total_arm_dat_ytd:,}, Berangkat: {total_arm_brg_ytd:,})")
print(f"Rentang Tanggal: {date_min} s/d {date_max} ({days_count} hari)")
print(f"Rata-rata Penumpang Harian: {round(total_passengers_ytd / days_count):,} pnp/hari")
print(f"Rata-rata Armada Harian: {round(total_armada_ytd / days_count):,} trip/hari")

# Simpan CSV bersih untuk arsip
clean_csv_path = os.path.join(BASE_DIR, "data", "siasati_multimoda_2026_clean_13okt.csv")
os.makedirs(os.path.dirname(clean_csv_path), exist_ok=True)
df_clean.to_csv(clean_csv_path, index=False)
print(f"File CSV bersih tersimpan di: {clean_csv_path}")
