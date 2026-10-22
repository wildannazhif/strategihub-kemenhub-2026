# 🇮🇩 StrategiHub Analytics 2026: Dashboard Mobilitas Nasional & Prediksi Nataru 2026/2027

[![GitHub Pages](https://img.shields.io/badge/Live-GitHub%20Pages-brightgreen?logo=github)](https://wildannazhif.github.io/strategihub-kemenhub-2026/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-blue)](https://wildannazhif.github.io/strategihub-kemenhub-2026/)
[![Data Source](https://img.shields.io/badge/Source-StrategiHub%20PUSDATIN%20Kemenhub-orange)](https://wildannazhif.github.io/strategihub-kemenhub-2026/)
[![Coverage](https://img.shields.io/badge/Verified%20Rows-209.885%20Baris-success)](https://wildannazhif.github.io/strategihub-kemenhub-2026/)

Dashboard terpadu pemantauan dan analisis mobilitas angkutan penumpang nasional lintas 5 moda transportasi (**✈ Udara, 🚆 Kereta Api, 🚌 Bus AKAP, ⛴ ASDP Feri Penyeberangan, dan 🚢 Transportasi Laut**) berbasis dataset operasional **StrategiHub PUSDATIN Kementerian Perhubungan Republik Indonesia Tahun 2026**.

---

## 🌐 Live Deployment
Akses langsung dashboard interaktif tanpa instalasi:
👉 **[https://wildannazhif.github.io/strategihub-kemenhub-2026/](https://wildannazhif.github.io/strategihub-kemenhub-2026/)**

---

## 🚀 Fitur & Modul Operasional

Dashboard ini terbagi menjadi **8 Modul Utama** yang dapat diakses melalui menu navigasi samping (*collapsible sidebar*):

1. **Kronologi Harian (272 Hari):** Tren pergerakan harian penumpang dan armada dari 1 Januari hingga 29 September 2026.
2. **Puncak Lebaran 2026 (13 – 29 Maret 2026):** Analisis komparatif periode mudik dan balik Lebaran (H-8 s/d H+8, Hari H: 21 Maret 2026) dengan metrik lonjakan volume. Label **Semua Moda** pada grafik persentase lonjakan dan tabel komparasi menunjukkan agregat kelima moda transportasi.
   * **Heatmap lonjakan:** Persentase lonjakan penumpang ditampilkan per moda dan periode dengan gradasi **merah muda hingga merah pekat**. Semua sel memakai skala yang sama; agregat **Semua Moda** dipisahkan di baris terakhir. Volume puncak dan baseline tersedia saat kursor diarahkan ke sel, dengan angka rinci pada tabel komparasi di bawah.
3. **Pangsa Pasar Antar-Moda:** Distribusi pangsa pasar (*modal share*) penumpang nasional dan tren pergeseran preferensi moda.
4. **Kinerja Load Factor (Rasio Beban Armada):** Analisis rasio penumpang per trip armada (P/A) untuk mengukur tingkat kepadatan fisik sarana.
5. **Registri Simpul Transportasi (Top 30 Hubs):** Peringkat dan performa 30 simpul terpadat nasional (bandara, stasiun, terminal, pelabuhan).
6. **Matriks Rekapitulasi 13 Indikator:** Rekap menyeluruh seluruh indikator utama operasional Kemenhub.
7. **Peta Spasial Simpul (Leaflet GIS):** Peta interaktif sebaran simpul transportasi di seluruh Indonesia dengan popup status performa dan koordinat geografis.
8. **Proyeksi Mobilitas Multimoda Q4 & Libur Nataru 2026/2027 (Horizon 100 Hari):**
   * **Model Prediktif Time Series:** Menggabungkan tren historis, siklus musiman akhir tahun (*end-of-year seasonal waves*), serta *event shocks* Natal 2026 dan Tahun Baru 2027.
   * **3 Skenario Prediksi:** Moderat (*Baseline*), Optimis (+12% Animo Wisata), dan Konservatif (Antisipasi Cuaca Ekstrem).
   * **Skenario Penambahan Armada Berangkat:** Target dihitung dari Rasio Normal historis setiap simpul, bukan tambahan persentase tetap berdasarkan kategori. Persentil nasional tetap digunakan untuk mengelompokkan urgensi.
   * **Sidebar Informasi & Kamus Rumus Dashboard:** Kompendium formula matematis lengkap untuk seluruh plot grafik, metrik dasar, rasio load factor, modal share, surge rate Lebaran 2026, indeks musiman mingguan, tolok ukur kepadatan simpul, formulasi model prediktif Nataru, hingga skenario penambahan Armada Berangkat.
   * **Rumus Perhitungan di Setiap Plot:** Setiap grafik, tabel, dan kartu KPI dilengkapi badge formula matematis transparan dan tautan rujukan langsung ke Informasi Dashboard.

---

## Status Urgensi dan Skenario Penambahan Armada Berangkat

Baseline menggunakan **median harian Penumpang Berangkat** dan **median harian Armada Berangkat**, dihitung terpisah dari pengamatan **1 Januari–12 Maret 2026**. Rasio Normal adalah hasil pembagian kedua median tersebut, tanpa pembulatan awal.

Tanggal puncak dipilih dari Penumpang Berangkat tertinggi pada **13–29 Maret 2026**; jika seri, digunakan tanggal paling awal. Armada Berangkat puncak diambil pada **tanggal yang sama**, bukan maksimum Armada Berangkat pada tanggal lain.

```text
Target Armada Berangkat = ceil(Penumpang Berangkat puncak × median Armada Berangkat / median Penumpang Berangkat)
Tambahan Armada Berangkat = max(0, target − Armada Berangkat puncak)
Total Armada Berangkat skenario = Armada Berangkat puncak + tambahan
Persentase tambahan = 100 × tambahan / Armada Berangkat puncak
```

`ceil` membulatkan ke atas ke bilangan bulat; perhitungan menggunakan nilai penuh. Armada Berangkat yang sudah ada tidak dikurangi, sehingga tambahan **0%** merupakan hasil valid.

**Pengelompokan urgensi tetap memakai persentil empiris nasional** dari `Rasio Puncak / Rasio Normal`: P90 ke atas = Sangat Kritis; P75–P90 = Tinggi / Kritis; P50–P75 = Padat; di bawah P50 = Terkendali. Batas bawah setiap kelompok termasuk dalam kelompok tersebut. Pengecualian volume kecil tetap didahulukan: Penumpang Berangkat puncak di bawah 100 masuk Terkendali. Simpul valid bervolume kecil tetap masuk populasi persentil. Persentil menggunakan interpolasi linear dan tidak dihitung ulang oleh filter. **Kategori tidak menentukan persentase tambahan.**

Median normal yang tidak tersedia/tidak positif, atau Armada Berangkat pada tanggal puncak yang tidak tersedia/tidak positif, menghasilkan **Data tidak cukup**. Baris tetap terlihat beserta alasannya, tetapi target, tambahan, total, dan persentase bernilai kosong (`—`), bukan angka sintetis, serta dikecualikan dari persentil dan agregat.

Agregat hanya memakai simpul valid: persentase agregat = 100 × total tambahan / total Armada Berangkat puncak dari simpul valid, bukan rata-rata persentase simpul. Tanggal puncak berbeda antarsimpul; agregat **bukan kebutuhan operasi serentak pada satu hari**. Ini skenario target beban historis, bukan bukti kapasitas nominal atau rekomendasi operasional final; penerapannya memerlukan kajian operator.

---

## 🛠️ Arsitektur Teknologi

* **Frontend:** HTML5, Tailwind CSS, Chart.js, Leaflet.js, Google Fonts (Inter & JetBrains Mono).
* **Pipeline Pengolahan Data:** Python 3 (Pandas, NumPy, Scipy, JSON).
* **Ukuran File Dashboard:** ~645 KB (*single-file self-contained bundle* yang langsung berjalan di semua peramban modern).

---

## 💻 Menjalankan & Membangun Ulang Secara Lokal

1. **Clone Repository:**
   ```bash
   git clone https://github.com/wildannazhif/strategihub-kemenhub-2026.git
   cd strategihub-kemenhub-2026
   ```

2. **Jalankan Dashboard:**
   Cukup buka file `index.html` atau `Dashboard_Mobilitas_Nasional_2026.html` langsung di Google Chrome, Microsoft Edge, atau browser lainnya.

3. **Menghitung Ulang Skenario dari CSV Operasional Lokal:**
   ```bash
   python scripts/generate_simpul_recommendations.py
   ```
   Perintah ini memperbarui `simpul_recommendations` dan `simpul_scenario_metadata` pada kedua bundle JSON dan kedua file HTML, tanpa membangun ulang template atau mengganti bagian dashboard lainnya.

4. **Membangun Ulang Template Lengkap (Opsional):**
   ```bash
   python scripts/build_production_dashboard_sidebar.py
   ```
   Rebuild template menimpa kedua file HTML. Untuk sekadar memperbarui skenario pada dashboard saat ini, gunakan perintah pada langkah 3.

5. **Menjalankan Pengujian Perhitungan Skenario:**
   ```bash
   python -m unittest discover -s tests -v
   ```

---

*Hak Cipta © 2026 PUSDATIN Kementerian Perhubungan Republik Indonesia.*
