"""Render empirical national urgency groups, separately from scenario additions."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
GROUPS = [
    ("controlled", "Terkendali", "#10b981"),
    ("medium", "Padat", "#f59e0b"),
    ("high", "Tinggi / Kritis", "#f97316"),
    ("critical", "Sangat Kritis", "#ef4444"),
    ("insufficient", "Data tidak cukup", "#94a3b8"),
]


def _format(value, digits=2):
    return "—" if value is None else f"{value:.{digits}f}".replace(".", ",")


def generate_infographic(bundle_path=None, output_path=None):
    bundle_path = Path(bundle_path) if bundle_path is not None else BASE_DIR / "scripts" / "mobility_data_bundle.json"
    output_path = Path(output_path) if output_path is not None else BASE_DIR / "persentil_load_factor_2026.png"
    with bundle_path.open(encoding="utf-8") as stream:
        bundle = json.load(stream)
    items = bundle["simpul_recommendations"]
    metadata = bundle["simpul_scenario_metadata"]
    valid = [
        item for item in items
        if item["scenarioValid"] and item["loadRatio"] is not None
        and np.isfinite(item["loadRatio"])
    ]
    ratios = np.array([item["loadRatio"] for item in valid], dtype=float)
    thresholds = metadata["thresholds"]
    counts = metadata["counts"]
    total = metadata["validCount"] + metadata["insufficientCount"]
    small_volume = metadata["smallVolumeThreshold"]

    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cbd5e1"
    fig = plt.figure(figsize=(14, 10), dpi=300, facecolor="white")
    grid = GridSpec(3, 1, height_ratios=[0.95, 1.4, 1.25], hspace=0.55)
    fig.subplots_adjust(top=0.88, bottom=0.13)
    fig.text(0.06, 0.965, "PERSENTIL URGENSI & SKENARIO ARMADA BERANGKAT", fontsize=17, weight="bold", color="#0f172a")
    fig.text(
        0.06, 0.938,
        f"{total:,} simpul nasional • {metadata['validCount']:,} skenario valid • "
        f"{metadata['insufficientCount']:,} data tidak cukup",
        fontsize=11, color="#64748b",
    )
    fig.text(
        0.06, 0.915,
        f"Baseline median {metadata['baselineStart']}–{metadata['baselineEnd']} • "
        f"Puncak Penumpang Berangkat {metadata['peakStart']}–{metadata['peakEnd']}",
        fontsize=9, color="#64748b",
    )

    # Actual classifications, not assumed percentile-sized groups: ties and the
    # small-volume exception mean empirical group counts need not be 50/25/15/10.
    ax_counts = fig.add_subplot(grid[0])
    positions = np.arange(len(GROUPS))
    bars = ax_counts.bar(positions, [counts[key] for key, _, _ in GROUPS], color=[color for _, _, color in GROUPS])
    ax_counts.set_xticks(positions, [label for _, label, _ in GROUPS], fontsize=9)
    ax_counts.set_ylabel("Jumlah simpul", fontsize=9)
    ax_counts.set_title("Klasifikasi empiris nasional (ambang tetap pada seluruh filter)", loc="left", fontsize=11, weight="bold")
    ax_counts.set_ylim(0, max(1, max(counts.values(), default=0)) * 1.25)
    for bar, (key, _, _) in zip(bars, GROUPS):
        count = counts[key]
        share = 100 * count / total if total else 0
        ax_counts.text(bar.get_x() + bar.get_width() / 2, count, f"{count:,} ({share:.1f}%)", ha="center", va="bottom", fontsize=9)
    ax_counts.spines[["top", "right"]].set_visible(False)

    ax_hist = fig.add_subplot(grid[1])
    ax_hist.set_facecolor("#f8fafc")
    ax_hist.grid(axis="y", linestyle=":", alpha=0.6)
    if ratios.size:
        lower, upper = ratios.min(), ratios.max()
        if lower == upper:
            lower, upper = lower / 2, upper * 2
        bins = np.geomspace(lower, upper, min(45, max(1, len(ratios))) + 1)
        ax_hist.set_xscale("log")
        ax_hist.hist(ratios, bins=bins, color="#64748b", edgecolor="white", zorder=3)
        for key, color in (("p50", "#047857"), ("p75", "#b45309"), ("p90", "#b91c1c")):
            threshold = thresholds[key]
            if threshold is not None:
                ax_hist.axvline(threshold, color=color, linestyle="--", linewidth=1.5, label=f"{key.upper()} = {_format(threshold)}x")
        ax_hist.legend(fontsize=9)
    else:
        ax_hist.text(0.5, 0.5, "Belum ada rasio valid; ambang persentil tidak tersedia.", transform=ax_hist.transAxes, ha="center", va="center", fontsize=10)
    ax_hist.set_title("Distribusi rasio valid saja — tanpa rasio sintetis atau pembulatan awal", loc="left", fontsize=11, weight="bold")
    ax_hist.set_xlabel("Rasio Puncak / Rasio Normal — skala logaritmik (Penumpang Berangkat per Armada Berangkat)", fontsize=9)
    ax_hist.set_ylabel("Jumlah simpul", fontsize=9)

    ax_cards = fig.add_subplot(grid[2])
    ax_cards.set_xlim(0, 1)
    ax_cards.set_ylim(0, 1)
    ax_cards.axis("off")
    conditions = {
        "controlled": f"Rasio < P50 atau Penumpang\nBerangkat puncak < {small_volume}",
        "medium": "P50 ≤ rasio < P75",
        "high": "P75 ≤ rasio < P90",
        "critical": "Rasio ≥ P90",
    }
    for index, (key, label, color) in enumerate(GROUPS[:4]):
        x = 0.008 + index * 0.25
        width = 0.234
        ax_cards.add_patch(patches.FancyBboxPatch((x, 0.02), width, 0.94, boxstyle="round,pad=0.008", facecolor="white", edgecolor=color, linewidth=1.5))
        ax_cards.text(x + width / 2, 0.87, label.upper(), ha="center", fontsize=10, weight="bold", color=color)
        ax_cards.text(x + 0.012, 0.72, conditions[key], fontsize=8.5, color="#334155", va="top")
        ax_cards.text(x + 0.012, 0.49, f"{counts[key]:,} simpul • urgensi relatif", fontsize=8.5, color="#64748b")
        examples = sorted((item for item in valid if item["statusKey"] == key), key=lambda item: item["pnpPuncak"], reverse=True)[:2]
        lines = [f"{item['name'][:26]}\n{_format(item['loadRatio'])}x • skenario +{_format(item['pctTambah'])}%" for item in examples]
        ax_cards.text(x + 0.012, 0.37, "\n\n".join(lines) if lines else "Tidak ada simpul pada kelompok ini.", fontsize=7.5, va="top", color="#0f172a")

    fig.text(0.06, 0.085, "Persentil hanya mengurutkan urgensi, bukan menetapkan persentase penambahan.", fontsize=10, weight="bold", color="#0f172a")
    fig.text(0.06, 0.062, "Skenario: requiredArm = ceil(Penumpang Berangkat puncak × median Armada Berangkat / median Penumpang Berangkat).", fontsize=8.5, color="#475569")
    fig.text(0.06, 0.041, "Tambahan = max(0, requiredArm − Armada Berangkat pada tanggal puncak); persentase = 100 × tambahan / Armada Berangkat puncak.", fontsize=8.5, color="#475569")
    fig.text(0.06, 0.020, "Target beban historis, bukan kebutuhan armada fisik atau bukti kapasitas nominal. Data tidak cukup dikecualikan dari rasio dan skenario.", fontsize=8.5, color="#475569")
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Infografis berhasil diperbarui: {output_path}")


if __name__ == "__main__":
    generate_infographic()
