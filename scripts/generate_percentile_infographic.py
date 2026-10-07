import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

simpuls = d['simpul_recommendations']
ratios = np.array([s['loadRatio'] for s in simpuls])

p50 = float(np.percentile(ratios, 50))
p75 = float(np.percentile(ratios, 75))
p90 = float(np.percentile(ratios, 90))

fig = plt.figure(figsize=(14, 9.4), dpi=300, facecolor='#ffffff')
gs = GridSpec(3, 1, height_ratios=[0.85, 1.25, 1.35], hspace=0.35)

# --- 1. HEADER & PIRAMIDA PERSENTIL ---
ax_bar = fig.add_subplot(gs[0])
ax_bar.set_facecolor('#ffffff')
ax_bar.set_xlim(0, 100)
ax_bar.set_ylim(0, 1)
ax_bar.axis('off')

fig.text(0.06, 0.958, 'DISTRIBUSI PERSENTIL LONJAKAN LOAD FACTOR 2026', fontsize=18, fontweight='bold', color='#0f172a')
fig.text(0.06, 0.934, 'Analisis Rasio Kepadatan Penumpang terhadap Armada (LF Puncak / LF Biasa) • 1.010 Simpul Prasarana Nasional', fontsize=11, color='#64748b')

# Segment 1: Terkendali (0-50%)
rect1 = patches.FancyBboxPatch((0, 0.35), 50, 0.46, boxstyle="square,pad=0", facecolor='#10b981', alpha=0.9, edgecolor='none')
ax_bar.add_patch(rect1)
ax_bar.text(25, 0.58, '50% SIMPUL NASIONAL (505 Simpul)\nStatus: Terkendali (+5% Armada)', ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')

# Segment 2: Padat (50-75%)
rect2 = patches.FancyBboxPatch((50, 0.35), 25, 0.46, boxstyle="square,pad=0", facecolor='#f59e0b', alpha=0.9, edgecolor='none')
ax_bar.add_patch(rect2)
ax_bar.text(62.5, 0.58, '25% (253 Simpul)\nPadat (+10%)', ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')

# Segment 3: Kritis (75-90%)
rect3 = patches.FancyBboxPatch((75, 0.35), 15, 0.46, boxstyle="square,pad=0", facecolor='#f97316', alpha=0.9, edgecolor='none')
ax_bar.add_patch(rect3)
ax_bar.text(82.5, 0.58, '15% (151)\nKritis (+15%)', ha='center', va='center', color='white', fontsize=9, fontweight='bold')

# Segment 4: Sangat Kritis (90-100%)
rect4 = patches.FancyBboxPatch((90, 0.35), 10, 0.46, boxstyle="square,pad=0", facecolor='#ef4444', alpha=0.95, edgecolor='none')
ax_bar.add_patch(rect4)
ax_bar.text(95, 0.58, 'Top 10%\n+20%', ha='center', va='center', color='white', fontsize=9, fontweight='bold')

# Threshold markers below bar
ax_bar.text(0, 0.12, 'Min: 0,1x', ha='left', va='center', fontsize=9.5, color='#64748b', fontweight='bold')
ax_bar.text(50, 0.12, f'P50 (Median) = {p50:.2f}x'.replace('.', ','), ha='center', va='center', fontsize=10, color='#0f172a', fontweight='bold')
ax_bar.plot([50, 50], [0.32, 0.83], color='#0f172a', lw=1.2, ls='--')

ax_bar.text(75, 0.12, f'P75 = {p75:.2f}x'.replace('.', ','), ha='center', va='center', fontsize=10, color='#0f172a', fontweight='bold')
ax_bar.plot([75, 75], [0.32, 0.83], color='#0f172a', lw=1.2, ls='--')

ax_bar.text(90, 0.12, f'P90 = {p90:.2f}x'.replace('.', ','), ha='center', va='center', fontsize=10, color='#ef4444', fontweight='bold')
ax_bar.plot([90, 90], [0.32, 0.83], color='#ef4444', lw=1.5, ls='--')

ax_bar.text(100, 0.90, f'Max: {ratios.max():.1f}x'.replace('.', ','), ha='right', va='center', fontsize=9.5, color='#64748b', fontweight='bold')

# --- 2. HISTOGRAM DISTRIBUSI LOG & DENSITAS EMPIRIS ---
ax_hist = fig.add_subplot(gs[1])
ax_hist.set_facecolor('#f8fafc')
ax_hist.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1', zorder=0)

clipped = np.clip(ratios, 0, 7)
n, bins, patches_list = ax_hist.hist(clipped, bins=45, range=(0, 7), edgecolor='#ffffff', linewidth=0.7, zorder=3)

for b_left, b_right, patch in zip(bins[:-1], bins[1:], patches_list):
    b_mid = (b_left + b_right) / 2
    if b_mid < p50:
        patch.set_facecolor('#10b981')
        patch.set_alpha(0.75)
    elif b_mid < p75:
        patch.set_facecolor('#f59e0b')
        patch.set_alpha(0.75)
    elif b_mid < p90:
        patch.set_facecolor('#f97316')
        patch.set_alpha(0.8)
    else:
        patch.set_facecolor('#ef4444')
        patch.set_alpha(0.85)

ax_hist.axvline(p50, color='#047857', linestyle='--', linewidth=1.5, zorder=5, label=f'P50 Median ({p50:.2f}x)'.replace('.', ','))
ax_hist.axvline(p75, color='#b45309', linestyle='--', linewidth=1.5, zorder=5, label=f'P75 Persentil 75 ({p75:.2f}x)'.replace('.', ','))
ax_hist.axvline(p90, color='#b91c1c', linestyle='--', linewidth=1.8, zorder=5, label=f'P90 Ambang Darurat ({p90:.2f}x)'.replace('.', ','))

ax_hist.set_xlabel('Lonjakan Beban Armada (Faktor Pengali: LF Puncak / LF Biasa)', fontsize=10.5, fontweight='bold', color='#334155')
ax_hist.set_ylabel('Jumlah Simpul Prasarana', fontsize=10.5, fontweight='bold', color='#334155')
ax_hist.set_title('Distribusi Frekuensi Kepadatan Armada Seluruh Indonesia (Skala 0x s.d. 7x lipat)', fontsize=11, fontweight='bold', color='#1e293b', loc='left')
ax_hist.legend(frameon=True, facecolor='white', edgecolor='#e2e8f0', fontsize=9, loc='upper right')
ax_hist.set_xlim(0, 7)

# --- 3. KARTU REKOMENDASI DAN CONTOH SIMPUL LAPANGAN ---
ax_cards = fig.add_subplot(gs[2])
ax_cards.set_xlim(0, 1)
ax_cards.set_ylim(0, 1)
ax_cards.axis('off')

card_w = 0.222
card_gap = 0.037
cards_data = [
    {
        'title': 'TERKENDALI (< P50)',
        'subtitle': f'Lonjakan: < {p50:.2f}x lipat'.replace('.', ','),
        'color': '#10b981',
        'badge': '+5% Armada (Siaga)',
        'count': '505 Simpul (50%)',
        'desc': 'Lonjakan beban di bawah median.\nArmada harian mampu menampung\npenumpang.',
        'examples': 'Simpul perintis lokal, rute reguler stabil.'
    },
    {
        'title': 'PADAT (P50 - P75)',
        'subtitle': f'Lonjakan: {p50:.2f}x – {p75:.2f}x'.replace('.', ','),
        'color': '#f59e0b',
        'badge': '+10% Armada',
        'count': '253 Simpul (25%)',
        'desc': 'Mulai terjadi antrean peron.\nPerlu perbantuan armada pada jam sibuk\npagi dan sore.',
        'examples': 'Juanda (1,9x), Gambir (1,8x), DPS (1,6x).'
    },
    {
        'title': 'TINGGI / KRITIS (P75-P90)',
        'subtitle': f'Lonjakan: {p75:.2f}x – {p90:.2f}x'.replace('.', ','),
        'color': '#f97316',
        'badge': '+15% Armada',
        'count': '151 Simpul (15%)',
        'desc': 'Beban berat signifikan!\nAntrean boarding mengular, buffer zone\nkendaraan mulai penuh.',
        'examples': 'Pasar Senen (2,8x), Ketapang (2,6x), Poto Tano.'
    },
    {
        'title': 'SANGAT KRITIS (≥ P90)',
        'subtitle': f'Lonjakan: ≥ {p90:.2f}x lipat'.replace('.', ','),
        'color': '#ef4444',
        'badge': '+20% Armada (Darurat)',
        'count': '101 Simpul (Top 10%)',
        'desc': 'Krisis kapasitas akut!\nPenumpang melonjak drastis tak sebanding\ndengan armada yang beroperasi.',
        'examples': 'Bakauheni (4,3x), Gilimanuk (4,2x), Merak (3,8x).'
    }
]

for idx, c in enumerate(cards_data):
    x_pos = idx * (card_w + card_gap)
    box = patches.FancyBboxPatch((x_pos, 0.02), card_w, 0.95, boxstyle="round,pad=0.015,rounding_size=0.025",
                                 facecolor='#ffffff', edgecolor=c['color'], linewidth=1.6)
    ax_cards.add_patch(box)
    
    header_strip = patches.FancyBboxPatch((x_pos, 0.81), card_w, 0.16, boxstyle="round,pad=0.01,rounding_size=0.02",
                                          facecolor=c['color'], edgecolor='none')
    ax_cards.add_patch(header_strip)
    ax_cards.text(x_pos + card_w/2, 0.88, c['title'], ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
    
    ax_cards.text(x_pos + 0.012, 0.73, c['subtitle'], fontsize=9, fontweight='bold', color='#1e293b')
    ax_cards.text(x_pos + 0.012, 0.65, f"Cakupan: {c['count']}", fontsize=8.2, color='#64748b')
    
    ax_cards.text(x_pos + card_w/2, 0.54, c['badge'], ha='center', va='center', fontsize=9, fontweight='bold', color=c['color'],
                  bbox=dict(boxstyle="round,pad=0.35", fc='#f8fafc', ec=c['color'], lw=1))
    
    ax_cards.text(x_pos + 0.012, 0.44, c['desc'], fontsize=7.8, color='#334155', va='top', linespacing=1.35)
    ax_cards.plot([x_pos + 0.012, x_pos + card_w - 0.012], [0.19, 0.19], color='#e2e8f0', lw=1)
    ax_cards.text(x_pos + 0.012, 0.14, 'Contoh Simpul Riil:', fontsize=7.5, fontweight='bold', color='#64748b')
    ax_cards.text(x_pos + 0.012, 0.05, c['examples'], fontsize=7.3, color='#0f172a', va='bottom')

output_path = 'persentil_load_factor_2026.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()
print(f'Infografis berhasil diperbarui: {output_path}')
