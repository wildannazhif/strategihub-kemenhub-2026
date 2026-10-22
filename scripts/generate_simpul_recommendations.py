import os
import json
import numpy as np
import pandas as pd

RAW_CSV = r"c:\Users\USER\Documents\PUSDATIN\siasati_multimoda_2026.csv"
BUNDLE_PATH = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"

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

def generate_recommendations():
    print(f"Membaca dataset mentah: {RAW_CSV}...")
    df = pd.read_csv(RAW_CSV, low_memory=False).drop_duplicates(keep='first')

    key_cols = ['tanggal', 'caturwulan', 'moda', 'id_prasarana']
    meta_cols = ['nama_prasarana', 'provinsi']
    metrics = ['penumpang_datang', 'penumpang_berangkat', 'armada_datang', 'armada_berangkat']

    agg_dict = {m: 'sum' for m in metrics}
    for c in meta_cols:
        agg_dict[c] = 'first'

    df_clean = df.groupby(key_cols, as_index=False, dropna=False).agg(agg_dict)

    # Baseline: Februari 2026
    feb = df_clean[df_clean['tanggal'].between('2026-02-01', '2026-02-28')]
    feb_hub = feb.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
        pnp_brg_biasa=('penumpang_berangkat', 'mean'),
        arm_brg_biasa=('armada_berangkat', 'mean')
    ).reset_index()

    # Peak: 13 - 29 Maret 2026
    peak = df_clean[df_clean['tanggal'].between('2026-03-13', '2026-03-29')]
    peak_hub = peak.groupby(['moda', 'nama_prasarana', 'provinsi']).agg(
        pnp_brg_puncak=('penumpang_berangkat', 'max'),
        arm_brg_puncak=('armada_berangkat', 'max')
    ).reset_index()

    merged = pd.merge(feb_hub, peak_hub, on=['moda', 'nama_prasarana', 'provinsi'], how='outer').fillna(0)
    merged = merged[(merged['arm_brg_puncak'] > 0) & (merged['pnp_brg_puncak'] > 0)]
    merged = merged.sort_values(by='pnp_brg_puncak', ascending=False).reset_index(drop=True)

    print(f"Total simpul aktif keberangkatan: {len(merged)}")

    # 1. Pra-kalkulasi rasio load factor untuk menentukan ambang persentil empiris nasional
    temp_calc = []
    for idx, r in merged.iterrows():
        pb = int(round(r['pnp_brg_biasa']))
        ab = int(round(r['arm_brg_biasa']))
        pp = int(round(r['pnp_brg_puncak']))
        ap = int(round(r['arm_brg_puncak']))
        lfb = round(pb / ab, 1) if ab > 0 else 0
        lfp = round(pp / ap, 1) if ap > 0 else 0
        ratio = round(lfp / lfb, 2) if lfb > 0 else (2.5 if pp >= 5000 else 1.2)
        temp_calc.append({'pb': pb, 'ab': ab, 'pp': pp, 'ap': ap, 'lfb': lfb, 'lfp': lfp, 'ratio': ratio})

    all_ratios = np.array([x['ratio'] for x in temp_calc])
    p50 = float(np.percentile(all_ratios, 50))
    p75 = float(np.percentile(all_ratios, 75))
    p90 = float(np.percentile(all_ratios, 90))
    print(f"Ambang Persentil Lonjakan Load Factor: P50={p50:.2f}x, P75={p75:.2f}x, P90={p90:.2f}x")

    items = []
    for idx, r in merged.iterrows():
        moda = r['moda']
        nama = r['nama_prasarana']
        prov = r['provinsi']
        calc = temp_calc[idx]
        
        pb = calc['pb']
        ab = calc['ab']
        pp = calc['pp']
        ap = calc['ap']
        lfb = calc['lfb']
        lfp = calc['lfp']
        ratio = calc['ratio']

        # Penentuan Persentase Kebutuhan Tambahan Armada Berbasis Persentil Lonjakan Load Factor (TCQSM & TRB Standard)
        # Simpul perintis sangat kecil (pp < 100) diklasifikasikan ke Terkendali karena tidak memicu defisit kapasitas nasional
        if ratio >= p90 and pp >= 100:
            pct = 20
            status_text = 'Sangat Kritis'
            status_badge = 'bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300'
        elif ratio >= p75 and pp >= 100:
            pct = 15
            status_text = 'Tinggi / Kritis'
            status_badge = 'bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-300'
        elif ratio >= p50 and pp >= 100:
            pct = 10
            status_text = 'Padat'
            status_badge = 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
        else:
            pct = 5
            status_text = 'Terkendali'
            status_badge = 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'
        add_arm = int(round(ap * (pct / 100.0)))
        total_arm = ap + add_arm

        # Label & Moda configuration
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
            sarana_type = 'Kapal Ro-Ro Feri'
            sarana_unit = 'trip kapal'
        else: # LAUT
            moda_label = '🚢 Laut'
            sarana_type = 'Kapal Penumpang & Cepat'
            sarana_unit = 'trip kapal'

        # Action rekomendasi
        if (moda, nama) in CUSTOM_ACTIONS:
            field_action = CUSTOM_ACTIONS[(moda, nama)]
        else:
            if moda == 'UDARA':
                if pct >= 15:
                    field_action = 'Pengajuan darurat slot extra flight ke Kemenhub/AirNav dan perpanjangan operasional bandara malam hari.'
                elif pct == 10:
                    field_action = 'Pemberian izin extra flight pada jam sepi/malam hari (red-eye flight) serta mitigasi antrean check-in.'
                else:
                    field_action = 'Penyiagaan stand-by aircraft perbantuan dan optimalisasi kelancaran bagasi terminal.'
            elif moda == 'KA':
                if pct >= 15:
                    field_action = 'Pengoperasian Kereta Luar Biasa (KLB) Tambahan relasi padat dan penambahan panjang stamformasi maksimal.'
                elif pct == 10:
                    field_action = 'Optimalisasi kapasitas gerbong penumpang (stamformasi 10-12 kereta) dan pengaturan flow boarding gate.'
                else:
                    field_action = 'Penyiagaan rangkaian perbantuan dan pengetatan inspeksi keandalan wesel/sinyal stasiun.'
            elif moda == 'ASDP':
                if pct >= 20:
                    field_action = 'Penerapan pola tiba-bongkar-berangkat (TBB), percepatan port time, dan pengerahan kapal feri kapasitas besar.'
                elif pct == 15:
                    field_action = 'Pengoperasian dermaga cadangan/ponton, percepatan giliran sandar, dan rekayasa buffer zone kendaraan.'
                else:
                    field_action = 'Penambahan trip pelayaran harian dan pengaturan pemisahan jalur antrean kendaraan roda dua vs roda empat.'
            elif moda == 'BUS':
                if pct >= 15:
                    field_action = 'Pengerahan bus bantuan pariwisata cadangan dan pemberlakuan rekayasa drop-off zona peron cepat terminal.'
                elif pct == 10:
                    field_action = 'Pengaturan rotasi kedatangan bus antar kota agar tidak menumpuk dan pelaksanaan ramp check armada.'
                else:
                    field_action = 'Penyiagaan armada cadangan PO bus di pool terminal dan pengawasan tarif batas atas.'
            else: # LAUT
                if pct >= 15:
                    field_action = 'Pemberian dispensasi penambahan trip kapal penumpang cepat dan pengawasan ketat manifes muatan.'
                elif pct == 10:
                    field_action = 'Optimalisasi ruang tunggu penumpang dermaga dan pengawasan ketat alat keselamatan (life jacket/sekoci).'
                else:
                    field_action = 'Penjadwalan extra trip kapal pelayaran rakyat dan koordinasi peringatan dini cuaca maritim BMKG.'

        items.append({
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

    # Simpan ke bundle JSON
    with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
        bundle_data = json.load(f)

    bundle_data['simpul_recommendations'] = items

    with open(BUNDLE_PATH, 'w', encoding='utf-8') as f:
        json.dump(bundle_data, f, ensure_ascii=False)

    print(f"Berhasil memperbarui {BUNDLE_PATH} dengan {len(items)} simpul rekomendasi!")
    print(f"Ukuran file bundle sekarang: {os.path.getsize(BUNDLE_PATH) / 1024:.1f} KB")

if __name__ == '__main__':
    generate_recommendations()
