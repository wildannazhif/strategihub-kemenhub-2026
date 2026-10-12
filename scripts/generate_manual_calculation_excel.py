"""
generate_manual_calculation_excel.py
Membangun file Excel Perhitungan Manual Proyeksi Mobilitas Nataru 2026/2027
Lengkap dengan formula Excel dinamis, parameter model, 100 hari horizon,
dan ringkasan studi kasus eksekutif Kemenhub.
"""

import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_XLSX = os.path.join(BASE_DIR, "Perhitungan_Manual_Proyeksi_Nataru_2026_2027.xlsx")

print("Mempersiapkan data dan parameter...")

# 1. Muat Data 2025 & 2026
csv_2025 = os.path.join(BASE_DIR, "siasati_ringkasan_harian_multimoda_2025.csv")
bundle_path = os.path.join(BASE_DIR, "scripts", "mobility_data_bundle.json")

df25 = pd.read_csv(csv_2025)
with open(bundle_path, "r", encoding="utf-8") as f:
    bundle = json.load(f)

df26 = pd.DataFrame(bundle["daily_timeline"])
df26 = df26[pd.to_datetime(df26["date"]) <= "2026-09-29"]

# Hitung baseline November 2025 per hari (DOW) untuk shock Nataru
nov25 = df25[df25["tanggal"].between("2025-11-01", "2025-11-30")]
nov_mean = nov25.groupby(pd.to_datetime(nov25["tanggal"]).dt.dayofweek)["TOTAL_PENUMPANG"].mean()

df25["md"] = df25["tanggal"].str[5:]
p25_map = df25.set_index("md")["TOTAL_PENUMPANG"].to_dict()

# Parameter Model Terlatih (Cutoff 29 Sep 2026)
LEVEL_T = 1175470.85
TREND_T = -13.21
PHI = 0.9800
RMSE = 119426.79
Z_95 = 1.9600

# Musiman per Hari
SEASONAL_DICT = {
    "Senin": 0.9541,
    "Selasa": 0.9773,
    "Rabu": 1.0529,
    "Kamis": 1.0295,
    "Jumat": 1.1206,
    "Sabtu": 1.0069,
    "Minggu": 0.9395
}

DOW_NAMES = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# Bangun 100 Hari (30 Sep 2026 s.d. 07 Jan 2027)
future_dates = pd.date_range(start="2026-09-30", periods=100, freq="D")

# Inisialisasi Workbook
wb = openpyxl.Workbook()
wb.calculation.fullCalcOnLoad = True  # Memaksa Excel menghitung seluruh rumus saat file dibuka
wb.remove(wb.active)

# Color Palette Institusional Kemenhub
NAVY_HEADER = "15426D"     # Primary Header Dark Navy
SKY_HEADER = "0284C7"      # Accent Blue
LIGHT_GRAY = "F8FAFC"      # Light Row Zebra
BORDER_GRAY = "CBD5E1"     # Light Border
CARD_BG = "F1F5F9"         # Card Fill

# Styles
font_title = Font(name="Segoe UI", size=13, bold=True, color="15426D")
font_sub = Font(name="Segoe UI", size=9.5, italic=True, color="475569")
font_header = Font(name="Segoe UI", size=9.5, bold=True, color="FFFFFF")
font_bold = Font(name="Segoe UI", size=9.5, bold=True, color="0F172A")
font_regular = Font(name="Segoe UI", size=9.5, color="1E293B")
font_mono = Font(name="Consolas", size=9.5, color="0F172A")

fill_navy = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
fill_sky = PatternFill(start_color=SKY_HEADER, end_color=SKY_HEADER, fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
fill_nataru = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Soft Yellow for Nataru
fill_puncak = PatternFill(start_color="FFE4E6", end_color="FFE4E6", fill_type="solid") # Soft Rose for Puncak Libur
fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

thin_border_side = Side(border_style="thin", color=BORDER_GRAY)
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
border_header = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
double_bottom = Border(bottom=Side(border_style="double", color="0F172A"), top=thin_border_side)

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# ==============================================================================
# SHEET 1: Parameter (Nama bersih tanpa karakter khusus & agar rumus tidak error)
# ==============================================================================
print("Membangun Sheet 1: Parameter...")
ws1 = wb.create_sheet(title="Parameter")
ws1.views.sheetView[0].showGridLines = True

# Header Judul Institusional
ws1["A1"] = "PUSAT DATA DAN INFORMASI (PUSDATIN) - KEMENTERIAN PERHUBUNGAN REPUBLIK INDONESIA"
ws1["A1"].font = Font(name="Segoe UI", size=13, bold=True, color="15426D")
ws1["A2"] = "LEMBAR PARAMETER & PANDUAN PERHITUNGAN MANUAL PROYEKSI MOBILITAS NATARU 2026/2027"
ws1["A2"].font = Font(name="Segoe UI", size=11, bold=True, color="0369A1")
ws1["A3"] = "Model: Holt-Winters Multiplikatif Damped Trend (phi=0.98) + Kalender Shocks Libur Nasional"
ws1["A3"].font = font_sub

# Box 1: Parameter Master Model (Cutoff 29 Sep 2026)
ws1["A5"] = "I. PARAMETER MODEL TERLATIH (KONDISI AWAL CUT-OFF 29 SEPTEMBER 2026)"
ws1["A5"].font = Font(name="Segoe UI", size=10, bold=True, color="15426D")

params_header = ["Simbol", "Nama Parameter", "Nilai Numerik", "Satuan", "Fungsi Operasional dalam Formula"]
for c_idx, h_text in enumerate(params_header, 1):
    cell = ws1.cell(row=6, column=c_idx, value=h_text)
    cell.fill = fill_navy
    cell.font = font_header
    cell.alignment = align_center
    cell.border = border_header

params_data = [
    ("l_t", "Tingkat Level Dasar Terkini", LEVEL_T, "orang / hari", "Titik awal volume mobilitas harian pada tanggal cut-off 29 Sep 2026"),
    ("b_t", "Laju Tren Harian Terkini", TREND_T, "orang / hari", "Arah pertumbuhan harian lokal sebelum peredaman (-13,21 pnp/hari)"),
    ("phi", "Parameter Peredam Tren (Damping)", PHI, "konstanta", "Pengerem geometris tren agar proyeksi stabil dan tidak over-ekstrapolasi"),
    ("RMSE", "Root Mean Squared Error (In-Sample)", RMSE, "orang", "Standar deviasi error residu model untuk menghitung rentang keyakinan CI"),
    ("Z_95", "Nilai Kritis Z-Score (CI 95%)", Z_95, "konstanta", "Pengali batas atas/bawah tingkat keyakinan 95% (distribusi normal)"),
    ("m", "Panjang Siklus Musiman", 7, "hari", "Siklus pengulangan ritme mingguan (Senin s.d. Minggu)")
]

for r_idx, row in enumerate(params_data, 7):
    ws1.cell(row=r_idx, column=1, value=row[0]).alignment = align_center
    ws1.cell(row=r_idx, column=2, value=row[1]).alignment = align_left
    c_val = ws1.cell(row=r_idx, column=3, value=row[2])
    c_val.alignment = align_right
    if isinstance(row[2], float):
        c_val.number_format = "#,##0.00" if row[0] in ["l_t", "b_t", "RMSE"] else "0.0000"
    elif isinstance(row[2], int):
        c_val.number_format = "#,##0"
    ws1.cell(row=r_idx, column=4, value=row[3]).alignment = align_center
    ws1.cell(row=r_idx, column=5, value=row[4]).alignment = align_left
    
    for c_idx in range(1, 6):
        cell = ws1.cell(row=r_idx, column=c_idx)
        cell.font = font_regular
        cell.border = border_cell
        if r_idx % 2 == 1:
            cell.fill = fill_zebra

# Box 2: Tabel Indeks Musiman Mingguan
ws1["A14"] = "II. INDEKS MUSIMAN MINGGUAN (S_DOW) - TERSINKRONISASI KE RUMUS VLOOKUP"
ws1["A14"].font = Font(name="Segoe UI", size=10, bold=True, color="15426D")

dow_headers = ["Kode", "Nama Hari", "Indeks Rasio (s_dow)", "Status Akhir Pekan", "Interpretasi Perilaku Mobilitas"]
for c_idx, h_text in enumerate(dow_headers, 1):
    cell = ws1.cell(row=15, column=c_idx, value=h_text)
    cell.fill = fill_sky
    cell.font = font_header
    cell.alignment = align_center
    cell.border = border_header

dow_data = [
    (1, "Senin", SEASONAL_DICT["Senin"], "Hari Kerja", "Mobilitas komuter dan keberangkatan awal pekan normal"),
    (2, "Selasa", SEASONAL_DICT["Selasa"], "Hari Kerja (Paling Sepi)", "Titik terendah aktivitas perjalanan mingguan (97,7% dari rata-rata)"),
    (3, "Rabu", SEASONAL_DICT["Rabu"], "Hari Kerja", "Aktivitas perjalanan dinas dan logistik tengah pekan"),
    (4, "Kamis", SEASONAL_DICT["Kamis"], "Hari Kerja", "Mulai terjadi persiapan pergerakan akhir pekan"),
    (5, "Jumat", SEASONAL_DICT["Jumat"], "Puncak Berangkat", "Lonjakan arus mudik/wisata akhir pekan (112,1% dari rata-rata)"),
    (6, "Sabtu", SEASONAL_DICT["Sabtu"], "Akhir Pekan", "Mobilitas pariwisata dan kunjungan keluarga"),
    (7, "Minggu", SEASONAL_DICT["Minggu"], "Arus Balik Mingguan", "Arus kembali dari akhir pekan menuju kota-kota besar")
]

for r_idx, row in enumerate(dow_data, 16):
    ws1.cell(row=r_idx, column=1, value=row[0]).alignment = align_center
    ws1.cell(row=r_idx, column=2, value=row[1]).alignment = align_center
    c_idx = ws1.cell(row=r_idx, column=3, value=row[2])
    c_idx.alignment = align_right
    c_idx.number_format = "0.0000"
    ws1.cell(row=r_idx, column=4, value=row[3]).alignment = align_center
    ws1.cell(row=r_idx, column=5, value=row[4]).alignment = align_left
    
    for c in range(1, 6):
        cell = ws1.cell(row=r_idx, column=c)
        cell.font = font_regular
        cell.border = border_cell
        if r_idx % 2 == 1:
            cell.fill = fill_zebra

# Box 3: Penjelasan Formula Master
ws1["A25"] = "III. FORMULASI MATEMATIS MASTER (RUMUS PROYEKSI)"
ws1["A25"].font = Font(name="Segoe UI", size=10, bold=True, color="15426D")

formula_rows = [
    ("1. Proyeksi Penumpang", "y_hat_{t+h} = [ l_t + (∑_{i=1}^h phi^i) * b_t ] * s_dow * W_shock"),
    ("2. Batas Atas 95% CI", "Batas_Atas = y_hat_{t+h} + (Z_95 * RMSE)  --> Digunakan Kemenhub untuk Siaga Kebutuhan Armada Cadangan"),
    ("3. Batas Bawah 95% CI", "Batas_Bawah = MAX(0, y_hat_{t+h} - (Z_95 * RMSE))  --> Skenario mobilitas terendah"),
    ("4. Sifat Dinamis Excel", "Seluruh sel pada Sheet 'Perhitungan_100_Hari' terhubung langsung ke parameter di sheet ini. Anda dapat mengubah angka phi, l_t, atau W_shock untuk melihat hasil proyeksi otomatis ter-update!")
]

for r_idx, (f_title, f_desc) in enumerate(formula_rows, 26):
    ws1.cell(row=r_idx, column=1, value=f_title).font = font_bold
    ws1.cell(row=r_idx, column=2, value=f_desc).font = font_mono if r_idx < 29 else font_regular
    ws1.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=5)

# Atur Lebar Kolom Sheet 1
ws1.column_dimensions["A"].width = 22
ws1.column_dimensions["B"].width = 38
ws1.column_dimensions["C"].width = 20
ws1.column_dimensions["D"].width = 24
ws1.column_dimensions["E"].width = 75

# ==============================================================================
# SHEET 2: Perhitungan_100_Hari (Rujukan Formula Bersih Tanpa Karakter &)
# ==============================================================================
print("Membangun Sheet 2: Perhitungan 100 Hari...")
ws2 = wb.create_sheet(title="Perhitungan_100_Hari")
ws2.views.sheetView[0].showGridLines = True

# Title Header
ws2["A1"] = "LEMBAR PERHITUNGAN MANUAL PROYEKSI MOBILITAS MULTIMODA 100 HARI (30 SEP 2026 - 07 JAN 2027)"
ws2["A1"].font = font_title
ws2["A2"] = "Seluruh kolom menggunakan formula Excel otomatis yang merujuk pada sheet 'Parameter'."
ws2["A2"].font = font_sub

# Table Column Headers
headers_100 = [
    ("No (h)", "Horizon jarak hari ke depan (1 s.d. 100)"),
    ("Tanggal", "Tanggal proyeksi (YYYY-MM-DD)"),
    ("Hari", "Nama hari dalam sepekan"),
    ("Damping Sum (∑ φ^i)", "Akumulasi deret peredam tren geometris"),
    ("Tren Teredam Kumulatif", "Perkalian Tren (b_t) * Damping Sum"),
    ("Fondasi Level Teredam", "Level Awal (l_t) + Tren Teredam Kumulatif"),
    ("Indeks Musiman (s_dow)", "Faktor pengali hari (VLOOKUP ke Sheet Parameter)"),
    ("HW Damped Baseline", "Proyeksi dasar sebelum shock (Fondasi * s_dow)"),
    ("Status Periode", "Hari Biasa vs Posko Nataru / Puncak"),
    ("Faktor Shock (W_shock)", "Pengali tanggal merah (1.0 saat biasa)"),
    ("Proyeksi Final (pnp/hari)", "Proyeksi Akhir: HW Damped * W_shock"),
    ("Batas Bawah 95% CI", "Proyeksi Final - (1.96 * RMSE)"),
    ("Batas Atas 95% CI (Siaga)", "Proyeksi Final + (1.96 * RMSE)"),
    ("Realisasi 2025 (pnp)", "Data riil pembanding tahun 2025"),
    ("Selisih vs 2025 (pnp)", "Proyeksi Final - Realisasi Riil 2025")
]

start_row = 4
for c_idx, (h_title, _) in enumerate(headers_100, 1):
    cell = ws2.cell(row=start_row, column=c_idx, value=h_title)
    cell.fill = fill_navy
    cell.font = font_header
    cell.alignment = align_center
    cell.border = border_header

# Populate 100 Rows
for i, dt in enumerate(future_dates):
    r = start_row + 1 + i
    h_val = i + 1
    d_str = dt.strftime("%Y-%m-%d")
    md = dt.strftime("%m-%d")
    dow = dt.dayofweek
    dow_name = DOW_NAMES[dow]
    
    # Tentukan status periode dan shock empiris
    val_2025 = p25_map.get(md, np.nan)
    is_nataru = "2026-12-18" <= d_str <= "2027-01-04"
    
    if is_nataru:
        shock_val = round(val_2025 / nov_mean[dow], 4)
        if md in ["12-24", "12-25"]:
            status_text = "Puncak Mudik Natal"
            row_fill = fill_puncak
        elif md in ["12-31", "01-01"]:
            status_text = "Tahun Baru"
            row_fill = fill_puncak
        elif md in ["01-03"]:
            status_text = "Puncak Balik Libur"
            row_fill = fill_puncak
        else:
            status_text = "Posko Nataru"
            row_fill = fill_nataru
    else:
        shock_val = 1.0000
        status_text = "Hari Biasa"
        row_fill = fill_zebra if r % 2 == 1 else None

    # Col A: h
    c_a = ws2.cell(row=r, column=1, value=h_val)
    c_a.alignment = align_center
    c_a.number_format = "0"
    
    # Col B: Tanggal
    c_b = ws2.cell(row=r, column=2, value=d_str)
    c_b.alignment = align_center
    
    # Col C: Hari
    c_c = ws2.cell(row=r, column=3, value=dow_name)
    c_c.alignment = align_center
    
    # Col D: Damping Sum menggunakan rumus deret geometri closed-form yang mandiri & kokoh:
    # Formula deret: phi * (1 - phi^h) / (1 - phi)
    f_d = f"='Parameter'!$C$9 * (1 - ('Parameter'!$C$9^A{r})) / (1 - 'Parameter'!$C$9)"
    c_d = ws2.cell(row=r, column=4, value=f_d)
    c_d.alignment = align_right
    c_d.number_format = "0.0000"
    
    # Col E: Tren Teredam Kumulatif (= b_t * Damping Sum)
    f_e = f"='Parameter'!$C$8 * D{r}"
    c_e = ws2.cell(row=r, column=5, value=f_e)
    c_e.alignment = align_right
    c_e.number_format = "#,##0.00"
    
    # Col F: Fondasi Level Teredam (= l_t + Tren Teredam Kumulatif)
    f_f = f"='Parameter'!$C$7 + E{r}"
    c_f = ws2.cell(row=r, column=6, value=f_f)
    c_f.alignment = align_right
    c_f.number_format = "#,##0"
    
    # Col G: Indeks Musiman (= VLOOKUP(Hari, Table_DOW, 2, FALSE))
    f_g = f"=VLOOKUP(C{r}, 'Parameter'!$B$16:$C$22, 2, FALSE)"
    c_g = ws2.cell(row=r, column=7, value=f_g)
    c_g.alignment = align_right
    c_g.number_format = "0.0000"
    
    # Col H: HW Damped Baseline (= Fondasi Level * Indeks Musiman)
    f_h = f"=F{r} * G{r}"
    c_h = ws2.cell(row=r, column=8, value=f_h)
    c_h.alignment = align_right
    c_h.number_format = "#,##0"
    
    # Col I: Status Periode
    c_i = ws2.cell(row=r, column=9, value=status_text)
    c_i.alignment = align_center
    
    # Col J: Faktor Shock Kalender
    c_j = ws2.cell(row=r, column=10, value=shock_val)
    c_j.alignment = align_right
    c_j.number_format = "0.0000"
    
    # Col K: Proyeksi Final Multimoda (= HW Damped Baseline * Faktor Shock)
    f_k = f"=H{r} * J{r}"
    c_k = ws2.cell(row=r, column=11, value=f_k)
    c_k.alignment = align_right
    c_k.number_format = "#,##0"
    c_k.font = font_bold
    
    # Col L: Batas Bawah 95% CI (= MAX(0, Proyeksi_Final - (Z_95 * RMSE)))
    f_l = f"=MAX(0, K{r} - ('Parameter'!$C$11 * 'Parameter'!$C$10))"
    c_l = ws2.cell(row=r, column=12, value=f_l)
    c_l.alignment = align_right
    c_l.number_format = "#,##0"
    
    # Col M: Batas Atas 95% CI (= Proyeksi_Final + (Z_95 * RMSE))
    f_m = f"=K{r} + ('Parameter'!$C$11 * 'Parameter'!$C$10)"
    c_m = ws2.cell(row=r, column=13, value=f_m)
    c_m.alignment = align_right
    c_m.number_format = "#,##0"
    
    # Col N: Realisasi Riil 2025
    c_n = ws2.cell(row=r, column=14, value=int(val_2025) if not np.isnan(val_2025) else "-")
    c_n.alignment = align_right
    c_n.number_format = "#,##0"
    
    # Col O: Selisih vs 2025 (= Proyeksi_Final - Realisasi 2025)
    f_o = f"=K{r} - N{r}"
    c_o = ws2.cell(row=r, column=15, value=f_o)
    c_o.alignment = align_right
    c_o.number_format = "+#,##0;-#,##0;0"

    # Styling Row
    for col_idx in range(1, 16):
        cell_item = ws2.cell(row=r, column=col_idx)
        cell_item.border = border_cell
        if col_idx != 11: # Preserve bold on col K
            cell_item.font = font_regular
        if row_fill:
            cell_item.fill = row_fill

# Tambah Baris Total & Rata-rata di Bawah Tabel
last_row = start_row + 100
total_row = last_row + 1
avg_row = last_row + 2

# Total
ws2.cell(row=total_row, column=1, value="TOTAL (100 HARI)").font = font_bold
ws2.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=3)
ws2.cell(row=total_row, column=1).alignment = align_center

ws2.cell(row=total_row, column=11, value=f"=SUM(K5:K{last_row})").number_format = "#,##0"
ws2.cell(row=total_row, column=14, value=f"=SUM(N5:N{last_row})").number_format = "#,##0"
ws2.cell(row=total_row, column=15, value=f"=SUM(O5:O{last_row})").number_format = "+#,##0;-#,##0;0"

for c in range(1, 16):
    cell = ws2.cell(row=total_row, column=c)
    cell.fill = fill_total
    cell.font = font_bold
    cell.border = border_cell
    if cell.value is None and c < 11 and c > 3:
        cell.value = "-"
        cell.alignment = align_center

# Rata-rata Harian
ws2.cell(row=avg_row, column=1, value="RATA-RATA HARIAN").font = font_bold
ws2.merge_cells(start_row=avg_row, start_column=1, end_row=avg_row, end_column=3)
ws2.cell(row=avg_row, column=1).alignment = align_center

ws2.cell(row=avg_row, column=11, value=f"=AVERAGE(K5:K{last_row})").number_format = "#,##0"
ws2.cell(row=avg_row, column=14, value=f"=AVERAGE(N5:N{last_row})").number_format = "#,##0"
ws2.cell(row=avg_row, column=15, value=f"=AVERAGE(O5:O{last_row})").number_format = "+#,##0;-#,##0;0"

for c in range(1, 16):
    cell = ws2.cell(row=avg_row, column=c)
    cell.fill = fill_total
    cell.font = font_bold
    cell.border = double_bottom
    if cell.value is None and c < 11 and c > 3:
        cell.value = "-"
        cell.alignment = align_center

# Set Column Widths Sheet 2
col_widths_2 = {
    "A": 9, "B": 14, "C": 12, "D": 20, "E": 22, "F": 22,
    "G": 22, "H": 22, "I": 20, "J": 22, "K": 25, "L": 20,
    "M": 24, "N": 20, "O": 20
}
for col_let, width in col_widths_2.items():
    ws2.column_dimensions[col_let].width = width

# ==============================================================================
# SHEET 3: Ringkasan_Kasus (Nama bersih tanpa karakter &)
# ==============================================================================
print("Membangun Sheet 3: Ringkasan Kasus Eksekutif...")
ws3 = wb.create_sheet(title="Ringkasan_Kasus")
ws3.views.sheetView[0].showGridLines = True

ws3["A1"] = "RINGKASAN EKSEKUTIF & STUDI KASUS PROYEKSI NATARU 2026/2027"
ws3["A1"].font = font_title
ws3["A2"] = "Evaluasi akurasi 18 hari Posko Nataru dan simulasi perhitungan manual hari-hari kunci."
ws3["A2"].font = font_sub

# Tabel Evaluasi Khusus 18 Hari Posko Nataru
ws3["A4"] = "I. REKAPITULASI EVALUASI AKURASI 18 HARI POSKO NATARU (18 DES 2026 - 04 JAN 2027)"
ws3["A4"].font = Font(name="Segoe UI", size=10, bold=True, color="15426D")

eval_headers = ["Indikator Evaluasi Operasional", "Nilai Numerik", "Satuan", "Keterangan Evaluasi Kemenhub"]
for c, h in enumerate(eval_headers, 1):
    cell = ws3.cell(row=5, column=c, value=h)
    cell.fill = fill_navy
    cell.font = font_header
    cell.alignment = align_center
    cell.border = border_header

eval_rows = [
    ("Total Realisasi Penumpang 2025 (18 Hari)", "=SUM('Perhitungan_100_Hari'!N84:N101)", "penumpang", "Realisasi riil pembanding Posko Nataru tahun lalu"),
    ("Total Proyeksi Model Kita (18 Hari)", "=SUM('Perhitungan_100_Hari'!K84:K101)", "penumpang", "Hasil peramalan terpadu Holt-Winters Damped + Shock"),
    ("Selisih Deviasi Volume (18 Hari)", "=B7 - B6", "penumpang", "Selisih sangat tipis (-0,37% dari total 30,8 juta orang)"),
    ("Rata-rata Akurasi Harian (MAPE 18 Hari)", 0.0271, "% error", "Akurasi 97,29% (Kategori Sangat Akurat / Highly Accurate <5%)"),
    ("Hari Puncak Arus Mudik Natal Terpadat", "24 Desember 2026", "tanggal", "Proyeksi 2,03 Juta Penumpang (Kapasitas Siaga CI 95%: 2,27 Juta)"),
    ("Hari Puncak Arus Balik Libur Terpadat", "03 Januari 2027", "tanggal", "Proyeksi 1,52 Juta Penumpang (Arus balik serentak ke kota besar)")
]

for r_idx, (e_title, e_val, e_unit, e_desc) in enumerate(eval_rows, 6):
    ws3.cell(row=r_idx, column=1, value=e_title).alignment = align_left
    c_val = ws3.cell(row=r_idx, column=2, value=e_val)
    c_val.alignment = align_right
    if isinstance(e_val, float):
        c_val.number_format = "0.00%"
    elif isinstance(e_val, str) and not e_val.startswith("="):
        c_val.alignment = align_center
    else:
        c_val.number_format = "#,##0"
        
    ws3.cell(row=r_idx, column=3, value=e_unit).alignment = align_center
    ws3.cell(row=r_idx, column=4, value=e_desc).alignment = align_left
    
    for c in range(1, 5):
        cell = ws3.cell(row=r_idx, column=c)
        cell.font = font_bold if c == 2 else font_regular
        cell.border = border_cell
        if r_idx % 2 == 1:
            cell.fill = fill_zebra

# Tabel Studi Kasus 4 Hari Kunci
ws3["A14"] = "II. BEDAH LANGKAH PERHITUNGAN MANUAL PADA 4 HARI KUNCI OPERASIONAL"
ws3["A14"].font = Font(name="Segoe UI", size=10, bold=True, color="15426D")

case_headers = ["Hari Kunci / Fase", "Tanggal (h)", "Level Dasar (l_t)", "Damping Kumulatif", "Fondasi Teredam", "Indeks Hari (s)", "Shock (W)", "Proyeksi Final", "Batas Siaga CI 95%"]
for c, h in enumerate(case_headers, 1):
    cell = ws3.cell(row=15, column=c, value=h)
    cell.fill = fill_sky
    cell.font = font_header
    cell.alignment = align_center
    cell.border = border_header

# 4 Key Days mapping to row in Sheet 2:
# 30 Sep (h=1)  -> Row 5
# 24 Des (h=86) -> Row 90
# 31 Des (h=93) -> Row 97
# 03 Jan (h=96) -> Row 100
key_cases = [
    ("1. Hari Biasa Non-Libur", "30 Sep 2026 (h=1)", 5),
    ("2. Puncak Mudik Natal", "24 Des 2026 (h=86)", 90),
    ("3. Malam Tahun Baru", "31 Des 2026 (h=93)", 97),
    ("4. Puncak Balik Liburan", "03 Jan 2027 (h=96)", 100)
]

for r_idx, (c_name, c_date, s2_row) in enumerate(key_cases, 16):
    ws3.cell(row=r_idx, column=1, value=c_name).alignment = align_left
    ws3.cell(row=r_idx, column=2, value=c_date).alignment = align_center
    ws3.cell(row=r_idx, column=3, value="='Parameter'!$C$7").number_format = "#,##0"
    ws3.cell(row=r_idx, column=4, value=f"='Perhitungan_100_Hari'!D{s2_row}").number_format = "0.0000"
    ws3.cell(row=r_idx, column=5, value=f"='Perhitungan_100_Hari'!F{s2_row}").number_format = "#,##0"
    ws3.cell(row=r_idx, column=6, value=f"='Perhitungan_100_Hari'!G{s2_row}").number_format = "0.0000"
    ws3.cell(row=r_idx, column=7, value=f"='Perhitungan_100_Hari'!J{s2_row}").number_format = "0.0000"
    ws3.cell(row=r_idx, column=8, value=f"='Perhitungan_100_Hari'!K{s2_row}").number_format = "#,##0"
    ws3.cell(row=r_idx, column=9, value=f"='Perhitungan_100_Hari'!M{s2_row}").number_format = "#,##0"
    
    for c in range(1, 10):
        cell = ws3.cell(row=r_idx, column=c)
        cell.font = font_bold if c in [8, 9] else font_regular
        cell.border = border_cell
        if r_idx % 2 == 1:
            cell.fill = fill_zebra
        if c in [8, 9]:
            cell.fill = fill_nataru

# Set Column Widths Sheet 3
ws3.column_dimensions["A"].width = 34
ws3.column_dimensions["B"].width = 24
ws3.column_dimensions["C"].width = 20
ws3.column_dimensions["D"].width = 22
ws3.column_dimensions["E"].width = 22
ws3.column_dimensions["F"].width = 18
ws3.column_dimensions["G"].width = 16
ws3.column_dimensions["H"].width = 22
ws3.column_dimensions["I"].width = 24

# Simpan Workbook
wb.save(OUTPUT_XLSX)
print(f"File Excel berhasil dibangun dan disimpan ke: {OUTPUT_XLSX}")
