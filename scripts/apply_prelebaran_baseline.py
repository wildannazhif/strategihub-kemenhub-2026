import os
import json
import re
import pandas as pd
import numpy as np

print("=" * 80)
print("PEMBARUAN RENTANG BASELINE MEDIAN: 1 JANUARI 2026 HINGGA 12 MARET 2026")
print("=" * 80)

# 1. Load siasati_multimoda_2026.csv
raw_csv = "siasati_multimoda_2026.csv"
print(f"1. Membaca dataset mentah: {raw_csv}...")
df_raw = pd.read_csv(raw_csv, low_memory=False).drop_duplicates(keep='first')

def clean_prov(p):
    p = str(p).strip()
    if p.upper() == 'SULAWESI SELATAN': return 'Sulawesi Selatan'
    if p in ['D.I. Yogyakarta', 'DI Yogyakarta', 'D.I Yogyakarta', 'DIY']: return 'D.I Yogyakarta'
    return p

df_raw['provinsi'] = df_raw['provinsi'].apply(clean_prov)
df_raw['date_dt'] = pd.to_datetime(df_raw['tanggal'])
df_raw['month'] = df_raw['date_dt'].dt.month

key_cols = ['tanggal', 'caturwulan', 'moda', 'id_prasarana']
meta_cols = ['nama_prasarana', 'provinsi']
metrics = ['penumpang_datang', 'penumpang_berangkat', 'armada_datang', 'armada_berangkat']
agg_dict = {m: 'sum' for m in metrics}
for c in meta_cols: agg_dict[c] = 'first'
df_clean = df_raw.groupby(key_cols, as_index=False, dropna=False).agg(agg_dict)
df_clean['total_penumpang'] = df_clean['penumpang_datang'] + df_clean['penumpang_berangkat']
df_clean['total_armada'] = df_clean['armada_datang'] + df_clean['armada_berangkat']

# 2. Load bundle JSON
bundle_path = "scripts/mobility_data_bundle.json"
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

df_daily = pd.DataFrame(bundle['daily_timeline'])
modes = ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']

# Filter periode pra-Lebaran: 1 Jan 2026 s.d. 12 Mar 2026 (71 hari)
df_daily_pre = df_daily[df_daily['date'].between('2026-01-01', '2026-03-12')].copy()
N_DAYS = len(df_daily_pre)
DAYS_PER_MONTH = 365.25 / 12.0 # 30.4375

print(f"2. Periode Baseline: 2026-01-01 s.d. 2026-03-12 ({N_DAYS} hari data harian)")

# ==============================================================================
# A. UPDATE SURGE SUMMARY BERDASARKAN MEDIAN 1 JAN - 12 MAR 2026
# ==============================================================================
med_pnp = {m: int(df_daily_pre[m].median()) for m in modes}
med_tot_pnp = int(df_daily_pre['TOTAL'].median())

med_arm = {m: int(df_daily_pre[f'arm_{m}'].median()) for m in modes}
med_tot_arm = int(df_daily_pre['arm_TOTAL'].median())

d_mudik = df_daily[df_daily['date'] == '2026-03-18'].iloc[0]
d_balik1 = df_daily[df_daily['date'] == '2026-03-24'].iloc[0]
d_balik2 = df_daily[df_daily['date'] == '2026-03-29'].iloc[0]

new_surge_summary = {}
for m in modes:
    base = med_pnp[m]
    vm = int(d_mudik[m])
    vb1 = int(d_balik1[m])
    vb2 = int(d_balik2[m])
    new_surge_summary[m] = {
        'baseline': base,
        'peak_mudik': vm,
        'surge_mudik_pct': round((vm - base) / base * 100, 1),
        'peak_balik1': vb1,
        'surge_balik1_pct': round((vb1 - base) / base * 100, 1),
        'peak_balik2': vb2,
        'surge_balik2_pct': round((vb2 - base) / base * 100, 1)
    }

new_surge_summary['TOTAL'] = {
    'baseline': med_tot_pnp,
    'peak_mudik': int(d_mudik['TOTAL']),
    'surge_mudik_pct': round((d_mudik['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1),
    'peak_balik1': int(d_balik1['TOTAL']),
    'surge_balik1_pct': round((d_balik1['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1),
    'peak_balik2': int(d_balik2['TOTAL']),
    'surge_balik2_pct': round((d_balik2['TOTAL'] - med_tot_pnp) / med_tot_pnp * 100, 1)
}

bundle['surge_summary'] = new_surge_summary
print("   • surge_summary diperbarui dengan baseline median 1 Jan - 12 Mar 2026.")

# ==============================================================================
# B. UPDATE LOAD FACTOR STATS
# ==============================================================================
new_load_factor_stats = {}
for m in modes:
    lf_base = round(med_pnp[m] / med_arm[m], 1) if med_arm[m] > 0 else 0
    p_mud = float(d_mudik[m])
    a_mud = float(d_mudik[f'arm_{m}'])
    lf_mud = round(p_mud / a_mud, 1) if a_mud > 0 else 0
    
    p_bal = float(d_balik1[m])
    a_bal = float(d_balik1[f'arm_{m}'])
    lf_bal = round(p_bal / a_bal, 1) if a_bal > 0 else 0
    
    peak_lf = max(lf_mud, lf_bal)
    surge_lf_pct = round((peak_lf - lf_base) / lf_base * 100, 1) if lf_base > 0 else 0
    
    new_load_factor_stats[m] = {
        'baseline_lf': lf_base,
        'mudik_lf': lf_mud,
        'balik_lf': lf_bal,
        'peak_lf': peak_lf,
        'surge_lf_pct': surge_lf_pct
    }

bundle['load_factor_stats'] = new_load_factor_stats
print("   • load_factor_stats diperbarui.")

# ==============================================================================
# C. UPDATE METRICS SUMMARY (6 METRIC COMBOS)
# ==============================================================================
metric_keys_map = {
    'pnp_tot': {'col': 'TOTAL', 'peak_date': '2026-03-24', 'mudik_date': '2026-03-18', 'label': 'Penumpang • Dua Arah (Total)', 'unit': 'penumpang', 'formula': '∑ (P_datang + P_berangkat)'},
    'pnp_dat': {'col': 'pdat_TOTAL', 'peak_date': '2026-03-24', 'mudik_date': '2026-03-18', 'label': 'Penumpang Datang (Kedatangan)', 'unit': 'penumpang datang', 'formula': '∑ P_datang'},
    'pnp_brg': {'col': 'pbrg_TOTAL', 'peak_date': '2026-03-24', 'mudik_date': '2026-03-18', 'label': 'Penumpang Berangkat (Keberangkatan)', 'unit': 'penumpang berangkat', 'formula': '∑ P_berangkat'},
    'arm_tot': {'col': 'arm_TOTAL', 'peak_date': '2026-03-17', 'mudik_date': '2026-03-17', 'label': 'Total Armada Beroperasi (Dua Arah)', 'unit': 'trip armada', 'formula': '∑ (Trip Datang + Trip Berangkat)'},
    'arm_dat': {'col': 'adat_TOTAL', 'peak_date': '2026-03-17', 'mudik_date': '2026-03-17', 'label': 'Armada Datang (Kedatangan)', 'unit': 'trip datang', 'formula': '∑ Trip_datang'},
    'arm_brg': {'col': 'abrg_TOTAL', 'peak_date': '2026-03-25', 'mudik_date': '2026-03-18', 'label': 'Armada Berangkat (Keberangkatan)', 'unit': 'trip berangkat', 'formula': '∑ Trip_berangkat'},
}

new_metrics_summary = {}
for m_code, info in metric_keys_map.items():
    col = info['col']
    base_val = int(df_daily_pre[col].median())
    
    # Peak
    p_date = info['peak_date']
    row_peak = df_daily[df_daily['date'] == p_date].iloc[0]
    p_val = int(row_peak[col])
    p_surge = round((p_val - base_val) / base_val * 100, 1)
    
    # Mudik
    m_date = info['mudik_date']
    row_mudik = df_daily[df_daily['date'] == m_date].iloc[0]
    m_val = int(row_mudik[col])
    m_surge = round((m_val - base_val) / base_val * 100, 1)
    
    ytd = int(df_daily[col].sum())
    avg = int(df_daily[col].mean())
    
    new_metrics_summary[m_code] = {
        'label': info['label'],
        'unit': info['unit'],
        'formula': info['formula'],
        'ytd': ytd,
        'avg': avg,
        'baseline': base_val,
        'peak_date': p_date,
        'peak_val': p_val,
        'peak_desc': f"{p_date} (Puncak)",
        'peak_surge_pct': p_surge,
        'mudik_date': m_date,
        'mudik_val': m_val,
        'mudik_desc': f"{m_date} (Mudik)",
        'mudik_surge_pct': m_surge
    }

bundle['metrics_summary'] = new_metrics_summary
print("   • metrics_summary (6 kombinasi) diperbarui.")

# ==============================================================================
# D. UPDATE SIMPUL RECOMMENDATIONS (1.010 SIMPUL)
# ==============================================================================
df_clean_pre = df_clean[df_clean['tanggal'].between('2026-01-01', '2026-03-12')].copy()
med_hub = df_clean_pre.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
    pnp_brg_biasa=('penumpang_berangkat', 'median'),
    arm_brg_biasa=('armada_berangkat', 'median')
).reset_index()

peak = df_clean[df_clean['tanggal'].between('2026-03-13', '2026-03-29')]
peak_hub = peak.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
    pnp_brg_puncak=('penumpang_berangkat', 'max'),
    arm_brg_puncak=('armada_berangkat', 'max')
).reset_index()

merged = pd.merge(med_hub, peak_hub, on=['moda', 'nama_prasarana', 'provinsi'], how='outer').fillna(0)
merged = merged[(merged['arm_brg_puncak'] > 0) & (merged['pnp_brg_puncak'] > 0)]
merged = merged.sort_values(by='pnp_brg_puncak', ascending=False).reset_index(drop=True)

# Preserve existing actions mapping from current bundle
existing_actions = { (item['moda'], item['name']): item['fieldAction'] for item in bundle.get('simpul_recommendations', []) }

simpul_items = []
for idx, r in merged.iterrows():
    moda = r['moda']
    nama = r['nama_prasarana']
    prov = r['provinsi']
    
    pb = int(round(r['pnp_brg_biasa']))
    ab = int(round(r['arm_brg_biasa']))
    pp = int(round(r['pnp_brg_puncak']))
    ap = int(round(r['arm_brg_puncak']))

    lfb = round(pb / ab, 1) if ab > 0 else 0
    lfp = round(pp / ap, 1) if ap > 0 else 0
    ratio = round(lfp / lfb, 2) if lfb > 0 else (2.5 if pp >= 5000 else 1.2)

    if ratio >= 3.0 or (ratio >= 2.0 and pp >= 20000):
        status_text = 'Sangat Kritis'
        status_badge = 'bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300'
    elif ratio >= 1.8 or (ratio >= 1.4 and pp >= 10000):
        status_text = 'Tinggi / Kritis'
        status_badge = 'bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-300'
    elif ratio >= 1.2 or pp >= 5000:
        status_text = 'Padat Tinggi'
        status_badge = 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
    else:
        status_text = 'Terkendali'
        status_badge = 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'

    # Logika Kebutuhan Trip Armada Saat Lonjakan
    # Agar beban per trip (penumpang per armada) tetap sama seperti hari biasa:
    # Trip yang dibutuhkan = (Penumpang lonjakan / Penumpang hari biasa) * Trip hari biasa
    if pb > 0 and ab > 0 and ap > 0:
        needed = int((pp / pb) * ab)
        add_arm = max(0, needed - ap)
        total_arm = ap + add_arm
        pct = int(round((add_arm / ap) * 100))
    else:
        needed = ap
        add_arm = 0
        total_arm = ap
        pct = 0

    if moda == 'UDARA': moda_label, sarana_type, sarana_unit = '✈ Udara', 'Pesawat Jet Komersial', 'penerbangan'
    elif moda == 'KA':
        moda_label = '🚆 Kereta Api'
        if 'KCJB' in nama.upper() or 'WHOOSH' in nama.upper(): sarana_type = 'Kereta Cepat Whoosh'
        elif 'KRL' in nama.upper() or 'COMMUTER' in nama.upper(): sarana_type = 'KRL Commuter Line'
        else: sarana_type = 'Rangkaian Kereta Api'
        sarana_unit = 'perjalanan KA'
    elif moda == 'BUS': moda_label, sarana_type, sarana_unit = '🚌 Bus AKAP', 'Armada Bus Antar Kota', 'trip bus'
    elif moda == 'ASDP': moda_label, sarana_type, sarana_unit = '⛴ ASDP Feri', 'Kapal Feri Ro-Ro', 'trip kapal feri'
    else: moda_label, sarana_type, sarana_unit = '🚢 Laut', 'Kapal Penumpang Pelni/Perintis', 'call kapal laut'

    field_action = existing_actions.get((moda, nama), 'Optimalisasi jadwal armada dan monitoring lonjakan penumpang.')

    simpul_items.append({
        'id': f'simpul_{idx+1}',
        'name': nama,
        'prov': prov,
        'moda': moda,
        'modaLabel': moda_label,
        'saranaType': sarana_type,
        'saranaUnit': sarana_unit,
        'pnpBiasa': pb,
        'armBiasa': ab,
        'pnpPuncak': pp,
        'armPuncak': ap,
        'lfBiasa': lfb,
        'lfPuncak': lfp,
        'loadRatio': ratio,
        'pctTambah': pct,
        'addArm': add_arm,
        'totalArm': total_arm,
        'statusText': status_text,
        'statusBadge': status_badge,
        'fieldAction': field_action
    })

bundle['simpul_recommendations'] = simpul_items
print(f"   • simpul_recommendations ({len(simpul_items)} simpul) diperbarui.")

# ==============================================================================
# E. UPDATE PROVINCE MONTHLY DATA (BASELINE 1 JAN - 12 MAR 2026)
# ==============================================================================
print("3. Memperbarui dataset tren bulanan provinsi (baseline 1 Jan - 12 Mar 2026)...")

month_names = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus', 9: 'September'}
short_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun', 7: 'Jul', 8: 'Agu', 9: 'Sep'}

metrics_map = {
    'pnp_brg': {'col': 'penumpang_berangkat', 'unit': 'pnp', 'label': 'Penumpang Berangkat'},
    'pnp_dat': {'col': 'penumpang_datang', 'unit': 'pnp', 'label': 'Penumpang Datang'},
    'pnp_tot': {'col': 'total_penumpang', 'unit': 'pnp', 'label': 'Total Penumpang'},
    'arm_brg': {'col': 'armada_berangkat', 'unit': 'trip', 'label': 'Armada Berangkat'},
    'arm_dat': {'col': 'armada_datang', 'unit': 'trip', 'label': 'Armada Datang'},
    'arm_tot': {'col': 'total_armada', 'unit': 'trip', 'label': 'Total Armada'}
}

df_raw_pre = df_raw[df_raw['tanggal'].between('2026-01-01', '2026-03-12')].copy()

all_metrics_data = {}

for m_key, m_info in metrics_map.items():
    col = m_info['col']
    
    # Monthly aggregation
    p_m = df_raw.groupby(['provinsi', 'month'])[col].sum().unstack(fill_value=0)
    p_m_moda = df_raw.groupby(['provinsi', 'month', 'moda'])[col].sum().unstack(fill_value=0).reset_index()
    top_provinces = p_m.sum(axis=1).sort_values(ascending=False).index.tolist()
    sorted_provinces = sorted(top_provinces)
    
    # Pre-lebaran daily data per province & per moda
    p_daily_pre = df_raw_pre.groupby(['provinsi', 'tanggal'])[col].sum().unstack(fill_value=0)
    p_daily_moda_pre = df_raw_pre.groupby(['provinsi', 'moda', 'tanggal'])[col].sum().unstack(fill_value=0)
    
    prov_summary = {}
    
    for p in top_provinces:
        # 1. Baseline median harian pra-Lebaran (1 Jan - 12 Mar) dikonversi ke ekuivalen bulanan
        if p in p_daily_pre.index:
            d_med = float(p_daily_pre.loc[p].median())
        else:
            d_med = 0.0
        med_monthly_baseline = int(round(d_med * DAYS_PER_MONTH))
        if med_monthly_baseline == 0 and p in p_m.index:
            med_monthly_baseline = int(round(p_m.loc[p].median()))
            
        # Baseline per moda dalam provinsi ini
        moda_baselines = {}
        for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
            if (p, mod) in p_daily_moda_pre.index:
                d_mod_med = float(p_daily_moda_pre.loc[(p, mod)].median())
                moda_baselines[mod] = int(round(d_mod_med * DAYS_PER_MONTH))
            else:
                moda_baselines[mod] = 0
                
        monthly = []
        prev_val = None
        peak_m = 1
        peak_vol = 0
        sub_moda = p_m_moda[p_m_moda['provinsi'] == p].set_index('month')
        
        for m in range(1, 10):
            val = int(p_m.loc[p, m])
            mom = round(((val - prev_val) / prev_val) * 100, 1) if (prev_val is not None and prev_val > 0) else None
            prev_val = val
            
            if val > peak_vol:
                peak_vol = val
                peak_m = m
                
            modas = {mod: int(sub_moda.loc[m, mod]) if (m in sub_moda.index and mod in sub_moda.columns) else 0 for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']}
            dom_moda = max(modas.items(), key=lambda x: x[1]) if modas else ('-', 0)
            dom_pct = round((dom_moda[1] / val * 100), 1) if val > 0 else 0
            
            vs_median = round(((val - med_monthly_baseline) / med_monthly_baseline) * 100, 1) if med_monthly_baseline > 0 else 0.0
            
            monthly.append({
                'm': m,
                'name': month_names[m],
                'short': short_names[m],
                'val': val,
                'brg': val,
                'mom': mom,
                'vs_median': vs_median,
                'dom_moda': dom_moda[0],
                'dom_pct': dom_pct,
                'is_peak': False,
                'modas': modas
            })
            
        for item in monthly:
            if item['m'] == peak_m:
                item['is_peak'] = True
                
        max_jump_vs_med = round(((peak_vol - med_monthly_baseline) / med_monthly_baseline) * 100, 1) if med_monthly_baseline > 0 else 0.0
        
        prov_summary[p] = {
            'provinsi': p,
            'total': int(p_m.loc[p].sum()),
            'total_brg': int(p_m.loc[p].sum()),
            'peak_month': month_names[peak_m],
            'peak_month_num': peak_m,
            'peak_vol': peak_vol,
            'median_vol': med_monthly_baseline,
            'baseline_vol': med_monthly_baseline,
            'moda_baselines': moda_baselines,
            'max_jump_month': month_names[peak_m],
            'max_jump_pct': max_jump_vs_med,
            'max_jump_vs_median_pct': max_jump_vs_med,
            'monthly': monthly
        }
        
    # Agregat Nasional (ALL)
    nat_daily_pre = df_raw_pre.groupby('tanggal')[col].sum()
    nat_d_med = float(nat_daily_pre.median())
    nat_monthly_baseline = int(round(nat_d_med * DAYS_PER_MONTH))
    
    nat_moda_baselines = {}
    for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
        df_mod_pre = df_raw_pre[df_raw_pre['moda'] == mod]
        if len(df_mod_pre) > 0:
            mod_d = df_mod_pre.groupby('tanggal')[col].sum()
            nat_moda_baselines[mod] = int(round(float(mod_d.median()) * DAYS_PER_MONTH))
        else:
            nat_moda_baselines[mod] = 0

    all_monthly = []
    all_prev_val = None
    all_peak_m = 1
    all_peak_vol = 0
    for m in range(1, 10):
        m_modas = {mod: sum(prov_summary[pr]['monthly'][m-1]['modas'][mod] for pr in top_provinces) for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']}
        m_val = sum(m_modas.values())
        mom = round(((m_val - all_prev_val) / all_prev_val) * 100, 1) if (all_prev_val is not None and all_prev_val > 0) else None
        all_prev_val = m_val
        
        if m_val > all_peak_vol:
            all_peak_vol = m_val
            all_peak_m = m
            
        dom_moda = max(m_modas.items(), key=lambda x: x[1]) if m_modas else ('-', 0)
        dom_pct = round((dom_moda[1] / m_val * 100), 1) if m_val > 0 else 0
        
        vs_median = round(((m_val - nat_monthly_baseline) / nat_monthly_baseline) * 100, 1) if nat_monthly_baseline > 0 else 0.0
        
        all_monthly.append({
            'm': m,
            'name': month_names[m],
            'short': short_names[m],
            'val': m_val,
            'brg': m_val,
            'mom': mom,
            'vs_median': vs_median,
            'dom_moda': dom_moda[0],
            'dom_pct': dom_pct,
            'is_peak': False,
            'modas': m_modas
        })
        
    for item in all_monthly:
        if item['m'] == all_peak_m:
            item['is_peak'] = True
            
    all_max_jump = round(((all_peak_vol - nat_monthly_baseline) / nat_monthly_baseline) * 100, 1) if nat_monthly_baseline > 0 else 0.0
    
    prov_summary['ALL'] = {
        'provinsi': 'Seluruh Provinsi (Nasional)',
        'total': sum(x['val'] for x in all_monthly),
        'total_brg': sum(x['val'] for x in all_monthly),
        'peak_month': month_names[all_peak_m],
        'peak_month_num': all_peak_m,
        'peak_vol': all_peak_vol,
        'median_vol': nat_monthly_baseline,
        'baseline_vol': nat_monthly_baseline,
        'moda_baselines': nat_moda_baselines,
        'max_jump_month': month_names[all_peak_m],
        'max_jump_pct': all_max_jump,
        'max_jump_vs_median_pct': all_max_jump,
        'monthly': all_monthly
    }
    prov_summary['Seluruh Provinsi'] = prov_summary['ALL']
    
    # Monthly Rankings
    monthly_rankings = {}
    for m in range(1, 10):
        vols = p_m[m].sort_values(ascending=False)
        top_vol = [{'provinsi': prov, 'vol': int(vols[prov])} for prov in vols.head(8).index]
        top_growth = []
        growths = {}
        for prov in top_provinces:
            v_curr = p_m.loc[prov, m]
            med_v = prov_summary[prov]['baseline_vol']
            threshold = 15000 if 'pnp' in m_key else 300
            if med_v > threshold:
                growths[prov] = round(((v_curr - med_v) / med_v) * 100, 1)
        sorted_g = sorted(growths.items(), key=lambda x: x[1], reverse=True)[:8]
        top_growth = [{'provinsi': k, 'mom': v, 'vs_median': v, 'vol': int(p_m.loc[k, m])} for k, v in sorted_g]
            
        monthly_rankings[m] = {
            'month': m,
            'name': month_names[m],
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

bundle['province_monthly_data'] = province_monthly_data

# Save updated bundle
with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)
print(f"4. File {bundle_path} berhasil disimpan dengan baseline 1 Jan - 12 Mar 2026!")

# ==============================================================================
# F. UPDATE index.html & Dashboard_Mobilitas_Nasional_2026.html
# ==============================================================================
print("5. Menyinkronkan index.html dan Dashboard_Mobilitas_Nasional_2026.html...")

bundle_json_str = json.dumps(bundle, ensure_ascii=False)

for filename in ['index.html', 'Dashboard_Mobilitas_Nasional_2026.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # 1. Update const DATA
    start_str = "const DATA = {"
    end_str = ";\n\nconst numFmt ="
    pos1 = html.find(start_str)
    pos2 = html.find(end_str, pos1)
    if pos1 == -1 or pos2 == -1:
        raise Exception(f"Cannot find const DATA block in {filename}")
    html = html[:pos1] + "const DATA = " + bundle_json_str + html[pos2:]
    
    # 2. Update Tab 1 JS: renderProvinceGrowthWorkspace to use provInfo.baseline_vol & moda_baselines
    old_scope_calc = """    const monthlyVals = provInfo.monthly.map(m => getMonthVal(m));
    const sortedVals = [...monthlyVals].sort((a, b) => a - b);
    const scopeMedian = sortedVals[4] || 0; // Robust Median 9 bulan (posisi ke-5)"""

    new_scope_calc = """    const monthlyVals = provInfo.monthly.map(m => getMonthVal(m));
    // Baseline Median Pra-Lebaran (1 Jan - 12 Mar 2026, 71 Hari)
    const scopeMedian = isAllModa
      ? (provInfo.baseline_vol || provInfo.median_vol || 0)
      : ((provInfo.moda_baselines && provInfo.moda_baselines[selectedModaForGrowth]) || provInfo.baseline_vol || provInfo.median_vol || 0);"""

    if old_scope_calc in html:
        html = html.replace(old_scope_calc, new_scope_calc)
        
    # 3. Update Subtitles & Headers in Tab 1
    html = html.replace(
        'Cek tren pergerakan bulanan dan analisis lonjakan terhadap baseline median (2026)',
        'Cek tren pergerakan bulanan dan analisis lonjakan terhadap baseline median pra-Lebaran (1 Jan - 12 Mar 2026)'
    )
    
    html = html.replace(
        'if (boxSubEl) boxSubEl.innerText = `${mCfg.label} • Baseline Median: ${numFmt(scopeMedian)} ${mCfg.unit}`;',
        'if (boxSubEl) boxSubEl.innerText = `${mCfg.label} • Baseline Median Pra-Lebaran (1 Jan - 12 Mar): ${numFmt(scopeMedian)} ${mCfg.unit}`;'
    )
    
    html = html.replace(
        'if (tableBadge) tableBadge.innerText = `Median: ${numFmt(scopeMedian)} ${mCfg.unit}/bln`;',
        'if (tableBadge) tableBadge.innerText = `Baseline Median: ${numFmt(scopeMedian)} ${mCfg.unit}/bln (1 Jan - 12 Mar)`;'
    )
    
    html = html.replace(
        '<th class="py-2.5 px-3 text-right text-slate-700 dark:text-slate-300">vs Median</th>',
        '<th class="py-2.5 px-3 text-right text-slate-700 dark:text-slate-300" title="Lonjakan terhadap Baseline Median Pra-Lebaran 1 Jan - 12 Mar 2026">vs Median (1 Jan - 12 Mar)</th>'
    )

    # 4. Update Tab 2 (Puncak Lebaran)
    html = html.replace(
        'Persentase Lonjakan (%) terhadap Baseline Normal (Median 2026)',
        'Persentase Lonjakan (%) terhadap Baseline Normal (Median 1 Jan - 12 Mar 2026)'
    )
    html = html.replace(
        'Perbandingan baseline harian normal (Median 2026) dengan volume puncak arus mudik dan arus balik',
        'Perbandingan baseline harian normal (Median 1 Jan - 12 Mar 2026) dengan volume puncak arus mudik dan arus balik'
    )
    html = html.replace(
        '<th>Baseline Normal (Median)</th>',
        '<th>Baseline Normal (1 Jan - 12 Mar)</th>'
    )
    html = html.replace(
        '<th class="py-2.5 px-3 text-right">Baseline Normal (Median)</th>',
        '<th class="py-2.5 px-3 text-right">Baseline Normal (1 Jan - 12 Mar)</th>'
    )
    
    # 5. Update Tab 3 (Modal Share)
    html = html.replace(
        'Periode Normal (Median 2026)',
        'Periode Normal (Median 1 Jan - 12 Mar 2026)'
    )
    html = html.replace(
        'antara periode normal (Median 2026) dan puncak arus mudik Lebaran (Maret)',
        'antara periode normal (Median 1 Jan - 12 Mar 2026) dan puncak arus mudik Lebaran (Maret)'
    )

    # 6. Update Metodologi / Kamus Rumus Modal
    html = html.replace(
        '$$P_{\\text{median}} = \\text{Median}(P_1, P_2, \\dots, P_{272}) = 1.321.644\\text{ pnp/h}$$',
        '$$P_{\\text{median}} = \\text{Median}(P_{1\\text{ Jan}}, \\dots, P_{12\\text{ Mar}}) = 1.203.870\\text{ pnp/h}$$'
    )
    html = html.replace(
        'Nilai tengah mobilitas 272 hari, bebas dari distorsi lonjakan ekstrem (Google Mobility standard).',
        'Nilai tengah mobilitas 71 hari pra-Lebaran (1 Jan s.d. 12 Mar 2026), bebas dari distorsi arus mudik posko resmi.'
    )
    html = html.replace(
        'Nilai Median harian dari seluruh 272 hari (Jan–Sep 2026) digunakan sebagai acuan normal sesuai metodologi robust Google Mobility & Van Lint (2005) agar kebal terhadap lonjakan ekstrem mudik.',
        'Nilai Median harian dari periode pra-Lebaran (1 Jan s.d. 12 Mar 2026, 71 hari) digunakan sebagai acuan baseline normal sebelum dimulainya Posko Angkutan Lebaran pada 13 Maret 2026 (H-8).'
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   • {filename} berhasil diperbarui.")

print("=" * 80)
print("SELESAI! Seluruh baseline median sistem telah beralih ke 1 JANUARI - 12 MARET 2026.")
print("=" * 80)
