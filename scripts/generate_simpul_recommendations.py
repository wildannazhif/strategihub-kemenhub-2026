"""Historical Normal Ratio scenarios and surgical dashboard data synchronization."""

import json
import math
import re
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "siasati_multimoda_2026.csv"
BASELINE_START = "2026-01-01"
BASELINE_END = "2026-03-12"
PEAK_START = "2026-03-13"
PEAK_END = "2026-03-29"
SMALL_VOLUME_THRESHOLD = 100

CUSTOM_ACTIONS = {
    ('ASDP', 'Bakauheni'): 'Pola operasi TBB (Tiba Bongkar Berangkat) tanpa memuat di Bakauheni untuk menguras antrean arus balik ke Jawa.',
    ('ASDP', 'Merak'): 'Percepatan port clearance (<45 mnt), aktivasi buffer zone di rest area KM 43/68, pengerahan kapal feri kapasitas besar (>5.000 GT).',
    ('UDARA', 'Soekarno Hatta'): 'Optimalisasi runway capacity (Runway 1, 2, 3), izin extra flight malam (red-eye flight), buffer time ground handling.',
    ('ASDP', 'Gilimanuk'): 'Penerapan skema bongkar cepat di Gilimanuk, rekayasa antrean di Cekik, serta pengerahan kapal perbantuan kapasitas besar.',
    ('ASDP', 'Ketapang'): 'Pengoperasian dermaga ponton & MB cadangan, pengerahan kapal kapasitas muat kendaraan roda empat/bus wisata.',
    ('UDARA', 'I Gusti Ngurah Rai'): 'Perpanjangan operasional bandara 24 jam penuh, slot extra flight dini hari, serta pengaturan ketat alokasi parking stand.',
    ('LAUT', 'Batam'): 'Penambahan trip fast ferry lintas Batam–Singapura/Johor dan rute domestik antarpulau Kepri.',
    ('BUS', 'Purabaya'): 'Penyiagaan armada bus pariwisata cadangan sebagai bus perbantuan angkutan malam hari rute Trans-Jawa.',
    ('BUS', 'Giwangan'): 'Sistem sirkulasi peron jalur cepat, buffer parkir bus cadangan di lingkar selatan Jogja, antisipasi lonjakan wisata.',
    ('UDARA', 'Juanda'): 'Penambahan slot extra flight koridor Surabaya–Jakarta/Balikpapan/Makassar dan percepatan turnaround time.',
    ('KA', 'PASARSENEN'): 'Pengoperasian KLB KA Tambahan Nataru relasi Pasar Senen–Yogyakarta/Solo/Surabaya/Malang.',
    ('BUS', 'Purboyo'): 'Manajemen peron transit lintas Madiun–Surabaya/Solo dan pengaturan antrean bus keluar tol Madiun.',
    ('BUS', 'Kertonegoro'): 'Pengendalian ritme kedatangan bus AKAP koridor tengah Jawa Timur–Jawa Tengah agar tidak menumpuk.',
    ('UDARA', 'Sultan Hasanuddin'): 'Penyediaan extra flight transit penghubung Indonesia Barat ke Indonesia Timur (Papua/Maluku).',
    ('KA', 'GAMBIR'): 'Penambahan stamformasi (panjang 10-12 kereta) dan jadwal KA Argo Lawu/Dwipangga Tambahan.',
    ('KA', 'YOGYAKARTA'): 'Penambahan frekuensi KRL Commuter Line Solo–Yogya serta integrasi KA Bandara YIA di jam padat.',
    ('UDARA', 'Kualanamu'): 'Optimalisasi extra flight rute Medan–Jakarta/Batam/Banda Aceh dan integrasi jadwal Kereta Bandara Railink.',
    ('ASDP', 'Poto Tano'): 'Percepatan jadwal trip kapal lintasan Lombok–Sumbawa dan penyiagaan kapal perbantuan saat arus balik.',
    ('KA', 'KCJB - HALIM'): 'Penambahan slot perjalanan Whoosh hingga headway 20–30 menit dan integrasi feeder LRT Jabodebek.',
    ('LAUT', 'Tanjung Balai Karimun'): 'Koordinasi KSOP untuk kelayakan armada laut, jaket keselamatan, dan jadwal penyeberangan reguler.',
    ('LAUT', 'Nusa Penida'): 'Pengawasan kapasitas muat fast boat rute Sanur–Nusa Penida dan pengetatan SOP keselamatan cuaca laut.',
    ('ASDP', 'Kayangan'): 'Pola operasi kapal cepat dan pemisahan antrean kendaraan roda dua dengan angkutan logistik berat.',
    ('BUS', 'Indihiang'): 'Penyiagaan armada bus AKAP cadangan koridor Priangan Timur menuju Jabodetabek dan Jawa Tengah.',
    ('KA', 'KCJB - PADALARANG'): 'Sinkronisasi jam keberangkatan KA Feeder Padalarang–Bandung agar tidak terjadi penumpukan penumpang.',
    ('KA', 'PURWOKERTO'): 'Penambahan gerbong KA lintas Kroya–Purwokerto–Cirebon dan penyiagaan lokomotif cadangan di dipo.',
    ('BUS', 'Pakupatan'): 'Penataan peron keluar-masuk bus dekat gerbang tol Serang Timur guna mencegah kemacetan arteri.',
    ('UDARA', 'Sultan Aji Muhammad Sulaiman Sepinggan'): 'Penambahan frekuensi extra flight rute Balikpapan–Surabaya/Jakarta dan dukungan mobilitas logistik IKN.',
    ('UDARA', 'Hang Nadim'): 'Extra flight rute Batam–Medan/Padang/Jakarta guna menampung lonjakan perantau lintas pulau.',
    ('KA', 'SURABAYA GUBENG'): 'Penambahan KA Sancaka Tambahan (Surabaya–Yogyakarta) dan KA Pasundan Tambahan (Surabaya–Kiaracondong).',
    ('BUS', 'Giri Adipura'): 'Pemberangkatan teratur konvoi bus AKAP rute Wonogiri–Jabodetabek dan ramp check kelayakan rem/ban.'
}

def normalize_province(value):
    """Use the province spellings used by the pre-Lebaran baseline."""
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.upper() == "SULAWESI SELATAN":
        return "Sulawesi Selatan"
    if value in {"D.I. Yogyakarta", "DI Yogyakarta", "D.I Yogyakarta", "DIY"}:
        return "D.I Yogyakarta"
    return value


def _number(value):
    if pd.isna(value) or not math.isfinite(value):
        return None
    return int(value) if value == int(value) else float(value)


def _labels(moda, name):
    labels = {
        "UDARA": ("✈ Udara", "Pesawat Jet Komersial"),
        "BUS": ("🚌 Bus AKAP", "Armada Bus Antar Kota"),
        "ASDP": ("⛴ ASDP Feri", "Kapal Ro-Ro Feri"),
        "LAUT": ("🚢 Laut", "Kapal Penumpang & Cepat"),
    }
    if moda == "KA":
        upper_name = name.upper()
        if "KCJB" in upper_name or "WHOOSH" in upper_name:
            sarana_type = "Kereta Cepat Whoosh"
        elif "KRL" in upper_name or "COMMUTER" in upper_name:
            sarana_type = "KRL Commuter Line"
        else:
            sarana_type = "Rangkaian Kereta Api"
        return "🚆 Kereta Api", sarana_type
    return labels.get(moda, (moda, "Armada Berangkat"))


STATUS = {
    "critical": ("Sangat Kritis", "bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300"),
    "high": ("Tinggi / Kritis", "bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-300"),
    "medium": ("Padat", "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300"),
    "controlled": ("Terkendali", "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"),
    "insufficient": ("Data tidak cukup", "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"),
}


def build_recommendations(df, existing_items=None):
    """Return node scenarios and national metadata from raw departure records.

    Medians use observed baseline dates, including observed zero values. The
    passenger peak and its Armada Berangkat always come from the same date.
    Percentiles classify urgency only; they never prescribe an addition.
    """
    raw = df.drop_duplicates().copy()
    raw["tanggal"] = pd.to_datetime(raw["tanggal"]).dt.strftime("%Y-%m-%d")
    raw["provinsi"] = raw["provinsi"].map(normalize_province)
    raw["nama_prasarana"] = raw["nama_prasarana"].fillna("").astype(str)
    metrics = ["penumpang_berangkat", "armada_berangkat"]
    for column in metrics:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")

    id_keys = ["tanggal", "moda", "id_prasarana"]
    grouped = raw.groupby(id_keys, dropna=False, sort=False)
    daily_ids = grouped[metrics].sum(min_count=1).join(
        grouped[["nama_prasarana", "provinsi"]].first()
    ).reset_index()
    node_keys = ["moda", "nama_prasarana", "provinsi"]
    daily = daily_ids.groupby(
        node_keys + ["tanggal"], as_index=False, dropna=False
    )[metrics].sum(min_count=1)
    baseline = daily[daily["tanggal"].between(BASELINE_START, BASELINE_END)]
    medians = baseline.groupby(node_keys, dropna=False)[metrics].median()
    peak = daily[daily["tanggal"].between(PEAK_START, PEAK_END)]
    maxima = peak.groupby(node_keys, dropna=False)[metrics].max()
    active = maxima[
        (maxima["penumpang_berangkat"] > 0) & (maxima["armada_berangkat"] > 0)
    ].index
    peak = peak.set_index(node_keys).loc[active].reset_index()
    peak = peak.sort_values(
        ["penumpang_berangkat", "tanggal"] + node_keys,
        ascending=[False, True, True, True, True], kind="stable",
    ).drop_duplicates(node_keys, keep="first").reset_index(drop=True)

    existing = {
        (item["moda"], item["name"], normalize_province(item.get("prov", ""))): item
        for item in (existing_items or [])
    }
    items = []
    for index, row in peak.iterrows():
        key = tuple(row[column] for column in node_keys)
        moda, name, province = key
        old = existing.get(key, {})
        normal = medians.loc[key] if key in medians.index else None
        pb = _number(normal["penumpang_berangkat"]) if normal is not None else None
        ab = _number(normal["armada_berangkat"]) if normal is not None else None
        pp = _number(row["penumpang_berangkat"])
        ap = _number(row["armada_berangkat"])
        reasons = []
        if pb is None or pb <= 0:
            reasons.append("Median Penumpang Berangkat baseline tidak tersedia atau tidak positif")
        if ab is None or ab <= 0:
            reasons.append("Median Armada Berangkat baseline tidak tersedia atau tidak positif")
        if ap is None or ap <= 0:
            reasons.append("Armada Berangkat pada tanggal puncak tidak tersedia atau tidak positif")
        valid = not reasons
        normal_ratio = pb / ab if pb is not None and pb > 0 and ab is not None and ab > 0 else None
        peak_ratio = pp / ap if ap is not None and ap > 0 else None
        load_ratio = peak_ratio / normal_ratio if valid else None
        required = additional = total = percentage = None
        if valid:
            # Exact rational ceiling avoids 21 / (7 / 10) becoming 31.
            target = Fraction(str(pp)) * Fraction(str(ab)) / Fraction(str(pb))
            required = math.ceil(target)
            additional = max(0, required - ap)
            total = ap + additional
            percentage = 100 * additional / ap
        moda_label, sarana_type = _labels(moda, name)
        items.append({
            "id": f"simpul_{index + 1}",
            "name": name, "prov": province, "moda": moda,
            "modaLabel": old.get("modaLabel", moda_label),
            "saranaType": old.get("saranaType", sarana_type),
            "saranaUnit": old.get("saranaUnit", "Armada Berangkat per hari"),
            "pnpBiasa": pb, "armBiasa": ab, "pnpPuncak": pp, "armPuncak": ap,
            "peakDate": row["tanggal"],
            "lfBiasa": normal_ratio, "lfPuncak": peak_ratio, "loadRatio": load_ratio,
            "scenarioValid": valid, "invalidReason": "; ".join(reasons),
            "requiredArm": required, "addArm": additional, "totalArm": total,
            "pctTambah": percentage,
            "fieldAction": old.get("fieldAction", CUSTOM_ACTIONS.get(
                (moda, name), "Optimalisasi jadwal armada dan monitoring lonjakan penumpang."
            )),
        })

    ratios = [item["loadRatio"] for item in items if item["scenarioValid"]]
    thresholds = dict.fromkeys(("p50", "p75", "p90"))
    if ratios:
        thresholds.update(zip(thresholds, map(float, np.percentile(ratios, [50, 75, 90]))))
    counts = dict.fromkeys(STATUS, 0)
    for item in items:
        if not item["scenarioValid"]:
            status = "insufficient"
        elif item["pnpPuncak"] < SMALL_VOLUME_THRESHOLD:
            status = "controlled"
        elif item["loadRatio"] >= thresholds["p90"]:
            status = "critical"
        elif item["loadRatio"] >= thresholds["p75"]:
            status = "high"
        elif item["loadRatio"] >= thresholds["p50"]:
            status = "medium"
        else:
            status = "controlled"
        item["statusKey"] = status
        item["statusText"], item["statusBadge"] = STATUS[status]
        counts[status] += 1
    metadata = {
        "baselineStart": BASELINE_START, "baselineEnd": BASELINE_END,
        "peakStart": PEAK_START, "peakEnd": PEAK_END,
        "validCount": len(ratios), "insufficientCount": counts["insufficient"],
        "smallVolumeThreshold": SMALL_VOLUME_THRESHOLD,
        "thresholds": thresholds, "counts": counts,
    }
    return items, metadata


def replace_json_fields(text, updates, start=0):
    """Replace only selected top-level JSON values, preserving all other bytes."""
    decoder = json.JSONDecoder()
    value, object_end = decoder.raw_decode(text, start)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    cursor = start + 1
    spans = {}
    while True:
        while text[cursor].isspace():
            cursor += 1
        if text[cursor] == "}":
            closing = cursor
            break
        key, cursor = decoder.raw_decode(text, cursor)
        while text[cursor].isspace():
            cursor += 1
        if text[cursor] != ":":
            raise ValueError("Expected a JSON object key separator")
        cursor += 1
        while text[cursor].isspace():
            cursor += 1
        value_start = cursor
        _, cursor = decoder.raw_decode(text, cursor)
        spans[key] = (value_start, cursor)
        while text[cursor].isspace():
            cursor += 1
        if text[cursor] == ",":
            cursor += 1
        elif text[cursor] != "}":
            raise ValueError("Expected a JSON object field separator")
    replacements = []
    additions = []
    for key, replacement in updates.items():
        encoded = json.dumps(replacement, ensure_ascii=False, allow_nan=False)
        if key in spans:
            replacements.append((*spans[key], encoded))
        else:
            additions.append(json.dumps(key) + ": " + encoded)
    if additions:
        replacements.append((closing, closing, (", " if value else "") + ", ".join(additions)))
    for left, right, replacement in sorted(replacements, reverse=True):
        text = text[:left] + replacement + text[right:]
    return text


def synchronize_recommendations(items, metadata, base_dir=BASE_DIR):
    """Update the two scenario fields only, in both bundles and root pages."""
    base_dir = Path(base_dir)
    updates = {
        "simpul_recommendations": items,
        "simpul_scenario_metadata": metadata,
    }
    targets = [
        (base_dir / "scripts" / "mobility_data_bundle.json", False),
        (base_dir / "data" / "mobility_data_bundle.json", False),
        (base_dir / "index.html", True),
        (base_dir / "Dashboard_Mobilitas_Nasional_2026.html", True),
    ]
    pending = []
    for path, embedded in targets:
        with path.open("r", encoding="utf-8", newline="") as stream:
            text = stream.read()
        if embedded:
            declaration = re.search(r"\bconst\s+DATA\s*=\s*", text)
            if declaration is None:
                raise ValueError(f"const DATA declaration not found in {path}")
            start = declaration.end()
        else:
            start = len(text) - len(text.lstrip())
        pending.append((path, replace_json_fields(text, updates, start)))
    for path, text in pending:
        with path.open("w", encoding="utf-8", newline="") as stream:
            stream.write(text)


def generate_recommendations():
    with (BASE_DIR / "scripts" / "mobility_data_bundle.json").open(encoding="utf-8") as stream:
        existing = json.load(stream).get("simpul_recommendations", [])
    items, metadata = build_recommendations(
        pd.read_csv(RAW_CSV, low_memory=False), existing
    )
    synchronize_recommendations(items, metadata)
    print(
        f"Skenario diperbarui: {metadata['validCount']} simpul valid, "
        f"{metadata['insufficientCount']} simpul dengan data tidak cukup."
    )


if __name__ == "__main__":
    generate_recommendations()
