import os
import json
import pandas as pd
import numpy as np

print("=== MEMBANGUN BUNDLE DATA MOBILITAS TERLENGKAP & MEMPERBARUI DASHBOARD ===")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")

clean_csv_path = os.path.join(DATA_DIR, "siasati_multimoda_2026_clean_13okt.csv")
print(f"Membaca dataset bersih: {clean_csv_path}...")
df_clean = pd.read_csv(clean_csv_path, low_memory=False)

# Pastikan tipe data numerik
for col in ['penumpang_datang', 'penumpang_berangkat', 'armada_datang', 'armada_berangkat', 'total_penumpang', 'total_armada']:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)

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

print(f"Baris bersih: {total_clean_rows:,} | Rentang: {date_min} s.d. {date_max} ({days_count} hari)")
print(f"Total Pax: {total_passengers_ytd:,} | Total Armada: {total_armada_ytd:,}")

# 1. TIMELINE HARIAN (286 HARI)
daily_pnp_tot = df_clean.groupby(['tanggal', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
daily_pnp_dat = df_clean.groupby(['tanggal', 'moda'])['penumpang_datang'].sum().unstack(fill_value=0)
daily_pnp_brg = df_clean.groupby(['tanggal', 'moda'])['penumpang_berangkat'].sum().unstack(fill_value=0)

daily_arm_tot = df_clean.groupby(['tanggal', 'moda'])['total_armada'].sum().unstack(fill_value=0)
daily_arm_dat = df_clean.groupby(['tanggal', 'moda'])['armada_datang'].sum().unstack(fill_value=0)
daily_arm_brg = df_clean.groupby(['tanggal', 'moda'])['armada_berangkat'].sum().unstack(fill_value=0)

dates = sorted(daily_pnp_tot.index.tolist())
daily_timeline = []

for d in dates:
    p_tot = daily_pnp_tot.loc[d]
    p_dat = daily_pnp_dat.loc[d]
    p_brg = daily_pnp_brg.loc[d]
    a_tot = daily_arm_tot.loc[d]
    a_dat = daily_arm_dat.loc[d]
    a_brg = daily_arm_brg.loc[d]
    
    daily_timeline.append({
        'date': d,
        # Penumpang Total
        'UDARA': int(p_tot.get('UDARA', 0)),
        'KA': int(p_tot.get('KA', 0)),
        'BUS': int(p_tot.get('BUS', 0)),
        'ASDP': int(p_tot.get('ASDP', 0)),
        'LAUT': int(p_tot.get('LAUT', 0)),
        'TOTAL': int(p_tot.sum()),
        # Penumpang Datang
        'pdat_UDARA': int(p_dat.get('UDARA', 0)),
        'pdat_KA': int(p_dat.get('KA', 0)),
        'pdat_BUS': int(p_dat.get('BUS', 0)),
        'pdat_ASDP': int(p_dat.get('ASDP', 0)),
        'pdat_LAUT': int(p_dat.get('LAUT', 0)),
        'pdat_TOTAL': int(p_dat.sum()),
        # Penumpang Berangkat
        'pbrg_UDARA': int(p_brg.get('UDARA', 0)),
        'pbrg_KA': int(p_brg.get('KA', 0)),
        'pbrg_BUS': int(p_brg.get('BUS', 0)),
        'pbrg_ASDP': int(p_brg.get('ASDP', 0)),
        'pbrg_LAUT': int(p_brg.get('LAUT', 0)),
        'pbrg_TOTAL': int(p_brg.sum()),
        # Armada Total
        'arm_UDARA': int(a_tot.get('UDARA', 0)),
        'arm_KA': int(a_tot.get('KA', 0)),
        'arm_BUS': int(a_tot.get('BUS', 0)),
        'arm_ASDP': int(a_tot.get('ASDP', 0)),
        'arm_LAUT': int(a_tot.get('LAUT', 0)),
        'arm_TOTAL': int(a_tot.sum()),
        # Armada Datang
        'adat_UDARA': int(a_dat.get('UDARA', 0)),
        'adat_KA': int(a_dat.get('KA', 0)),
        'adat_BUS': int(a_dat.get('BUS', 0)),
        'adat_ASDP': int(a_dat.get('ASDP', 0)),
        'adat_LAUT': int(a_dat.get('LAUT', 0)),
        'adat_TOTAL': int(a_dat.sum()),
        # Armada Berangkat
        'abrg_UDARA': int(a_brg.get('UDARA', 0)),
        'abrg_KA': int(a_brg.get('KA', 0)),
        'abrg_BUS': int(a_brg.get('BUS', 0)),
        'abrg_ASDP': int(a_brg.get('ASDP', 0)),
        'abrg_LAUT': int(a_brg.get('LAUT', 0)),
        'abrg_TOTAL': int(a_brg.sum()),
    })

print(f"Daily timeline dibangun: {len(daily_timeline)} hari")

# 2. AGREGAT BULANAN
df_clean['bulan'] = df_clean['tanggal'].str[:7]
m_pnp_tot = df_clean.groupby(['bulan', 'moda'])['total_penumpang'].sum().unstack(fill_value=0)
m_pnp_dat = df_clean.groupby(['bulan', 'moda'])['penumpang_datang'].sum().unstack(fill_value=0)
m_pnp_brg = df_clean.groupby(['bulan', 'moda'])['penumpang_berangkat'].sum().unstack(fill_value=0)

m_arm_tot = df_clean.groupby(['bulan', 'moda'])['total_armada'].sum().unstack(fill_value=0)
m_arm_dat = df_clean.groupby(['bulan', 'moda'])['armada_datang'].sum().unstack(fill_value=0)
m_arm_brg = df_clean.groupby(['bulan', 'moda'])['armada_berangkat'].sum().unstack(fill_value=0)

months = sorted(m_pnp_tot.index.tolist())
month_names = {
    '2026-01': 'Januari', '2026-02': 'Februari', '2026-03': 'Maret (Lebaran)',
    '2026-04': 'April', '2026-05': 'Mei', '2026-06': 'Juni (Liburan Sekolah)',
    '2026-07': 'Juli (Liburan Sekolah)', '2026-08': 'Agustus', '2026-09': 'September',
    '2026-10': 'Oktober (s.d. 13 Okt)*'
}

monthly_summary = []
for m in months:
    pt = m_pnp_tot.loc[m]
    pd_ = m_pnp_dat.loc[m]
    pb = m_pnp_brg.loc[m]
    at = m_arm_tot.loc[m]
    ad = m_arm_dat.loc[m]
    ab = m_arm_brg.loc[m]
    
    tot_pt = int(pt.sum())
    tot_pd = int(pd_.sum())
    tot_pb = int(pb.sum())
    tot_at = int(at.sum())
    tot_ad = int(ad.sum())
    tot_ab = int(ab.sum())

    monthly_summary.append({
        'bulan': m,
        'label': month_names.get(m, m),
        # Penumpang Total
        'UDARA': int(pt.get('UDARA', 0)), 'KA': int(pt.get('KA', 0)), 'BUS': int(pt.get('BUS', 0)), 'ASDP': int(pt.get('ASDP', 0)), 'LAUT': int(pt.get('LAUT', 0)), 'TOTAL': tot_pt,
        'share_UDARA': round(float(pt.get('UDARA', 0)) / tot_pt * 100, 1) if tot_pt > 0 else 0,
        'share_KA': round(float(pt.get('KA', 0)) / tot_pt * 100, 1) if tot_pt > 0 else 0,
        'share_BUS': round(float(pt.get('BUS', 0)) / tot_pt * 100, 1) if tot_pt > 0 else 0,
        'share_ASDP': round(float(pt.get('ASDP', 0)) / tot_pt * 100, 1) if tot_pt > 0 else 0,
        'share_LAUT': round(float(pt.get('LAUT', 0)) / tot_pt * 100, 1) if tot_pt > 0 else 0,
        # Penumpang Datang
        'pdat_UDARA': int(pd_.get('UDARA', 0)), 'pdat_KA': int(pd_.get('KA', 0)), 'pdat_BUS': int(pd_.get('BUS', 0)), 'pdat_ASDP': int(pd_.get('ASDP', 0)), 'pdat_LAUT': int(pd_.get('LAUT', 0)), 'pdat_TOTAL': tot_pd,
        'pdat_share_UDARA': round(float(pd_.get('UDARA', 0)) / tot_pd * 100, 1) if tot_pd > 0 else 0,
        'pdat_share_KA': round(float(pd_.get('KA', 0)) / tot_pd * 100, 1) if tot_pd > 0 else 0,
        'pdat_share_BUS': round(float(pd_.get('BUS', 0)) / tot_pd * 100, 1) if tot_pd > 0 else 0,
        'pdat_share_ASDP': round(float(pd_.get('ASDP', 0)) / tot_pd * 100, 1) if tot_pd > 0 else 0,
        'pdat_share_LAUT': round(float(pd_.get('LAUT', 0)) / tot_pd * 100, 1) if tot_pd > 0 else 0,
        # Penumpang Berangkat
        'pbrg_UDARA': int(pb.get('UDARA', 0)), 'pbrg_KA': int(pb.get('KA', 0)), 'pbrg_BUS': int(pb.get('BUS', 0)), 'pbrg_ASDP': int(pb.get('ASDP', 0)), 'pbrg_LAUT': int(pb.get('LAUT', 0)), 'pbrg_TOTAL': tot_pb,
        'pbrg_share_UDARA': round(float(pb.get('UDARA', 0)) / tot_pb * 100, 1) if tot_pb > 0 else 0,
        'pbrg_share_KA': round(float(pb.get('KA', 0)) / tot_pb * 100, 1) if tot_pb > 0 else 0,
        'pbrg_share_BUS': round(float(pb.get('BUS', 0)) / tot_pb * 100, 1) if tot_pb > 0 else 0,
        'pbrg_share_ASDP': round(float(pb.get('ASDP', 0)) / tot_pb * 100, 1) if tot_pb > 0 else 0,
        'pbrg_share_LAUT': round(float(pb.get('LAUT', 0)) / tot_pb * 100, 1) if tot_pb > 0 else 0,
        # Armada Total
        'arm_UDARA': int(at.get('UDARA', 0)), 'arm_KA': int(at.get('KA', 0)), 'arm_BUS': int(at.get('BUS', 0)), 'arm_ASDP': int(at.get('ASDP', 0)), 'arm_LAUT': int(at.get('LAUT', 0)), 'arm_TOTAL': tot_at, 'TOTAL_ARMADA': tot_at,
        'arm_share_UDARA': round(float(at.get('UDARA', 0)) / tot_at * 100, 1) if tot_at > 0 else 0,
        'arm_share_KA': round(float(at.get('KA', 0)) / tot_at * 100, 1) if tot_at > 0 else 0,
        'arm_share_BUS': round(float(at.get('BUS', 0)) / tot_at * 100, 1) if tot_at > 0 else 0,
        'arm_share_ASDP': round(float(at.get('ASDP', 0)) / tot_at * 100, 1) if tot_at > 0 else 0,
        'arm_share_LAUT': round(float(at.get('LAUT', 0)) / tot_at * 100, 1) if tot_at > 0 else 0,
        # Armada Datang
        'adat_UDARA': int(ad.get('UDARA', 0)), 'adat_KA': int(ad.get('KA', 0)), 'adat_BUS': int(ad.get('BUS', 0)), 'adat_ASDP': int(ad.get('ASDP', 0)), 'adat_LAUT': int(ad.get('LAUT', 0)), 'adat_TOTAL': tot_ad,
        # Armada Berangkat
        'abrg_UDARA': int(ab.get('UDARA', 0)), 'abrg_KA': int(ab.get('KA', 0)), 'abrg_BUS': int(ab.get('BUS', 0)), 'abrg_ASDP': int(ab.get('ASDP', 0)), 'abrg_LAUT': int(ab.get('LAUT', 0)), 'abrg_TOTAL': tot_ab,
    })

print(f"Monthly summary dibangun: {len(monthly_summary)} bulan")

# 3. PERIODE KHUSUS LEBARAN
lebaran_phase = {
    '2026-03-13': ('H-8', 'Awal Masa Posko Angkutan Lebaran'),
    '2026-03-14': ('H-7 (Sabtu)', 'Awal Arus Mudik Akhir Pekan'),
    '2026-03-15': ('H-6 (Minggu)', 'Arus Mudik Akhir Pekan'),
    '2026-03-16': ('H-5 (Senin)', 'Arus Mudik Mulai Meningkat'),
    '2026-03-17': ('H-4 (Selasa)', 'Arus Mudik Padat'),
    '2026-03-18': ('H-3 (Rabu)', '★ PUNCAK ARUS MUDIK (2,26M)'),
    '2026-03-19': ('H-2 (Kamis)', 'Arus Mudik Lanjutan'),
    '2026-03-20': ('H-1 (Jumat)', 'Malam Takbiran'),
    '2026-03-21': ('Hari H (Sabtu)', 'Hari Raya Idul Fitri 1447 H'),
    '2026-03-22': ('H+1 (Minggu)', 'Silaturahmi & Awal Arus Balik'),
    '2026-03-23': ('H+2 (Senin)', 'Arus Balik Tinggi'),
    '2026-03-24': ('H+3 (Selasa)', '★★ PUNCAK TERTINGGI TAHUN 2026 (2,42M)'),
    '2026-03-25': ('H+4 (Rabu)', 'Arus Balik Masih Tinggi (2,35M)'),
    '2026-03-26': ('H+5 (Kamis)', 'Arus Balik Berlanjut (2,21M)'),
    '2026-03-27': ('H+6 (Jumat)', 'Arus Balik Gelombang Akhir Pekan (2,17M)'),
    '2026-03-28': ('H+7 (Sabtu)', 'Arus Balik Akhir Pekan (2,28M)'),
    '2026-03-29': ('H+8 (Minggu)', '★ PUNCAK BALIK GELOMBANG 2 & PENUTUPAN (2,33M)'),
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
        item['is_h_day'] = (d == '2026-03-21')
        lebaran_daily.append(item)

# 4. LONJAKAN BASELINE FEBRUARI
feb_daily = df_clean[df_clean['tanggal'].between('2026-02-01', '2026-02-28')]
baseline_pnp = feb_daily.groupby('moda')['total_penumpang'].sum() / 28.0
baseline_arm = feb_daily.groupby('moda')['total_armada'].sum() / 28.0

total_baseline_pnp = float(baseline_pnp.sum())
total_baseline_arm = float(baseline_arm.sum())

d_mudik = daily_pnp_tot.loc['2026-03-18']
d_balik1 = daily_pnp_tot.loc['2026-03-24']
d_balik2 = daily_pnp_tot.loc['2026-03-29']

arm_mudik = daily_arm_tot.loc['2026-03-18']
arm_balik1 = daily_arm_tot.loc['2026-03-24']
arm_balik2 = daily_arm_tot.loc['2026-03-29']

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

# 5. LOAD FACTOR
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

# 6. TOP HUBS (PEAK VS YTD 286 HARI)
peak_slice = df_clean[df_clean['tanggal'].between('2026-03-13', '2026-03-29')]
top_hubs_peak = {}
top_hubs_ytd = {}

for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    # Peak (top 30)
    sub_p = peak_slice[peak_slice['moda'] == m]
    top_p = sub_p.groupby(['nama_prasarana', 'provinsi']).agg(
        pnp=('total_penumpang', 'sum'),
        p_dat=('penumpang_datang', 'sum'),
        p_brg=('penumpang_berangkat', 'sum'),
        arm=('total_armada', 'sum'),
        a_dat=('armada_datang', 'sum'),
        a_brg=('armada_berangkat', 'sum')
    ).reset_index().sort_values(by='pnp', ascending=False).head(30)
    top_hubs_peak[m] = top_p.to_dict(orient='records')

    # YTD 286 hari (top 30)
    sub_y = df_clean[df_clean['moda'] == m]
    top_y = sub_y.groupby(['nama_prasarana', 'provinsi']).agg(
        pnp=('total_penumpang', 'sum'),
        p_dat=('penumpang_datang', 'sum'),
        p_brg=('penumpang_berangkat', 'sum'),
        arm=('total_armada', 'sum'),
        a_dat=('armada_datang', 'sum'),
        a_brg=('armada_berangkat', 'sum')
    ).reset_index().sort_values(by='pnp', ascending=False).head(30)
    top_hubs_ytd[m] = top_y.to_dict(orient='records')

# 7. DAY OF WEEK PROFILE (SENIN - MINGGU)
dow_df = pd.DataFrame(daily_timeline).set_index('date')
dow_df['dow'] = pd.to_datetime(dow_df.index).day_name()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_names = {'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'}

dow_summary = []
for d in dow_order:
    sub = dow_df[dow_df['dow'] == d]
    if len(sub) > 0:
        dow_summary.append({
            'dow': dow_names[d],
            'UDARA': round(float(sub['UDARA'].mean())),
            'KA': round(float(sub['KA'].mean())),
            'BUS': round(float(sub['BUS'].mean())),
            'ASDP': round(float(sub['ASDP'].mean())),
            'LAUT': round(float(sub['LAUT'].mean())),
            'TOTAL': round(float(sub['TOTAL'].mean())),
            'pdat_UDARA': round(float(sub['pdat_UDARA'].mean())),
            'pdat_KA': round(float(sub['pdat_KA'].mean())),
            'pdat_BUS': round(float(sub['pdat_BUS'].mean())),
            'pdat_ASDP': round(float(sub['pdat_ASDP'].mean())),
            'pdat_LAUT': round(float(sub['pdat_LAUT'].mean())),
            'pdat_TOTAL': round(float(sub['pdat_TOTAL'].mean())),
            'pbrg_UDARA': round(float(sub['pbrg_UDARA'].mean())),
            'pbrg_KA': round(float(sub['pbrg_KA'].mean())),
            'pbrg_BUS': round(float(sub['pbrg_BUS'].mean())),
            'pbrg_ASDP': round(float(sub['pbrg_ASDP'].mean())),
            'pbrg_LAUT': round(float(sub['pbrg_LAUT'].mean())),
            'pbrg_TOTAL': round(float(sub['pbrg_TOTAL'].mean())),
            'arm_UDARA': round(float(sub['arm_UDARA'].mean())),
            'arm_KA': round(float(sub['arm_KA'].mean())),
            'arm_BUS': round(float(sub['arm_BUS'].mean())),
            'arm_ASDP': round(float(sub['arm_ASDP'].mean())),
            'arm_LAUT': round(float(sub['arm_LAUT'].mean())),
            'arm_TOTAL': round(float(sub['arm_TOTAL'].mean())),
            'adat_UDARA': round(float(sub['adat_UDARA'].mean())),
            'adat_KA': round(float(sub['adat_KA'].mean())),
            'adat_BUS': round(float(sub['adat_BUS'].mean())),
            'adat_ASDP': round(float(sub['adat_ASDP'].mean())),
            'adat_LAUT': round(float(sub['adat_LAUT'].mean())),
            'adat_TOTAL': round(float(sub['adat_TOTAL'].mean())),
            'abrg_UDARA': round(float(sub['abrg_UDARA'].mean())),
            'abrg_KA': round(float(sub['abrg_KA'].mean())),
            'abrg_BUS': round(float(sub['abrg_BUS'].mean())),
            'abrg_ASDP': round(float(sub['abrg_ASDP'].mean())),
            'abrg_LAUT': round(float(sub['abrg_LAUT'].mean())),
            'abrg_TOTAL': round(float(sub['abrg_TOTAL'].mean())),
        })

# 8. SIMPUL SPASIAL (GIS LEAFLET)
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
            if lt == 0 and ln == 0:
                is_empty = True
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

spatial_nodes.sort(key=lambda x: x['pnp'], reverse=True)

# 9. METRICS SUMMARY (6 METRIK)
combos = {
    'pnp_tot': ('total_penumpang', 'Penumpang • Dua Arah (Total)', 'penumpang', '∑ (P_datang + P_berangkat)'),
    'pnp_dat': ('penumpang_datang', 'Penumpang Datang (Kedatangan)', 'penumpang datang', '∑ P_datang'),
    'pnp_brg': ('penumpang_berangkat', 'Penumpang Berangkat (Keberangkatan)', 'penumpang berangkat', '∑ P_berangkat'),
    'arm_tot': ('total_armada', 'Total Armada Beroperasi (Dua Arah)', 'trip armada', '∑ (Trip Datang + Trip Berangkat)'),
    'arm_dat': ('armada_datang', 'Armada Datang (Kedatangan)', 'trip datang', '∑ Trip_datang'),
    'arm_brg': ('armada_berangkat', 'Armada Berangkat (Keberangkatan)', 'trip berangkat', '∑ Trip_berangkat'),
}

metrics_summary = {}
for code, (col, label, unit, formula) in combos.items():
    s_daily = df_clean.groupby('tanggal')[col].sum()
    ytd_val = int(s_daily.sum())
    avg_val = int(round(s_daily.mean()))
    
    p_max = int(s_daily.max())
    d_max = s_daily.idxmax()
    
    mudik_s = s_daily.loc['2026-03-13':'2026-03-20']
    p_mud = int(mudik_s.max())
    d_mud = mudik_s.idxmax()
    
    feb_avg = float(s_daily.loc['2026-02-01':'2026-02-28'].mean())
    surge_peak = round((p_max - feb_avg) / feb_avg * 100, 1) if feb_avg > 0 else 0
    surge_mud = round((p_mud - feb_avg) / feb_avg * 100, 1) if feb_avg > 0 else 0
    
    tag_peak = lebaran_phase.get(d_max, ('Puncak', ''))[0]
    tag_mud = lebaran_phase.get(d_mud, ('Puncak Mudik', ''))[0]

    metrics_summary[code] = {
        'label': label,
        'unit': unit,
        'formula': formula,
        'ytd': ytd_val,
        'avg': avg_val,
        'peak_date': d_max,
        'peak_val': p_max,
        'peak_tag': tag_peak,
        'peak_surge_pct': surge_peak,
        'mudik_date': d_mud,
        'mudik_val': p_mud,
        'mudik_tag': tag_mud,
        'mudik_surge_pct': surge_mud,
        'baseline_feb': round(feb_avg)
    }

# 10. MULTI-METRIC PROVINCE MONTHLY DATA (10 BULAN)
df_clean['month_num'] = pd.to_datetime(df_clean['tanggal']).dt.month
m_names = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei',
    6: 'Juni', 7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober*'
}
s_names = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei',
    6: 'Jun', 7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt'
}

metrics_map = {
    'pnp_brg': {'col': 'penumpang_berangkat', 'unit': 'pnp', 'label': 'Penumpang Berangkat'},
    'pnp_dat': {'col': 'penumpang_datang', 'unit': 'pnp', 'label': 'Penumpang Datang'},
    'pnp_tot': {'col': 'total_penumpang', 'unit': 'pnp', 'label': 'Total Penumpang'},
    'arm_brg': {'col': 'armada_berangkat', 'unit': 'trip', 'label': 'Armada Berangkat'},
    'arm_dat': {'col': 'armada_datang', 'unit': 'trip', 'label': 'Armada Datang'},
    'arm_tot': {'col': 'total_armada', 'unit': 'trip', 'label': 'Total Armada'}
}

all_metrics_data = {}
for m_key, m_info in metrics_map.items():
    col = m_info['col']
    p_m = df_clean.groupby(['provinsi', 'month_num'])[col].sum().unstack(fill_value=0)
    p_m_moda = df_clean.groupby(['provinsi', 'month_num', 'moda'])[col].sum().unstack(fill_value=0).reset_index()
    top_provinces = p_m.sum(axis=1).sort_values(ascending=False).index.tolist()
    sorted_provinces = sorted(top_provinces)
    
    prov_summary = {}
    for p in top_provinces:
        monthly = []
        prev_val = None
        peak_m = 1
        peak_vol = 0
        sub_moda = p_m_moda[p_m_moda['provinsi'] == p].set_index('month_num')
        
        for m in range(1, 11):
            val = int(p_m.loc[p, m]) if (p in p_m.index and m in p_m.columns) else 0
            mom = round(((val - prev_val) / prev_val) * 100, 1) if (prev_val is not None and prev_val > 0) else None
            prev_val = val
            
            if val > peak_vol:
                peak_vol = val
                peak_m = m
                
            modas = {mod: int(sub_moda.loc[m, mod]) if (m in sub_moda.index and mod in sub_moda.columns) else 0 for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']}
            dom_moda = max(modas.items(), key=lambda x: x[1]) if modas else ('-', 0)
            dom_pct = round((dom_moda[1] / val * 100), 1) if val > 0 else 0
            
            monthly.append({
                'm': m,
                'name': m_names[m],
                'short': s_names[m],
                'val': val,
                'brg': val,
                'mom': mom,
                'dom_moda': dom_moda[0],
                'dom_pct': dom_pct,
                'is_peak': False,
                'modas': modas
            })
            
        vals = [x['val'] for x in monthly]
        med_vol = float(np.median(vals))
        for item in monthly:
            if item['m'] == peak_m:
                item['is_peak'] = True
            item['vs_median'] = round(((item['val'] - med_vol) / med_vol) * 100, 1) if med_vol > 0 else 0.0
                
        max_jump_vs_med = round(((peak_vol - med_vol) / med_vol) * 100, 1) if med_vol > 0 else 0.0
        
        prov_summary[p] = {
            'provinsi': p,
            'total': int(p_m.loc[p].sum()) if p in p_m.index else 0,
            'total_brg': int(p_m.loc[p].sum()) if p in p_m.index else 0,
            'peak_month': m_names[peak_m],
            'peak_month_num': peak_m,
            'peak_vol': peak_vol,
            'median_vol': int(med_vol),
            'max_jump_month': m_names[peak_m],
            'max_jump_pct': max_jump_vs_med,
            'max_jump_vs_median_pct': max_jump_vs_med,
            'monthly': monthly
        }
    
    # Nasional
    all_monthly = []
    all_prev_val = None
    all_peak_m = 1
    all_peak_vol = 0
    for m in range(1, 11):
        m_modas = {mod: sum(prov_summary[pr]['monthly'][m-1]['modas'][mod] for pr in top_provinces) for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']}
        m_val = sum(m_modas.values())
        mom = round(((m_val - all_prev_val) / all_prev_val) * 100, 1) if (all_prev_val is not None and all_prev_val > 0) else None
        all_prev_val = m_val
        
        if m_val > all_peak_vol:
            all_peak_vol = m_val
            all_peak_m = m
            
        dom_moda = max(m_modas.items(), key=lambda x: x[1]) if m_modas else ('-', 0)
        dom_pct = round((dom_moda[1] / m_val * 100), 1) if m_val > 0 else 0
        
        all_monthly.append({
            'm': m,
            'name': m_names[m],
            'short': s_names[m],
            'val': m_val,
            'brg': m_val,
            'mom': mom,
            'dom_moda': dom_moda[0],
            'dom_pct': dom_pct,
            'is_peak': False,
            'modas': m_modas
        })
        
    all_vals = [x['val'] for x in all_monthly]
    all_med_vol = float(np.median(all_vals))
    for item in all_monthly:
        if item['m'] == all_peak_m:
            item['is_peak'] = True
        item['vs_median'] = round(((item['val'] - all_med_vol) / all_med_vol) * 100, 1) if all_med_vol > 0 else 0.0
        
    all_max_jump = round(((all_peak_vol - all_med_vol) / all_med_vol) * 100, 1) if all_med_vol > 0 else 0.0
    
    prov_summary['ALL'] = {
        'provinsi': 'Seluruh Provinsi (Nasional)',
        'total': sum(all_vals),
        'total_brg': sum(all_vals),
        'peak_month': m_names[all_peak_m],
        'peak_month_num': all_peak_m,
        'peak_vol': all_peak_vol,
        'median_vol': int(all_med_vol),
        'max_jump_month': m_names[all_peak_m],
        'max_jump_pct': all_max_jump,
        'max_jump_vs_median_pct': all_max_jump,
        'monthly': all_monthly
    }
    prov_summary['Seluruh Provinsi'] = prov_summary['ALL']
        
    monthly_rankings = {}
    for m in range(1, 11):
        vols = p_m[m].sort_values(ascending=False) if m in p_m.columns else pd.Series(dtype=float)
        top_vol = [{'provinsi': prov, 'vol': int(vols[prov])} for prov in vols.head(8).index]
        top_growth = []
        growths = {}
        for prov in top_provinces:
            v_curr = p_m.loc[prov, m] if (prov in p_m.index and m in p_m.columns) else 0
            med_v = prov_summary[prov]['median_vol']
            threshold = 15000 if 'pnp' in m_key else 300
            if med_v > threshold:
                growths[prov] = round(((v_curr - med_v) / med_v) * 100, 1)
        sorted_g = sorted(growths.items(), key=lambda x: x[1], reverse=True)[:8]
        top_growth = [{'provinsi': k, 'mom': v, 'vs_median': v, 'vol': int(p_m.loc[k, m])} for k, v in sorted_g]
            
        monthly_rankings[m] = {
            'month': m,
            'name': m_names[m],
            'top_vol': top_vol,
            'top_growth': top_growth
        }
        
    all_metrics_data[m_key] = {
        'provinces': sorted_provinces,
        'by_province': prov_summary,
        'by_month': monthly_rankings
    }

province_monthly_data = {
    **all_metrics_data,
    'by_metric': all_metrics_data,
    'provinces': all_metrics_data['pnp_brg']['provinces'],
    'by_province': all_metrics_data['pnp_brg']['by_province'],
    'by_month': all_metrics_data['pnp_brg']['by_month']
}

# 11. BACA BUNDLE LAMA UNTUK MEMPERTAHANKAN MODEL PREDIKSI & GEODATA
existing_bundle_path = os.path.join(SCRIPTS_DIR, "mobility_data_bundle.json")
with open(existing_bundle_path, 'r', encoding='utf-8') as f:
    old_bundle = json.load(f)

# Pertahankan load_factor_stats ekstensi (provinces, by_province, ALL)
for k in ['ALL', 'provinces', 'by_province']:
    if k in old_bundle.get('load_factor_stats', {}):
        load_factor_stats[k] = old_bundle['load_factor_stats'][k]

meta = {
    'total_clean_rows': total_clean_rows,
    'total_passengers_ytd': total_passengers_ytd,
    'total_armada_ytd': total_armada_ytd,
    'total_pnp_dat_ytd': total_pnp_dat_ytd,
    'total_pnp_brg_ytd': total_pnp_brg_ytd,
    'total_arm_dat_ytd': total_arm_dat_ytd,
    'total_arm_brg_ytd': total_arm_brg_ytd,
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

# Susun bundle baru lengkap
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
    'metrics_summary': metrics_summary,
    'meta': meta,
    # Bagian ekstensi yang dipertahankan utuh
    'forecast_nataru': old_bundle.get('forecast_nataru', {}),
    'timeline_2025': old_bundle.get('timeline_2025', []),
    'simpul_recommendations': old_bundle.get('simpul_recommendations', []),
    'province_monthly_data': province_monthly_data,
    'province_geojson': old_bundle.get('province_geojson', {})
}

# Simpan bundle ke scripts/ dan data/
with open(existing_bundle_path, 'w', encoding='utf-8') as f:
    json.dump(data_bundle, f, ensure_ascii=False)
print(f"Bundle tersimpan di {existing_bundle_path} ({os.path.getsize(existing_bundle_path)/1024:.1f} KB)")

bundle_data_path = os.path.join(DATA_DIR, "mobility_data_bundle.json")
with open(bundle_data_path, 'w', encoding='utf-8') as f:
    json.dump(data_bundle, f, ensure_ascii=False)
print(f"Bundle tersimpan di {bundle_data_path} ({os.path.getsize(bundle_data_path)/1024:.1f} KB)")

# =========================================================================
# 12. UPDATE INDEX.HTML SECARA PRESISI
# =========================================================================
index_path = os.path.join(BASE_DIR, "index.html")
print(f"\nMemperbarui {index_path}...")

with open(index_path, 'r', encoding='utf-8') as f:
    html_lines = f.readlines()

new_lines = []
avg_pnp_daily_fmt = f"{round(total_passengers_ytd / days_count):,}".replace(',', '.')
total_pnp_ytd_fmt = f"{total_passengers_ytd:,}".replace(',', '.')
total_clean_rows_fmt = f"{total_clean_rows:,}".replace(',', '.')

bundle_json_single_line = json.dumps(data_bundle, ensure_ascii=False)

for i, line in enumerate(html_lines, 1):
    # Line 2572 adalah deklarasi const DATA
    if line.startswith("const DATA ="):
        new_lines.append(f"const DATA = {bundle_json_single_line};\n")
        continue
        
    l = line
    # Teks rentang waktu & hari
    l = l.replace("Kronologi Harian (272 Hari)", "Kronologi Harian (286 Hari)")
    l = l.replace("Kronologi Harian (272H)", "Kronologi Harian (286H)")
    l = l.replace("Kronologi Harian (272 HARI)", "Kronologi Harian (286 HARI)")
    l = l.replace("(272 HARI)", "(286 HARI)")
    l = l.replace("1 Jan - 29 Sep (272H)", "1 Jan - 13 Okt (286H)")
    l = l.replace("1 Jan - 29 Sep", "1 Jan - 13 Okt")
    l = l.replace("1 Jan s.d. 29 Sep 2026", "1 Jan s.d. 13 Okt 2026")
    l = l.replace("01 Jan s.d. 29 Sep 2026", "01 Jan s.d. 13 Okt 2026")
    l = l.replace("1 Jan 2026 - 29 Sep 2026 (272 Hari)", "1 Jan 2026 - 13 Okt 2026 (286 Hari)")
    l = l.replace("1 Jan  29 Sep 2026", "1 Jan - 13 Okt 2026")
    l = l.replace("1 Jan - 29 Sep 2026", "1 Jan - 13 Okt 2026")
    l = l.replace("(272 hari)", "(286 hari)")
    l = l.replace("(272 hari kontinu)", "(286 hari kontinu)")
    l = l.replace(">272 Hari<", ">286 Hari<")
    l = l.replace(">272H<", ">286H<")
    l = l.replace("'all': '1 Jan 2026 - 29 Sep 2026 (272 Hari)'", "'all': '1 Jan 2026 - 13 Okt 2026 (286 Hari)'")
    l = l.replace("/ 272)", f"/ {days_count})")
    
    # Static card values fallback
    l = l.replace("209.143.560", f"{total_pnp_brg_ytd:,}".replace(',', '.'))
    l = l.replace("768.910", f"{round(total_pnp_brg_ytd / days_count):,}".replace(',', '.'))
    l = l.replace("5.096.641", f"{total_arm_brg_ytd:,}".replace(',', '.'))
    
    # Catatan bulanan
    if "Data bulan September 2026 merupakan data berjalan" in l:
        l = "              Data bulan Oktober 2026 merupakan data berjalan s.d. 13 Oktober (13 hari kalender operasional).\n"
    
    # Rumus KaTeX
    if "371.890.120" in l and "272" in l:
        l = f"              $$P_{{\\text{{avg}}}} = \\frac{{\\sum_{{t=1}}^{{N}} P_{{\\text{{total}}, t}}}}{{N}} = \\frac{{{total_pnp_ytd_fmt}}}{{286}} = {avg_pnp_daily_fmt}\\text{{ pnp/hari}}$$\n"
    elif "371.890.120" in l:
        l = l.replace("371.890.120", total_pnp_ytd_fmt)
        
    if "371890120" in l:
        l = l.replace("371890120", str(total_passengers_ytd))
    if "10033092" in l:
        l = l.replace("10033092", str(total_armada_ytd))
        
    if "Terverifikasi Bersih:" in l and "1 Jan - 29 Sep" in l:
        l = f"              Terverifikasi Bersih: {total_clean_rows_fmt} baris • 1 Jan - 13 Okt 2026\n"
        
    new_lines.append(l)

with open(index_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"File index.html berhasil diperbarui ({os.path.getsize(index_path)/1024:.1f} KB)!")

# Salin ke Dashboard_Mobilitas_Nasional_2026.html
dash_path = os.path.join(BASE_DIR, "Dashboard_Mobilitas_Nasional_2026.html")
with open(dash_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"File Dashboard_Mobilitas_Nasional_2026.html berhasil disinkronkan secara identik ({os.path.getsize(dash_path)/1024:.1f} KB)!")
print("=== SEMUA PROSES PEMUTAKHIRAN BERHASIL SELESAI DENGAN PARITAS 100% ===")
