import json
import re

BUNDLE_PATH = r"c:\Users\USER\Documents\PUSDATIN\scripts\mobility_data_bundle.json"
FILES_TO_UPDATE = [
    r"c:\Users\USER\Documents\PUSDATIN\Dashboard_Mobilitas_Nasional_2026.html",
    r"c:\Users\USER\Documents\PUSDATIN\index.html"
]

NEW_BOX_7 = """      <!-- Box 7: Penentuan Kebutuhan Tambahan Armada Simpul Berbasis Persentil Lonjakan Load Factor -->
      <div class="space-y-3.5">
        <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
          <h4 class="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            7. Standar Penentuan Penambahan Armada Simpul (Persentil Lonjakan Load Factor)
          </h4>
          <p class="text-[11px] text-slate-500 mt-0.5">Penentuan persentase tambahan armada dihitung murni berbasis rasio lonjakan kepadatan per armada (Load Factor) dengan ambang persentil empiris nasional (TCQSM & TRB Standard):</p>
        </div>

        <!-- Tolok Ukur A -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>A. Mengapa Menggunakan Lonjakan Load Factor (LF Puncak / LF Biasa)?</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">TCQSM Standard</span>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-300">
            Kemacetan dan antrean tidak semata-mata diukur dari jumlah penumpang, melainkan dari <strong>rasio kepadatan penumpang per unit armada yang beroperasi (LF = Penumpang / Armada)</strong>. Ketika LF puncak melonjak jauh di atas LF biasa, kapasitas sarana gagal menyerap arus sehingga terjadi antrean dan penumpukan kendaraan.
          </p>
        </div>

        <!-- Tolok Ukur B -->
        <div class="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 space-y-2.5">
          <div class="font-bold text-slate-900 dark:text-white text-xs flex items-center justify-between">
            <span>B. Ambang Batas Persentil Empiris Lonjakan Beban (1.010 Simpul Nasional)</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300">P50 • P75 • P90</span>
          </div>
          <div class="overflow-x-auto rounded border border-slate-200 dark:border-slate-700">
            <table class="w-full text-left text-[11px] font-sans">
              <thead class="bg-slate-100 dark:bg-slate-800 font-bold text-slate-600 dark:text-slate-400">
                <tr>
                  <th class="p-1.5">Klasifikasi Beban</th>
                  <th class="p-1.5">Kriteria Persentil Empiris</th>
                  <th class="p-1.5">Rekomendasi Tambahan (%)</th>
                  <th class="p-1.5">Cakupan Simpul Nasional</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
                <tr>
                  <td class="p-1.5 font-bold text-rose-600 dark:text-rose-400">🔴 Sangat Kritis</td>
                  <td class="p-1.5 font-mono">Top 10% Terparah (&ge; P90 = 3,43x lipat)</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+20%</td>
                  <td class="p-1.5">87 Simpul (Bakauheni 4,3x, Gilimanuk 4,2x, Merak 3,8x, Giwangan 3,6x)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-orange-600 dark:text-orange-400">🟠 Tinggi / Kritis</td>
                  <td class="p-1.5 font-mono">P75 s.d. P90 (2,33x &ndash; 3,42x lipat)</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+15%</td>
                  <td class="p-1.5">122 Simpul (Pasar Senen 2,8x, Ketapang 2,6x, Poto Tano 2,5x)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-amber-600 dark:text-amber-400">🟡 Padat</td>
                  <td class="p-1.5 font-mono">P50 s.d. P75 (1,54x &ndash; 2,32x lipat)</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+10%</td>
                  <td class="p-1.5">211 Simpul (Juanda 1,9x, Gambir 1,8x, DPS Bali 1,6x, Soetta 1,5x)</td>
                </tr>
                <tr>
                  <td class="p-1.5 font-bold text-emerald-600 dark:text-emerald-400">🟢 Terkendali</td>
                  <td class="p-1.5 font-mono">&lt; P50 (&lt; 1,54x lipat / armada mencukupi)</td>
                  <td class="p-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">+5%</td>
                  <td class="p-1.5">590 Simpul (Simpul perintis & rute reguler stabil)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tolok Ukur C: Rujukan Akademis -->
        <div class="bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 rounded-lg p-3 space-y-1.5">
          <div class="font-bold text-indigo-900 dark:text-indigo-200 text-xs flex items-center gap-1.5">
            <span>📚 Landasan Akademis & Standar Rekayasa Transportasi:</span>
          </div>
          <div class="text-[10px] text-slate-600 dark:text-slate-300 space-y-1">
            <div>• <strong>TRB TCQSM (TCRP Report 165):</strong> Kualitas layanan simpul ditentukan oleh rasio Passenger Load Factor terhadap kapasitas sarana.</div>
            <div>• <strong>Ceder, A. (2015):</strong> <em>Public Transit Planning and Operation</em>. Penambahan frekuensi/armada jam puncak diformulasikan dari rasio defisit load factor.</div>
            <div>• <strong>Jara-Díaz et al. (2017):</strong> <em>Transportation Research Part A</em>. Ukuran armada optimal dialokasikan proporsional terhadap rasio periode puncak vs normal.</div>
          </div>
        </div>
      </div>"""

def update_dashboards():
    with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
        bundle_data = json.load(f)
    
    bundle_str = json.dumps(bundle_data, ensure_ascii=False)

    for filepath in FILES_TO_UPDATE:
        print(f"Memproses {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Update DATA = ...
        content = re.sub(r'const DATA = \{.*?\};', f'const DATA = {bundle_str};', content, count=1)

        # 2. Update Box 7
        box7_pattern = r'<!-- Box 7: Penentuan Kebutuhan Tambahan Armada Simpul.*?<!-- Box 8:'
        replacement_box7 = NEW_BOX_7 + '\n\n      <!-- Box 8:'
        content = re.sub(box7_pattern, replacement_box7, content, flags=re.DOTALL)

        # 3. Update deskripsi tabel Tab 8
        content = content.replace(
            'Dihitung murni berdasarkan data keberangkatan empiris SIASATI (penumpang berangkat / armada berangkat). Dilengkapi filter jumlah baris (Top 10, Top 25, Top 50, Top 100, hingga Semua Simpul), filter moda, status urgensi, dan pencarian cepat.',
            'Dihitung berbasis metodologi persentil lonjakan Load Factor (LF Puncak / LF Biasa) standar TCQSM TRB. Dilengkapi filter jumlah baris (Top 10 s.d. Semua Simpul), filter moda, status urgensi, dan pencarian cepat.'
        )

        # 4. Update opsi status Padat Tinggi -> Padat
        content = content.replace(
            '<option value="10">🟡 Padat Tinggi (+10%)</option>',
            '<option value="10">🟡 Padat (+10%)</option>'
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Selesai memperbarui {filepath}")

if __name__ == '__main__':
    update_dashboards()
