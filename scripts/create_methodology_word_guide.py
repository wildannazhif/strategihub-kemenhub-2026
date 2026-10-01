import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_DOCX = r"c:\Users\USER\Documents\PUSDATIN\Buku_Panduan_Metodologi_Forecasting_Nataru_2026.docx"

print(f"Membangun dokumen Word Buku Panduan Metodologi: {OUTPUT_DOCX}...")
doc = docx.Document()

# 1. Page Setup (Margin Normal 1 inch)
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.different_first_page_header_footer = True
    
    # Header
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("Pusat Data dan Informasi Kemenhub • Panduan Metodologi Forecasting Multimoda")
    hrun.font.name = "Segoe UI"
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = RGBColor(100, 116, 139)
    
    # Footer
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Buku Panduan Metodologi Peramalan Mobilitas & Kebutuhan Armada Nataru 2026/2027 • Dokumen Teknis")
    frun.font.name = "Segoe UI"
    frun.font.size = Pt(8.5)
    frun.font.color.rgb = RGBColor(148, 163, 184)

# 2. Helper Styling Functions
def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(21, 66, 109) # Kemenhub Navy
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_body_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Segoe UI"
        r_pre.font.size = Pt(10)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Segoe UI"
        r_pre.font.size = Pt(9.5)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_callout_box(doc, text, title="CATATAN METODOLOGI", border_color="15426D", bg_color="F0F5FA"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.bold = True
    run_t.font.name = "Segoe UI"
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(int(border_color[:2], 16), int(border_color[2:4], 16), int(border_color[4:], 16))
    
    run_b = p.add_run(text)
    run_b.font.name = "Segoe UI"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_formula_box(doc, formula_text, caption=None):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="3B82F6"/><w:top w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/><w:right w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/></w:tcBorders>')
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    
    rf = p.add_run(formula_text)
    rf.font.name = "Consolas"
    rf.font.size = Pt(10.5)
    rf.bold = True
    rf.font.color.rgb = RGBColor(30, 58, 138)
    
    if caption:
        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(2)
        rc = p2.add_run(caption)
        rc.font.name = "Segoe UI"
        rc.font.size = Pt(8.5)
        rc.italic = True
        rc.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def format_table_header(row, col_widths=None, bg_color="15426D"):
    for idx, cell in enumerate(row.cells):
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Segoe UI"
                r.font.size = Pt(9)
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and idx < len(col_widths):
            cell.width = col_widths[idx]

def format_table_rows(table, col_widths=None, alt_color="F8FAFC"):
    for row_idx, row in enumerate(table.rows[1:]):
        bg = alt_color if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(1.5)
                p.paragraph_format.space_after = Pt(1.5)
                for r in p.runs:
                    r.font.name = "Segoe UI"
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = RGBColor(30, 41, 59)
            if col_widths and col_idx < len(col_widths):
                cell.width = col_widths[col_idx]

# =========================================================================
# COVER / HEADER TITLE
# =========================================================================
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(24)
title_p.paragraph_format.space_after = Pt(6)
r_title = title_p.add_run("BUKU PANDUAN METODOLOGI PERAMALAN MOBILITAS NASIONAL & SIMULASI KEBUTUHAN ARMADA NATARU 2026/2027")
r_title.font.name = "Segoe UI"
r_title.font.size = Pt(18)
r_title.bold = True
r_title.font.color.rgb = RGBColor(21, 66, 109)

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_before = Pt(0)
sub_p.paragraph_format.space_after = Pt(16)
r_sub = sub_p.add_run("Kajian Matematis, Formulasi Algoritma Holt-Winters Damped Trend, Validasi Backtest 28 Hari, dan Rekomendasi Kapasitas Lapangan di 1.010 Simpul Prasarana SIASATI")
r_sub.font.name = "Segoe UI"
r_sub.font.size = Pt(11)
r_sub.italic = True
r_sub.font.color.rgb = RGBColor(100, 116, 139)

# Meta Table
tbl_meta = doc.add_table(rows=4, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("Instansi Pengkaji", "Pusat Data dan Informasi (PUSDATIN) - Kementerian Perhubungan RI"),
    ("Dataset Sumber", "SIASATI Multimoda 2026 (209.885 baris data bersih, 5 moda, 1.010 simpul)"),
    ("Model Peramalan", "Holt-Winters Multiplicative Exponential Smoothing + Damped Trend (φ=0,98) + Calendar Shocks"),
    ("Tingkat Akurasi Model", "MAPE = 6,53% | RMSE = 94.259 pnp/hari | Nilai Keyakinan 95% (CI_95%)")
]
for i, (k, v) in enumerate(meta_data):
    row = tbl_meta.rows[i]
    row.cells[0].text = k
    row.cells[1].text = v
format_table_header(tbl_meta.rows[0], [Inches(2.2), Inches(4.3)], bg_color="15426D")
format_table_rows(tbl_meta, [Inches(2.2), Inches(4.3)], alt_color="F0F5FA")

doc.add_paragraph().paragraph_format.space_after = Pt(12)

# =========================================================================
# BAB 1: PENDAHULUAN & KARAKTERISTIK DATASET SIASATI
# =========================================================================
add_heading_1(doc, "BAB 1: Latar Belakang & Karakteristik Data Mobilitas")

add_body_p(doc, 
    "Peramalan mobilitas penumpang dan kebutuhan armada pada momentum hari libur nasional (seperti Natal & Tahun Baru / Nataru) "
    "memiliki tantangan ilmiah yang sangat berbeda dibandingkan peramalan deret waktu pada domain keuangan atau inventori ritel. "
    "Data mobilitas transportasi nasional memiliki 4 karakteristik utama yang saling berinteraksi:", 
    "Hakikat Data Deret Waktu Transportasi: ")

add_bullet_p(doc, "Pergerakan penumpang sangat dipengaruhi oleh rutinitas siklus mingguan (Senin s.d. Minggu). Hari Jumat dan Minggu selalu menjadi puncak mingguan (*weekend surges*), sedangkan Selasa dan Rabu menjadi titik terendah.", "1. Pola Musiman Mingguan yang Dominan: ")
add_bullet_p(doc, "Tren pertumbuhan tidak bergerak statis, melainkan memiliki laju pertumbuhan tahunan (*Year-over-Year Growth*) yang bergerak lambat namun pasti seiring pertumbuhan ekonomi nasional.", "2. Tren Jangka Menengah: ")
add_bullet_p(doc, "Kapasitas fisik sarana (jumlah gerbong, kursi pesawat, armada feri) memiliki batas jenuh maksimum. Peramalan tidak boleh memproyeksikan angka yang menanjak linier tanpa henti (*unbounded linear growth*).", "3. Batasan Kapasitas Fisik (*Physical Saturation*): ")
add_bullet_p(doc, "Libur keagamaan dan pergantian tahun menimbulkan lonjakan pergerakan masif serentak dalam rentang 1–3 hari yang berkali-kali lipat lebih tinggi dari hari normal biasa.", "4. Kejutan Eksogen Terjadwal (*Calendar Event Shocks*): ")

add_callout_box(doc, 
    "Buku panduan ini disusun agar tim teknis PUSDATIN Kemenhub dapat memahami rumus, cara pembuktian akurasi, "
    "dan alur eksekusi komputasi secara transparan, dapat direplikasi secara mandiri (*reproducible*), dan siap dipertanggungjawabkan dalam forum pimpinan.", 
    "Tujuan Dokumen Pembelajaran Ini", "15426D", "F0F5FA")

# =========================================================================
# BAB 2: ANATOMI METODE HOLT-WINTERS DAMPED TREND
# =========================================================================
add_heading_1(doc, "BAB 2: Anatomi Model Holt-Winters Damped Trend")

add_body_p(doc, 
    "Model yang digunakan adalah Holt-Winters Triple Exponential Smoothing varian Multiplikatif dengan penambahan parameter peredam tren (Damped Trend) "
    "yang dipelopori oleh Gardner & McKenzie (1985), serta disempurnakan dengan kalender pengali lonjakan libur nasional (*event shocks*).")

add_heading_2(doc, "2.1 Mengapa Multiplikatif (Bukan Aditif)?")
add_body_p(doc, 
    "Dalam model aditif, variasi musiman mingguan diasumsikan memiliki selisih konstan berupa angka tetap (misalnya hari Minggu selalu +100.000 penumpang). "
    "Namun kenyataan lapangan di lapangan Kemenhub membuktikan bahwa ketika level mobilitas nasional naik dari 1,2 juta pnp/hari (hari biasa) menjadi 2,3 juta pnp/hari (hari libur puncak), "
    "lonjakan akhir pekan juga membesar secara proporsional. "
    "Oleh karena itu, komponen musiman harus bersifat multiplikatif (dikalikan terhadap level, bukan dijumlahkan).")

add_heading_2(doc, "2.2 Mengapa Damped Trend (φ = 0,98)?")
add_body_p(doc, 
    "Dalam model Holt-Winters linier standar, proyeksi tren jangka panjang dihitung dengan formula (h × b_t). "
    "Jika rumus linier standar ini diterapkan pada horizon 100 hari (Oktober 2026 s.d. Januari 2027), "
    "tren pertumbuhan positif akan terus diekstrapolasikan secara linier hingga menghasilkan angka proyeksi yang tidak rasional (over-optimistic / over-extrapolation). "
    "Parameter peredam φ = 0,98 berfungsi mengerem laju tren seiring bertambahnya horizon ramalan:")

add_formula_box(doc, 
    "Tren Teredam Kumulatif = b_t × (φ + φ² + φ³ + ... + φ^h) = b_t × ∑_{i=1}^h φ^i", 
    "Formula Peluruhan Tren Gardner & McKenzie (φ = 0,98)")

add_body_p(doc, "Perilaku matematis peredam tren φ = 0,98 adalah sebagai berikut:")
add_bullet_p(doc, "Bobot tren masih aktif sebesar 98% (hampir linier).", "• Hari ke-1 ramalan: ")
add_bullet_p(doc, "Bobot tren tersisa (0,98)^14 = 75,4% dari laju awal.", "• Hari ke-14 ramalan: ")
add_bullet_p(doc, "Bobot tren tersisa (0,98)^30 = 54,5%.", "• Hari ke-30 ramalan: ")
add_bullet_p(doc, "Bobot tren melandai stabil ke titik asimtot maksimum, mencegah lonjakan proyeksi yang melampaui daya tampung sarana nasional.", "• Hari ke-100 ramalan: ")

add_heading_2(doc, "2.3 Mengapa Weekly Seasonality (s = 7)?")
add_body_p(doc, 
    "Karena data beresolusi harian, siklus musiman paling fundamental yang berulang terus-menerus adalah siklus 7 hari (Senin = 1, Selasa = 2, ..., Minggu = 7). "
    "Indeks musiman s_t merepresentasikan pengali alami untuk tiap hari dalam sepekan.")

add_heading_2(doc, "2.4 Kalibrasi Calendar Event Shock (W_shock)")
add_body_p(doc, 
    "Model time series statistik standar hanya mengenal siklus hari Senin s.d. Minggu. Model tersebut tidak memiliki kalender tanggal merah libur Natal dan Tahun Baru. "
    "Oleh karena itu, dimasukkan pengali eksogen W_shock yang dikalibrasi langsung dari elastisitas lonjakan empiris Nataru 2025 dan Idul Fitri 2026:")

tbl_shock = doc.add_table(rows=5, cols=4)
tbl_shock.alignment = WD_TABLE_ALIGNMENT.CENTER
shock_data = [
    ("Fase Libur Nataru", "Rentang Tanggal", "Nilai Shock (W_shock)", "Makna Operasional Lapangan"),
    ("Puncak Mudik Natal", "24 - 25 Des 2026", "1,25 s/d 1,35 (+25% - +35%)", "Keberangkatan mudik liburan sekolah & pekerja luar kota"),
    ("Puncak Wisata Libur", "27 - 28 Des 2026", "1,15 s/d 1,22 (+15% - +22%)", "Arus wisata darat, penyeberangan feri, dan penerbangan"),
    ("Malam Tahun Baru", "31 Des 2026 - 1 Jan 2027", "1,10 s/d 1,18 (+10% - +18%)", "Mobilitas aglomerasi perkotaan & penyeberangan wisata"),
    ("Puncak Balik Serentak", "03 Januari 2027", "1,35 s/d 1,45 (+35% - +45%)", "Arus balik serentak seluruh moda menuju kota-kota besar")
]
for i, r in enumerate(shock_data):
    for j, val in enumerate(r):
        tbl_shock.rows[i].cells[j].text = val
format_table_header(tbl_shock.rows[0], [Inches(1.8), Inches(1.5), Inches(1.5), Inches(1.7)], bg_color="15426D")
format_table_rows(tbl_shock, [Inches(1.8), Inches(1.5), Inches(1.5), Inches(1.7)], alt_color="F8FAFC")

# =========================================================================
# BAB 3: PERSAMAAN MATEMATIS STEP-BY-STEP
# =========================================================================
add_heading_1(doc, "BAB 3: Formulasi Matematis Lengkap Step-by-Step")

add_body_p(doc, "Setiap kali titik data observasi baru (y_t) masuk, model memperbarui tiga status internal secara berulang (rekursif):")

add_heading_2(doc, "1. Persamaan Pembaruan Level (ℓ_t)")
add_formula_box(doc, 
    "ℓ_t = α × (y_t / s_{t-m}) + (1 - α) × (ℓ_{t-1} + φ × b_{t-1})", 
    "Level Baru = Rata-rata bobot data terkini ter-deseasonalisasi + Level lalu yang diredam")
add_body_p(doc, "Di mana α (alpha) adalah konstanta pemulusan level (0 < α < 1). Pembagian dengan s_{t-m} bertujuan membuang efek musiman dari data aktual agar didapatkan level riil yang bersih.")

add_heading_2(doc, "2. Persamaan Pembaruan Tren (b_t)")
add_formula_box(doc, 
    "b_t = β × (ℓ_t - ℓ_{t-1}) + (1 - β) × φ × b_{t-1}", 
    "Tren Baru = Rata-rata perubahan level terkini + Tren lalu yang diredam")
add_body_p(doc, "Di mana β (beta) adalah konstanta pemulusan tren (0 < β < 1), dan φ adalah parameter peredam tren (0,98).")

add_heading_2(doc, "3. Persamaan Pembaruan Musiman (s_t)")
add_formula_box(doc, 
    "s_t = γ × (y_t / ℓ_t) + (1 - γ) × s_{t-m}", 
    "Indeks Musiman Baru = Rasio data terhadap level + Indeks musiman periode minggu lalu")
add_body_p(doc, "Di mana γ (gamma) adalah konstanta pemulusan musiman (0 < γ < 1), dan m = 7 adalah panjang siklus mingguan.")

add_heading_2(doc, "4. Persamaan Prediksi Horizon h Langkah ke Depan (ŷ_{t+h})")
add_formula_box(doc, 
    "ŷ_{t+h} = [ ℓ_t + (∑_{i=1}^h φ^i) × b_t ] × s_{t+h-m(k+1)} × ∏ W_shock", 
    "Formulasi Master Prediksi Holt-Winters Damped Multiplikatif dengan Shock")

add_heading_2(doc, "5. Interval Keyakinan 95% (Confidence Interval)")
add_formula_box(doc, 
    "CI_95% = ŷ_{t+h} ± 1,96 × RMSE", 
    "Batas Atas dan Batas Bawah Ketidakpastian Prediksi")
add_body_p(doc, "Berdasarkan nilai RMSE empiris (94.259 penumpang), rentang ketidakpastian 95% adalah ± 5,5% dari nilai prediksi pusat.")

# =========================================================================
# BAB 4: PEMBAGIAN DATA & UJI BACKTESTING
# =========================================================================
add_heading_1(doc, "BAB 4: Pembagian Data & Evaluasi Akurasi (Backtesting)")

add_body_p(doc, 
    "Kunci integritas ilmiah model peramalan terletak pada prosedur validasinya. "
    "Banyak kesalahan pemodelan terjadi karena praktisi mengacak data secara sembarangan (*random train-test split*). "
    "Dalam peramalan deret waktu, pemisahan data wajib dilakukan secara kronologis (*Temporal Out-of-Time Split*).")

add_heading_2(doc, "4.1 Rincian Pembagian Dataset 270 Hari")
tbl_split = doc.add_table(rows=4, cols=4)
tbl_split.alignment = WD_TABLE_ALIGNMENT.CENTER
split_rows = [
    ("Himpunan Data", "Rentang Kalender", "Jumlah Hari", "Persentase & Peran Ilmiah"),
    ("Data Latih (Training Set)", "01 Jan 2026 s.d. 30 Agu 2026", "242 hari", "89,6% • Melatih nilai awal Level, Tren, dan Indeks Musiman"),
    ("Data Uji (Testing Set)", "31 Agu 2026 s.d. 27 Sep 2026", "28 hari", "10,4% • Menguji prediksi tanpa model melihat data riilnya"),
    ("Total Dataset 2026", "01 Jan 2026 s.d. 27 Sep 2026", "270 hari", "100,0% • Dataset bersih SIASATI PUSDATIN Kemenhub")
]
for i, r in enumerate(split_rows):
    for j, val in enumerate(r):
        tbl_split.rows[i].cells[j].text = val
format_table_header(tbl_split.rows[0], [Inches(1.8), Inches(2.0), Inches(1.1), Inches(1.6)], bg_color="15426D")
format_table_rows(tbl_split, [Inches(1.8), Inches(2.0), Inches(1.1), Inches(1.6)], alt_color="F8FAFC")

add_callout_box(doc, 
    "Data uji dipilih tepat 28 hari karena 28 adalah kelipatan bulat dari 7 (28 = 4 × 7 hari). "
    "Artinya, data uji memiliki tepat 4 hari Senin, 4 hari Selasa, ..., dan 4 hari Minggu. "
    "Hal ini mutlak diperlukan agar evaluasi tidak bias terhadap hari tertentu (*day-of-week balance*).", 
    "Mengapa Memilih Tepat 28 Hari untuk Testing?", "059669", "ECFDF5")

add_heading_2(doc, "4.2 Rumus Metrik Evaluasi Akurasi")

add_body_p(doc, "Tiga metrik standar internasional dihitung untuk mengukur deviasi antara data riil (y_t) dan hasil ramalan (ŷ_t):")

add_formula_box(doc, "MAPE = (100% / n) × ∑_{t=1}^n | (y_t - ŷ_t) / y_t |", "Mean Absolute Percentage Error (MAPE) - Mengukur deviasi persentase rata-rata")
add_formula_box(doc, "RMSE = √ [ (1 / n) × ∑_{t=1}^n (y_t - ŷ_t)² ]", "Root Mean Squared Error (RMSE) - Memberi penalti besar pada deviasi ekstrem")
add_formula_box(doc, "MAE  = (1 / n) × ∑_{t=1}^n | y_t - ŷ_t |", "Mean Absolute Error (MAE) - Rata-rata selisih volume penumpang absolut")

add_heading_2(doc, "4.3 Hasil Uji Empiris Backtesting (Hasil Script evaluate_backtest.py)")
tbl_res = doc.add_table(rows=7, cols=5)
tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
res_rows = [
    ("Moda Transportasi", "MAPE (%)", "RMSE (pnp/hari)", "Rata-rata Riil (pnp/h)", "Rasio Error (RMSE/Mean)"),
    ("✈ Udara", "4,89%", "15.549 pnp", "182.493 pnp", "8,52% (Sangat Stabil)"),
    ("🚆 Kereta Api", "6,05%", "16.598 pnp", "238.115 pnp", "6,97% (Akurat Tinggi)"),
    ("🚌 Bus AKAP", "7,42%", "40.718 pnp", "452.880 pnp", "8,99% (Akurat Baik)"),
    ("🚢 Laut", "8,24%", "10.428 pnp", "102.340 pnp", "10,19% (Akurat Baik)"),
    ("⛴ ASDP Feri", "11,28%", "38.077 pnp", "469.752 pnp", "8,11% (Dinamika Cuaca)"),
    ("TOTAL MULTIMODA", "6,53%", "94.259 pnp", "1.445.580 pnp", "6,52% (Akurat Tinggi)")
]
for i, r in enumerate(res_rows):
    for j, val in enumerate(r):
        tbl_res.rows[i].cells[j].text = val
format_table_header(tbl_res.rows[0], [Inches(1.8), Inches(1.1), Inches(1.3), Inches(1.3), Inches(1.0)], bg_color="15426D")
format_table_rows(tbl_res, [Inches(1.8), Inches(1.1), Inches(1.3), Inches(1.3), Inches(1.0)], alt_color="F8FAFC")

add_callout_box(doc, 
    "Berdasarkan literatur ilmiah peramalan (Lewis, 1982 & Armstrong, 2001), "
    "nilai MAPE di bawah 10% diklasifikasikan sebagai 'High Accuracy Forecasting' (Peramalan Akurasi Sangat Tinggi). "
    "Dengan MAPE agregat 6,53%, model dinyatakan sah dan layak menjadi dasar kebijakan mitigasi Nataru Kemenhub.", 
    "Kesimpulan Validasi Ilmiah", "15426D", "F0F5FA")

# =========================================================================
# BAB 5: METODE PERHITUNGAN KEBUTUHAN TAMBAHAN ARMADA
# =========================================================================
add_heading_1(doc, "BAB 5: Metode Perhitungan Kebutuhan Tambahan Armada (1.010 Simpul)")

add_body_p(doc, 
    "Setelah total volume nasional berhasil diproyeksikan, langkah selanjutnya adalah mendistribusikan rekomendasi "
    "kebutuhan tambahan armada ke seluruh 1.010 simpul prasarana nasional (bandara, stasiun, terminal, pelabuhan penyeberangan, dan pelabuhan laut).")

add_heading_2(doc, "5.1 Mengapa Murni Menggunakan Data Keberangkatan?")
add_body_p(doc, 
    "Kemacetan, antrean kendaraan bermil-mil, dan penumpukan orang 100% terjadi di alur keberangkatan "
    "(penumpang menunggu di ruang tunggu, kendaraan tertahan di buffer zone pelabuhan, antrean peron keberangkatan). "
    "Sebaliknya, pada alur kedatangan, penumpang yang tiba langsung meninggalkan simpul sehingga tidak memicu bottleneck. "
    "Oleh karena itu, formula evaluasi beban hanya membandingkan penumpang berangkat dan armada berangkat:")

add_formula_box(doc, 
    "Beban Keberangkatan (Load per Trip) = Penumpang_Berangkat / Armada_Berangkat", 
    "Rata-rata Penumpang yang Harus Diangkut per Satu Kali Keberangkatan Sarana")

add_heading_2(doc, "5.2 Formula Rasio Lonjakan Beban (Load Ratio)")
add_formula_box(doc, 
    "Rasio Lonjakan = Beban_Puncak_Libur / Beban_Rata_Rata_Biasa", 
    "Mengukur Berapa Kali Lipat Kepadatan Naik Dibanding Hari Normal")

add_heading_2(doc, "5.3 Matriks Penentuan Persentase Tambahan Armada")
tbl_kriteria = doc.add_table(rows=5, cols=4)
tbl_kriteria.alignment = WD_TABLE_ALIGNMENT.CENTER
kriteria_rows = [
    ("Klasifikasi Status", "Syarat Ambang Batas Empiris", "Rekomendasi Tambah", "Aksi Operasional Kemenhub"),
    ("🔴 Sangat Kritis", "Rasio ≥ 3,0x ATAU (Rasio ≥ 2,0x & Pnp Puncak ≥ 20.000)", "+20% Armada", "Pola TBB (Tiba Bongkar Berangkat), kapal kapasitas besar, extra flight 24 jam"),
    ("🟠 Tinggi / Kritis", "Rasio ≥ 1,8x ATAU (Rasio ≥ 1,4x & Pnp Puncak ≥ 10.000)", "+15% Armada", "KLB KA Tambahan, dermaga cadangan/ponton, pembukaan jalur peron cepat"),
    ("🟡 Padat Tinggi", "Rasio ≥ 1,2x ATAU Pnp Puncak ≥ 5.000", "+10% Armada", "Stamformasi KA maksimal (12 kereta), extra flight slot malam (red-eye flight)"),
    ("🟢 Terkendali", "Rasio < 1,2x (Kondisi normal / terkendali)", "+5% Armada", "Penyiagaan armada cadangan bantuan di pool, ramp check kelaikan jalan")
]
for i, r in enumerate(kriteria_rows):
    for j, val in enumerate(r):
        tbl_kriteria.rows[i].cells[j].text = val
format_table_header(tbl_kriteria.rows[0], [Inches(1.5), Inches(2.2), Inches(1.3), Inches(1.5)], bg_color="15426D")
format_table_rows(tbl_kriteria, [Inches(1.5), Inches(2.2), Inches(1.3), Inches(1.5)], alt_color="F8FAFC")

add_heading_2(doc, "5.4 Rumus Tambahan Unit Fisik Harian")
add_formula_box(doc, 
    "Tambahan Armada Fisik (Unit/hari) = Round [ Armada_Puncak × (Persentase_Tambah / 100) ]", 
    "Konversi Persentase Menjadi Unit Nyata Bus, Kereta Api, Penerbangan, atau Kapal")

# =========================================================================
# BAB 6: STUDI KASUS & CONTOH PERHITUNGAN NUMERIK
# =========================================================================
add_heading_1(doc, "BAB 6: Studi Kasus Perhitungan Numerik di Lapangan")

add_body_p(doc, "Berikut adalah contoh perhitungan matematis nyata pada 3 simpul transportasi strategis nasional:")

add_heading_2(doc, "Studi Kasus 1: Pelabuhan Merak (ASDP Feri)")
add_bullet_p(doc, "Penumpang Berangkat = 25.319 orang | Armada Berangkat = 108 trip kapal → Beban Biasa = 25.319 / 108 = 234 pnp/kapal.", "• Data Normal (Februari): ")
add_bullet_p(doc, "Penumpang Berangkat = 115.459 orang | Armada Berangkat = 130 trip kapal → Beban Puncak = 115.459 / 130 = 888 pnp/kapal.", "• Data Puncak (Libur): ")
add_bullet_p(doc, "Rasio = 888 / 234 = 3,79x lipat lonjakan beban (Kategori: Sangat Kritis).", "• Perhitungan Rasio: ")
add_bullet_p(doc, "+20% armada fisik tambahan.", "• Rekomendasi Persentase: ")
add_bullet_p(doc, "130 trip × 20% = +26 trip kapal Ro-Ro per hari (Total Armada Operasi: 156 trip kapal/hari).", "• Tambahan Unit Fisik: ")

add_heading_2(doc, "Studi Kasus 2: Stasiun Pasar Senen (Kereta Api)")
add_bullet_p(doc, "Penumpang Berangkat = 8.889 orang | Armada Berangkat = 34 KA → Beban Biasa = 8.889 / 34 = 265 pnp/KA.", "• Data Normal (Februari): ")
add_bullet_p(doc, "Penumpang Berangkat = 25.021 orang | Armada Berangkat = 46 KA → Beban Puncak = 25.021 / 46 = 544 pnp/KA.", "• Data Puncak (Libur): ")
add_bullet_p(doc, "Rasio = 544 / 265 = 2,06x lipat lonjakan beban dengan volume puncak > 20.000 pnp (Kategori: Sangat Kritis).", "• Perhitungan Rasio: ")
add_bullet_p(doc, "+15% perjalanan KA tambahan.", "• Rekomendasi Persentase: ")
add_bullet_p(doc, "46 KA × 15% = +7 perjalanan KA jarak jauh tambahan per hari (Total Armada Operasi: 53 KA/hari).", "• Tambahan Unit Fisik: ")

add_heading_2(doc, "Studi Kasus 3: Bandara Soekarno-Hatta CGK (Penerbangan)")
add_bullet_p(doc, "Penumpang Berangkat = 70.958 orang | Armada Berangkat = 493 flight → Beban Biasa = 144 pnp/flight.", "• Data Normal (Februari): ")
add_bullet_p(doc, "Penumpang Berangkat = 105.172 orang | Armada Berangkat = 614 flight → Beban Puncak = 171 pnp/flight.", "• Data Puncak (Libur): ")
add_bullet_p(doc, "Rasio = 171 / 144 = 1,19x lipat. Karena volume puncak mencapai 105.172 pnp/hari (skala mega-hub), masuk kategori Padat Tinggi.", "• Perhitungan Rasio: ")
add_bullet_p(doc, "+10% extra flight.", "• Rekomendasi Persentase: ")
add_bullet_p(doc, "614 flight × 10% = +61 extra flight per hari via slot malam 24 jam (Total Armada Operasi: 675 flight/hari).", "• Tambahan Unit Fisik: ")

# =========================================================================
# BAB 7: GLOSARIUM & KESIMPULAN
# =========================================================================
add_heading_1(doc, "BAB 7: Glosarium Istilah Teknis & Penutup")

tbl_glo = doc.add_table(rows=7, cols=2)
tbl_glo.alignment = WD_TABLE_ALIGNMENT.CENTER
glo_rows = [
    ("Istilah Teknis", "Penjelasan Praktis bagi Perencana Transportasi"),
    ("Exponential Smoothing", "Metode peramalan deret waktu yang memberi bobot lebih besar pada data pengamatan terbaru dan bobot menurun secara eksponensial pada data yang lebih lama."),
    ("Damped Trend (φ)", "Teknik peredaman matematis untuk mencegah ekstrapolasi tren linier jangka panjang melambung tak terhingga, disesuaikan batas saturasi fisik infrastruktur."),
    ("Multiplicative Seasonality", "Model musiman di mana fluktuasi siklikal membesar atau mengecil sebanding dengan level rata-rata data saat itu."),
    ("Out-of-Time Backtesting", "Pengujian akurasi model menggunakan data masa depan terpotong yang tidak pernah dilihat model saat proses pelatihan untuk menghindari bias optimis."),
    ("MAPE", "Mean Absolute Percentage Error; indikator standar akurasi peramalan. Semakin kecil nilainya (<10%), semakin tinggi presisi peramalan."),
    ("TBB (Tiba Bongkar Berangkat)", "Pola operasional kapal feri penyeberangan saat puncak di mana kapal hanya membongkar muatan di pelabuhan tujuan lalu segera bertolak kosong untuk menyedot antrean di pelabuhan asal.")
]
for i, r in enumerate(glo_rows):
    for j, val in enumerate(r):
        tbl_glo.rows[i].cells[j].text = val
format_table_header(tbl_glo.rows[0], [Inches(2.2), Inches(4.3)], bg_color="15426D")
format_table_rows(tbl_glo, [Inches(2.2), Inches(4.3)], alt_color="F8FAFC")

add_body_p(doc, 
    "Dengan memahami seluruh bab dalam buku panduan ini, tim PUSDATIN Kemenhub memiliki pegangan metodologis yang kokoh, "
    "terverifikasi secara empiris, dan siap dipresentasikan kepada Menteri Perhubungan maupun pemangku kepentingan transportasi nasional.", 
    "Penutup: ")

# Save Document
doc.save(OUTPUT_DOCX)
print(f"Dokumen Word berhasil dibuat: {OUTPUT_DOCX}")
print(f"Ukuran file: {os.path.getsize(OUTPUT_DOCX) / 1024:.1f} KB")
