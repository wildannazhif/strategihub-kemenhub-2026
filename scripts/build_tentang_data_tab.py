import re
import os

FILES = [
    r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html",
    r"c:\Users\USER\Documents\PUSDATIN\index.html"
]

KATEX_HEAD = """  <!-- KaTeX Professional Mathematical Typesetting -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" onload="if(window.renderKaTeXFormulas)renderKaTeXFormulas();"></script>
"""

TAB_BUTTON = """          <!-- TAB 9: TENTANG DATA & KAMUS RUMUS -->
          <button id="nav-btn-tentang-data" onclick="switchTab('tab-tentang-data', 'Informasi & Kamus Rumus Dashboard', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 shrink-0"></span>
            <span class="truncate font-semibold text-indigo-700 dark:text-indigo-400">Tentang Data & Rumus</span>
          </button>"""

TAB_CONTENT = """      <!-- ========================================================= -->
      <!-- TAB 9: INFORMASI, METODOLOGI & KAMUS RUMUS DASHBOARD        -->
      <!-- ========================================================= -->
      <div id="tab-tentang-data" class="tab-content hidden space-y-6">

        <!-- Header Banner -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-xl p-6 text-white border border-indigo-900/50 shadow-md">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  DOKUMENTASI RESMI METODOLOGI
                </span>
                <span class="text-xs text-slate-400 font-mono">• PUSDATIN KEMENHUB 2026</span>
              </div>
              <h2 class="text-xl sm:text-2xl font-black tracking-tight text-white">
                Informasi Sistem, Metodologi Analisis & Kamus Rumus
              </h2>
              <p class="text-xs sm:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
                Kamus lengkap formulasi matematis, definisi notasi variabel, standar rekayasa transportasi (TCQSM & TRB), serta protokol integritas data operasional StrategiHub Multimoda 2026.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span class="px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-md border border-white/15 text-xs font-mono text-cyan-300">
                100% Notasi Matematis Terverifikasi
              </span>
            </div>
          </div>

          <!-- Quick Jump Navigation Chips -->
          <div class="mt-5 pt-4 border-t border-white/10 flex flex-wrap items-center gap-2 text-xs">
            <span class="text-[11px] font-bold text-indigo-300 uppercase tracking-wider mr-1">Lompat Cepat:</span>
            <a href="#rumus-sec-1" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">1. Integritas Data</a>
            <a href="#rumus-sec-2" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">2. Metrik Dasar</a>
            <a href="#rumus-sec-3" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">3. Load Factor</a>
            <a href="#rumus-sec-4" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">4. Modal Share</a>
            <a href="#rumus-sec-5" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">5. Arus Lebaran</a>
            <a href="#rumus-sec-6" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">6. Tren Provinsi</a>
            <a href="#rumus-sec-7" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">7. Rekomendasi Armada (Persentil)</a>
            <a href="#rumus-sec-8" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">8. Model Nataru</a>
            <a href="#rumus-sec-9" class="px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 transition-all text-slate-200">9. Tabel Simpul</a>
          </div>
        </div>

        <!-- Section 1: Sumber Data & Integritas Dataset -->
        <div id="rumus-sec-1" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-indigo-600"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                1. Sumber Data & Integritas Dataset Operasional
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold">
              SIASATI PUSDATIN
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Seluruh data operasional di dalam dashboard bersumber dari transaksi log harian <strong>StrategiHub PUSDATIN Kementerian Perhubungan 2026</strong> (<code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[11px] font-mono text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-slate-700">strategihub_multimoda_2026.csv</code>, 18,3 MB).
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Baris Tervalidasi</div>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white mt-1">209.964 Baris</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Dibersihkan dari 211.361 log mentah</div>
            </div>
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Rentang Pengamatan</div>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white mt-1">272 Hari</div>
              <div class="text-[11px] text-slate-500 mt-0.5">1 Jan s.d. 29 Sep 2026</div>
            </div>
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cakupan Prasarana</div>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white mt-1">1.208 Simpul</div>
              <div class="text-[11px] text-slate-500 mt-0.5">1.014 koordinat valid, 194 perintis</div>
            </div>
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cakupan Moda</div>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white mt-1">5 Moda Transportasi</div>
              <div class="text-[11px] text-slate-500 mt-0.5">Udara, KA, Bus, ASDP, Laut</div>
            </div>
          </div>
        </div>

        <!-- Section 2: Rumus Metrik Dasar -->
        <div id="rumus-sec-2" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-sky-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                2. Rumus Metrik Dasar (Total Penumpang & Armada Beroperasi)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-50 dark:bg-sky-950 text-sky-700 dark:text-sky-300 font-bold">
              Agregasi Dua Arah
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300">
            Setiap transaksi simpul prasarana mencatat pergerakan dua arah secara simultan, yaitu kedatangan (*arrival*) dan keberangkatan (*departure*).
          </p>

          <!-- Formula Box -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Total Penumpang Simpul / Harian:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                $$P_{\\text{total}} = P_{\\text{datang}} + P_{\\text{berangkat}}$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Total Pergerakan Armada:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                $$A_{\\text{total}} = A_{\\text{datang}} + A_{\\text{berangkat}}$$
              </div>
            </div>
          </div>

          <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
            <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">C. Rata-rata Penumpang Harian Nasional:</div>
            <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
              $$P_{\\text{avg}} = \\frac{\\sum_{t=1}^{N} P_{\\text{total}, t}}{N} = \\frac{371.890.120}{272} = 1.367.243\\text{ pnp/hari}$$
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$P_{\\text{total}}$$</td>
                  <td class="p-2.5 font-semibold">Total Penumpang</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang</td>
                  <td class="p-2.5">Jumlah seluruh pergerakan manusia di simpul prasarana (kedatangan + keberangkatan).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$P_{\\text{datang}}$$</td>
                  <td class="p-2.5 font-semibold">Penumpang Datang</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang</td>
                  <td class="p-2.5">Jumlah penumpang yang tiba atau turun dari sarana transportasi di simpul tujuan.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$P_{\\text{berangkat}}$$</td>
                  <td class="p-2.5 font-semibold">Penumpang Berangkat</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang</td>
                  <td class="p-2.5">Jumlah penumpang yang naik atau bertolak meninggalkan simpul awal (alasan antrean).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$A_{\\text{total}}$$</td>
                  <td class="p-2.5 font-semibold">Total Armada</td>
                  <td class="p-2.5 text-slate-500 font-mono">trip / flight / KA</td>
                  <td class="p-2.5">Total frekuensi pergerakan sarana transportasi yang beroperasi melayani mobilitas.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$N$$</td>
                  <td class="p-2.5 font-semibold">Periode Hari</td>
                  <td class="p-2.5 text-slate-500 font-mono">hari</td>
                  <td class="p-2.5">Jumlah hari kalender operasional pengamatan tahun 2026 (272 hari kontinu).</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 3: Rumus Load Factor Proxy -->
        <div id="rumus-sec-3" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-indigo-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                3. Rumus Rasio Okupansi Armada (Load Factor Proxy P/A)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold">
              Kepadatan per Armada
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300">
            <em>Load Factor Proxy</em> mengukur intensitas okupansi fisik rata-rata per satu satuan pergerakan armada sarana transportasi.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Rasio Beban Okupansi Armada (LF):</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                $$LF = \\frac{P_{\\text{total}}}{A_{\\text{total}}}$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Pertumbuhan Beban Okupansi (ΔLF):</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-rose-600 dark:text-rose-400 font-semibold text-sm">
                $$\\Delta LF = \\left( \\frac{LF_{\\text{puncak}} - LF_{\\text{baseline}}}{LF_{\\text{baseline}}} \\right) \\times 100\\%$$
              </div>
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$LF$$</td>
                  <td class="p-2.5 font-semibold">Load Factor Proxy</td>
                  <td class="p-2.5 text-slate-500 font-mono">pnp / armada</td>
                  <td class="p-2.5">Rata-rata penumpang yang dimuat per satu perjalanan armada (flight, trip bus, trip KA, kapal).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$LF_{\\text{puncak}}$$</td>
                  <td class="p-2.5 font-semibold">LF Periode Puncak</td>
                  <td class="p-2.5 text-slate-500 font-mono">pnp / armada</td>
                  <td class="p-2.5">Kepadatan muatan pada hari puncak ekstrem (H-3 Mudik atau H+3 Balik).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$LF_{\\text{baseline}}$$</td>
                  <td class="p-2.5 font-semibold">LF Kondisi Normal</td>
                  <td class="p-2.5 text-slate-500 font-mono">pnp / armada</td>
                  <td class="p-2.5">Kepadatan muatan pada hari kerja normal reguler tanpa pengaruh libur panjang.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-rose-600 dark:text-rose-400">$$\\Delta LF$$</td>
                  <td class="p-2.5 font-semibold">Persentase Lonjakan LF</td>
                  <td class="p-2.5 text-slate-500 font-mono">%</td>
                  <td class="p-2.5">Tingkat kelipatan desak per armada di lapangan dibanding hari biasa.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 4: Rumus Pangsa Pasar Antar-Moda -->
        <div id="rumus-sec-4" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                4. Rumus Pangsa Pasar Antar-Moda (Modal Share %)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold">
              Proporsi Multimoda
            </span>
          </div>

          <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
            <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">Pangsa Pasar Moda Transportasi m:</div>
            <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold text-sm">
              $$\\text{MS}_{m} = \\left( \\frac{P_{m}}{\\sum_{k \\in M} P_{k}} \\right) \\times 100\\%$$
            </div>
            <div class="text-[11px] text-slate-500 text-center">
              Di mana: $$\sum_{k \\in M} P_{k} = P_{\\text{Udara}} + P_{\\text{KA}} + P_{\\text{Bus}} + P_{\\text{ASDP}} + P_{\\text{Laut}}$$
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-emerald-600 dark:text-emerald-400">$$\\text{MS}_{m}$$</td>
                  <td class="p-2.5 font-semibold">Modal Share Moda m</td>
                  <td class="p-2.5 text-slate-500 font-mono">%</td>
                  <td class="p-2.5">Porsi kontribusi moda $m$ terhadap mobilitas nasional (contoh: Udara 32,0%, ASDP 23,4%).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-emerald-600 dark:text-emerald-400">$$P_{m}$$</td>
                  <td class="p-2.5 font-semibold">Volume Penumpang Moda m</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang</td>
                  <td class="p-2.5">Total penumpang yang memilih dan terangkut pada moda transportasi spesifik $m$.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 5: Rumus Periode Lebaran & Surge -->
        <div id="rumus-sec-5" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-rose-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                5. Rumus Analisis Puncak Lebaran & Lonjakan (Surge %)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950 text-rose-700 dark:text-rose-300 font-bold">
              Baseline Median Robust
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300">
            Posko Nasional Angkutan Lebaran 2026 berlangsung 17 Hari (13 s.d. 29 Maret 2026) dengan Hari H tunggal pada 21 Maret 2026.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Baseline Median Normal:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                $$P_{\\text{median}} = \\text{Median}(P_1, P_2, \\dots, P_{272}) = 1.321.644\\text{ pnp/h}$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Persentase Lonjakan (Surge %):</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-rose-600 dark:text-rose-400 font-semibold text-sm">
                $$\\text{Surge} = \\left( \\frac{P_{\\text{puncak}} - P_{\\text{median}}}{P_{\\text{median}}} \\right) \\times 100\\%$$
              </div>
            </div>
          </div>

          <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
            <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">C. Penomoran Hari Relatif Posko Lebaran:</div>
            <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 font-semibold text-sm">
              $$\\Delta \\text{Hari} = \\text{Tanggal Kalender} - 21\\text{ Maret } 2026$$
            </div>
            <div class="text-[11px] text-slate-500 text-center">
              Jika $\Delta < 0 \rightarrow \mathbf{H-|\Delta|}$ (Mudik) • Jika $\Delta = 0 \rightarrow \mathbf{Hari\ H}$ • Jika $\Delta > 0 \rightarrow \mathbf{H+|\Delta|}$ (Balik)
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$P_{\\text{median}}$$</td>
                  <td class="p-2.5 font-semibold">Baseline Median</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang / hari</td>
                  <td class="p-2.5">Nilai tengah mobilitas 272 hari, bebas dari distorsi lonjakan ekstrem (Google Mobility standard).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-rose-600 dark:text-rose-400">$$P_{\\text{puncak}}$$</td>
                  <td class="p-2.5 font-semibold">Volume Hari Puncak</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang / hari</td>
                  <td class="p-2.5">Realisasi tertinggi penumpang (contoh: 24 Maret 2026 = 2.415.296 orang).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-rose-600 dark:text-rose-400">$$\\text{Surge}$$</td>
                  <td class="p-2.5 font-semibold">Persentase Lonjakan</td>
                  <td class="p-2.5 text-slate-500 font-mono">%</td>
                  <td class="p-2.5">Persentase kelipatan pergerakan di atas kapasitas hari biasa (contoh: +103,2% di arus balik).</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

                <!-- Section 6: Rumus Analisis Tren & Lonjakan Bulanan per Provinsi -->
        <div id="rumus-sec-6" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                6. Rumus Analisis Tren & Lonjakan Bulanan per Provinsi (38 Provinsi)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-bold">
              Tab 1 • Wilayah & MoM
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Menghitung dinamika pertumbuhan bulanan, mengidentifikasi bulan puncak mobilitas regional, serta menentukan moda transportasi dominan di masing-masing 38 provinsi di Indonesia (aktif di panel kanan Tab 1).
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Laju Pertumbuhan Bulanan (Month-over-Month / MoM %):</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-blue-600 dark:text-blue-400 font-semibold text-sm">
                $$\text{MoM}_{\text{prov}, t} = \left( \frac{P_{\text{prov}, t} - P_{\text{prov}, t-1}}{P_{\text{prov}, t-1}} \right) \times 100\%$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Pangsa Moda Dominan Provinsi (%):</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-blue-600 dark:text-blue-400 font-semibold text-sm">
                $$\text{Share}_{m, \text{prov}} = \left( \frac{P_{m, \text{prov}}}{P_{\text{total}, \text{prov}}} \right) \times 100\%$$
              </div>
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-32">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-blue-600 dark:text-blue-400">$$\text{MoM}_{\text{prov}, t}$$</td>
                  <td class="p-2.5 font-semibold">Pertumbuhan MoM</td>
                  <td class="p-2.5 text-slate-500 font-mono">%</td>
                  <td class="p-2.5">Laju akselerasi keberangkatan penumpang provinsi pada bulan $t$ dibanding bulan sebelumnya $(t-1)$.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-blue-600 dark:text-blue-400">$$P_{\text{prov}, t}$$</td>
                  <td class="p-2.5 font-semibold">Volume Penumpang Provinsi</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang / bulan</td>
                  <td class="p-2.5">Total keberangkatan seluruh simpul prasarana dalam batas teritorial provinsi pada bulan $t$.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-blue-600 dark:text-blue-400">$$\text{Share}_{m, \text{prov}}$$</td>
                  <td class="p-2.5 font-semibold">Pangsa Moda Dominan</td>
                  <td class="p-2.5 text-slate-500 font-mono">%</td>
                  <td class="p-2.5">Porsi moda utama di provinsi tersebut (contoh: Jatim dominan KA/Bus, Bali dominan Udara, Kepri dominan Laut).</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 7: Standar Penambahan Armada (Persentil Load Factor) -->
        <div id="rumus-sec-7" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-rose-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                7. Standar Penentuan Penambahan Armada Simpul (Persentil Lonjakan Load Factor TCQSM TRB)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950 text-rose-700 dark:text-rose-300 font-bold">
              Standar TCQSM & TRB
            </span>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Sesuai standar internasional <em>Transit Capacity and Quality of Service Manual (TCQSM, TCRP Report 165)</em> dan <em>Ceder (2015)</em>, kebutuhan armada tambahan dihitung dari rasio lonjakan kepadatan per armada (Load Factor Puncak terhadap Load Factor Biasa) dengan ambang persentil empiris $P_{50}, P_{75}, P_{90}$ dari 1.010 simpul nasional.
          </p>

          <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
            <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Rasio Lonjakan Beban Armada Simpul:</div>
            <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
              $$\\text{Rasio Lonjakan LF} = \\frac{LF_{\\text{puncak}}}{LF_{\\text{biasa}}} = \\frac{P_{\\text{puncak}} / A_{\\text{puncak}}}{P_{\\text{biasa}} / A_{\\text{biasa}}}$$
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Tambahan Unit Armada Perbantuan:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                $$A_{\\text{tambah}} = \\left\\lceil A_{\\text{puncak}} \\times \\left( \\frac{\\%\\text{ Tambah}}{100} \\right) \\right\\rceil$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">C. Total Armada Beroperasi Puncak:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold text-sm">
                $$A_{\\text{total}} = A_{\\text{puncak}} + A_{\\text{tambah}}$$
              </div>
            </div>
          </div>

          <!-- Matriks Persentil Table -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5">Klasifikasi Status</th>
                  <th class="p-2.5">Kriteria Persentil Empiris</th>
                  <th class="p-2.5 text-center">Rekomendasi Tambah</th>
                  <th class="p-2.5">Jumlah Simpul</th>
                  <th class="p-2.5">Contoh Simpul Riil Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-bold text-rose-600 dark:text-rose-400">🔴 Sangat Kritis</td>
                  <td class="p-2.5 font-mono">$$\\text{Rasio} \\ge P_{90} = 3{,}43\\times$$ (Top 10%)</td>
                  <td class="p-2.5 font-mono font-bold text-center text-indigo-600 dark:text-indigo-400">+20%</td>
                  <td class="p-2.5 font-bold">87 Simpul</td>
                  <td class="p-2.5">Bakauheni (4,3x), Gilimanuk (4,2x), Merak (3,8x), Giwangan (3,6x)</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-bold text-orange-600 dark:text-orange-400">🟠 Tinggi / Kritis</td>
                  <td class="p-2.5 font-mono">$$P_{75} \\le \\text{Rasio} < P_{90}$$ ($$2{,}33\\times - 3{,}42\\times$$)</td>
                  <td class="p-2.5 font-mono font-bold text-center text-indigo-600 dark:text-indigo-400">+15%</td>
                  <td class="p-2.5 font-bold">122 Simpul</td>
                  <td class="p-2.5">Pasar Senen (2,8x), Ketapang (2,6x), Poto Tano (2,5x)</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-bold text-amber-600 dark:text-amber-400">🟡 Padat</td>
                  <td class="p-2.5 font-mono">$$P_{50} \\le \\text{Rasio} < P_{75}$$ ($$1{,}54\\times - 2{,}32\\times$$)</td>
                  <td class="p-2.5 font-mono font-bold text-center text-indigo-600 dark:text-indigo-400">+10%</td>
                  <td class="p-2.5 font-bold">211 Simpul</td>
                  <td class="p-2.5">Juanda (1,9x), Gambir (1,8x), DPS Bali (1,6x), Soetta (1,5x)</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">🟢 Terkendali</td>
                  <td class="p-2.5 font-mono">$$\\text{Rasio} < P_{50} = 1{,}54\\times$$ (atau $$P < 100$$)</td>
                  <td class="p-2.5 font-mono font-bold text-center text-indigo-600 dark:text-indigo-400">+5%</td>
                  <td class="p-2.5 font-bold">590 Simpul</td>
                  <td class="p-2.5">Simpul perintis lokal & rute reguler dengan armada memadai</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Sumber Regulasi & Jurnal Ilmiah Rekomendasi Aksi Lapangan -->
          <div class="space-y-3 pt-2">
            
            <!-- Box A: Regulasi Resmi Kemenhub RI -->
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-2">
              <div class="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span>
                <span>🏛 Landasan Regulasi Resmi Kemenhub RI untuk Aksi Lapangan:</span>
              </div>
              <div class="text-[11px] text-slate-600 dark:text-slate-300 space-y-1.5 leading-relaxed">
                <div>• <strong>Pola TBB & Buffer Zone Pelabuhan ASDP:</strong> Didasarkan pada <em>Surat Keputusan Bersama (SKB) Tiga Menteri</em> (Kementerian Perhubungan, Korlantas Polri, dan Kementerian PUPR) tentang Pengaturan Lalu Lintas Jalan serta Penyeberangan Masa Angkutan Lebaran &amp; Nataru, yang menetapkan skema Tiba Bongkar Berangkat (TBB) tanpa muat di Bakauheni/Merak, pengalihan pelabuhan Ciwandan/BBJ, dan delaying system di rest area Tol Tangerang–Merak KM 43/68.</div>
                <div>• <strong>Extra Flight & Slot Runway Bandara:</strong> Berpedoman pada <em>Surat Edaran Direktur Jenderal Perhubungan Udara</em> tentang Pengendalian Pengoperasian Pesawat Udara pada Periode Hari Raya, yang mengatur dispensasi slot terbang tambahan (extra flight / red-eye flight malam) serta jam operasi bandara 24 jam penuh.</div>
                <div>• <strong>Kereta Luar Biasa (KLB) & Stamformasi KA:</strong> Berdasarkan <em>Instruksi Direktur Jenderal Perkeretaapian</em> tentang Penyelenggaraan Posko Angkutan Kereta Api Terpadu, yang mengatur pengoperasian rangkaian KLB Tambahan dan maksimasi formasi rangkaian 10–12 gerbong per perjalanan.</div>
                <div>• <strong>Armada Bus Bantuan & Ramp Check:</strong> Mengacu pada <em>Surat Edaran Direktur Jenderal Perhubungan Darat</em> mengenai Kesiapan Angkutan Jalan, yang mewajibkan inspeksi keselamatan jalan (Ramp Check) dan penyiagaan armada bus pariwisata cadangan sebagai angkutan perbantuan di terminal tipe A.</div>
              </div>
            </div>

            <!-- Box B: Rujukan Jurnal Ilmiah Peer-Reviewed dengan Tautan Langsung -->
            <div class="p-4 rounded-lg bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 text-xs space-y-2.5">
              <div class="font-bold text-indigo-900 dark:text-indigo-200 flex items-center justify-between">
                <span class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
                  <span>📚 Rujukan Jurnal Ilmiah Peer-Reviewed & Manual Standar Rekayasa Transportasi:</span>
                </span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-200/60 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200">Klik tautan untuk membaca</span>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-[11px]">
                
                <!-- Jurnal 1: ASDP -->
                <div class="p-2.5 rounded bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/60 space-y-1">
                  <div class="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>⛴ Penyeberangan ASDP (TBB & Buffer)</span>
                    <a href="https://garuda.kemdiktisaintek.go.id/journal/view/41858" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold text-[10px]">Buka Jurnal ↗</a>
                  </div>
                  <div class="text-slate-600 dark:text-slate-300">
                    <strong>Jurnal Penelitian Transportasi Darat</strong> (Badan Litbang Perhubungan, SINTA 2 / Garuda Kemdiktisaintek).
                  </div>
                  <div class="text-slate-500 text-[10px]">
                    Evaluasi pola operasi dan kapasitas angkutan penyeberangan lintas Merak–Bakauheni pada periode puncak. Kajian internasional pendukung: <a href="https://doi.org/10.1057/s41278-020-00155-2" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-mono">Maritime Economics &amp; Logistics (Springer, 2020)</a> mengenai mitigasi antrean pelabuhan ferry Ro-Ro.
                  </div>
                </div>

                <!-- Jurnal 2: Udara -->
                <div class="p-2.5 rounded bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/60 space-y-1">
                  <div class="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>✈ Penerbangan Udara (Slot & Extra Flight)</span>
                    <a href="https://doi.org/10.1016/j.jairtraman.2025.102751" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold text-[10px]">Buka Jurnal ↗</a>
                  </div>
                  <div class="text-slate-600 dark:text-slate-300">
                    <strong>Journal of Air Transport Management</strong> (Elsevier / ScienceDirect, 2025).
                  </div>
                  <div class="text-slate-500 text-[10px]">
                    <em>A novel slot optimization model for congested airports integrating IATA guidelines</em> (Zeng et al., 2025). Mengkaji manajemen slot bandara padat dan izin extra flight. Rujukan standar: <a href="https://www.iata.org/en/policy/slots/wasg/" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-mono">IATA Worldwide Airport Slot Guidelines (WASG)</a>.
                  </div>
                </div>

                <!-- Jurnal 3: KA -->
                <div class="p-2.5 rounded bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/60 space-y-1">
                  <div class="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>🚆 Kereta Api (KLB & Stamformasi)</span>
                    <a href="https://doi.org/10.1016/j.cie.2025.111166" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold text-[10px]">Buka Jurnal ↗</a>
                  </div>
                  <div class="text-slate-600 dark:text-slate-300">
                    <strong>Computers &amp; Industrial Engineering</strong> (Elsevier / ScienceDirect, 2025).
                  </div>
                  <div class="text-slate-500 text-[10px]">
                    <em>Integrated optimization of line planning and additional trains scheduling during demand surges</em> (2025). Kajian pendukung: <a href="https://doi.org/10.1016/j.jrtpm.2024.100450" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-mono">Journal of Rail Transport Planning &amp; Management (Elsevier)</a> tentang optimasi stamformasi gerbong.
                  </div>
                </div>

                <!-- Jurnal 4: Bus & Teori Armada -->
                <div class="p-2.5 rounded bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/60 space-y-1">
                  <div class="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>🚌 Bus &amp; Optimasi Armada Transit</span>
                    <a href="https://www.nationalacademies.org/publications/24766" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold text-[10px]">Buka Manual TRB ↗</a>
                  </div>
                  <div class="text-slate-600 dark:text-slate-300">
                    <strong>TRB TCQSM (TCRP Report 165)</strong> &amp; <strong>Ceder (CRC Press, 2015)</strong>.
                  </div>
                  <div class="text-slate-500 text-[10px]">
                    <em>Transit Capacity and Quality of Service Manual</em> Part 2 &amp; Part 7 (Terminal Circulation &amp; Reserve Bus Deployment). Landasan optimasi armada puncak: <a href="https://doi.org/10.1016/j.transa.2017.09.006" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline font-mono">Transportation Research Part A (Jara-Díaz et al., 2017)</a>.
                  </div>
                </div>

              </div>
            </div>

          </div>
        </div>

        <!-- Section 8: Model Prediksi Time Series Holt-Winters Nataru -->
        <div id="rumus-sec-8" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-purple-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                8. Rumus 1 Model Holt-Winters Terpadu (Damped Trend & Calendar Shocks)
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-950 text-purple-700 dark:text-purple-300 font-bold">
              Horizon 100 Hari Nataru
            </span>
          </div>

          <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
            <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">Formulasi Model Prediksi Time Series:</div>
            <div class="text-center py-2.5 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
              $$\\hat{y}_{t+h} = \\left( \\ell_t + \\sum_{i=1}^{h} \\phi^i b_t \\right) \\times s_{t+h-m(k+1)} \\times \\prod W_{\\text{shock}}$$
            </div>
            <div class="text-center py-1.5 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 font-mono text-xs">
              $$\\text{CI}_{95\\%} = \\hat{y}_{t+h} \\pm 1{,}96 \\times \\text{RMSE}$$
            </div>
          </div>

          <!-- Metrik Evaluasi Akurasi -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div class="p-3.5 rounded-lg bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60">
              <div class="text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase">MAPE (Akurasi Tinggi)</div>
              <div class="text-xl font-black font-mono text-emerald-700 dark:text-emerald-400 mt-1">4,10%</div>
              <div class="text-[10px] font-mono text-slate-500 mt-0.5">$$\\frac{100\\%}{n} \\sum \\left|\\frac{y-\\hat{y}}{y}\\right|$$</div>
            </div>
            <div class="p-3.5 rounded-lg bg-sky-50/70 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/60">
              <div class="text-[10px] font-bold text-sky-800 dark:text-sky-300 uppercase">WAPE Tertimbang</div>
              <div class="text-xl font-black font-mono text-sky-700 dark:text-sky-400 mt-1">4,02%</div>
              <div class="text-[10px] font-mono text-slate-500 mt-0.5">$$\\frac{\\sum |y-\\hat{y}|}{\\sum y} \\times 100\\%$$</div>
            </div>
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <div class="text-[10px] font-bold text-slate-500 uppercase">RMSE</div>
              <div class="text-xl font-black font-mono text-slate-900 dark:text-white mt-1">62.051</div>
              <div class="text-[10px] font-mono text-slate-500 mt-0.5">$$\\sqrt{\\frac{1}{n} \\sum (y-\\hat{y})^2}$$</div>
            </div>
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <div class="text-[10px] font-bold text-slate-500 uppercase">MAE</div>
              <div class="text-xl font-black font-mono text-slate-900 dark:text-white mt-1">49.146</div>
              <div class="text-[10px] font-mono text-slate-500 mt-0.5">$$\\frac{1}{n} \\sum |y-\\hat{y}|$$</div>
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$\\hat{y}_{t+h}$$</td>
                  <td class="p-2.5 font-semibold">Proyeksi Penumpang</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang / hari</td>
                  <td class="p-2.5">Nilai perkiraan volume mobilitas multimoda pada horizon $h$ hari ke depan (30 Sep '26 s.d. 7 Jan '27).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$\\ell_t$$</td>
                  <td class="p-2.5 font-semibold">Tingkat Level Dasar</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang</td>
                  <td class="p-2.5">Estimasi tingkat pergerakan dasar pada waktu cutoff terkini setelah memperhitungkan data latih 635 hari.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$b_t$$</td>
                  <td class="p-2.5 font-semibold">Komponen Tren</td>
                  <td class="p-2.5 text-slate-500 font-mono">orang / hari</td>
                  <td class="p-2.5">Kemiringan laju pertumbuhan riil (+5,13% YoY dari tahun 2025 ke 2026).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$\\phi$$</td>
                  <td class="p-2.5 font-semibold">Peredam Tren (Damping)</td>
                  <td class="p-2.5 text-slate-500 font-mono">konstanta (0,98)</td>
                  <td class="p-2.5">Parameter peredam agar model tidak over-ekstrapolasi tanpa batas pada proyeksi horizon 100 hari.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">$$s_{t}$$</td>
                  <td class="p-2.5 font-semibold">Faktor Musiman Mingguan</td>
                  <td class="p-2.5 text-slate-500 font-mono">multiplikatif</td>
                  <td class="p-2.5">Pola ritme 7 hari yang secara konsisten menangkap puncak akhir pekan (Jumat-Minggu vs Selasa).</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-purple-600 dark:text-purple-400">$$W_{\\text{shock}}$$</td>
                  <td class="p-2.5 font-semibold">Shock Kalender Libur</td>
                  <td class="p-2.5 text-slate-500 font-mono">elastisitas</td>
                  <td class="p-2.5">Faktor pengali lonjakan cuti bersama Nataru yang dikalibrasi dari realisasi shock Nataru 2025.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-slate-600 dark:text-slate-400">$$\\text{CI}_{95\\%}$$</td>
                  <td class="p-2.5 font-semibold">Interval Keyakinan 95%</td>
                  <td class="p-2.5 text-slate-500 font-mono">rentang penumpang</td>
                  <td class="p-2.5">Batas atas dan batas bawah probabilitas 95% untuk penyusunan skenario terburuk (*worst-case scenario*).</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 9: Formula Matematis Simulasi Tambahan Armada -->
        <div id="rumus-sec-9" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                9. Formula Matematis Simulasi Intervensi Tambahan Armada Simpul
              </h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold">
              Kapasitas Terbuka
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">A. Tambahan Unit Armada:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold text-xs">
                $$A_{\\text{tambah}} = A_{\\text{biasa}} \\times \\left( \\frac{\\%\\text{ Tambah}}{100} \\right)$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">B. Kapasitas Terbuka:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold text-xs">
                $$C_{\\text{terbuka}} = P_{\\text{biasa}} \\times \\left( \\frac{\\%\\text{ Tambah}}{100} \\right)$$
              </div>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300">C. Rasio Kepadatan Baru:</div>
              <div class="text-center py-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold text-xs">
                $$\\text{Beban Baru} = \\frac{\\text{Beban Awal}}{1 + \\left( \\frac{\\%\\text{ Tambah}}{100} \\right)}$$
              </div>
            </div>
          </div>

          <!-- Table of Notation -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-xs font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300">
                <tr>
                  <th class="p-2.5 w-28">Simbol</th>
                  <th class="p-2.5 w-44">Nama Notasi</th>
                  <th class="p-2.5 w-32">Satuan</th>
                  <th class="p-2.5">Penjelasan Makna Operasional Lapangan</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">
                <tr>
                  <td class="p-2.5 font-mono font-bold text-emerald-600 dark:text-emerald-400">$$A_{\\text{tambah}}$$</td>
                  <td class="p-2.5 font-semibold">Tambahan Trip Armada</td>
                  <td class="p-2.5 text-slate-500 font-mono">trip / flight / KA</td>
                  <td class="p-2.5">Berapa unit pergerakan armada cadangan yang disuntikkan ke simpul per hari.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-emerald-600 dark:text-emerald-400">$$C_{\\text{terbuka}}$$</td>
                  <td class="p-2.5 font-semibold">Kapasitas Muat Terbuka</td>
                  <td class="p-2.5 text-slate-500 font-mono">kursi / penumpang</td>
                  <td class="p-2.5">Berapa banyak kuota tempat duduk atau ruang muat tambahan yang berhasil diciptakan.</td>
                </tr>
                <tr>
                  <td class="p-2.5 font-mono font-bold text-emerald-600 dark:text-emerald-400">$$\\text{Beban Baru}$$</td>
                  <td class="p-2.5 font-semibold">Tingkat Okupansi Baru</td>
                  <td class="p-2.5 text-slate-500 font-mono">rasio relatif</td>
                  <td class="p-2.5">Penurunan rasio kepadatan setelah intervensi penambahan armada diberlakukan.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
"""

KATEX_SCRIPT_TRIGGER = """
// ---------------------------------------------------------------
// KATEX FORMULA RENDERING TRIGGER
// ---------------------------------------------------------------
function renderKaTeXFormulas() {
  const target = document.getElementById('tab-tentang-data');
  if (target && window.renderMathInElement) {
    window.renderMathInElement(target, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false }
      ],
      throwOnError: false
    });
  }
}
"""

def apply_transformation():
    for fpath in FILES:
        print(f"Memproses {fpath}...")
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Masukkan KaTeX CSS/JS di <head> jika belum ada
        if 'katex.min.css' not in content:
            content = content.replace('</head>', f'{KATEX_HEAD}\n</head>')

        # 2. Hapus drawer lama: backdrop & aside
        content = re.sub(
            r'<!-- =+\s*-->\s*<!-- SIDEBAR INFORMASI & KAMUS RUMUS DASHBOARD \(DRAWER\)\s*-->\s*<div id="backdrop-penjelasan".*?</aside>',
            '',
            content,
            flags=re.DOTALL
        )

        # 3. Ganti tombol lama di sidebar navigasi dengan tombol Tab 9
        content = re.sub(
            r'<!-- BUTTON BUKA SIDEBAR METODOLOGI KEPADATAN -->\s*<button onclick="toggleExplanationSidebar\(true\)".*?</button>',
            TAB_BUTTON,
            content,
            flags=re.DOTALL
        )

        # 4. Ganti tombol di header & floating action button agar membuka Tab 9
        content = re.sub(
            r'<button onclick="toggleExplanationSidebar\(true\)" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-indigo-300.*?</span>\s*</button>',
            '<button onclick="switchTab(\'tab-tentang-data\', \'Informasi & Kamus Rumus Dashboard\', document.getElementById(\'nav-btn-tentang-data\'))" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all" title="Buka Informasi & Kamus Rumus Dashboard"><svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg><span class="hidden sm:inline">Tentang Data</span><span class="sm:hidden">Info</span></button>',
            content
        )

        # Floating Action Button
        content = re.sub(
            r'<button onclick="toggleExplanationSidebar\(true\)" class="fixed bottom-6 right-6.*?</span>\s*</button>',
            '<button onclick="switchTab(\'tab-tentang-data\', \'Informasi & Kamus Rumus Dashboard\', document.getElementById(\'nav-btn-tentang-data\'))" class="fixed bottom-6 right-6 z-40 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2.5 px-3.5 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2 border border-indigo-400 group" title="Buka Informasi & Kamus Rumus Dashboard"><svg class="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg><span class="hidden sm:inline">📘 Tentang Data & Rumus</span><span class="sm:hidden">📘 Rumus</span></button>',
            content
        )

        # Tab 8 tombol Metodologi Data
        content = re.sub(
            r'<button onclick="toggleExplanationSidebar\(true\)" class="px-2.5 py-1.5 rounded-md border border-indigo-300.*?<span>📘 Metodologi Data</span>\s*</button>',
            '<button onclick="switchTab(\'tab-tentang-data\', \'Informasi & Kamus Rumus Dashboard\', document.getElementById(\'nav-btn-tentang-data\'))" class="px-2.5 py-1.5 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold shadow-xs transition-all flex items-center gap-1.5" title="Buka Informasi & Kamus Rumus Dashboard"><svg class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg><span>📘 Metodologi Data</span></button>',
            content
        )

        # 5. Pasang TAB_CONTENT di dalam <main> tepat sebelum </main>
        if 'id="tab-tentang-data"' not in content:
            content = content.replace('    </main>', f'{TAB_CONTENT}\n    </main>')

        # 6. Update switchTab JavaScript agar memicu renderKaTeXFormulas()
        if 'renderKaTeXFormulas()' not in content:
            content = content.replace(
                "if (targetId === 'tab-forecasting') {",
                "if (targetId === 'tab-tentang-data') { renderKaTeXFormulas(); }\n    if (targetId === 'tab-forecasting') {"
            )

        # 7. Tambahkan fungsi renderKaTeXFormulas dan update toggleExplanationSidebar
        if 'function renderKaTeXFormulas' not in content:
            content = content.replace('function toggleExplanationSidebar(open) {', f'{KATEX_SCRIPT_TRIGGER}\nfunction toggleExplanationSidebar(open) {{')

        # Update toggleExplanationSidebar body agar redirect ke tab-tentang-data
        content = re.sub(
            r'function toggleExplanationSidebar\(open\)\s*\{.*?\}',
            'function toggleExplanationSidebar(open) {\n  if (open) {\n    const navBtn = document.getElementById(\'nav-btn-tentang-data\');\n    switchTab(\'tab-tentang-data\', \'Informasi & Kamus Rumus Dashboard\', navBtn);\n  }\n}',
            content,
            flags=re.DOTALL
        )

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Selesai memperbarui {fpath}")

if __name__ == '__main__':
    apply_transformation()
