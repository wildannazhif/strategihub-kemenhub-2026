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
            
        for item in monthly:
            if item['m'] == peak_m:
                item['is_peak'] = True
                
        valid_jumps = [x for x in monthly if x['mom'] is not None and x['mom'] > 0]
        max_jump_item = max(valid_jumps, key=lambda x: x['mom']) if valid_jumps else None
        
        prov_summary[p] = {
            'provinsi': p,
            'total': int(p_m.loc[p].sum()),
            'total_brg': int(p_m.loc[p].sum()), # backward compat alias
            'peak_month': month_names[peak_m],
            'peak_month_num': peak_m,
            'peak_vol': peak_vol,
            'max_jump_month': max_jump_item['name'] if max_jump_item else '-',
            'max_jump_pct': max_jump_item['mom'] if max_jump_item else 0.0,
            'monthly': monthly
        }
        
    monthly_rankings = {}
    for m in range(1, 10):
        vols = p_m[m].sort_values(ascending=False)
        top_vol = [{'provinsi': prov, 'vol': int(vols[prov])} for prov in vols.head(8).index]
        top_growth = []
        if m > 1:
            growths = {}
            for prov in top_provinces:
                v_curr = p_m.loc[prov, m]
                v_prev = p_m.loc[prov, m-1]
                threshold = 15000 if 'pnp' in m_key else 300
                if v_prev > threshold:
                    growths[prov] = round(((v_curr - v_prev) / v_prev) * 100, 1)
            sorted_g = sorted(growths.items(), key=lambda x: x[1], reverse=True)[:8]
            top_growth = [{'provinsi': k, 'mom': v, 'vol': int(p_m.loc[k, m])} for k, v in sorted_g]
            
        monthly_rankings[m] = {
            'month': m,
            'name': month_names[m],
            'top_vol': top_vol,
            'top_growth': top_growth
        }
        
    all_metrics_data[m_key] = {
        'provinces': top_provinces,
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
