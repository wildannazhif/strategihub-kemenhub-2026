import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

assets_dir = r"c:\Users\USER\Documents\PUSDATIN\laporan_anomali_assets"
os.makedirs(assets_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'

# -------------------------------------------------------------
# 1. SS ANOMALI KA: FIELD MAPPING ERROR
# -------------------------------------------------------------
print("Membuat visual 1: Anomali KA Field Mapping...")
fig = plt.figure(figsize=(12, 6.5), dpi=200)

# Kiri: Tabel dengan Highlight Merah
ax1 = fig.add_subplot(1, 2, 1)
ax1.axis('off')

table_data = [
    ["Tanggal", "Stasiun", "KA Datang", "Pnp Datang", "KA Brgkt", "Pnp Brgkt"],
    ["2026-01-01", "ARJAWINANGUN", "5", "119", "5", "5 (KEMBAR!)"],
    ["2026-01-02", "ARJAWINANGUN", "8", "137", "8", "8 (KEMBAR!)"],
    ["2026-01-03", "ARJAWINANGUN", "9", "160", "8", "8 (KEMBAR!)"],
    ["2026-01-04", "ARJAWINANGUN", "7", "185", "9", "9 (KEMBAR!)"],
    ["2026-01-05", "ARJAWINANGUN", "7", "142", "7", "7 (KEMBAR!)"]
]

tbl = ax1.table(cellText=table_data, loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1.15, 2.0)

# Format header & highlight
for (r, c), cell in tbl.get_celld().items():
    if r == 0:
        cell.set_facecolor('#1e3a8a')
        cell.set_text_props(color='white', weight='bold')
    else:
        if c in [4, 5]:
            cell.set_facecolor('#fee2e2') # Red highlight
            cell.set_text_props(color='#b91c1c', weight='bold')
        elif c == 3:
            cell.set_facecolor('#e0f2fe') # Normal passenger highlight
            cell.set_text_props(color='#0369a1')
        else:
            cell.set_facecolor('#f8fafc' if r % 2 == 0 else 'white')

ax1.set_title("Bukti Data Mentah: Stasiun Arjawinangun (AWN)\nKolom Penumpang Berangkat = Kereta Berangkat", fontsize=11, weight='bold', pad=18)

# Kanan: Grafik Kerusakan Nilai Agregat
ax2 = fig.add_subplot(1, 2, 2)
bars = ax2.bar(['Penumpang Datang\n(Relatif Riil)', 'Penumpang Berangkat\n(Rusak / Jumlah Trip KA)'], [41.17, 0.86], color=['#0284c7', '#ef4444'], width=0.55)
ax2.set_ylabel("Juta Penumpang Kumulatif", fontsize=10.5)
ax2.set_title("Dampak Agregat Nasional Penumpang KA 2026\nJurang Anomali Sebesar 40,31 Juta Orang", fontsize=11, weight='bold', pad=18)
for bar in bars:
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, y + 1.0, f"{y:.2f} Juta\n({'-98%' if y < 1 else 'Normal'})", ha='center', va='bottom', fontsize=10, weight='bold', color='#1e293b')
ax2.set_ylim(0, 48)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "01_anomali_ka_mapping.png"))
plt.close()

# -------------------------------------------------------------
# 2. SS ANOMALI ASDP: SIMETRI 100%
# -------------------------------------------------------------
print("Membuat visual 2: Anomali ASDP Simetri...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)

ax1.axis('off')
asdp_table = [
    ["Tanggal", "Pelabuhan", "Kapal Datang", "Kapal Brgkt", "Pnp Datang", "Pnp Brgkt"],
    ["2026-01-01", "Tanjung Uban", "13", "13 (1:1)", "3.267", "3.267 (1:1)"],
    ["2026-01-02", "Tanjung Uban", "15", "15 (1:1)", "3.620", "3.620 (1:1)"],
    ["2026-01-01", "Bakauheni", "84", "84 (1:1)", "52.140", "52.140 (1:1)"],
    ["2026-01-01", "Merak", "84", "84 (1:1)", "52.140", "52.140 (1:1)"],
    ["2026-01-02", "Ketapang", "62", "62 (1:1)", "28.450", "28.450 (1:1)"]
]
tbl = ax1.table(cellText=asdp_table, loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1.15, 2.0)
for (r, c), cell in tbl.get_celld().items():
    if r == 0:
        cell.set_facecolor('#047857')
        cell.set_text_props(color='white', weight='bold')
    else:
        if c in [2, 3]:
            cell.set_facecolor('#ecfdf5')
            cell.set_text_props(color='#065f46')
        elif c in [4, 5]:
            cell.set_facecolor('#d1fae5')
            cell.set_text_props(color='#047857', weight='bold')
        else:
            cell.set_facecolor('white')
ax1.set_title("Bukti Data Mentah ASDP: Tanjung Uban, Merak, Bakauheni\nSimetri Sempurna 100% di 19.736 Baris", fontsize=11, weight='bold', pad=18)

# Pie 50-50
ax2.pie([43.55, 43.55], labels=['Penumpang Datang\n43,55 Juta (50%)', 'Penumpang Berangkat\n43,55 Juta (50%)'], autopct='%1.1f%%', colors=['#10b981', '#059669'], startangle=90, wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 2}, textprops={'fontsize': 10, 'weight': 'bold'})
ax2.set_title("Kloning Nilai Datang vs Berangkat ASDP\nManifest Round-Trip per Lintasan Dermaga", fontsize=11, weight='bold', pad=18)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "02_anomali_asdp_simetri.png"))
plt.close()

# -------------------------------------------------------------
# 3. SS ANOMALI DUPLIKASI: DUMMY 0 VS KEDUANYA BERNILAI
# -------------------------------------------------------------
print("Membuat visual 3: Anomali Duplikasi...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), dpi=200)

ax1.axis('off')
dup_ka_table = [
    ["Tanggal", "ID", "Nama Stasiun", "KA Datang", "Pnp Datang", "KA Brgkt", "Pnp Brgkt", "Kategori Kasus"],
    ["2026-01-01", "ARB", "ARASKABU", "6", "48", "9", "9", "Baris Riil (Aktif)"],
    ["2026-01-01", "ARB", "ARASKABU", "0", "0", "0", "0", "Dummy Nol (Kosong)"],
    ["2026-09-24", "ARB", "ARASKABU", "6", "11", "4", "4", "Ada Nilainya! (KA Lokal)"],
    ["2026-09-24", "ARB", "ARASKABU", "2", "44", "2", "2", "Ada Nilainya! (KA Bandara)"]
]
tbl1 = ax1.table(cellText=dup_ka_table, loc='center', cellLoc='center')
tbl1.auto_set_font_size(False)
tbl1.set_fontsize(9)
tbl1.scale(1.1, 1.8)
for (r, c), cell in tbl1.get_celld().items():
    if r == 0:
        cell.set_facecolor('#6b21a8')
        cell.set_text_props(color='white', weight='bold')
    else:
        if r == 2:
            cell.set_facecolor('#fee2e2') # dummy 0
            cell.set_text_props(color='#991b1b')
        elif r in [3, 4]:
            cell.set_facecolor('#fef3c7') # both have values
            cell.set_text_props(color='#92400e', weight='bold')
        else:
            cell.set_facecolor('white')
ax1.set_title("Kasus Duplikasi Stasiun KA: Pola Dummy Nol vs Pola Dua Layanan Bernilai", fontsize=10.5, weight='bold', pad=12)

ax2.axis('off')
dup_laut_table = [
    ["Tanggal", "ID", "Nama Pelabuhan", "Kapal Datang", "Pnp Datang", "Kapal Brgkt", "Pnp Brgkt", "Kategori Kasus"],
    ["2026-01-01", "1", "Belawan", "2", "2.692", "1", "1.439", "Baris Riil (Aktif)"],
    ["2026-01-01", "1", "Belawan", "0", "0", "0", "0", "Dummy Nol (Kosong)"],
    ["2026-01-01", "7", "Selat Panjang", "29", "803", "28", "820", "Ada Nilainya! (Rute Domestik)"],
    ["2026-01-01", "7", "Selat Panjang", "5", "42", "4", "62", "Ada Nilainya! (Rute Internasional)"]
]
tbl2 = ax2.table(cellText=dup_laut_table, loc='center', cellLoc='center')
tbl2.auto_set_font_size(False)
tbl2.set_fontsize(9)
tbl2.scale(1.1, 1.8)
for (r, c), cell in tbl2.get_celld().items():
    if r == 0:
        cell.set_facecolor('#0e7490')
        cell.set_text_props(color='white', weight='bold')
    else:
        if r == 2:
            cell.set_facecolor('#fee2e2') # dummy 0
            cell.set_text_props(color='#991b1b')
        elif r in [3, 4]:
            cell.set_facecolor('#dcfce7') # both have values
            cell.set_text_props(color='#166534', weight='bold')
        else:
            cell.set_facecolor('white')
ax2.set_title("Kasus Duplikasi Pelabuhan Laut: Pola Dummy Nol vs Pola Pelayaran Berbeda", fontsize=10.5, weight='bold', pad=12)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "03_anomali_duplikasi_ka_laut.png"))
plt.close()

# -------------------------------------------------------------
# 4. SS ANOMALI SPASIAL: PETA NULL ISLAND & KUTUB UTARA
# -------------------------------------------------------------
print("Membuat visual 4: Anomali Spasial Peta...")
fig, ax = plt.subplots(figsize=(13, 6.5), dpi=200)

# Gambar skema peta dunia sederhana
ax.set_facecolor('#0f172a')
# Batas dunia
ax.set_xlim(-30, 160)
ax.set_ylim(-25, 85)

# Bounding box Indonesia normal
rect_indo = patches.Rectangle((95, -11), 46, 17, linewidth=2, edgecolor='#22c55e', facecolor='#166534', alpha=0.3)
ax.add_patch(rect_indo)
ax.text(118, -2, "WILAYAH INDONESIA NORMAL\n(Lat: -11 s/d +6, Lon: 95 s/d 141)\n1.275 Simpul Prasarana Terpetakan", color='#86efac', fontsize=10, weight='bold', ha='center', bbox=dict(boxstyle="round,pad=0.3", fc="#064e3b", ec="#22c55e"))

# Null Island (0,0) di Afrika
ax.plot(0, 0, marker='o', markersize=14, color='#ef4444', markeredgecolor='white', markeredgewidth=2)
ax.annotate("ANOMALI: NULL ISLAND (0,0)\nSamudera Atlantik / Lepas Pantai Afrika\n23 Simpul (18 Terminal Bus termasuk Cileungsi,\nSukoharjo, Purwantoro, Padang, dll.)",
            xy=(0, 0), xytext=(10, -18),
            arrowprops=dict(facecolor='#ef4444', shrink=0.08, width=2, headwidth=8),
            fontsize=9.5, weight='bold', color='#fca5a5',
            bbox=dict(boxstyle="round,pad=0.4", fc="#7f1d1d", ec="#ef4444"))

# Kutub Utara / Siberia (Lat 128, Lon -3) -> clamped on map
ax.plot(-3.6, 75, marker='^', markersize=14, color='#f59e0b', markeredgecolor='white', markeredgewidth=2)
ax.annotate("ANOMALI: LAT/LON TERTUKAR TERBALIK\nTerlempar ke Wilayah Lingkar Kutub Utara\nPelabuhan ASDP Poka & Haruku (Maluku)\nInput mentah: Lat = 128.199, Lon = -3.656",
            xy=(-3.6, 75), xytext=(20, 70),
            arrowprops=dict(facecolor='#f59e0b', shrink=0.08, width=2, headwidth=8),
            fontsize=9.5, weight='bold', color='#fde68a',
            bbox=dict(boxstyle="round,pad=0.4", fc="#78350f", ec="#f59e0b"))

ax.set_title("Visualisasi Anomali Spasial Koordinat Mentah SIASATI 2026", fontsize=13, weight='bold', color='white', pad=15)
ax.set_xlabel("Garis Bujur (Longitude)", fontsize=10, color='#94a3b8')
ax.set_ylabel("Garis Lintang (Latitude)", fontsize=10, color='#94a3b8')
ax.tick_params(colors='#94a3b8')
ax.grid(color='#334155', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "04_anomali_peta_spasial.png"))
plt.close()

# -------------------------------------------------------------
# 5. SS ANOMALI BUS: TIPE "0"
# -------------------------------------------------------------
print("Membuat visual 5: Anomali Bus Tipe 0...")
fig, ax = plt.subplots(figsize=(12, 5.5), dpi=200)
ax.axis('off')

tipe0_table = [
    ["ID", "Nama Terminal", "Provinsi", "Tipe Mentah", "Hari Lapor", "Status Regulasi (UU 22/2009)", "Fakta Operasional Lapangan"],
    ["B1787", "BSD", "Banten", "0", "6 hari", "Bukan Terminal Resmi Pemda", "Terminal Intermoda Kawasan Swasta (Sinarmas Land)"],
    ["B1460", "Depok", "Jawa Barat", "0", "1 hari", "Non-Definitif", "Titik Pantau Posko Arus Balik (29 April 2026)"],
    ["B280", "Pinrang", "Sulawesi Selatan", "0", "1 hari", "Non-Definitif", "Titik Pantau Posko Mudik Lebaran (19 April 2026)"],
    ["B348", "Wonosobo", "Jawa Tengah", "0", "1 hari", "Non-Definitif", "Sub-terminal / Pangkalan transit lokal"],
    ["B1496", "Wonosari", "D.I. Yogyakarta", "0", "1 hari", "Non-Definitif", "Pangkalan transit pembantu"],
    ["B1618", "Kasipute", "Sulawesi Tenggara", "0", "1 hari", "Non-Definitif", "Pos pemantauan perintis"]
]

tbl = ax.table(cellText=tipe0_table, loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1.15, 2.0)
for (r, c), cell in tbl.get_celld().items():
    if r == 0:
        cell.set_facecolor('#b45309')
        cell.set_text_props(color='white', weight='bold')
    else:
        if c == 3:
            cell.set_facecolor('#fee2e2')
            cell.set_text_props(color='#b91c1c', weight='bold')
        elif c == 5:
            cell.set_facecolor('#fef3c7')
            cell.set_text_props(color='#92400e')
        else:
            cell.set_facecolor('#f8fafc' if r % 2 == 0 else 'white')

ax.set_title("Daftar 6 Terminal Bus dengan Kategori Anomali Tipe '0'\n(Secara Regulasi Kemenhub Hanya Ada Tipe A, B, dan C)", fontsize=11, weight='bold', pad=18)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "05_anomali_bus_tipe0.png"))
plt.close()

# -------------------------------------------------------------
# 6. SS ANOMALI OPERASIONAL: RASIO EKSTREM & ARMADA KOSONG
# -------------------------------------------------------------
print("Membuat visual 6: Anomali Rasio & Armada Kosong...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)

# Tabel kiri: Rasio Ekstrem ASDP
ax1.axis('off')
ratio_table = [
    ["Tanggal", "Pelabuhan", "Kapal", "Penumpang", "Rasio Org/Kapal", "Keterangan"],
    ["2026-01-04", "Nusa Penida", "2", "9.018", "4.509 org/kapal", "Mustahil untuk 1 kapal ferry"],
    ["2026-01-01", "Stagen", "2", "6.058", "3.029 org/kapal", "Mustahil untuk 1 kapal ferry"],
    ["2026-01-02", "Stagen", "2", "3.440", "1.720 org/kapal", "Akumulasi armada tak tercatat"]
]
tbl_r = ax1.table(cellText=ratio_table, loc='center', cellLoc='center')
tbl_r.auto_set_font_size(False)
tbl_r.set_fontsize(9)
tbl_r.scale(1.15, 2.0)
for (r, c), cell in tbl_r.get_celld().items():
    if r == 0:
        cell.set_facecolor('#c2410c')
        cell.set_text_props(color='white', weight='bold')
    else:
        if c == 4:
            cell.set_facecolor('#fee2e2')
            cell.set_text_props(color='#b91c1c', weight='bold')
        else:
            cell.set_facecolor('white')
ax1.set_title("Bukti Rasio Penumpang per Kapal Ekstrem di ASDP\n(Ratusan Speedboat Tak Tercatat Armadanya)", fontsize=10.5, weight='bold', pad=15)

# Bar kanan: Armada Ada tapi 0 Penumpang (Kargo)
counts = [2606, 1253, 438, 178, 81]
modes = ['Laut\n(Kapal Barang)', 'Udara\n(Pesawat Kargo)', 'KA\n(Kereta Barang)', 'ASDP\n(Ferry Logistik)', 'Bus\n(Bus Kosong)']
bars = ax2.bar(modes, counts, color=['#0f766e', '#0284c7', '#8b5cf6', '#10b981', '#f59e0b'], width=0.6)
ax2.set_ylabel("Jumlah Hari Lapor (Baris Data)", fontsize=10)
ax2.set_title("Frekuensi Hari Operasional Armada Aktif tapi 0 Penumpang\n(Tercampurnya Angkutan Barang/Kargo ke Tabel Penumpang)", fontsize=10.5, weight='bold', pad=15)
for bar in bars:
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, y + 50, f"{y:,}", ha='center', va='bottom', fontsize=9.5, weight='bold', color='#1e293b')
ax2.set_ylim(0, 3100)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(assets_dir, "06_anomali_rasio_kargo.png"))
plt.close()

print("\n[SELESAI] Seluruh 6 visual bukti anomali berhasil dibuat!")
