import os
import json
import pandas as pd
import numpy as np

print("Generating province monthly growth dataset...")

raw_csv = "siasati_multimoda_2026.csv"
df = pd.read_csv(raw_csv, low_memory=False)

def clean_prov(p):
    p = str(p).strip()
    if p.upper() == 'SULAWESI SELATAN':
        return 'Sulawesi Selatan'
    if p in ['D.I. Yogyakarta', 'DI Yogyakarta', 'D.I Yogyakarta', 'DIY']:
        return 'D.I Yogyakarta'
    return p

df['provinsi'] = df['provinsi'].apply(clean_prov)
df['month'] = pd.to_datetime(df['tanggal']).dt.month

month_names = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei',
    6: 'Juni', 7: 'Juli', 8: 'Agustus', 9: 'September'
}
short_names = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei',
    6: 'Jun', 7: 'Jul', 8: 'Agu', 9: 'Sep'
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
    p_m = df.groupby(['provinsi', 'month'])[col].sum().unstack(fill_value=0)
    p_m_moda = df.groupby(['provinsi', 'month', 'moda'])[col].sum().unstack(fill_value=0).reset_index()
    top_provinces = p_m.sum(axis=1).sort_values(ascending=False).index.tolist()
    sorted_provinces = sorted(top_provinces)
    
    prov_summary = {}
    for p in top_provinces:
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
            
            monthly.append({
                'm': m,
                'name': month_names[m],
                'short': short_names[m],
                'val': val,
                'brg': val, # backward compat alias
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
            'total': int(p_m.loc[p].sum()),
            'total_brg': int(p_m.loc[p].sum()), # backward compat alias
            'peak_month': month_names[peak_m],
            'peak_month_num': peak_m,
            'peak_vol': peak_vol,
            'median_vol': int(med_vol),
            'max_jump_month': month_names[peak_m],
            'max_jump_pct': max_jump_vs_med,
            'max_jump_vs_median_pct': max_jump_vs_med,
            'monthly': monthly
        }
    
    # Agregat Nasional (Seluruh Provinsi)
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
        
        all_monthly.append({
            'm': m,
            'name': month_names[m],
            'short': short_names[m],
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
        'peak_month': month_names[all_peak_m],
        'peak_month_num': all_peak_m,
        'peak_vol': all_peak_vol,
        'median_vol': int(all_med_vol),
        'max_jump_month': month_names[all_peak_m],
        'max_jump_pct': all_max_jump,
        'max_jump_vs_median_pct': all_max_jump,
        'monthly': all_monthly
    }
    prov_summary['Seluruh Provinsi'] = prov_summary['ALL']
        
    monthly_rankings = {}
    for m in range(1, 10):
        vols = p_m[m].sort_values(ascending=False)
        top_vol = [{'provinsi': prov, 'vol': int(vols[prov])} for prov in vols.head(8).index]
        top_growth = []
        growths = {}
        for prov in top_provinces:
            v_curr = p_m.loc[prov, m]
            med_v = prov_summary[prov]['median_vol']
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

# Update mobility_data_bundle.json
bundle_path = 'scripts/mobility_data_bundle.json'
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle['province_monthly_data'] = province_monthly_data

with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print(f"Berhasil memperbarui {bundle_path} dengan multi-metric province_monthly_data (6 metrik x 38 provinsi).")
