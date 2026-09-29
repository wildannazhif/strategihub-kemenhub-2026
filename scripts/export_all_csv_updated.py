import os
import glob
import json
import pandas as pd
import numpy as np

raw_dir = r"c:\Users\USER\Documents\PUSDATIN\dataset_siasati_2026"
out_dir = r"c:\Users\USER\Documents\PUSDATIN\dataset_csv_2026"
os.makedirs(out_dir, exist_ok=True)

modes_config = [
    {
        "code": "BUS",
        "pattern": "dm_bus_2026_T*.json",
        "rename": {
            "nama_terminal": "nama_prasarana",
            "nama_provinsi": "provinsi",
            "bus_datang": "armada_datang",
            "bus_berangkat": "armada_berangkat"
        }
    },
    {
        "code": "ASDP",
        "pattern": "dm_asdp_2026_T*.json",
        "rename": {
            "nama_pelabuhan": "nama_prasarana",
            "nama_provinsi": "provinsi",
            "kapal_datang": "armada_datang",
            "kapal_berangkat": "armada_berangkat"
        }
    },
    {
        "code": "UDARA",
        "pattern": "dm_udara_2026_T*.json",
        "rename": {
            "nama_bandara": "nama_prasarana",
            "nama_provinsi": "provinsi",
            "pesawat_datang": "armada_datang",
            "pesawat_berangkat": "armada_berangkat"
        }
    },
    {
        "code": "LAUT",
        "pattern": "dm_laut_2026_T*.json",
        "rename": {
            "nama_pelabuhan": "nama_prasarana",
            "nama_provinsi": "provinsi",
            "kapal_datang": "armada_datang",
            "kapal_berangkat": "armada_berangkat"
        }
    },
    {
        "code": "KA",
        "pattern": "dm_ka_2026_T*.json",
        "rename": {
            "nama": "nama_prasarana",
            "kereta_datang": "armada_datang",
            "kereta_berangkat": "armada_berangkat"
        }
    }
]

print("=== MEMPROSES DAN MENGEKSPOR DATA TERBARU KE FORMAT CSV ===")

all_dfs = []
per_mode_dfs = {}

cols_order = [
    'tanggal', 'caturwulan', 'moda', 'id_prasarana', 'nama_prasarana', 'provinsi',
    'lat', 'lon', 'tipe',
    'armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat',
    'total_penumpang', 'total_armada'
]

for cfg in modes_config:
    files = sorted(glob.glob(os.path.join(raw_dir, cfg["pattern"])))
    mode_parts = []
    for f in files:
        t_part = "T1" if "T1" in f else ("T2" if "T2" in f else "T3")
        df_part = pd.read_json(f)
        df_part["caturwulan"] = t_part
        df_part["moda"] = cfg["code"]
        df_part.rename(columns=cfg["rename"], inplace=True)
        mode_parts.append(df_part)
        
    df_mode = pd.concat(mode_parts, ignore_index=True)
    
    # Hitung total
    df_mode['penumpang_datang'] = pd.to_numeric(df_mode['penumpang_datang'], errors='coerce').fillna(0)
    df_mode['penumpang_berangkat'] = pd.to_numeric(df_mode['penumpang_berangkat'], errors='coerce').fillna(0)
    df_mode['armada_datang'] = pd.to_numeric(df_mode['armada_datang'], errors='coerce').fillna(0)
    df_mode['armada_berangkat'] = pd.to_numeric(df_mode['armada_berangkat'], errors='coerce').fillna(0)
    
    df_mode['total_penumpang'] = df_mode['penumpang_datang'] + df_mode['penumpang_berangkat']
    df_mode['total_armada'] = df_mode['armada_datang'] + df_mode['armada_berangkat']
    
    for c in cols_order:
        if c not in df_mode.columns:
            df_mode[c] = None
    df_mode = df_mode[cols_order].copy()
    
    per_mode_dfs[cfg["code"]] = df_mode
    all_dfs.append(df_mode)
    
    # Simpan CSV per moda di folder dataset_csv_2026 dan root
    csv_mode_path = os.path.join(out_dir, f"siasati_{cfg['code'].lower()}_2026.csv")
    csv_root_path = os.path.join(r"c:\Users\USER\Documents\PUSDATIN", f"siasati_{cfg['code'].lower()}_2026.csv")
    try:
        df_mode.to_csv(csv_mode_path, index=False)
        print(f"Moda {cfg['code']}: {len(df_mode):,} baris -> Tersimpan di {csv_mode_path}")
    except PermissionError:
        print(f"Moda {cfg['code']}: {csv_mode_path} sedang dibuka (Excel), menyimpan ke file alternatif...")
        alt_mode_path = os.path.join(out_dir, f"siasati_{cfg['code'].lower()}_2026_terbaru.csv")
        df_mode.to_csv(alt_mode_path, index=False)
        print(f"Moda {cfg['code']}: {len(df_mode):,} baris -> Tersimpan di {alt_mode_path}")

    try:
        df_mode.to_csv(csv_root_path, index=False)
    except PermissionError:
        alt_root_path = os.path.join(r"c:\Users\USER\Documents\PUSDATIN", f"siasati_{cfg['code'].lower()}_2026_terbaru.csv")
        df_mode.to_csv(alt_root_path, index=False)

# Master Multimoda Gabungan
df_master = pd.concat(all_dfs, ignore_index=True)
master_csv_path = os.path.join(r"c:\Users\USER\Documents\PUSDATIN", "siasati_multimoda_2026.csv")
master_folder_path = os.path.join(out_dir, "siasati_multimoda_2026.csv")

try:
    df_master.to_csv(master_csv_path, index=False)
except PermissionError:
    master_csv_path = os.path.join(r"c:\Users\USER\Documents\PUSDATIN", "siasati_multimoda_2026_terbaru.csv")
    df_master.to_csv(master_csv_path, index=False)

try:
    df_master.to_csv(master_folder_path, index=False)
except PermissionError:
    master_folder_path = os.path.join(out_dir, "siasati_multimoda_2026_terbaru.csv")
    df_master.to_csv(master_folder_path, index=False)

print("\n=== RINGKASAN DATASET CSV TERBARU ===")
print(f"Total Gabungan 5 Moda: {len(df_master):,} baris")
print(f"Rentang Tanggal: {df_master['tanggal'].min()} s/d {df_master['tanggal'].max()}")
print(f"Lokasi Master CSV: {master_csv_path} ({os.path.getsize(master_csv_path)/(1024*1024):.2f} MB)")

for code, d in per_mode_dfs.items():
    print(f"  - {code}: {len(d):,} baris | Penumpang: {d['total_penumpang'].sum():,.0f} | Armada: {d['total_armada'].sum():,.0f}")
