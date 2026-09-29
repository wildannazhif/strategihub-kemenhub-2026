import glob
import os
import pandas as pd

raw_dir = r"c:\Users\USER\Documents\PUSDATIN\dataset_siasati_2026"
out_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026_raw.csv"
out_folder = r"c:\Users\USER\Documents\PUSDATIN\data_raw"
os.makedirs(out_folder, exist_ok=True)

raw_modes = [
    {
        'moda': 'BUS',
        'pattern': 'dm_bus_2026_T*.json',
        'rename': {
            'nama_terminal': 'nama_prasarana',
            'nama_provinsi': 'provinsi',
            'bus_datang': 'armada_datang',
            'bus_berangkat': 'armada_berangkat'
        }
    },
    {
        'moda': 'ASDP',
        'pattern': 'dm_asdp_2026_T*.json',
        'rename': {
            'nama_pelabuhan': 'nama_prasarana',
            'nama_provinsi': 'provinsi',
            'kapal_datang': 'armada_datang',
            'kapal_berangkat': 'armada_berangkat'
        }
    },
    {
        'moda': 'UDARA',
        'pattern': 'dm_udara_2026_T*.json',
        'rename': {
            'nama_bandara': 'nama_prasarana',
            'nama_provinsi': 'provinsi',
            'pesawat_datang': 'armada_datang',
            'pesawat_berangkat': 'armada_berangkat'
        }
    },
    {
        'moda': 'LAUT',
        'pattern': 'dm_laut_2026_T*.json',
        'rename': {
            'nama_pelabuhan': 'nama_prasarana',
            'nama_provinsi': 'provinsi',
            'kapal_datang': 'armada_datang',
            'kapal_berangkat': 'armada_berangkat'
        }
    },
    {
        'moda': 'KA',
        'pattern': 'dm_ka_2026_T*.json',
        'rename': {
            'nama': 'nama_prasarana',
            'kereta_datang': 'armada_datang',
            'kereta_berangkat': 'armada_berangkat'
        }
    }
]

dfs = []
for cfg in raw_modes:
    files = sorted(glob.glob(os.path.join(raw_dir, cfg['pattern'])))
    for f in files:
        t_part = 'T1' if 'T1' in f else ('T2' if 'T2' in f else 'T3')
        df_part = pd.read_json(f)
        df_part['caturwulan'] = t_part
        df_part['moda'] = cfg['moda']
        df_part.rename(columns=cfg['rename'], inplace=True)
        dfs.append(df_part)

df_raw_master = pd.concat(dfs, ignore_index=True)

# Susun urutan kolom yang rapi
cols_order = [
    'tanggal', 'caturwulan', 'moda', 'id_prasarana', 'nama_prasarana', 'provinsi',
    'lat', 'lon', 'tipe',
    'armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat'
]
for c in cols_order:
    if c not in df_raw_master.columns:
        df_raw_master[c] = None

df_raw_master = df_raw_master[cols_order].copy()

# Total mentah
df_raw_master['total_penumpang_raw'] = pd.to_numeric(df_raw_master['penumpang_datang'], errors='coerce').fillna(0) + pd.to_numeric(df_raw_master['penumpang_berangkat'], errors='coerce').fillna(0)
df_raw_master['total_armada_raw'] = pd.to_numeric(df_raw_master['armada_datang'], errors='coerce').fillna(0) + pd.to_numeric(df_raw_master['armada_berangkat'], errors='coerce').fillna(0)

# Simpan ke root folder dan data_raw
df_raw_master.to_csv(out_csv, index=False)
out_csv_sub = os.path.join(out_folder, "siasati_multimoda_2026_raw.csv")
df_raw_master.to_csv(out_csv_sub, index=False)

# Export juga per moda versi mentah agar mudah dibuka per moda jika diinginkan
for m in ['BUS', 'ASDP', 'UDARA', 'LAUT', 'KA']:
    sub_df = df_raw_master[df_raw_master['moda'] == m]
    sub_path = os.path.join(out_folder, f"siasati_raw_{m.lower()}_2026.csv")
    sub_df.to_csv(sub_path, index=False)

print(f"Berhasil mengekspor Master CSV Data Mentah:")
print(f"1. {out_csv} ({os.path.getsize(out_csv)/(1024*1024):.2f} MB, {len(df_raw_master):,} baris)")
print(f"2. {out_csv_sub}")
print(f"3. CSV terpisah per moda di folder {out_folder}")
