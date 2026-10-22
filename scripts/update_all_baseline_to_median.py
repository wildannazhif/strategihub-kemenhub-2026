import json
import re
import pandas as pd
import numpy as np

print("=" * 80)
print("MEMULAI PEMBARUAN BASELINE MENJADI NILAI MEDIAN PADA SELURUH SISTEM")
print("=" * 80)

# 1. Load siasati_multimoda_2026.csv
raw_csv = "siasati_multimoda_2026.csv"
print(f"1. Membaca dataset mentah: {raw_csv}...")
df_raw = pd.read_csv(raw_csv, low_memory=False).drop_duplicates(keep='first')

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

# ==============================================================================
# A. HITUNG METRIK BASELINE MEDIAN HARIAN 2026 (NASIONAL & PER MODA)
# ==============================================================================
med_pnp = {m: int(df_daily[m].median()) for m in modes}
med_tot_pnp = int(df_daily['TOTAL'].median())

med_arm = {m: int(df_daily[f'arm_{m}'].median()) for m in modes}
med_tot_arm = int(df_daily['arm_TOTAL'].median())

print(f"Baseline Median Total Penumpang : {med_tot_pnp:,} pnp/hari (N = {len(df_daily)} hari)")
print(f"Baseline Median Per Moda Penumpang: {med_pnp}")
print(f"Baseline Median Per Moda Armada   : {med_arm}")

# ==============================================================================
# B. UPDATE SURGE SUMMARY BERDASARKAN MEDIAN
# ==============================================================================
# Tanggal puncak Lebaran: Mudik 18 Mar, Balik 1 24 Mar, Balik 2 29 Mar
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
print("2. surge_summary berhasil diperbarui dengan baseline median.")

# ==============================================================================
# C. UPDATE LOAD FACTOR STATS BERDASARKAN MEDIAN
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
print("3. load_factor_stats berhasil diperbarui dengan baseline median.")

# ==============================================================================
# D. UPDATE SIMPUL RECOMMENDATIONS (1.010 SIMPUL) BERDASARKAN MEDIAN HARIAN SIMPUL
# ==============================================================================
print("4. Menghitung baseline Median harian untuk seluruh 1.010 simpul prasarana...")
med_hub = df_clean.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
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

# Custom actions mapping dari scripts/generate_simpul_recommendations.py
CUSTOM_ACTIONS = {
    ('ASDP', 'Bakauheni'): 'Pola operasi TBB (Tiba Bongkar Berangkat) tanpa memuat di Bakauheni untuk menguras antrean arus balik ke Jawa.',
    ('ASDP', 'Merak'): 'Percepatan port clearance (<45 mnt), aktivasi buffer zone di rest area KM 43/68, pengerahan kapal feri kapasitas besar (>5.000 GT).',
    ('UDARA', 'Soekarno Hatta'): 'Optimalisasi runway capacity (Runway 1, 2, 3), izin extra flight malam (red-eye flight), buffer time ground handling.',
    ('ASDP', 'Gilimanuk'): 'Penerapan skema bongkar cepat di Gilimanuk, rekayasa antrean di Cekik, serta pengerahan kapal perbantuan kapasitas besar.',
    ('ASDP', 'Ketapang'): 'Pengoperasian dermaga ponton & MB cadangan, pengerahan kapal kapasitas muat kendaraan roda empat/bus wisata.',
    ('UDARA', 'I Gusti Ngurah Rai'): 'Perpanjangan operasional bandara 24 jam penuh, slot extra flight dini hari, serta pengaturan ketat alokasi parking stand.',
    ('LAUT', 'Batam'): 'Penambahan trip fast ferry lintas Batam–Singapura/Johor dan rute domestik antarpulau Kepri.',
    ('BUS', 'Purabaya'): 'Penyiagaan armada bus pariwisata cadangan sebagai bus perbantuan angkutan malam hari rute Trans-Jawa.',
    ('BUS', 'Giwangan'): 'Sistem sirkulasi peron jalur cepat, buffer parkir bus cadangan di lingkar selatan Jogja, antisipasi lonjakan wisata.',
    ('UDARA', 'Juanda'): 'Penambahan slot extra flight koridor Surabaya–Jakarta/Balikpapan/Makassar dan percepatan turnaround time.',
    ('KA', 'PASARSENEN'): 'Pengoperasian KLB KA Tambahan Nataru relasi Pasar Senen–Yogyakarta/Solo/Surabaya/Malang.',
    ('BUS', 'Purboyo'): 'Manajemen peron transit lintas Madiun–Surabaya/Solo dan pengaturan antrean bus keluar tol Madiun.',
    ('BUS', 'Kertonegoro'): 'Pengendalian ritme kedatangan bus AKAP koridor tengah Jawa Timur–Jawa Tengah agar tidak menumpuk.',
    ('UDARA', 'Sultan Hasanuddin'): 'Penyediaan extra flight transit penghubung Indonesia Barat ke Indonesia Timur (Papua/Maluku).',
    ('KA', 'GAMBIR'): 'Penambahan stamformasi (panjang 10-12 kereta) dan jadwal KA Argo Lawu/Dwipangga Tambahan.',
    ('KA', 'YOGYAKARTA'): 'Penambahan frekuensi KRL Commuter Line Solo–Yogya serta integrasi KA Bandara YIA di jam padat.',
    ('UDARA', 'Kualanamu'): 'Optimalisasi extra flight rute Medan–Jakarta/Batam/Banda Aceh dan integrasi jadwal Kereta Bandara Railink.',
    ('ASDP', 'Poto Tano'): 'Percepatan jadwal trip kapal lintasan Lombok–Sumbawa dan penyiagaan kapal perbantuan saat arus balik.',
    ('KA', 'KCJB - HALIM'): 'Penambahan slot perjalanan Whoosh hingga headway 20–30 menit dan integrasi feeder LRT Jabodebek.',
    ('LAUT', 'Tanjung Balai Karimun'): 'Koordinasi KSOP untuk kelayakan armada laut, jaket keselamatan, dan jadwal penyeberangan reguler.',
    ('LAUT', 'Nusa Penida'): 'Pengawasan kapasitas muat fast boat rute Sanur–Nusa Penida dan pengetatan SOP keselamatan cuaca laut.',
    ('ASDP', 'Kayangan'): 'Pola operasi kapal cepat dan pemisahan antrean kendaraan roda dua dengan angkutan logistik berat.',
    ('BUS', 'Indihiang'): 'Penyiagaan armada bus AKAP cadangan koridor Priangan Timur menuju Jabodetabek dan Jawa Tengah.',
    ('KA', 'KCJB - PADALARANG'): 'Sinkronisasi jam keberangkatan KA Feeder Padalarang–Bandung agar tidak terjadi penumpukan penumpang.',
    ('KA', 'PURWOKERTO'): 'Penambahan gerbong KA lintas Kroya–Purwokerto–Cirebon dan penyiagaan lokomotif cadangan di dipo.',
    ('BUS', 'Pakupatan'): 'Penataan peron keluar-masuk bus dekat gerbang tol Serang Timur guna mencegah kemacetan arteri.',
    ('UDARA', 'Sultan Aji Muhammad Sulaiman Sepinggan'): 'Penambahan frekuensi extra flight rute Balikpapan–Surabaya/Jakarta dan dukungan mobilitas logistik IKN.',
    ('UDARA', 'Hang Nadim'): 'Extra flight rute Batam–Medan/Padang/Jakarta guna menampung lonjakan perantau lintas pulau.',
    ('KA', 'SURABAYA GUBENG'): 'Penambahan KA Sancaka Tambahan (Surabaya–Yogyakarta) dan KA Pasundan Tambahan (Surabaya–Kiaracondong).',
    ('BUS', 'Giri Adipura'): 'Pemberangkatan teratur konvoi bus AKAP rute Wonogiri–Jabodetabek dan ramp check kelayakan rem/ban.'
}

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

    # Tingkatan Kebutuhan Armada
    if ratio >= 3.0 or (ratio >= 2.0 and pp >= 20000):
        pct = 20
        status_text = 'Sangat Kritis'
        status_badge = 'bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300'
    elif ratio >= 1.8 or (ratio >= 1.4 and pp >= 10000):
        pct = 15
        status_text = 'Tinggi / Kritis'
        status_badge = 'bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-300'
    elif ratio >= 1.2 or pp >= 5000:
        pct = 10
        status_text = 'Padat Tinggi'
        status_badge = 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
    else:
        pct = 5
        status_text = 'Terkendali'
        status_badge = 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'

    add_arm = int(round(ap * (pct / 100.0)))
    total_arm = ap + add_arm

    if moda == 'UDARA':
        moda_label = '✈ Udara'
        sarana_type = 'Pesawat Jet Komersial'
        sarana_unit = 'penerbangan'
    elif moda == 'KA':
        moda_label = '🚆 Kereta Api'
        if 'KCJB' in nama.upper() or 'WHOOSH' in nama.upper():
            sarana_type = 'Kereta Cepat Whoosh'
        elif 'KRL' in nama.upper() or 'COMMUTER' in nama.upper():
            sarana_type = 'KRL Commuter Line'
        else:
            sarana_type = 'Rangkaian Kereta Api'
        sarana_unit = 'perjalanan KA'
    elif moda == 'BUS':
        moda_label = '🚌 Bus AKAP'
        sarana_type = 'Armada Bus Antar Kota'
        sarana_unit = 'trip bus'
    elif moda == 'ASDP':
        moda_label = '⛴ ASDP Feri'
        sarana_type = 'Kapal Feri Ro-Ro'
        sarana_unit = 'trip kapal feri'
    else:
        moda_label = '🚢 Laut'
        sarana_type = 'Kapal Penumpang Pelni/Perintis'
        sarana_unit = 'call kapal laut'

    key = (moda, nama)
    if key in CUSTOM_ACTIONS:
        field_action = CUSTOM_ACTIONS[key]
    else:
        if moda == 'UDARA':
            field_action = 'Pengajuan izin extra flight pada rute padat, percepatan turnaround pesawat, dan koordinasi alokasi parking stand.' if pct >= 15 else 'Monitoring keterisian kursi penerbangan (SLF) dan optimalisasi boarding gate bandara.'
        elif moda == 'KA':
            field_action = 'Penambahan stamformasi kereta menjadi 10–12 gerbong dan penyiagaan lokomotif cadangan di dipo relasi utama.' if pct >= 15 else 'Pengawasan antrean boarding pass cetak mandiri dan sterilisasi peron stasiun.'
        elif moda == 'BUS':
            field_action = 'Pengoperasian armada bus pariwisata cadangan sebagai bus AKAP perbantuan dan ramp check kelayakan armada.' if pct >= 15 else 'Pemisahan jalur naik-turun penumpang terminal dan koordinasi jadwal keberangkatan bus.'
        elif moda == 'ASDP':
            field_action = 'Pemberlakuan pola tiba-bongkar-berangkat (TBB) di dermaga serta pengerahan kapal feri kapasitas muat besar.' if pct >= 15 else 'Pengaturan buffer zone antrean kendaraan roda dua dan sosialisasi tiket daring Ferizy.'
        else:
            field_action = 'Pemberian dispensasi penambahan trip kapal penumpang cepat dan pengawasan ketat manifes muatan.' if pct >= 15 else 'Optimalisasi ruang tunggu penumpang dermaga dan pengawasan ketat alat keselamatan (life jacket/sekoci).'

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
print(f"5. simpul_recommendations ({len(simpul_items)} simpul) berhasil diperbarui.")

# Simpan kembali ke bundle
with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)
print(f"6. File {bundle_path} berhasil disimpan!")

# ==============================================================================
# E. UPDATE INDEX.HTML DAN DASHBOARD_MOBILITAS_NASIONAL_2026.HTML
# ==============================================================================
print("7. Memperbarui index.html dan Dashboard_Mobilitas_Nasional_2026.html...")

bundle_str = json.dumps(bundle, ensure_ascii=False)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update const DATA = ...
data_pattern = re.compile(r'const DATA = \{.*?\};\n', re.DOTALL)
html = data_pattern.sub(f"const DATA = {bundle_str};\n", html, count=1)

# 2. Update modal rumus / methodology text
html = html.replace(
    'A. Baseline Normal (Februari 2026):',
    'A. Baseline Normal Operasional (Median 2026):'
)
html = html.replace(
    'P̃_Feb = (∑ P_Februari) / 28 Hari = 1.188.888 pnp/hari',
    'P̃_Median = Median(P_Harian 2026) = 1.321.644 pnp/hari'
)
html = html.replace(
    'Bulan Februari digunakan sebagai acuan normal karena bebas libur panjang nasional.',
    'Nilai Median harian dari seluruh 272 hari (Jan–Sep 2026) digunakan sebagai acuan normal sesuai metodologi robust Google Mobility & Van Lint (2005) agar kebal terhadap lonjakan ekstrem mudik.'
)

# 3. Update Tab 2 (Puncak Lebaran)
html = html.replace(
    'Persentase Lonjakan (%) terhadap Rata-rata Normal Februari',
    'Persentase Lonjakan (%) terhadap Baseline Normal (Median 2026)'
)
html = html.replace(
    'Perbandingan baseline harian Februari dengan volume puncak arus mudik dan arus balik',
    'Perbandingan baseline harian normal (Median 2026) dengan volume puncak arus mudik dan arus balik'
)
html = html.replace(
    'Baseline Normal (Feb)',
    'Baseline Normal (Median)'
)

# 4. Update Tab 3 (Modal Share)
html = html.replace(
    'Februari (Normal)',
    'Periode Normal (Median)'
)
html = html.replace(
    'antara periode normal (Februari) dan puncak arus mudik Lebaran (Maret)',
    'antara periode normal (Median 2026) dan puncak arus mudik Lebaran (Maret)'
)

# 5. Dropdown filter di Tab 1 (jika ada opsi Februari Baseline Normal)
html = html.replace(
    '<option value="2">Februari 2026 (Baseline Normal)</option>',
    '<option value="2">Februari 2026 (Kondisi Reguler)</option>'
)

# Simpan ke index.html dan Dashboard_Mobilitas_Nasional_2026.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('Dashboard_Mobilitas_Nasional_2026.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("=" * 80)
print("SUKSES PENUH! Seluruh dashboard, JSON bundle, dan HTML telah beralih ke BASELINE MEDIAN!")
print("=" * 80)
