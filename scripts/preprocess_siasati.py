import os
import glob
import json
import pandas as pd
import numpy as np

def clean_province(prov):
    if not isinstance(prov, str) or not prov.strip():
        return "Tidak Terdefinisi"
    prov = prov.strip().title()
    # Standarisasi beberapa nama provinsi umum
    prov_map = {
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "D.I. Yogyakarta",
        "D.I Yogyakarta": "D.I. Yogyakarta",
        "D.I. Yogyakarta": "D.I. Yogyakarta",
        "Kepulauan Bangka Belitung": "Bangka Belitung",
        "Bangka Belitung": "Bangka Belitung",
        "Kepulauan Riau": "Kepulauan Riau",
        "Kep. Riau": "Kepulauan Riau",
        "Nusa Tenggara Barat": "NTB",
        "Nusa Tenggara Timur": "NTT",
        "Papua Barat Daya": "Papua Barat Daya",
        "Papua Selatan": "Papua Selatan",
        "Papua Pegunungan": "Papua Pegunungan",
        "Papua Tengah": "Papua Tengah"
    }
    return prov_map.get(prov, prov)

def process_datasets():
    input_dir = r"c:\Users\USER\Documents\PUSDATIN\dataset_siasati_2026"
    output_dir = r"c:\Users\USER\Documents\PUSDATIN\data_clean"
    os.makedirs(output_dir, exist_ok=True)
    
    modes_config = [
        {
            "code": "BUS",
            "name": "Bus (Terminal)",
            "file_pattern": "dm_bus_2026_T*.json",
            "rename": {
                "nama_terminal": "nama_prasarana",
                "nama_provinsi": "provinsi",
                "bus_datang": "armada_datang",
                "bus_berangkat": "armada_berangkat"
            }
        },
        {
            "code": "ASDP",
            "name": "Penyeberangan (ASDP)",
            "file_pattern": "dm_asdp_2026_T*.json",
            "rename": {
                "nama_pelabuhan": "nama_prasarana",
                "nama_provinsi": "provinsi",
                "kapal_datang": "armada_datang",
                "kapal_berangkat": "armada_berangkat"
            }
        },
        {
            "code": "UDARA",
            "name": "Udara (Bandara)",
            "file_pattern": "dm_udara_2026_T*.json",
            "rename": {
                "nama_bandara": "nama_prasarana",
                "nama_provinsi": "provinsi",
                "pesawat_datang": "armada_datang",
                "pesawat_berangkat": "armada_berangkat"
            }
        },
        {
            "code": "LAUT",
            "name": "Laut (Pelabuhan)",
            "file_pattern": "dm_laut_2026_T*.json",
            "rename": {
                "nama_pelabuhan": "nama_prasarana",
                "nama_provinsi": "provinsi",
                "kapal_datang": "armada_datang",
                "kapal_berangkat": "armada_berangkat"
            }
        },
        {
            "code": "KA",
            "name": "Kereta Api (Stasiun)",
            "file_pattern": "dm_ka_2026_T*.json",
            "rename": {
                "nama": "nama_prasarana",
                "kereta_datang": "armada_datang",
                "kereta_berangkat": "armada_berangkat"
            }
        }
    ]
    
    all_dfs = []
    print("=== MEMULAI PREPROCESSING DATASET SIASATI 2026 ===")
    
    for cfg in modes_config:
        files = sorted(glob.glob(os.path.join(input_dir, cfg["file_pattern"])))
        print(f"\nMemproses Moda: {cfg['code']} ({len(files)} file)...")
        mode_dfs = []
        for f in files:
            t_part = "T1" if "T1" in f else ("T2" if "T2" in f else "T3")
            df_part = pd.read_json(f)
            df_part["caturwulan"] = t_part
            mode_dfs.append(df_part)
            print(f"  -> {os.path.basename(f)}: {len(df_part):,} baris")
        
        df_mode = pd.concat(mode_dfs, ignore_index=True)
        df_mode.rename(columns=cfg["rename"], inplace=True)
        df_mode["moda"] = cfg["code"]
        df_mode["moda_label"] = cfg["name"]
        
        all_dfs.append(df_mode)
    
    # Gabung semua moda
    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal Gabungan Baris Data: {len(df_all):,}")
    
    # Standarisasi kolom
    target_cols = [
        "tanggal", "caturwulan", "moda", "moda_label", "id_prasarana", "nama_prasarana",
        "provinsi", "lat", "lon", "tipe",
        "armada_datang", "penumpang_datang", "armada_berangkat", "penumpang_berangkat"
    ]
    for c in target_cols:
        if c not in df_all.columns:
            df_all[c] = np.nan
            
    df_all = df_all[target_cols].copy()
    
    # Parsing Tanggal & Waktu
    print("Mengolah fitur tanggal dan temporal...")
    df_all["tanggal"] = pd.to_datetime(df_all["tanggal"], errors="coerce")
    df_all.dropna(subset=["tanggal"], inplace=True)
    df_all.sort_values(by=["tanggal", "moda", "nama_prasarana"], inplace=True)
    
    df_all["tahun"] = df_all["tanggal"].dt.year
    df_all["bulan"] = df_all["tanggal"].dt.month
    
    bulan_names = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September"
    }
    df_all["nama_bulan"] = df_all["bulan"].map(bulan_names)
    
    hari_names = {
        0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
        4: "Jumat", 5: "Sabtu", 6: "Minggu"
    }
    df_all["hari_idx"] = df_all["tanggal"].dt.dayofweek
    df_all["hari"] = df_all["hari_idx"].map(hari_names)
    df_all["is_weekend"] = df_all["hari_idx"].apply(lambda x: 1 if x in [5, 6] else 0)
    df_all["minggu_ke"] = df_all["tanggal"].dt.isocalendar().week
    
    # Pembersihan Nama Prasarana dan Provinsi
    print("Membersihkan nama prasarana dan standarisasi provinsi...")
    df_all["nama_prasarana"] = df_all["nama_prasarana"].astype(str).str.strip()
    df_all["provinsi"] = df_all["provinsi"].apply(clean_province)
    
    # Numerik Konversi
    num_cols = ["armada_datang", "penumpang_datang", "armada_berangkat", "penumpang_berangkat"]
    for col in num_cols:
        df_all[col] = pd.to_numeric(df_all[col], errors="coerce").fillna(0).clip(lower=0)
    
    # Koordinat
    df_all["lat"] = pd.to_numeric(df_all["lat"], errors="coerce")
    df_all["lon"] = pd.to_numeric(df_all["lon"], errors="coerce")
    
    # Imputasi koordinat yang kosong dari master prasarana yang memiliki koordinat valid
    print("Melakukan imputasi koordinat simpul...")
    valid_coords = df_all[df_all["lat"].notna() & df_all["lon"].notna()].groupby(["moda", "nama_prasarana"])[["lat", "lon"]].first().reset_index()
    coords_dict = {(r["moda"], r["nama_prasarana"]): (r["lat"], r["lon"]) for _, r in valid_coords.iterrows()}
    
    def fill_lat(row):
        if pd.isna(row["lat"]):
            val = coords_dict.get((row["moda"], row["nama_prasarana"]))
            return val[0] if val else np.nan
        return row["lat"]
        
    def fill_lon(row):
        if pd.isna(row["lon"]):
            val = coords_dict.get((row["moda"], row["nama_prasarana"]))
            return val[1] if val else np.nan
        return row["lon"]
        
    df_all["lat"] = df_all.apply(fill_lat, axis=1)
    df_all["lon"] = df_all.apply(fill_lon, axis=1)
    
    # Metrik Total
    df_all["total_penumpang"] = df_all["penumpang_datang"] + df_all["penumpang_berangkat"]
    df_all["total_armada"] = df_all["armada_datang"] + df_all["armada_berangkat"]
    df_all["penumpang_per_armada"] = np.where(df_all["total_armada"] > 0, df_all["total_penumpang"] / df_all["total_armada"], 0)
    
    print("\n--- RINGKASAN DATA BERSIH ---")
    print(f"Total baris akhir: {len(df_all):,}")
    print(f"Rentang tanggal: {df_all['tanggal'].min().strftime('%Y-%m-%d')} s/d {df_all['tanggal'].max().strftime('%Y-%m-%d')}")
    print("Distribusi baris per moda:")
    for m, c in df_all["moda"].value_counts().items():
        print(f"  - {m}: {c:,} baris")
        
    # Ekspor ke Parquet dan CSV
    clean_csv_path = os.path.join(output_dir, "siasati_multimoda_2026_clean.csv")
    print(f"\nMenyimpan dataset gabungan bersih ke: {clean_csv_path}...")
    df_all.to_csv(clean_csv_path, index=False)
    
    # 1. Agregasi Harian Multimoda
    daily_agg = df_all.groupby(["tanggal", "moda"]).agg(
        penumpang_datang=("penumpang_datang", "sum"),
        penumpang_berangkat=("penumpang_berangkat", "sum"),
        total_penumpang=("total_penumpang", "sum"),
        armada_datang=("armada_datang", "sum"),
        armada_berangkat=("armada_berangkat", "sum"),
        total_armada=("total_armada", "sum"),
        jumlah_simpul_aktif=("nama_prasarana", "nunique")
    ).reset_index()
    daily_agg["penumpang_per_armada"] = np.where(daily_agg["total_armada"] > 0, daily_agg["total_penumpang"] / daily_agg["total_armada"], 0)
    daily_agg.to_csv(os.path.join(output_dir, "siasati_multimoda_summary_daily.csv"), index=False)
    print("  -> Saved: siasati_multimoda_summary_daily.csv")
    
    # 2. Agregasi Bulanan Multimoda
    monthly_agg = df_all.groupby(["bulan", "nama_bulan", "moda"]).agg(
        penumpang_datang=("penumpang_datang", "sum"),
        penumpang_berangkat=("penumpang_berangkat", "sum"),
        total_penumpang=("total_penumpang", "sum"),
        armada_datang=("armada_datang", "sum"),
        armada_berangkat=("armada_berangkat", "sum"),
        total_armada=("total_armada", "sum")
    ).reset_index().sort_values(by=["bulan", "moda"])
    monthly_agg.to_csv(os.path.join(output_dir, "siasati_multimoda_summary_monthly.csv"), index=False)
    print("  -> Saved: siasati_multimoda_summary_monthly.csv")
    
    # 3. Agregasi Hari dalam Seminggu
    dow_agg = df_all.groupby(["hari_idx", "hari", "moda"]).agg(
        total_penumpang=("total_penumpang", "sum"),
        total_armada=("total_armada", "sum"),
        rata_harian_penumpang=("total_penumpang", "mean")
    ).reset_index().sort_values(by=["hari_idx", "moda"])
    dow_agg.to_csv(os.path.join(output_dir, "siasati_multimoda_summary_dow.csv"), index=False)
    print("  -> Saved: siasati_multimoda_summary_dow.csv")

    # 4. Agregasi Simpul Prasarana (Top Hubs)
    hubs_agg = df_all.groupby(["moda", "nama_prasarana", "provinsi"]).agg(
        lat=("lat", "first"),
        lon=("lon", "first"),
        tipe=("tipe", "first"),
        penumpang_datang=("penumpang_datang", "sum"),
        penumpang_berangkat=("penumpang_berangkat", "sum"),
        total_penumpang=("total_penumpang", "sum"),
        total_armada=("total_armada", "sum"),
        hari_aktif=("tanggal", "nunique")
    ).reset_index()
    hubs_agg["rata_penumpang_harian"] = np.round(hubs_agg["total_penumpang"] / hubs_agg["hari_aktif"], 1)
    hubs_agg.sort_values(by=["moda", "total_penumpang"], ascending=[True, False], inplace=True)
    hubs_agg.to_csv(os.path.join(output_dir, "siasati_multimoda_top_prasarana.csv"), index=False)
    print("  -> Saved: siasati_multimoda_top_prasarana.csv")

    # 5. Agregasi Provinsi
    prov_agg = df_all.groupby(["provinsi", "moda"]).agg(
        total_penumpang=("total_penumpang", "sum"),
        total_armada=("total_armada", "sum"),
        jumlah_simpul=("nama_prasarana", "nunique")
    ).reset_index().sort_values(by="total_penumpang", ascending=False)
    prov_agg.to_csv(os.path.join(output_dir, "siasati_multimoda_provinsi.csv"), index=False)
    print("  -> Saved: siasati_multimoda_provinsi.csv")
    
    # 6. JSON Prasarana Nodes untuk Peta Leaflet
    nodes_for_map = hubs_agg[hubs_agg["lat"].notna() & hubs_agg["lon"].notna()].copy()
    nodes_list = []
    for _, r in nodes_for_map.iterrows():
        nodes_list.append({
            "m": r["moda"],
            "nama": r["nama_prasarana"],
            "p": r["provinsi"],
            "lat": round(float(r["lat"]), 5),
            "lon": round(float(r["lon"]), 5),
            "t": str(r["tipe"]),
            "tot_p": int(r["total_penumpang"]),
            "p_dat": int(r["penumpang_datang"]),
            "p_brg": int(r["penumpang_berangkat"]),
            "tot_a": int(r["total_armada"]),
            "avg_p": float(r["rata_penumpang_harian"])
        })
    with open(os.path.join(output_dir, "prasarana_map_nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes_list, f, ensure_ascii=False)
    print(f"  -> Saved: prasarana_map_nodes.json ({len(nodes_list)} simpul berpeta)")
    
    print("\n[SELESAI] Pipeline pre-processing berhasil 100%!")

if __name__ == "__main__":
    process_datasets()
