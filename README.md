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
2. **Puncak Lebaran 2026 (13 – 29 Maret 2026):** Analisis komparatif periode mudik dan balik Lebaran (H-8 s/d H+8, Hari H: 21 Maret 2026) dengan metrik lonjakan volume.
3. **Pangsa Pasar Antar-Moda:** Distribusi pangsa pasar (*modal share*) penumpang nasional dan tren pergeseran preferensi moda.
4. **Kinerja Load Factor (Rasio Beban Armada):** Analisis rasio penumpang per trip armada (P/A) untuk mengukur tingkat kepadatan fisik sarana.
5. **Registri Simpul Transportasi (Top 30 Hubs):** Peringkat dan performa 30 simpul terpadat nasional (bandara, stasiun, terminal, pelabuhan).
6. **Matriks Rekapitulasi 13 Indikator:** Rekap menyeluruh seluruh indikator utama operasional Kemenhub.
7. **Peta Spasial Simpul (Leaflet GIS):** Peta interaktif sebaran simpul transportasi di seluruh Indonesia dengan popup status performa dan koordinat geografis.
8. **Proyeksi Mobilitas Multimoda Q4 & Libur Nataru 2026/2027 (Horizon 100 Hari):**
   * **Model Prediktif Time Series:** Menggabungkan tren historis, siklus musiman akhir tahun (*end-of-year seasonal waves*), serta *event shocks* Natal 2026 dan Tahun Baru 2027.
   * **3 Skenario Prediksi:** Moderat (*Baseline*), Optimis (+12% Animo Wisata), dan Konservatif (Antisipasi Cuaca Ekstrem).
   * **Simulasi Kebutuhan Armada Berdasarkan Prasarana / Simpul:** Simulator kebutuhan penambahan kapal feri di pelabuhan (Merak, Bakauheni, Ketapang), kereta api di stasiun (Pasar Senen, Gambir, Yogyakarta), penerbangan di bandara (Ngurah Rai, Soekarno-Hatta), dan bus di terminal (Purabaya).
   * **Sidebar Informasi & Kamus Rumus Dashboard:** Kompendium formula matematis lengkap untuk seluruh plot grafik, metrik dasar, rasio load factor, modal share, surge rate Lebaran 2026, indeks musiman mingguan, tolok ukur kepadatan simpul, formulasi model prediktif Nataru, hingga simulasi kapasitas armada.
   * **Rumus Perhitungan di Setiap Plot:** Setiap grafik, tabel, dan kartu KPI dilengkapi badge formula matematis transparan dan tautan rujukan langsung ke Informasi Dashboard.

---

## 📊 Metodologi Penentuan Status Kepadatan Simpul

Status kesibukan simpul ditentukan melalui **3 tolok ukur matematis dan operasional**:
1. **Rasio Beban per Armada ($\frac{\text{Penumpang}}{\text{Trip Armada}}$):** Membandingkan rasio hari normal vs hari puncak. Contoh: Pelabuhan Bakauheni melonjak dari 206 pnp/kapal menjadi **614 pnp/kapal** saat puncak.
2. **Persentase Lonjakan vs Hari Normal (*Surge %*):**
   * 🔴 **Sangat Kritis (95% – 99%):** Lonjakan > +80% s/d +200% (Merak +92%, Bakauheni +195%, Pasar Senen +88%).
   * 🟠 **Padat Tinggi / Siaga (85% – 94%):** Lonjakan +50% s/d +80% (Gambir +56%, Yogyakarta +61%, Ngurah Rai).
   * 🟡 **Sibuk Terkendali (65% – 84%):** Lonjakan +25% s/d +50% (Purabaya +49%, Batam Center +59%).
   * 🟢 **Stabil / Normal (< 65%):** Lonjakan < +25%.
3. **Batas Kapasitas Fisik Prasarana:** Daya tampung kantong parkir buffer zone pelabuhan, batas kursi gerbong KA, batas utilisasi runway slot bandara (98%), dan waktu tunggu peron terminal bus.

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

3. **Membangun Ulang dari Data Mentah (Opsional):**
   ```bash
   python scripts/build_production_dashboard_sidebar.py
   ```

---

*Hak Cipta © 2026 PUSDATIN Kementerian Perhubungan Republik Indonesia.*
