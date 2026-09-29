import os
import json
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
print(f"Membaca dataset terbaru dari: {raw_csv}...")
df = pd.read_csv(raw_csv, low_memory=False)

print(f"Total baris mentah: {len(df):,}")

# =========================================================================
# 1. CLEANING SESUAI INSTRUKSI USER:
# - Duplikat sama persis diambil salah satu
# - Duplikat berbeda di agregat sum
# - Lat long yang kosong dikosongkan aja dulu
# =========================================================================

# A. Drop duplikat sama persis (ambil salah satu / keep='first')
df_dedup = df.drop_duplicates(keep='first').copy()
print(f"Baris setelah drop duplikat sama persis: {len(df_dedup):,}")

# B. Agregat sum untuk duplikat berbeda (pada tanggal, caturwulan, moda, id_prasarana yang sama)
key_cols = ['tanggal', 'caturwulan', 'moda', 'id_prasarana']
meta_cols = ['nama_prasarana', 'provinsi', 'lat', 'lon', 'tipe']
metrics = ['penumpang_datang', 'penumpang_berangkat', 'armada_datang', 'armada_berangkat']

agg_dict = {m: 'sum' for m in metrics}
for c in meta_cols:
    agg_dict[c] = 'first'

df_clean = df_dedup.groupby(key_cols, as_index=False, dropna=False).agg(agg_dict)
df_clean['total_penumpang'] = df_clean['penumpang_datang'] + df_clean['penumpang_berangkat']
df_clean['total_armada'] = df_clean['armada_datang'] + df_clean['armada_berangkat']

total_clean_rows = len(df_clean)
total_passengers_ytd = int(df_clean['total_penumpang'].sum())
total_armada_ytd = int(df_clean['total_armada'].sum())
date_min = df_clean['tanggal'].min()
date_max = df_clean['tanggal'].max()
days_count = df_clean['tanggal'].nunique()

print(f"Baris bersih final setelah agregasi sum: {total_clean_rows:,}")
print(f"Total Mobilitas Penumpang YTD: {total_passengers_ytd:,}")
print(f"Total Armada Beroperasi YTD: {total_armada_ytd:,}")
print(f"Rentang Tanggal: {date_min} s/d {date_max} ({days_count} hari)")

# =========================================================================
# 2. TIMELINE HARIAN (272 HARI)
# =========================================================================
daily_pnp = df_clean.groupby(['tanggal', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
daily_arm = df_clean.groupby(['tanggal', 'moda'])['total_armada'].sum().unstack(fill_value=0)
dates = sorted(daily_pnp.index.tolist())

daily_timeline = []
for d in dates:
    p = daily_pnp.loc[d]
    a = daily_arm.loc[d]
    tot_p = int(p.sum())
    tot_a = int(a.sum())
    daily_timeline.append({
        'date': d,
        'UDARA': int(p.get('UDARA', 0)),
        'KA': int(p.get('KA', 0)),
        'BUS': int(p.get('BUS', 0)),
        'ASDP': int(p.get('ASDP', 0)),
        'LAUT': int(p.get('LAUT', 0)),
        'TOTAL': tot_p,
        'arm_UDARA': int(a.get('UDARA', 0)),
        'arm_KA': int(a.get('KA', 0)),
        'arm_BUS': int(a.get('BUS', 0)),
        'arm_ASDP': int(a.get('ASDP', 0)),
        'arm_LAUT': int(a.get('LAUT', 0)),
        'arm_TOTAL': tot_a,
    })

# =========================================================================
# 3. AGREGAT BULANAN (JANUARI - SEPTEMBER 2026)
# =========================================================================
df_clean['bulan'] = df_clean['tanggal'].str[:7]
month_pnp = df_clean.groupby(['bulan', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
month_arm = df_clean.groupby(['bulan', 'moda'])['total_armada'].sum().unstack(fill_value=0)
months = sorted(month_pnp.index.tolist())

month_names = {
    '2026-01': 'Januari', '2026-02': 'Februari', '2026-03': 'Maret (Lebaran)',
    '2026-04': 'April', '2026-05': 'Mei', '2026-06': 'Juni (Libur Sek.)',
    '2026-07': 'Juli (Libur Sek.)', '2026-08': 'Agustus', '2026-09': 'September*'
}

monthly_summary = []
for m in months:
    p = month_pnp.loc[m]
    a = month_arm.loc[m]
    tot_p = int(p.sum())
    tot_a = int(a.sum())
    monthly_summary.append({
        'bulan': m,
        'label': month_names.get(m, m),
        'UDARA': int(p.get('UDARA', 0)),
        'KA': int(p.get('KA', 0)),
        'BUS': int(p.get('BUS', 0)),
        'ASDP': int(p.get('ASDP', 0)),
        'LAUT': int(p.get('LAUT', 0)),
        'TOTAL': tot_p,
        'TOTAL_ARMADA': tot_a,
        'share_UDARA': round(float(p.get('UDARA', 0)) / tot_p * 100, 1) if tot_p > 0 else 0,
        'share_KA': round(float(p.get('KA', 0)) / tot_p * 100, 1) if tot_p > 0 else 0,
        'share_BUS': round(float(p.get('BUS', 0)) / tot_p * 100, 1) if tot_p > 0 else 0,
        'share_ASDP': round(float(p.get('ASDP', 0)) / tot_p * 100, 1) if tot_p > 0 else 0,
        'share_LAUT': round(float(p.get('LAUT', 0)) / tot_p * 100, 1) if tot_p > 0 else 0,
    })

# =========================================================================
# 4. PERIODE KHUSUS LEBARAN (10 MAR - 05 APR 2026)
# =========================================================================
lebaran_phase = {
    '2026-03-10': ('Pra-Mudik Awal', 'Normal'),
    '2026-03-11': ('Pra-Mudik', 'Normal'),
    '2026-03-12': ('H-8', 'Mulai Bergerak'),
    '2026-03-13': ('H-7', 'Awal Lonjakan Mudik'),
    '2026-03-14': ('H-6 (Sabtu)', 'Arus Mudik Tinggi'),
    '2026-03-15': ('H-5 (Minggu)', 'Arus Mudik Tinggi'),
    '2026-03-16': ('H-4 (Senin)', 'Arus Mudik Tinggi'),
    '2026-03-17': ('H-3 (Selasa)', 'Arus Mudik Sangat Padat'),
    '2026-03-18': ('H-2 (Rabu)', '★ PUNCAK ARUS MUDIK (2,26M)'),
    '2026-03-19': ('H-1 (Kamis)', 'Malam Takbiran'),
    '2026-03-20': ('H1 Lebaran (Jumat)', 'Hari Raya Idul Fitri (Drop)'),
    '2026-03-21': ('H2 Lebaran (Sabtu)', 'Silaturahmi Lokal'),
    '2026-03-22': ('H+1 (Minggu)', 'Awal Arus Balik'),
    '2026-03-23': ('H+2 (Senin)', 'Arus Balik Tinggi'),
    '2026-03-24': ('H+3 (Selasa)', '★★ PUNCAK TERTINGGI TAHUN 2026 (2,42M)'),
    '2026-03-25': ('H+4 (Rabu)', 'Puncak Bus (556k) / Balik Gel. 1'),
    '2026-03-26': ('H+5 (Kamis)', 'Arus Balik Masih Tinggi'),
    '2026-03-27': ('H+6 (Jumat)', 'Arus Balik Melandai'),
    '2026-03-28': ('H+7 (Sabtu)', 'Awal Balik Gelombang 2'),
    '2026-03-29': ('H+8 (Minggu)', '★ PUNCAK BALIK GELOMBANG 2 (1,84M)'),
    '2026-03-30': ('H+9 (Senin)', 'Mulai Normalisasi'),
    '2026-03-31': ('H+10 (Selasa)', 'Pasca Lebaran'),
    '2026-04-01': ('H+11', 'Pasca Lebaran'),
    '2026-04-02': ('H+12', 'Pasca Lebaran'),
    '2026-04-03': ('H+13', 'Pasca Lebaran'),
    '2026-04-04': ('H+14', 'Pasca Lebaran Akhir Pekan'),
    '2026-04-05': ('H+15', 'Penutupan Posko Nasional Lebaran'),
}

lebaran_daily = []
for entry in daily_timeline:
    d = entry['date']
    if d in lebaran_phase:
        tag, desc = lebaran_phase[d]
        item = dict(entry)
        item['tag'] = tag
        item['desc'] = desc
        item['is_peak_mudik'] = (d == '2026-03-18')
        item['is_peak_balik1'] = (d == '2026-03-24')
        item['is_peak_balik2'] = (d == '2026-03-29')
        lebaran_daily.append(item)

# =========================================================================
# 5. LONJAKAN TERHADAP BASELINE FEBRUARI (NORMAL)
# =========================================================================
feb_daily = df_clean[df_clean['tanggal'].between('2026-02-01', '2026-02-28')]
baseline_pnp = feb_daily.groupby('moda')['total_penumpang'].sum() / 28.0
baseline_arm = feb_daily.groupby('moda')['total_armada'].sum() / 28.0

total_baseline_pnp = float(baseline_pnp.sum())
total_baseline_arm = float(baseline_arm.sum())

d_mudik = daily_pnp.loc['2026-03-18']
d_balik1 = daily_pnp.loc['2026-03-24']
d_balik2 = daily_pnp.loc['2026-03-29']

arm_mudik = daily_arm.loc['2026-03-18']
arm_balik1 = daily_arm.loc['2026-03-24']
arm_balik2 = daily_arm.loc['2026-03-29']

surge_summary = {}
for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    base = float(baseline_pnp.get(m, 1))
    val_mudik = int(d_mudik.get(m, 0))
    val_balik1 = int(d_balik1.get(m, 0))
    val_balik2 = int(d_balik2.get(m, 0))
    surge_summary[m] = {
        'baseline': round(base),
        'peak_mudik': val_mudik,
        'surge_mudik_pct': round((val_mudik - base) / base * 100, 1),
        'peak_balik1': val_balik1,
        'surge_balik1_pct': round((val_balik1 - base) / base * 100, 1),
        'peak_balik2': val_balik2,
        'surge_balik2_pct': round((val_balik2 - base) / base * 100, 1),
    }

surge_summary['TOTAL'] = {
    'baseline': round(total_baseline_pnp),
    'peak_mudik': int(d_mudik.sum()),
    'surge_mudik_pct': round((d_mudik.sum() - total_baseline_pnp) / total_baseline_pnp * 100, 1),
    'peak_balik1': int(d_balik1.sum()),
    'surge_balik1_pct': round((d_balik1.sum() - total_baseline_pnp) / total_baseline_pnp * 100, 1),
    'peak_balik2': int(d_balik2.sum()),
    'surge_balik2_pct': round((d_balik2.sum() - total_baseline_pnp) / total_baseline_pnp * 100, 1),
}

# =========================================================================
# 6. LOAD FACTOR PROXY (PENUMPANG / ARMADA)
# =========================================================================
load_factor_stats = {}
for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    base_p = float(baseline_pnp.get(m, 0))
    base_a = float(baseline_arm.get(m, 1))
    lf_base = base_p / base_a if base_a > 0 else 0

    p_mud = float(d_mudik.get(m, 0))
    a_mud = float(arm_mudik.get(m, 1))
    lf_mud = p_mud / a_mud if a_mud > 0 else 0

    p_bal = float(d_balik1.get(m, 0))
    a_bal = float(arm_balik1.get(m, 1))
    lf_bal = p_bal / a_bal if a_bal > 0 else 0

    peak_lf = max(lf_mud, lf_bal)
    load_factor_stats[m] = {
        'baseline_lf': round(lf_base, 1),
        'mudik_lf': round(lf_mud, 1),
        'balik_lf': round(lf_bal, 1),
        'peak_lf': round(peak_lf, 1),
        'surge_lf_pct': round((peak_lf - lf_base) / lf_base * 100, 1) if lf_base > 0 else 0
    }

# =========================================================================
# 7. REGISTRI TOP HUBS (PEAK LEBARAN VS YTD)
# =========================================================================
peak_slice = df_clean[df_clean['tanggal'].between('2026-03-10', '2026-04-05')]

top_hubs_peak = {}
top_hubs_ytd = {}

for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    # Peak
    sub_p = peak_slice[peak_slice['moda'] == m]
    top_p = sub_p.groupby(['nama_prasarana', 'provinsi']).agg(
        pnp=('total_penumpang', 'sum'),
        arm=('total_armada', 'sum')
    ).reset_index().sort_values(by='pnp', ascending=False).head(10)
    top_hubs_peak[m] = top_p.to_dict(orient='records')

    # YTD
    sub_y = df_clean[df_clean['moda'] == m]
    top_y = sub_y.groupby(['nama_prasarana', 'provinsi']).agg(
        pnp=('total_penumpang', 'sum'),
        arm=('total_armada', 'sum')
    ).reset_index().sort_values(by='pnp', ascending=False).head(10)
    top_hubs_ytd[m] = top_y.to_dict(orient='records')

# =========================================================================
# 8. DAY OF WEEK PROFILE (SENIN - MINGGU)
# =========================================================================
df_clean['dow'] = pd.to_datetime(df_clean['tanggal']).dt.day_name()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_names = {'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'}

dow_pnp = df_clean.groupby(['dow', 'moda'])['total_penumpang'].mean().unstack(fill_value=0)
dow_summary = []
for d in dow_order:
    if d in dow_pnp.index:
        row = dow_pnp.loc[d]
        tot = int(row.sum())
        dow_summary.append({
            'dow': dow_names[d],
            'UDARA': round(float(row.get('UDARA', 0))),
            'KA': round(float(row.get('KA', 0))),
            'BUS': round(float(row.get('BUS', 0))),
            'ASDP': round(float(row.get('ASDP', 0))),
            'LAUT': round(float(row.get('LAUT', 0))),
            'TOTAL': tot
        })

# =========================================================================
# 9. EKSTRAKSI SIMPUL SPASIAL (LEAFLET GIS)
# Sesuai instruksi: "lat long yang kosong dikosongkan aja dulu"
# =========================================================================
nodes_df = df_clean.groupby(['moda', 'id_prasarana', 'nama_prasarana', 'provinsi'], as_index=False, dropna=False).agg(
    tipe=('tipe', 'first'),
    lat=('lat', 'first'),
    lon=('lon', 'first'),
    pnp=('total_penumpang', 'sum'),
    arm=('total_armada', 'sum'),
    p_dat=('penumpang_datang', 'sum'),
    p_brg=('penumpang_berangkat', 'sum'),
    a_dat=('armada_datang', 'sum'),
    a_brg=('armada_berangkat', 'sum'),
    days=('tanggal', 'nunique')
)

spatial_nodes = []
empty_latlon_count = 0
valid_latlon_count = 0

for _, r in nodes_df.iterrows():
    lat_str = str(r['lat']).strip() if pd.notna(r['lat']) else ''
    lon_str = str(r['lon']).strip() if pd.notna(r['lon']) else ''

    is_empty = (lat_str == '' or lat_str.lower() == 'nan' or lon_str == '' or lon_str.lower() == 'nan')
    lat_val = None
    lon_val = None
    has_coords = False

    if not is_empty:
        try:
            lt = float(lat_str)
            ln = float(lon_str)
            # Null Island (0, 0)
            if lt == 0 and ln == 0:
                is_empty = True
            # Swapped coordinates (lat > 50 & lon < 0 di Indonesia e.g. Haruku/Poka Maluku)
            elif lt > 50 and ln < 0:
                lat_val = round(ln, 6)
                lon_val = round(lt, 6)
                has_coords = True
            elif -12 <= lt <= 8 and 94 <= ln <= 142:
                lat_val = round(lt, 6)
                lon_val = round(ln, 6)
                has_coords = True
            else:
                lat_val = round(lt, 6)
                lon_val = round(ln, 6)
                has_coords = True
        except:
            is_empty = True

    if has_coords:
        valid_latlon_count += 1
    else:
        empty_latlon_count += 1
        lat_val = None
        lon_val = None

    spatial_nodes.append({
        'id': str(r['id_prasarana']),
        'm': str(r['moda']),
        'nama': str(r['nama_prasarana']),
        'p': str(r['provinsi']) if pd.notna(r['provinsi']) else '-',
        'tipe': str(r['tipe']) if pd.notna(r['tipe']) else '-',
        'lat': lat_val,
        'lon': lon_val,
        'has_coords': has_coords,
        'pnp': int(r['pnp']),
        'arm': int(r['arm']),
        'p_dat': int(r['p_dat']),
        'p_brg': int(r['p_brg']),
        'a_dat': int(r['a_dat']),
        'a_brg': int(r['a_brg']),
        'days': int(r['days'])
    })

# Urutkan simpul dari volume tertinggi
spatial_nodes.sort(key=lambda x: x['pnp'], reverse=True)

print(f"Total simpul prasarana: {len(spatial_nodes):,}")
print(f"  - Terpetakan dengan koordinat valid: {valid_latlon_count:,}")
print(f"  - Koordinat kosong (dikosongkan sesuai arahan): {empty_latlon_count:,}")

# =========================================================================
# 10. SIMPAN BUNDLE JSON TERLENGKAP
# =========================================================================
data_bundle = {
    'daily_timeline': daily_timeline,
    'monthly_summary': monthly_summary,
    'lebaran_daily': lebaran_daily,
    'surge_summary': surge_summary,
    'load_factor_stats': load_factor_stats,
    'top_hubs_peak': top_hubs_peak,
    'top_hubs_ytd': top_hubs_ytd,
    'dow_summary': dow_summary,
    'spatial_nodes': spatial_nodes,
    'meta': {
        'total_clean_rows': total_clean_rows,
        'total_passengers_ytd': total_passengers_ytd,
        'total_armada_ytd': total_armada_ytd,
        'date_min': date_min,
        'date_max': date_max,
        'days_count': days_count,
        'all_time_peak_date': '2026-03-24',
        'all_time_peak_val': int(d_balik1.sum()),
        'all_time_peak_surge_pct': round((d_balik1.sum() - total_baseline_pnp) / total_baseline_pnp * 100, 1),
        'peak_mudik_date': '2026-03-18',
        'peak_mudik_val': int(d_mudik.sum()),
        'peak_mudik_surge_pct': round((d_mudik.sum() - total_baseline_pnp) / total_baseline_pnp * 100, 1),
        'baseline_feb_avg': round(total_baseline_pnp),
        'valid_latlon_count': valid_latlon_count,
        'empty_latlon_count': empty_latlon_count,
        'total_nodes_count': len(spatial_nodes)
    }
}

json_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data_bundle, f, ensure_ascii=False)

print(f"Data bundle terbaru berhasil disimpan di {json_path}")
print(f"Ukuran file: {os.path.getsize(json_path)/(1024):.1f} KB")
