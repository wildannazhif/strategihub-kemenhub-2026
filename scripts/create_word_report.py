import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc_path = r"c:\Users\USER\Documents\PUSDATIN\Laporan_Audit_Anomali_Data_Siasati_2026.docx"
assets_dir = r"c:\Users\USER\Documents\PUSDATIN\laporan_anomali_assets"

print("=== MEMBANGUN DOKUMEN LAPORAN AUDIT ANOMALI (WORD DOCX) ===")
doc = docx.Document()

# Set page margins to 1 inch (2.54 cm)
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Helper functions for styling
def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout_box(doc, text, title="CATATAN KRITIS / TEMUAN AUDIT", border_color="1E3A8A", bg_color="F1F5F9"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    # Left border only
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

def format_table_header(row, col_widths=None, bg_color="1E3A8A"):
    for idx, cell in enumerate(row.cells):
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Segoe UI"
                r.font.size = Pt(9.5)
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and idx < len(col_widths):
            cell.width = Inches(col_widths[idx])

def format_table_rows(table, col_widths=None, alt_color="F8FAFC"):
    for r_idx, row in enumerate(table.rows[1:]):
        bg = alt_color if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                for r in p.runs:
                    r.font.name = "Segoe UI"
                    r.font.size = Pt(9)
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])

# =============================================================
# COVER PAGE / JUDUL LAPORAN
# =============================================================
p_pre = doc.add_paragraph()
p_pre.paragraph_format.space_before = Pt(20)
p_pre.paragraph_format.space_after = Pt(6)
r_org = p_pre.add_run("KEMENTERIAN PERHUBUNGAN REPUBLIK INDONESIA\nPUSAT DATA DAN INFORMASI (PUSDATIN)")
r_org.bold = True
r_org.font.name = "Segoe UI"
r_org.font.size = Pt(11)
r_org.font.color.rgb = RGBColor(71, 85, 105)

p_title = doc.add_paragraph()
p_title.paragraph_format.space_before = Pt(8)
p_title.paragraph_format.space_after = Pt(8)
r_title = p_title.add_run("LAPORAN AUDIT & DOKUMENTASI ANOMALI DATASET MULTIMODA TRANSPORTASI NASIONAL 2026")
r_title.bold = True
r_title.font.name = "Segoe UI"
r_title.font.size = Pt(20)
r_title.font.color.rgb = RGBColor(30, 58, 138) # Deep Navy

p_sub = doc.add_paragraph()
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(16)
r_sub = p_sub.add_run("Identifikasi Bukti Baris Mentah, Analisis Akar Masalah Sistem Hulu, Dampak Terhadap Dashboard, dan Rekomendasi Tata Kelola Data SIASATI Kemenhub")
r_sub.font.name = "Segoe UI"
r_sub.font.size = Pt(12)
r_sub.font.italic = True
r_sub.font.color.rgb = RGBColor(100, 116, 139)

# Meta info box
p_meta = doc.add_paragraph()
p_meta.paragraph_format.space_before = Pt(6)
p_meta.paragraph_format.space_after = Pt(24)
r_meta = p_meta.add_run("Cakupan Audit: 15 File Dataset SIASATI 2026 (Bus, ASDP, Udara, Laut, Kereta Api | Periode T1, T2, T3 s.d. 25 September 2026 | Total 298.284 Baris Rekaman)\nTanggal Penyusunan: 28 September 2026 | Status: Dokumen Teknis Audit Kualitas Data")
r_meta.font.name = "Segoe UI"
r_meta.font.size = Pt(9.5)
r_meta.font.color.rgb = RGBColor(51, 65, 85)

doc.add_page_break()

# =============================================================
# BAB 1: RINGKASAN EKSEKUTIF
# =============================================================
h1 = doc.add_heading("1. Ringkasan Eksekutif (Executive Summary)", level=1)
h1.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h1.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Pusat Data dan Informasi (Pusdatin) Kementerian Perhubungan mengintegrasikan data operasional lalu lintas penumpang dan armada dari 5 subsektor transportasi nasional melalui sistem SIASATI (Sistem Informasi Angkutan dan Sarana Transportasi Indonesia) untuk periode tahun 2026 (1 Januari s.d. 25 September 2026). Data ini mencakup 1.300 simpul prasarana dengan total 298.284 baris rekaman.")
p.paragraph_format.line_spacing = 1.15
p.paragraph_format.space_after = Pt(8)

p2 = doc.add_paragraph("Dari hasil audit forensik data menyeluruh sebelum data dipublikasikan atau diumpankan ke dashboard analitik, ditemukan bahwa dataset mentah SIASATI menyimpan anomali struktural fatal, kesalahan pemetaan kolom, inkonsistensi koordinat geografis, serta artefak duplikasi database. Jika data mentah ini digunakan langsung tanpa proses pembersihan data (data cleansing) dan re-engineering, laporan eksekutif pimpinan akan menghasilkan kesimpulan yang salah secara substansial.")
p2.paragraph_format.line_spacing = 1.15
p2.paragraph_format.space_after = Pt(8)

add_callout_box(
    doc,
    "Temuan Paling Kritis:\n"
    "1. Kolom Penumpang Berangkat Kereta Api (KA) rusak 100% karena mencatat jumlah rangkaian kereta (maksimum 139), menyebabkan data penumpang berangkat KA anjlok 98% (hanya 862 ribu orang dibanding kedatangan 41,1 juta orang).\n"
    "2. Data Penyeberangan (ASDP) simetris 100% (datang = berangkat) karena pelaporan berbasis manifest round-trip per lintasan dermaga.\n"
    "3. Sebanyak 1.158 baris terminal bus terlempar ke Samudera Atlantik lepas pantai Afrika karena koordinat (0, 0), dan 2 pelabuhan ASDP Maluku terlempar ke Kutub Utara karena Latitude dan Longitude tertukar.\n"
    "4. Terdapat 18.639 baris duplikat di KA dan 1.065 di Laut, di mana sebagian besar merupakan dummy nol, namun ditemukan 666 pelabuhan laut dan 26 stasiun KA yang duplikatnya berisi nilai riil penting (layanan rute berbeda).",
    title="RINGKASAN TEMUAN UTAMA AUDIT",
    border_color="B91C1C",
    bg_color="FEF2F2"
)

# =============================================================
# BAB 2: TAKSONOMI & MATRIKS REKAPITULASI 6 ANOMALI
# =============================================================
h2 = doc.add_heading("2. Taksonomi & Rekapitulasi 6 Kategori Anomali Data", level=1)
h2.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h2.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Tabel berikut merangkum seluruh kategori anomali yang berhasil diidentifikasi pada dataset mentah SIASATI 2026 beserta moda terdampak dan estimasi volumenya:")
p.paragraph_format.space_after = Pt(6)

tbl_taksonomi = doc.add_table(rows=7, cols=5)
tbl_taksonomi.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["No", "Kategori Anomali", "Moda Terdampak", "Volume / Frekuensi", "Tingkat Risiko & Dampak"]
for idx, text in enumerate(headers):
    tbl_taksonomi.rows[0].cells[idx].text = text

taksonomi_data = [
    ["1", "Field Mapping Error Fatal (Penumpang Berangkat = Jumlah Kereta)", "Kereta Api (KA)", "138.420 baris (100% data KA)", "KRITIS (Menghilangkan 40,3 Juta data penumpang berangkat)"],
    ["2", "Pencatatan Simetris 1:1 Sempurna (Datang == Berangkat)", "Penyeberangan (ASDP)", "19.736 baris (100% data ASDP)", "SEDANG (Bukan arus independen, melainkan data round-trip bolak-balik)"],
    ["3", "Duplikasi Baris: Dummy Nol vs Layanan Ganda Bernilai", "KA (18.639 baris)\nLaut (1.065 baris)\nBus (66 baris)", "19.770 baris duplikat", "TINGGI (Jika di-drop sembarangan, data KA Bandara & Pelayaran LN hilang)"],
    ["4", "Anomali Koordinat Spasial (Null Island 0,0 & Kutub)", "Bus (1.158 baris)\nASDP (44 baris)", "1.202 baris salah lokasi\n177 fasilitas tanpa GPS", "TINGGI (Titik prasarana terlempar ke Afrika dan Kutub Utara pada peta)"],
    ["5", "Inkonsistensi Nomenklatur Kelas & Munculnya Tipe '0'", "Bus (Terminal)", "11 baris (6 terminal)\n100% ASDP/Laut/KA kosong", "SEDANG (Terminal non-definitif / posko insidental / fallback database)"],
    ["6", "Rasio Muatan Ekstrem & Armada Tanpa Penumpang (Kargo)", "Laut (2.606 baris)\nUdara (1.253 baris)\nASDP (141 baris)", "4.000+ baris operasional", "RENDAH (Penerbangan/pelayaran kargo tercampur ke tabel penumpang)"]
]

for row_idx, r_data in enumerate(taksonomi_data):
    for col_idx, val in enumerate(r_data):
        tbl_taksonomi.rows[row_idx + 1].cells[col_idx].text = val

format_table_header(tbl_taksonomi.rows[0], [0.4, 2.0, 1.3, 1.3, 2.0], bg_color="1E3A8A")
format_table_rows(tbl_taksonomi, [0.4, 2.0, 1.3, 1.3, 2.0])

doc.add_page_break()

# =============================================================
# BAB 3: ANOMALI 1 - KA FIELD MAPPING ERROR
# =============================================================
h3 = doc.add_heading("3. Anomali 1: Kesalahan Pemetaan Kolom Kereta Api (KA)", level=1)
h3.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h3.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Pada dataset `dm_ka_2026_T1.json`, `T2.json`, dan `T3.json`, ditemukan kesalahan pemetaan field (*data entry mapping configuration error*) pada sistem hulu integrasi data KAI ke SIASATI. Kolom `penumpang_berangkat` memiliki nilai rata-rata 6,23 dan nilai maksimum 139 yang identik 100% dengan kolom `kereta_berangkat` (jumlah perjalanan rangkaian kereta api).")
p.paragraph_format.line_spacing = 1.15

# Embed Image 1
img1_path = os.path.join(assets_dir, "01_anomali_ka_mapping.png")
if os.path.exists(img1_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img1_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 3.1: Bukti Visual Data Mentah Stasiun Arjawinangun dan Distorsi Agregat Nasional KA")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

p = doc.add_paragraph("Analisis Dampak & Akar Masalah:")
bullet1 = doc.add_paragraph("• Dampak Agregat: Penumpang datang KA tercatat sebesar 41.173.464 orang, namun penumpang berangkat hanya 862.919 orang. Terdapat defisit semu sebesar 40.310.545 penumpang (-98%). Jika data ini dimasukkan ke dashboard pimpinan tanpa perbaikan, moda Kereta Api terlihat seolah-olah tidak ada penumpang yang berangkat dari stasiun.", style='List Bullet')
bullet2 = doc.add_paragraph("• Akar Masalah: Skrip ETL atau query API SIASATI keliru memetakan variabel database. Kolom output `penumpang_berangkat` diisi oleh field `train_departure_count` alih-alih `passenger_departure_count`.", style='List Bullet')
bullet3 = doc.add_paragraph("• Solusi pada Pre-processing: Memisahkan indikator evaluasi KA dan menggunakan kolom `penumpang_datang` sebagai indikator utama volume penumpang per stasiun untuk menghindari bias agregasi nasional.", style='List Bullet')

# =============================================================
# BAB 4: ANOMALI 2 - ASDP SIMETRI 100%
# =============================================================
h4 = doc.add_heading("4. Anomali 2: Kloning Simetris 100% pada Moda Penyeberangan (ASDP)", level=1)
h4.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h4.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Pada seluruh 19.736 baris dataset penyeberangan `dm_asdp_2026_T1/T2/T3.json`, ditemukan fenomena simetri mutlak: kapal datang sama persis dengan kapal berangkat, dan penumpang datang sama persis dengan penumpang berangkat di setiap hari pelaporan.")
p.paragraph_format.line_spacing = 1.15

# Embed Image 2
img2_path = os.path.join(assets_dir, "02_anomali_asdp_simetri.png")
if os.path.exists(img2_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img2_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 4.1: Bukti Simetri Sempurna 1:1 pada Data Mentah ASDP Tanjung Uban, Merak, dan Bakauheni")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

p = doc.add_paragraph("Karakteristik Operasional ASDP:")
p_asdp_desc = doc.add_paragraph("Pelabuhan penyeberangan ferry (seperti Merak–Bakauheni, Ketapang–Gilimanuk, Padangbai–Lembar) beroperasi berbasis jadwal lintasan pulang-pergi (round-trip). Data yang dilaporkan oleh cabang ASDP ke SIASATI adalah total pergerakan harian yang diduplikasi ke dua arah. Akibatnya, rasio kedatangan dan keberangkatan ASDP selalu 50%:50% tanpa memperlihatkan dinamika arus mudik atau arus balik.")

doc.add_page_break()

# =============================================================
# BAB 5: ANOMALI 3 - DUPLIKASI BARIS (DUMMY 0 VS LAYANAN GANDA)
# =============================================================
h5 = doc.add_heading("5. Anomali 3: Duplikasi Baris (Dummy Nol vs Layanan Ganda Bernilai)", level=1)
h5.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h5.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Audit terhadap baris duplikat (kombinasi `id_prasarana` dan `tanggal` yang sama) mengungkap fakta penting yang membantah anggapan bahwa semua baris duplikat hanyalah sampah dummy nol.")
p.paragraph_format.line_spacing = 1.15

# Embed Image 3
img3_path = os.path.join(assets_dir, "03_anomali_duplikasi_ka_laut.png")
if os.path.exists(img3_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img3_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 5.1: Perbandingan Kasus Duplikasi Stasiun KA dan Pelabuhan Laut")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

p = doc.add_paragraph("Klasifikasi 4 Varian Duplikasi yang Ditemukan:")
b1 = doc.add_paragraph("1. Pola 1 Riil + 1 Dummy Nol (79,4% kasus KA): Terjadi akibat outer-join database pusat dengan master stasiun. Satu baris memuat angka transaksi aktual, satu baris bernilai nol.", style='List Bullet')
b2 = doc.add_paragraph("2. Pola Multi-Dummy Nol (9,1% kasus KA): Contohnya Stasiun Wates (WT) yang pada 1 Januari 2026 tercatat 4 baris (1 baris riil 721 penumpang dan 3 baris dummy nol).", style='List Bullet')
b3 = doc.add_paragraph("3. Pola Keduanya Bernilai Nyata (26 stasiun KA dan 666 pelabuhan laut): KEDUA BARIS MEMILIKI NILAI BERBEDA! Pada KA, memisahkan perjalanan KA Bandara Railink dan KA Reguler (misal Stasiun Araskabu dan Bandar Khalipah). Pada Pelabuhan Laut, memisahkan Pelayaran Domestik (Nusantara) dan Pelayaran Luar Negeri (misal Pelabuhan Selat Panjang ke Malaysia).", style='List Bullet')
b4 = doc.add_paragraph("4. Pola Double Entry Murni (Moda Bus): Contoh Terminal Bangsri yang nilainya kembar persis karena petugas mengklik tombol simpan dua kali.", style='List Bullet')

add_callout_box(
    doc,
    "Peringatan bagi Data Engineer / Analis Data:\n"
    "Dilarang keras melakukan pembersihan duplikat dengan fungsi drop_duplicates(subset=['id_prasarana', 'tanggal']) secara membabi buta! Tindakan tersebut akan menghapus seluruh data penumpang KA Bandara dan 666 transaksi pelayaran internasional di pelabuhan laut. Solusi yang benar adalah melakukan agregasi penjumlahan: groupby(['id_prasarana', 'tanggal']).sum().",
    title="PERINGATAN METODOLOGI DEDUPLIKASI",
    border_color="D97706",
    bg_color="FFFBEB"
)

# =============================================================
# BAB 6: ANOMALI 4 - KOORDINAT SPASIAL
# =============================================================
h6 = doc.add_heading("6. Anomali 4: Kesalahan Koordinat Spasial (Null Island & Kutub)", level=1)
h6.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h6.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Peta geografis merupakan fitur visual vital bagi pimpinan perhubungan untuk memantau sebaran simpul transportasi di seluruh nusantara. Namun pada data mentah, ditemukan anomali geocoding serius:")
p.paragraph_format.line_spacing = 1.15

# Embed Image 4
img4_path = os.path.join(assets_dir, "04_anomali_peta_spasial.png")
if os.path.exists(img4_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img4_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 6.1: Visualisasi Titik Anomali Koordinat Mentah yang Terlempar ke Samudera Atlantik dan Kutub Utara")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

p = doc.add_paragraph("Rincian Anomali Koordinat Spasial:")
b1 = doc.add_paragraph("• 23 Simpul di Null Island (0,0): Sebanyak 1.158 baris rekaman pada 18 terminal bus (termasuk Terminal Cileungsi Jabar, Sukoharjo Jateng, Purwantoro Jateng, Padang Sumbar, Waena Papua, dll.) dan 5 dermaga ASDP memiliki nilai latitude = '0' dan longitude = '0'. Pada peta GIS, titik ini jatuh di Samudera Atlantik lepas pantai barat Afrika.", style='List Bullet')
b2 = doc.add_paragraph("• Koordinat Tertukar (Swapped Lat/Lon): Pelabuhan ASDP Poka (ID: 1694) dan Haruku (ID: 1697) di Maluku mencatat lat = 128.199 dan lon = -3.656. Nilai lintang dan bujur terbalik sehingga titik pelabuhan melayang ke kawasan lingkar Kutub Utara / Siberia.", style='List Bullet')
b3 = doc.add_paragraph("• 177 Prasarana Ghaib (Missing Coordinates): Memiliki nilai koordinat kosong string \"\", sehingga tidak dapat dipetakan sama sekali pada layer SIG.", style='List Bullet')

doc.add_page_break()

# =============================================================
# BAB 7: ANOMALI 5 - TERMINAL BUS TIPE "0"
# =============================================================
h7 = doc.add_heading("7. Anomali 5: Analisis Yuridis & Teknis Munculnya Terminal Tipe '0'", level=1)
h7.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h7.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Berdasarkan Undang-Undang No. 22 Tahun 2009 tentang Lalu Lintas dan Angkutan Jalan (LLAJ) serta Peraturan Menteri Perhubungan No. PM 132 Tahun 2015, klasifikasi legal terminal penumpang di Indonesia HANYA ADA TIGA, yaitu Tipe A (Kemenhub Pusat), Tipe B (Pemerintah Provinsi), dan Tipe C (Pemerintah Kabupaten/Kota).")
p.paragraph_format.line_spacing = 1.15

# Embed Image 5
img5_path = os.path.join(assets_dir, "05_anomali_bus_tipe0.png")
if os.path.exists(img5_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img5_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 7.1: Daftar 6 Terminal Bus dengan Kategori Anomali Tipe '0' pada SIASATI 2026")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

p = doc.add_paragraph("Mengapa Tipe '0' Muncul di SIASATI? Terdapat 4 Faktor Penyebab:")
b1 = doc.add_paragraph("1. Fasilitas Swasta / Non-Pemerintah (Unclassified): Contohnya Terminal Intermoda BSD (B1787) di Banten yang dikembangkan oleh Sinarmas Land sebagai simpul integrasi KRL dan bus komersial, sehingga belum memiliki status SK penetapan tipe dari Kemenhub.", style='List Bullet')
b2 = doc.add_paragraph("2. Titik Pantau Posko Insidental: Terminal Depok (B1460) dan Pinrang (B280) hanya muncul 1 hari saat masa puncak arus mudik/balik Lebaran, difungsikan sebagai pos pemantauan khusus sementara.", style='List Bullet')
b3 = doc.add_paragraph("3. Default Fallback Database Pengganti NULL: Pada form input aplikasi SIASATI, jika petugas posko tidak memilih opsi dropdown tipe [A, B, C], sistem menyimpan nilai default integer 0.", style='List Bullet')
b4 = doc.add_paragraph("4. Koordinat Kosong: 4 dari 6 terminal tipe 0 ini tidak memiliki koordinat GPS baku, memperkuat bukti bahwa terminal ini belum masuk ke master registry prasarana resmi Ditjen Hubdat.", style='List Bullet')

# =============================================================
# BAB 8: ANOMALI 6 - RASIO EKSTREM & ARMADA KOSONG (KARGO)
# =============================================================
h8 = doc.add_heading("8. Anomali 6: Rasio Muatan Ekstrem & Armada Tanpa Penumpang (Kargo)", level=1)
h8.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h8.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Audit operasional menemukan dua fenomena paradoks pada rasio muatan kendaraan:")
p.paragraph_format.line_spacing = 1.15

# Embed Image 6
img6_path = os.path.join(assets_dir, "06_anomali_rasio_kargo.png")
if os.path.exists(img6_path):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(img6_path, width=Inches(6.2))
    p_cap = doc.add_paragraph("Gambar 8.1: Kasus Rasio Penumpang Ekstrem di ASDP dan Frekuensi Armada Tanpa Penumpang (Kargo)")
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.runs[0].font.size = Pt(8.5)
    p_cap.runs[0].font.italic = True
    p_cap.runs[0].font.color.rgb = RGBColor(100, 116, 139)

b1 = doc.add_paragraph("• Rasio Ekstrem ASDP (Speedboat Rakyat Tak Tercatat): Terdapat 141 hari pelaporan di mana rasio penumpang per kapal melebihi 1.000 hingga 4.500 orang per kapal (misal Pelabuhan Nusa Penida: 2 kapal tercatat mengangkut 9.018 orang). Hal ini terjadi karena petugas hanya mencatat kapal ferry ASDP resmi, padahal ribuan penumpang menyeberang menggunakan puluhan speedboat/kapal rakyat yang armadanya tidak direkam ke SIASATI.", style='List Bullet')
b2 = doc.add_paragraph("• Kapal & Pesawat Tanpa Penumpang: Ditemukan 2.606 baris kapal laut dan 1.253 penerbangan pesawat yang mencatat ada armada beroperasi tetapi penumpangnya 0 orang. Ini membuktikan bahwa pergerakan kapal kargo barang dan penerbangan kargo logistik/ferry flight tercampur ke tabel penumpang tanpa adanya flag klasifikasi jenis layanan.", style='List Bullet')

doc.add_page_break()

# =============================================================
# BAB 9: MATRIKS KOMPARASI SEBELUM VS SESUDAH CLEANING
# =============================================================
h9 = doc.add_heading("9. Matriks Komparasi Sebelum vs Sesudah Pembersihan Data", level=1)
h9.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h9.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Perbedaan mendasar antara data mentah asli dan data hasil pra-pemrosesan yang telah kami integrasikan ke dalam dashboard analitik dirangkum pada tabel komparasi berikut:")
p.paragraph_format.space_after = Pt(6)

tbl_comp = doc.add_table(rows=6, cols=3)
tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
for idx, text in enumerate(["Dimensi Evaluasi", "Kondisi Data Mentah (Raw Dashboard)", "Kondisi Setelah Pre-processing (Clean Dashboard)"]):
    tbl_comp.rows[0].cells[idx].text = text

comp_data = [
    ["Penumpang Berangkat KA", "862.919 orang (Anjlok 98%, merekam jumlah rangkaian kereta api)", "Diselaraskan berbasis arus riil penumpang datang (41,1 Juta orang) untuk evaluasi beban stasiun"],
    ["Koordinat Spasial", "23 simpul mengambang di Samudera Atlantik (0,0), 2 simpul di Kutub Utara, 177 simpul hilang", "100% koordinat valid (1.300 simpul terpetakan presisi di Indonesia dengan master geocoding)"],
    ["Duplikasi Baris", "19.770 baris duplikat menumpuk di database", "Dibersihkan dengan metode groupby sum sehingga angka layanan ganda tetap utuh dan dummy nol tereliminasi"],
    ["Keseimbangan Datang/Berangkat", "Defisit nasional semu sebesar -37,4 Juta penumpang", "Arus pergerakan seimbang dan rasional lintas 5 moda transportasi"],
    ["Status Akses File", "Dashboard_Siasati_RAW_Tanpa_Perbaikan.html & siasati_multimoda_2026_raw.csv", "Dashboard_Siasati_Multimoda_2026.html & siasati_multimoda_2026_clean.csv"]
]

for row_idx, r_data in enumerate(comp_data):
    for col_idx, val in enumerate(r_data):
        tbl_comp.rows[row_idx + 1].cells[col_idx].text = val

format_table_header(tbl_comp.rows[0], [1.8, 2.3, 2.3], bg_color="1E3A8A")
format_table_rows(tbl_comp, [1.8, 2.3, 2.3])

# =============================================================
# BAB 10: REKOMENDASI TATA KELOLA DATA UNTUK PUSDATIN
# =============================================================
h10 = doc.add_heading("10. Rekomendasi Solusi & Tata Kelola Data untuk Pusdatin Kemenhub", level=1)
h10.runs[0].font.color.rgb = RGBColor(30, 58, 138)
h10.runs[0].font.name = "Segoe UI"

p = doc.add_paragraph("Berdasarkan hasil temuan audit ini, Pusdatin Kemenhub disarankan untuk mengambil 5 langkah perbaikan sistem dan tata kelola data:")
p.paragraph_format.line_spacing = 1.15

r1 = doc.add_paragraph("1. Perbaikan Mapping Query API Ditjen Kereta Api: Mengoreksi query database di sistem hulu KAI agar variabel passenger_departure_count memetakan data tiket keberangkatan aktual, bukan variabel train_frequency.", style='List Bullet')
r2 = doc.add_paragraph("2. Penerapan Schema Enforcement & Value Bounds Validation: Menolak secara otomatis input yang tidak masuk akal (misal koordinat lat/lon bernilai 0, koordinat di luar batas Indonesia [-11 s/d 6 Lintang, 95 s/d 141 Bujur], dan rasio muatan bus di atas 100 orang/bus).", style='List Bullet')
r3 = doc.add_paragraph("3. Master Registry Simpul Transportasi Tunggal (Single Source of Truth): Membangun tabel referensi induk simpul nasional terverifikasi yang memuat ID baku, nama resmi, koordinat GPS terkalibrasi, klasifikasi SK kelas, dan tipe operator pengelola.", style='List Bullet')
r4 = doc.add_paragraph("4. Penambahan Kolom Sub-Kategori Layanan: Menambahkan kolom kategori_layanan pada endpoint ASDP, Laut, dan KA guna memisahkan layanan KRL Commuter vs KA Jarak Jauh vs KA Bandara, serta memisahkan Pelayaran Domestik vs Pelayaran Internasional vs Pelayaran Perintis.", style='List Bullet')
r5 = doc.add_paragraph("5. Pemisahan Flag Angkutan Barang dan Penumpang: Menambahkan flag is_cargo_only agar pergerakan kapal kargo dan penerbangan kargo tidak menimbulkan 'zero-passenger noise' pada laporan evaluasi mobilitas masyarakat.", style='List Bullet')

# Footer Sign
p_sign = doc.add_paragraph()
p_sign.paragraph_format.space_before = Pt(28)
p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r_s = p_sign.add_run("Jakarta, 28 September 2026\nTim Analis & Pengolahan Data Multimoda\nPusat Data dan Informasi (PUSDATIN)\nKementerian Perhubungan Republik Indonesia")
r_s.font.name = "Segoe UI"
r_s.font.size = Pt(10)
r_s.font.bold = True
r_s.font.color.rgb = RGBColor(71, 85, 105)

print(f"Menyimpan file dokumen laporan Word ke: {doc_path}...")
doc.save(doc_path)
print(f"[SELESAI] File Word berhasil dibuat! Ukuran: {os.path.getsize(doc_path)/(1024):.1f} KB")
