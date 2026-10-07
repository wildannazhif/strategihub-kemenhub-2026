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

# Groupings
p_m_brg = df.groupby(['provinsi', 'month'])['penumpang_berangkat'].sum().unstack(fill_value=0)
p_m_dat = df.groupby(['provinsi', 'month'])['penumpang_datang'].sum().unstack(fill_value=0)
p_m_tot = df.groupby(['provinsi', 'month'])['total_penumpang'].sum().unstack(fill_value=0)
p_m_moda = df.groupby(['provinsi', 'month', 'moda'])['penumpang_berangkat'].sum().unstack(fill_value=0).reset_index()

top_provinces = p_m_brg.sum(axis=1).sort_values(ascending=False).index.tolist()

prov_summary = {}
for p in top_provinces:
    monthly = []
    prev_brg = None
    peak_m = 1
    peak_vol = 0
    
    sub_moda = p_m_moda[p_m_moda['provinsi'] == p].set_index('month')
    
    for m in range(1, 10):
        brg = int(p_m_brg.loc[p, m])
        dat = int(p_m_dat.loc[p, m])
        tot = int(p_m_tot.loc[p, m])
        
        mom = None
        if prev_brg is not None and prev_brg > 0:
            mom = round(((brg - prev_brg) / prev_brg) * 100, 1)
        prev_brg = brg
        
        if brg > peak_vol:
            peak_vol = brg
            peak_m = m
            
        modas = {}
        for mod in ['UDARA', 'KA', 'BUS', 'ASDP', 'LAUT']:
            if m in sub_moda.index and mod in sub_moda.columns:
                modas[mod] = int(sub_moda.loc[m, mod])
            else:
                modas[mod] = 0
                
        # Find dominant moda in month m
        dom_moda = max(modas.items(), key=lambda x: x[1]) if modas else ('-', 0)
        dom_pct = round((dom_moda[1] / brg * 100), 1) if brg > 0 else 0
        
        # Status
        status = 'Normal'
        if mom is not None:
            if mom >= 25.0:
                status = 'Lonjakan Tajam'
            elif mom >= 10.0:
                status = 'Kenaikan Wajar'
            elif mom <= -15.0:
                status = 'Penurunan Signifikan'
            elif mom < 0:
                status = 'Penurunan Ringan'
            else:
                status = 'Stabil'
                
        monthly.append({
            'm': m,
            'name': month_names[m],
            'short': short_names[m],
            'brg': brg,
            'dat': dat,
            'tot': tot,
            'mom': mom,
            'dom_moda': dom_moda[0],
            'dom_pct': dom_pct,
            'status': status,
            'modas': modas
        })
        
    # Mark peak month status
    for item in monthly:
        if item['m'] == peak_m:
            item['is_peak'] = True
            item['status'] = 'Puncak Tahunan'
        else:
            item['is_peak'] = False
            
    # Max mom jump (excluding initial)
    valid_jumps = [x for x in monthly if x['mom'] is not None and x['mom'] > 0]
    max_jump_item = max(valid_jumps, key=lambda x: x['mom']) if valid_jumps else None
    
    # Generate human insight narration
    insight_text = ""
    if peak_m == 3:
        insight_text = f"Mobilitas di {p} mencapai puncak tahunan pada bulan Maret 2026 ({peak_vol:,.0f} penumpang, naik {max_jump_item['mom'] if max_jump_item else 0:+.1f}% vs Februari), didorong oleh arus mudik Lebaran 1447 H."
    elif peak_m in [7, 8]:
        insight_text = f"Mobilitas di {p} mencapai puncak tahunan pada bulan {month_names[peak_m]} 2026 ({peak_vol:,.0f} penumpang), sejalan dengan periode liburan pertengahan tahun dan wisatawan."
    elif peak_m == 4:
        insight_text = f"Mobilitas di {p} melonjak dan mencapai puncaknya pada bulan April 2026 ({peak_vol:,.0f} penumpang) sejalan dengan arus balik Lebaran dan libur panjang Paskah."
    elif peak_m == 6:
        insight_text = f"Mobilitas di {p} mencapai puncak tertinggi pada bulan Juni 2026 ({peak_vol:,.0f} penumpang) sejalan dengan dimulainya musim libur sekolah nasional."
    else:
        insight_text = f"Mobilitas di {p} mencapai titik tertinggi pada bulan {month_names[peak_m]} 2026 ({peak_vol:,.0f} penumpang) dengan kenaikan MoM tertinggi pada {max_jump_item['name'] if max_jump_item else '-'}."

    prov_summary[p] = {
        'provinsi': p,
        'total_brg': int(p_m_brg.loc[p].sum()),
        'peak_month': month_names[peak_m],
        'peak_month_num': peak_m,
        'peak_vol': peak_vol,
        'max_jump_month': max_jump_item['name'] if max_jump_item else '-',
        'max_jump_pct': max_jump_item['mom'] if max_jump_item else 0.0,
        'insight': insight_text,
        'monthly': monthly
    }

# Rankings per month
monthly_rankings = {}
for m in range(1, 10):
    vols = p_m_brg[m].sort_values(ascending=False)
    top_vol = [{'provinsi': prov, 'vol': int(vols[prov])} for prov in vols.head(8).index]
    
    top_growth = []
    if m > 1:
        growths = {}
        for prov in top_provinces:
            v_curr = p_m_brg.loc[prov, m]
            v_prev = p_m_brg.loc[prov, m-1]
            if v_prev > 15000: # Threshold for significant volume
                growths[prov] = round(((v_curr - v_prev) / v_prev) * 100, 1)
        sorted_g = sorted(growths.items(), key=lambda x: x[1], reverse=True)[:8]
        top_growth = [{'provinsi': k, 'mom': v, 'vol': int(p_m_brg.loc[k, m])} for k, v in sorted_g]
        
    monthly_rankings[m] = {
        'month': m,
        'name': month_names[m],
        'top_vol': top_vol,
        'top_growth': top_growth
    }

province_monthly_data = {
    'provinces': top_provinces,
    'by_province': prov_summary,
    'by_month': monthly_rankings
}

# Update mobility_data_bundle.json
bundle_path = 'scripts/mobility_data_bundle.json'
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle['province_monthly_data'] = province_monthly_data

with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print(f"Berhasil memperbarui {bundle_path} dengan data province_monthly_data ({len(top_provinces)} provinsi).")
