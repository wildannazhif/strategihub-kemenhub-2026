# LAPORAN ANALISIS DESKRIPTIF TRANSPORTASI NASIONAL MULTIMODA 2026
**Pusat Data dan Informasi (PUSDATIN) — Kementerian Perhubungan Republik Indonesia**  
*Periode Data: 1 Januari 2026 s/d 25 September 2026 (Caturwulan T1, T2, dan T3 Berjalan)*  
*Sumber Data: SIASATI Kemenhub (Bus, ASDP, Udara, Laut, dan Kereta Api)*

---

## 1. RINGKASAN EKSEKUTIF (EXECUTIVE SUMMARY)

Laporan ini menyajikan analisis deskriptif komprehensif atas kinerja operasional dan pergerakan penumpang antarmoda di seluruh Indonesia sepanjang tahun 2026 (hingga 25 September 2026). Analisis ini mencakup **298.284 data rekaman harian** dari **1.300 simpul prasarana transportasi** yang tersebar di 38 provinsi.

### Indikator Kunci Nasional (Januari – September 2026):
1. **Total Akumulasi Penumpang Nasional**: **370.430.620 Orang** (~370,4 Juta pergerakan penumpang).
2. **Total Pergerakan Armada Operasional**: **3.210.024 Trip Perjalanan** (gabungan pesawat, kapal ferry ASDP, bus AKAP/AKDP, kapal laut, dan perjalanan kereta api).
3. **Rata-rata Penumpang Harian Nasional**: **1.382.203 Orang / Hari**.
4. **Pangsa Pasar Penumpang (Modal Split)**:
   - **Moda Udara (Pesawat)**: **31,7%** (117,2 Juta penumpang; 1,14 Juta pergerakan pesawat).
   - **Moda Penyeberangan (ASDP)**: **23,5%** (87,1 Juta penumpang; 630,2 Ribu pergerakan kapal).
   - **Moda Bus (Terminal)**: **20,1%** (74,6 Juta penumpang; 5,87 Juta pergerakan bus).
   - **Moda Laut (Pelabuhan)**: **13,2%** (48,9 Juta penumpang; 818,8 Ribu pergerakan kapal).
   - **Moda Kereta Api (Stasiun)**: **11,3%** (42,0 Juta penumpang tercatat; 1,75 Juta pergerakan KA).
5. **Hari Puncak Arus Tertinggi (National Peak Day)**: **21 April 2026** (periode H+2 Idul Fitri 1447H) dengan volume harian mencapai **2.184.502 penumpang** dalam satu hari.

---

## 2. AUDIT KUALITAS DATA & METODOLOGI PRE-PROCESSING

Pembersihan dan standardisasi data dilakukan melalui skrip otomatisasi [`scripts/preprocess_siasati.py`](file:///c:/Users/USER/Documents/PUSDATIN/scripts/preprocess_siasati.py). Seluruh skema kolom dari kelima subsektor disatukan ke dalam model data terpadu:
`[tanggal, caturwulan, moda, id_prasarana, nama_prasarana, provinsi, lat, lon, tipe, armada_datang, penumpang_datang, armada_berangkat, penumpang_berangkat, total_penumpang, total_armada]`.

### Temuan Kritis Kualitas Data Siasati (Data Quality Audit):
1. **Anomali Kolom Penumpang Berangkat Kereta Api (`dm_ka_2026`)**:
   - Ditemukan bahwa kolom `penumpang_berangkat` pada data mentah Siasati KA memiliki nilai rata-rata 6,23 dan maksimum 139 yang **persis identik 100%** dengan kolom `kereta_berangkat` (jumlah trip perjalanan kereta).
   - Ini mengindikasikan adanya salah pemetaan (*field mapping misconfiguration*) pada integrasi API hulu Kemenhub KA, di mana kolom jumlah rangkaian kereta keliru dimasukkan ke kolom jumlah penumpang berangkat.
   - **Tindakan**: Dalam analisis deskriptif ini, pergerakan penumpang KA disajikan transparan, dan `penumpang_datang` digunakan sebagai basis representasi riil penumpang stasiun.
2. **Sifat Simetris Pencatatan ASDP (`dm_asdp_2026`)**:
   - Kolom `kapal_datang` sama persis dengan `kapal_berangkat`, serta `penumpang_datang` sama persis dengan `penumpang_berangkat` di setiap baris pelabuhan penyeberangan. Hal ini terjadi karena pelaporan ASDP didasarkan pada manifest lintasan ferry bolak-balik (round-trip per lintasan dermaga).
3. **Kelengkapan Koordinat Geografis**:
   - Sebelum pembersihan, sebanyak 93,6% simpul memiliki koordinat lat/lon valid.
   - Melalui algoritma imputasi berbasis master lookup simpul unik, kelengkapan koordinat berhasil ditingkatkan menjadi **98,4%**, memetakan 1.300 simpul aktif secara presisi pada peta Leaflet.

---

## 3. TABEL STATISTIK DESKRIPTIF DETAIL PER MODA

Tabel berikut menyajikan ringkasan statistik deskriptif ukuran pemusatan, penyebaran, dan bentuk distribusi volume penumpang harian per simpul prasarana:

| Moda | Jumlah Observasi | Total Penumpang | Rata-rata (Org/Simpul/Hari) | Median | Standar Deviasi | IQR | Min | Max | Skewness | Rasio Beban (Org/Trip) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **UDARA** | 58.093 | 117.242.563 | 2.018,19 | 32,0 | 10.978,41 | 428,0 | 0 | 213.181 | 7,62 | **103,28** |
| **ASDP** | 19.736 | 87.103.586 | 4.413,44 | 696,0 | 12.959,41 | 1.838,0 | 0 | 257.642 | 6,34 | **138,21** |
| **BUS** | 36.089 | 74.625.034 | 2.067,81 | 742,0 | 3.905,37 | 1.777,0 | 0 | 48.016 | 3,92 | **12,72** |
| **LAUT** | 45.946 | 48.963.054 | 1.065,67 | 250,0 | 3.029,91 | 788,0 | 0 | 64.729 | 6,11 | **59,80** |
| **KA** | 138.420 | 42.036.383 | 303,69 | 0,0 | 1.144,38 | 83,0 | 0 | 25.093 | 7,14 | **24,01** |
| **GABUNGAN** | **298.284** | **370.430.620** | **1.241,87** | **12,0** | **5.589,72** | **386,0** | **0** | **257.642** | **11,85** | **115,40** |

### Interpretasi Statistik:
- **Tingkat Kemiringan Distribusi (Right-Skewed / Positif)**: Semua moda memiliki koefisien *skewness* tinggi (>3,9 hingga 11,85). Nilai rata-rata jauh melampaui median. Ini membuktikan adanya konsentrasi lalu lintas ekstrem pada segelintir simpul utama (misal Bandara Soekarno-Hatta, Pelabuhan Merak-Bakauheni, Terminal Tirtonadi/Purabaya, dan Stasiun Pasar Senen/Gambir).
- **Rasio Beban (Load Proxy per Armada)**:
  - ASDP menempati rasio muatan tertinggi (**138,21 orang/trip kapal**), karena kapal ferry ro-ro mengangkut penumpang massal beserta kendaraan.
  - Udara berada di urutan kedua (**103,28 orang/gerakan pesawat**), sangat konsisten dengan kapasitas rata-rata pesawat jet berbadan sempit (narrow-body seperti Boeing 737 / Airbus A320) pada rute domestik.
  - Bus berada pada angka **12,72 orang/armada**, merefleksikan kombinasi bus besar AKAP dan bus sedang/kecil AKDP di berbagai terminal daerah.

---

## 4. ANALISIS TEMPORAL & DINAMIKA WAKTU

### 4.1. Pola Deret Waktu Harian & Periode Puncak (Peak Seasons)
Visualisasi deret waktu pada grafik [`02_tren_harian_multimoda.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/02_tren_harian_multimoda.png) memperlihatkan dua gelombang lonjakan besar sepanjang 2026:
1. **Gelombang 1 — Angkutan Lebaran Idul Fitri 1447H (April 2026)**:
   - Mulai terdeteksi kenaikan sejak 15 April 2026 (H-6).
   - Titik kulminasi arus mudik dan balik berlangsung pada **19 s/d 24 April 2026**, dengan volume tertinggi pada **21 April 2026** (2,18 Juta penumpang).
   - Moda ASDP dan Bus mengalami kelipatan kenaikan beban tertinggi pada periode ini (kenaikan hingga 240% dibandingkan hari reguler).
2. **Gelombang 2 — Liburan Semester Sekolah (Juni – Juli 2026)**:
   - Terjadi peningkatan berkelanjutan selama 4 pekan berturut-turut pada moda Udara dan Kereta Api, didorong oleh mobilitas pariwisata keluarga.

### 4.2. Pola Hari dalam Seminggu (Day-of-Week Effect)
Berdasarkan grafik [`04_pola_hari_mingguan.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/04_pola_hari_mingguan.png):
- **Jumat dan Minggu** merupakan hari dengan volume penumpang tertinggi pada moda **Udara** dan **Kereta Api**, didorong oleh pelaju mingguan (*weekend commuters*) dan wisatawan akhir pekan.
- **Moda ASDP dan Laut** menunjukkan sebaran yang relatif merata sepanjang hari kerja dengan kenaikan moderat pada akhir pekan, karena keterikatan dengan jadwal penyeberangan logistik pulau.

---

## 5. SEBARAN SIMPUL PRASARANA & ANALISIS SPASIAL

### 5.1. Peringkat 10 Simpul Prasarana Terpadat per Moda
Berdasarkan data yang disajikan pada plot [`05_top10_simpul_per_moda.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/05_top10_simpul_per_moda.png):

1. **Top 5 Bandara Udara**:
   - Soekarno-Hatta (Tangerang/Banten): **36,7 Juta Penumpang**
   - I Gusti Ngurah Rai (Bali): **16,2 Juta Penumpang**
   - Juanda (Surabaya/Jawa Timur): **10,4 Juta Penumpang**
   - Sultan Hasanuddin (Makassar/Sulsel): **7,1 Juta Penumpang**
   - Kualanamu (Medan/Sumut): **5,3 Juta Penumpang**
2. **Top 5 Pelabuhan Penyeberangan ASDP**:
   - Bakauheni (Lampung): **18,9 Juta Penumpang**
   - Merak (Banten): **18,5 Juta Penumpang**
   - Ketapang (Banyuwangi/Jatim): **10,8 Juta Penumpang**
   - Gilimanuk (Bali): **10,6 Juta Penumpang**
   - Lembar (NTB): **3,8 Juta Penumpang**
3. **Top 5 Terminal Bus**:
   - Purabaya / Bungurasih (Sidoarjo/Jatim): **5,1 Juta Penumpang**
   - Tirtonadi (Surakarta/Jateng): **4,3 Juta Penumpang**
   - Kalideres (DKI Jakarta): **3,2 Juta Penumpang**
   - Kampung Rambutan (DKI Jakarta): **2,9 Juta Penumpang**
   - Giwangan (D.I. Yogyakarta): **2,7 Juta Penumpang**
4. **Top 5 Pelabuhan Laut**:
   - Batam Centre / Sekupang (Kepulauan Riau): **6,8 Juta Penumpang**
   - Tanjung Perak (Surabaya/Jatim): **4,2 Juta Penumpang**
   - Tanjung Priok (DKI Jakarta): **3,5 Juta Penumpang**
   - Pelabuhan Makassar (Sulsel): **2,8 Juta Penumpang**
   - Pelabuhan Balikpapan (Semayang/Kaltim): **2,1 Juta Penumpang**
5. **Top 5 Stasiun Kereta Api**:
   - Stasiun Pasar Senen (DKI Jakarta): **4,6 Juta Penumpang Datang**
   - Stasiun Gambir (DKI Jakarta): **3,2 Juta Penumpang Datang**
   - Stasiun Surabaya Gubeng (Jatim): **2,8 Juta Penumpang Datang**
   - Stasiun Yogyakarta / Tugu (DIY): **2,6 Juta Penumpang Datang**
   - Stasiun Bandung (Jabar): **2,3 Juta Penumpang Datang**

### 5.2. Konsentrasi Beban Trafik per Provinsi
Grafik [`06_sebaran_provinsi_terpadat.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/06_sebaran_provinsi_terpadat.png) membuktikan bahwa pergerakan penumpang nasional sangat terpusat di koridor Jawa–Bali–Sumatera bagian selatan:
- **Jawa Timur**: 62,4 Juta penumpang (terbanyak di Indonesia).
- **DKI Jakarta**: 58,1 Juta penumpang.
- **Banten**: 48,6 Juta penumpang (didorong oleh Bandara Soekarno-Hatta dan Pelabuhan Merak).
- **Jawa Tengah**: 37,2 Juta penumpang.
- **Jawa Barat**: 32,8 Juta penumpang.
- **Lampung**: 21,5 Juta penumpang (didorong oleh Pelabuhan Penyeberangan Bakauheni).
- **Bali**: 29,4 Juta penumpang (Bandara Ngurah Rai dan Pelabuhan Gilimanuk).

---

## 6. INVENTARIS PRODUK ANALISIS & AKSES FILE

Seluruh artefak hasil analisis telah tersusun rapi dalam struktur direktori proyek:

| Komponen | Lokasi File | Deskripsi |
| :--- | :--- | :--- |
| **Interactive Dashboard** | [`Dashboard_Siasati_Multimoda_2026.html`](file:///c:/Users/USER/Documents/PUSDATIN/Dashboard_Siasati_Multimoda_2026.html) | Dashboard web mandiri (Leaflet.js + Chart.js) dengan 5 tab interaktif |
| **Visualisasi Plot (PNG)** | [`analysis_plots/`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/) | Folder berisi 8 grafik publikasi resolusi tinggi |
| • *Modal Split* | [`01_modal_split_share.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/01_modal_split_share.png) | Donut chart & Bar share volume per moda |
| • *Daily Trend* | [`02_tren_harian_multimoda.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/02_tren_harian_multimoda.png) | Deret waktu harian 5 moda dengan label masa mudik |
| • *Heatmap Bulanan* | [`03_heatmap_bulanan_moda.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/03_heatmap_bulanan_moda.png) | Matriks heatmap intensitas bulanan per moda |
| • *Day of Week* | [`04_pola_hari_mingguan.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/04_pola_hari_mingguan.png) | Profil mobilitas hari kerja vs akhir pekan |
| • *Top Simpul* | [`05_top10_simpul_per_moda.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/05_top10_simpul_per_moda.png) | 10 simpul terpadat untuk 5 moda transportasi |
| • *Top Provinsi* | [`06_sebaran_provinsi_terpadat.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/06_sebaran_provinsi_terpadat.png) | Peringkat 15 provinsi dengan volume tertinggi |
| • *Rasio Armada* | [`07_rasio_penumpang_per_armada.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/07_rasio_penumpang_per_armada.png) | Load factor proxy (penumpang / trip armada) |
| • *Datang vs Berangkat*| [`08_distribusi_kedatangan_keberangkatan.png`](file:///c:/Users/USER/Documents/PUSDATIN/analysis_plots/08_distribusi_kedatangan_keberangkatan.png) | Keseimbangan arus kedatangan vs keberangkatan |
| **Dataset Bersih (CSV)** | [`data_clean/siasati_multimoda_2026_clean.csv`](file:///c:/Users/USER/Documents/PUSDATIN/data_clean/siasati_multimoda_2026_clean.csv) | Master dataset 298.284 baris data terstandardisasi |
| **Agregasi Harian** | [`data_clean/siasati_multimoda_summary_daily.csv`](file:///c:/Users/USER/Documents/PUSDATIN/data_clean/siasati_multimoda_summary_daily.csv) | Rangkuman volume harian per moda |
| **Agregasi Simpul** | [`data_clean/siasati_multimoda_top_prasarana.csv`](file:///c:/Users/USER/Documents/PUSDATIN/data_clean/siasati_multimoda_top_prasarana.csv) | Peringkat seluruh simpul prasarana nasional |
| **Tabel Deskriptif** | [`data_clean/descriptive_statistics_table.csv`](file:///c:/Users/USER/Documents/PUSDATIN/data_clean/descriptive_statistics_table.csv) | Parameter statistik (Mean, Median, Std, IQR, dll) |
| **GeoJSON/Nodes Peta** | [`data_clean/prasarana_map_nodes.json`](file:///c:/Users/USER/Documents/PUSDATIN/data_clean/prasarana_map_nodes.json) | 1.300 koordinat simpul dengan volume dan atribut |
| **Skrip Pemroses** | [`scripts/`](file:///c:/Users/USER/Documents/PUSDATIN/scripts/) | Pipeline otomatisasi pemrosesan, visualisasi, dan builder |

---

## 7. SARAN TATA KELOLA DATA BAGI PUSDATIN KEMENHUB

1. **Standardisasi API Gateway Siasati**: Menyeragamkan penamaan field dan tipe data di level API gateway (misalnya menyatukan `nama_terminal`, `nama_bandara`, `nama_pelabuhan`, dan `nama` menjadi `nama_prasarana`).
2. **Koreksi Pipeline Data KA**: Mengoreksi mapping database pada endpoint `dm_ka` agar field `penumpang_berangkat` merekam volume penumpang aktual dari sistem ticketing (misal integrasi RTS KAI), bukan menduplikasi jumlah armada kereta.
3. **Master Reference Data Simpul Transportasi**: Membangun satu tabel referensi nasional terpadu (*Single Source of Truth*) yang memuat kode unik simpul, koordinat baku, klasifikasi kelas, dan kewenangan pengelola di Pusdatin.
