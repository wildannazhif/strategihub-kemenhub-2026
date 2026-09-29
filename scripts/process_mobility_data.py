import os
import json
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
print(f"Membaca {raw_csv}...")
df = pd.read_csv(raw_csv, low_memory=False)

# Bersihkan duplikat identik & dummy 0 ganda
metrics = ['armada_datang', 'penumpang_datang', 'armada_berangkat', 'penumpang_berangkat']
key_cols = ['moda', 'id_prasarana', 'tanggal']
df_clean = df.drop_duplicates(subset=key_cols + metrics, keep='first').copy()
tot_metric = df_clean[metrics].sum(axis=1)
dup_keys = df_clean.duplicated(subset=key_cols, keep=False)
df_clean = df_clean[~(dup_keys & (tot_metric == 0))].copy()

print(f"Data valid setelah cleaning: {len(df_clean):,} baris")

# 1. Timeline Harian
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

# 2. Agregat Bulanan
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

# 3. Periode Khusus Lebaran (10 Mar - 5 Apr 2026)
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
    '2026-03-27': ('H+6 (Jumat)', 'Arus Balik Menuju Weekend'),
    '2026-03-28': ('H+7 (Sabtu)', 'Arus Balik Gelombang 2'),
    '2026-03-29': ('H+8 (Minggu)', '★ PUNCAK BALIK GEL. 2 / UDARA (649k)'),
    '2026-03-30': ('H+9 (Senin)', 'Mulai Normalisasi'),
    '2026-03-31': ('H+10', 'Normalisasi'),
    '2026-04-01': ('H+11', 'Normalisasi'),
    '2026-04-02': ('H+12', 'Normal'),
    '2026-04-03': ('H+13', 'Normal'),
    '2026-04-04': ('H+14', 'Normal'),
    '2026-04-05': ('H+15', 'Normal'),
}

lebaran_daily = []
for item in daily_timeline:
    d = item['date']
    if d in lebaran_phase:
        tag, desc = lebaran_phase[d]
        lebaran_daily.append({
            **item,
            'tag': tag,
            'desc': desc,
            'is_peak_mudik': (d == '2026-03-18'),
            'is_peak_balik1': (d == '2026-03-24'),
            'is_peak_balik2': (d == '2026-03-29'),
            'is_h_day': (d in ['2026-03-20', '2026-03-21'])
        })

# 4. Baseline vs Peak Surges
feb_df = daily_pnp.loc['2026-02-01':'2026-02-28']
baseline = feb_df.mean().to_dict()
baseline['TOTAL'] = sum(baseline.values())

peak_mudik = daily_pnp.loc['2026-03-18'].to_dict()
peak_mudik['TOTAL'] = sum(peak_mudik.values())

peak_balik1 = daily_pnp.loc['2026-03-24'].to_dict()
peak_balik1['TOTAL'] = sum(peak_balik1.values())

peak_balik2 = daily_pnp.loc['2026-03-29'].to_dict()
peak_balik2['TOTAL'] = sum(peak_balik2.values())

surge_summary = {}
for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT', 'TOTAL']:
    b = baseline[m]
    pm = peak_mudik[m]
    pb1 = peak_balik1[m]
    pb2 = peak_balik2[m]
    surge_summary[m] = {
        'baseline': round(b),
        'peak_mudik': pm,
        'surge_mudik_pct': round((pm - b) / b * 100, 1),
        'peak_balik1': pb1,
        'surge_balik1_pct': round((pb1 - b) / b * 100, 1),
        'peak_balik2': pb2,
        'surge_balik2_pct': round((pb2 - b) / b * 100, 1),
    }

# 5. Load Factor Proxy
df_valid_armada = df_clean[df_clean['total_armada'] > 0]
feb_valid = df_valid_armada[(df_valid_armada['tanggal'] >= '2026-02-01') & (df_valid_armada['tanggal'] <= '2026-02-28')]
peak_valid = df_valid_armada[(df_valid_armada['tanggal'] >= '2026-03-18') & (df_valid_armada['tanggal'] <= '2026-03-29')]

load_factor_stats = {}
for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    sub_feb = feb_valid[feb_valid['moda'] == m]
    sub_pk = peak_valid[peak_valid['moda'] == m]
    
    r_feb = sub_feb['total_penumpang'].sum() / sub_feb['total_armada'].sum() if sub_feb['total_armada'].sum() > 0 else 0
    r_pk = sub_pk['total_penumpang'].sum() / sub_pk['total_armada'].sum() if sub_pk['total_armada'].sum() > 0 else 0
    
    load_factor_stats[m] = {
        'normal_ratio': round(r_feb, 1),
        'peak_ratio': round(r_pk, 1),
        'growth_pct': round((r_pk - r_feb) / r_feb * 100, 1) if r_feb > 0 else 0,
        'unit': 'pnp/flight' if m == 'UDARA' else ('pnp/bus' if m == 'BUS' else ('pnp/trip' if m == 'ASDP' else ('pnp/kapal' if m == 'LAUT' else 'pnp/trip KA')))
    }

# 6. Top Hubs (Peak Lebaran vs YTD)
peak_slice = df_clean[(df_clean['tanggal'] >= '2026-03-18') & (df_clean['tanggal'] <= '2026-03-29')]

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

# 7. Day of Week Analysis
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

print("Semua data agregasi mobilitas berhasil diproses!")
data_bundle = {
    'daily_timeline': daily_timeline,
    'monthly_summary': monthly_summary,
    'lebaran_daily': lebaran_daily,
    'surge_summary': surge_summary,
    'load_factor_stats': load_factor_stats,
    'top_hubs_peak': top_hubs_peak,
    'top_hubs_ytd': top_hubs_ytd,
    'dow_summary': dow_summary,
    'meta': {
        'total_clean_rows': len(df_clean),
        'total_passengers_ytd': int(df_clean['total_penumpang'].sum()),
        'total_armada_ytd': int(df_clean['total_armada'].sum()),
        'date_min': df_clean['tanggal'].min(),
        'date_max': df_clean['tanggal'].max(),
        'all_time_peak_date': '2026-03-24',
        'all_time_peak_val': 2415296
    }
}

json_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data_bundle, f, ensure_ascii=False)

print(f"Data bundle tersimpan di {json_path}")
