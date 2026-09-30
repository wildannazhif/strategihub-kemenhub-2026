import os
import json
import pandas as pd
import numpy as np

raw_csv = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
print(f"Membaca dataset terbaru dari: {raw_csv}...")
df = pd.read_csv(raw_csv, low_memory=False)

print(f"Total baris mentah: {len(df):,}")

# 1. CLEANING
# A. Drop duplikat sama persis
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
total_pnp_dat_ytd = int(df_clean['penumpang_datang'].sum())
total_pnp_brg_ytd = int(df_clean['penumpang_berangkat'].sum())

total_armada_ytd = int(df_clean['total_armada'].sum())
total_arm_dat_ytd = int(df_clean['armada_datang'].sum())
total_arm_brg_ytd = int(df_clean['armada_berangkat'].sum())

date_min = df_clean['tanggal'].min()
date_max = df_clean['tanggal'].max()
days_count = df_clean['tanggal'].nunique()

print(f"Baris bersih final setelah agregasi sum: {total_clean_rows:,}")
print(f"Total Mobilitas Penumpang YTD: {total_passengers_ytd:,} (Datang: {total_pnp_dat_ytd:,}, Berangkat: {total_pnp_brg_ytd:,})")
print(f"Total Armada Beroperasi YTD: {total_armada_ytd:,} (Datang: {total_arm_dat_ytd:,}, Berangkat: {total_arm_brg_ytd:,})")
print(f"Rentang Tanggal: {date_min} s/d {date_max} ({days_count} hari)")

# =========================================================================
# 2. TIMELINE HARIAN (272 HARI) DENGAN METRIK TOTAL, DATANG, BERANGKAT
# =========================================================================
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

# =========================================================================
# 3. AGREGAT BULANAN
# =========================================================================
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
    '2026-07': 'Juli (Liburan Sekolah)', '2026-08': 'Agustus', '2026-09': 'September*'
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

# =========================================================================
# 4. PERIODE KHUSUS LEBARAN (13 MAR - 29 MAR 2026 • 17 HARI)
# =========================================================================
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

# =========================================================================
# 5. LONJAKAN TERHADAP BASELINE FEBRUARI (NORMAL)
# =========================================================================
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
# 7. REGISTRI TOP HUBS (PEAK LEBARAN VS YTD) DENGAN METRIK DIRECTIONAL
# =========================================================================
peak_slice = df_clean[df_clean['tanggal'].between('2026-03-13', '2026-03-29')]

top_hubs_peak = {}
top_hubs_ytd = {}

for m in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
    # Peak (ambil 30 teratas)
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

    # YTD
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

# =========================================================================
# 8. DAY OF WEEK PROFILE (SENIN - MINGGU) - RATA-RATA HARIAN NASIONAL
# =========================================================================
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
            # Penumpang Total
            'UDARA': round(float(sub['UDARA'].mean())),
            'KA': round(float(sub['KA'].mean())),
            'BUS': round(float(sub['BUS'].mean())),
            'ASDP': round(float(sub['ASDP'].mean())),
            'LAUT': round(float(sub['LAUT'].mean())),
            'TOTAL': round(float(sub['TOTAL'].mean())),
            # Penumpang Datang
            'pdat_UDARA': round(float(sub['pdat_UDARA'].mean())),
            'pdat_KA': round(float(sub['pdat_KA'].mean())),
            'pdat_BUS': round(float(sub['pdat_BUS'].mean())),
            'pdat_ASDP': round(float(sub['pdat_ASDP'].mean())),
            'pdat_LAUT': round(float(sub['pdat_LAUT'].mean())),
            'pdat_TOTAL': round(float(sub['pdat_TOTAL'].mean())),
            # Penumpang Berangkat
            'pbrg_UDARA': round(float(sub['pbrg_UDARA'].mean())),
            'pbrg_KA': round(float(sub['pbrg_KA'].mean())),
            'pbrg_BUS': round(float(sub['pbrg_BUS'].mean())),
            'pbrg_ASDP': round(float(sub['pbrg_ASDP'].mean())),
            'pbrg_LAUT': round(float(sub['pbrg_LAUT'].mean())),
            'pbrg_TOTAL': round(float(sub['pbrg_TOTAL'].mean())),
            # Armada Total
            'arm_UDARA': round(float(sub['arm_UDARA'].mean())),
            'arm_KA': round(float(sub['arm_KA'].mean())),
            'arm_BUS': round(float(sub['arm_BUS'].mean())),
            'arm_ASDP': round(float(sub['arm_ASDP'].mean())),
            'arm_LAUT': round(float(sub['arm_LAUT'].mean())),
            'arm_TOTAL': round(float(sub['arm_TOTAL'].mean())),
            # Armada Datang
            'adat_UDARA': round(float(sub['adat_UDARA'].mean())),
            'adat_KA': round(float(sub['adat_KA'].mean())),
            'adat_BUS': round(float(sub['adat_BUS'].mean())),
            'adat_ASDP': round(float(sub['adat_ASDP'].mean())),
            'adat_LAUT': round(float(sub['adat_LAUT'].mean())),
            'adat_TOTAL': round(float(sub['adat_TOTAL'].mean())),
            # Armada Berangkat
            'abrg_UDARA': round(float(sub['abrg_UDARA'].mean())),
            'abrg_KA': round(float(sub['abrg_KA'].mean())),
            'abrg_BUS': round(float(sub['abrg_BUS'].mean())),
            'abrg_ASDP': round(float(sub['abrg_ASDP'].mean())),
            'abrg_LAUT': round(float(sub['abrg_LAUT'].mean())),
            'abrg_TOTAL': round(float(sub['abrg_TOTAL'].mean())),
        })

# =========================================================================
# 9. EKSTRAKSI SIMPUL SPASIAL (LEAFLET GIS)
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

# =========================================================================
# 10. PRE-CALCULATE METRICS SUMMARY FOR ALL 6 COMBINATIONS
# =========================================================================
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
    
    # All time peak
    p_max = int(s_daily.max())
    d_max = s_daily.idxmax()
    
    # Mudik peak (13-20 Mar)
    mudik_s = s_daily.loc['2026-03-13':'2026-03-20']
    p_mud = int(mudik_s.max())
    d_mud = mudik_s.idxmax()
    
    # Baseline normal (Februari)
    feb_avg = float(s_daily.loc['2026-02-01':'2026-02-28'].mean())
    surge_peak = round((p_max - feb_avg) / feb_avg * 100, 1) if feb_avg > 0 else 0
    surge_mud = round((p_mud - feb_avg) / feb_avg * 100, 1) if feb_avg > 0 else 0
    
    # Date label tags
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

# =========================================================================
# 11. SIMPAN BUNDLE JSON TERLENGKAP
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
    'metrics_summary': metrics_summary,
    'meta': {
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
}

json_path = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data_bundle, f, ensure_ascii=False)

print(f"Data bundle terbaru berhasil disimpan di {json_path}")
print(f"Ukuran file: {os.path.getsize(json_path)/(1024):.1f} KB")
