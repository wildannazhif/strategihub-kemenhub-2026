import json
import re
import os

print("Implementing Spatial Choropleth Heatmap with Provincial Boundaries...")

# 1. Load bundle with province_geojson
with open('scripts/mobility_data_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

bundle_json_str = json.dumps(bundle, ensure_ascii=False)
print("Bundle loaded, size:", len(bundle_json_str) / 1024, "KB")

new_spatial_js = """// ---------------------------------------------------------------
// TAB 7: LEAFLET SPATIAL MAP (GIS) WITH PROVINCIAL CHOROPLETH HEATMAP
// ---------------------------------------------------------------
let currentSpatialScale = 'all'; // all, top10, top20, top30, top50, pareto80, pareto90
let spatialChoroplethGroup = null;
let showMapHeatmap = true;
let showMapNodes = true;

function normalizeProvinceName(p) {
  if (!p) return '';
  p = p.trim();
  if (p === 'D.I Aceh' || p === 'DI Aceh' || p === 'Aceh') return 'Aceh';
  if (p === 'D.I. Yogyakarta' || p === 'DI Yogyakarta' || p === 'D.I Yogyakarta' || p === 'DIY' || p === 'Daerah Istimewa Yogyakarta') return 'Daerah Istimewa Yogyakarta';
  if (p.toUpperCase() === 'SULAWESI SELATAN') return 'Sulawesi Selatan';
  return p;
}

function getBasemapConfig() {
  return {
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    maxZoom: 18
  };
}

function getHeatmapColor(val, maxVal, isDark) {
  if (!val || val <= 0 || maxVal <= 0) {
    return { color: isDark ? '#334155' : '#cbd5e1', fillOpacity: 0.15 };
  }
  const r = val / maxVal;
  // Sequential Heatmap Gradient: Sky -> Cyan -> Emerald -> Amber -> Red (Puncak)
  if (r < 0.05) {
    return { color: '#38bdf8', fillOpacity: isDark ? 0.40 : 0.35 };
  } else if (r < 0.15) {
    return { color: '#06b6d4', fillOpacity: isDark ? 0.48 : 0.42 };
  } else if (r < 0.35) {
    return { color: '#10b981', fillOpacity: isDark ? 0.58 : 0.52 };
  } else if (r < 0.65) {
    return { color: '#f59e0b', fillOpacity: isDark ? 0.68 : 0.62 };
  } else {
    return { color: '#ef4444', fillOpacity: isDark ? 0.78 : 0.72 };
  }
}

function initSpatialMap() {
  if (spatialMap) return;

  const baseConfig = getBasemapConfig();

  spatialMap = L.map('spatialMapCanvas', {
    center: [-2.2, 117.5],
    zoom: 5,
    minZoom: 4,
    maxZoom: 18,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(spatialMap);

  mapTileLayer = L.tileLayer(baseConfig.url, {
    attribution: baseConfig.attr,
    maxZoom: baseConfig.maxZoom
  }).addTo(spatialMap);

  // Layer Group Order: Choropleth Heatmap (bawah) -> Simpul Markers (atas)
  spatialChoroplethGroup = L.layerGroup().addTo(spatialMap);
  spatialMarkerGroup = L.layerGroup().addTo(spatialMap);

  const legend = L.control({ position: 'bottomleft' });
  legend.onAdd = function() {
    const div = L.DomUtil.create('div', 'p-3 rounded-lg bg-white/95 dark:bg-slate-900/95 backdrop-blur border border-slate-200 dark:border-slate-800 text-[11px] font-sans shadow-lg space-y-2.5 max-w-[220px]');
    div.innerHTML = `
      <!-- Section 1: Heatmap Wilayah -->
      <div>
        <div class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 mb-1">
          <span class="w-2.5 h-2.5 rounded-sm bg-gradient-to-r from-sky-400 via-emerald-400 to-rose-500"></span>
          <span>Heatmap Wilayah:</span>
        </div>
        <div class="space-y-1 text-[10px]">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span>Intensitas:</span>
            <span class="font-semibold text-slate-700 dark:text-slate-300">Rendah ➔ Puncak</span>
          </div>
          <div class="h-2 w-full rounded-sm bg-gradient-to-r from-sky-400 via-cyan-400 via-emerald-400 via-amber-400 to-rose-600"></div>
          <div class="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>&lt;5%</span><span>15%</span><span>35%</span><span>65%+</span>
          </div>
        </div>
      </div>

      <!-- Section 2: Titik Simpul Moda -->
      <div class="border-t border-slate-200 dark:border-slate-700 pt-2">
        <div class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 mb-1">
          <span class="w-2 rounded-full bg-emerald-500"></span>
          <span>Titik Simpul per Moda:</span>
        </div>
        <div class="space-y-0.5 text-[10px]">
          <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Udara (257)</span></div>
          <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Kereta Api (193)</span></div>
          <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-green-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Bus (139)</span></div>
          <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-purple-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">ASDP (158)</span></div>
          <div class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-600 shrink-0"></span><span class="text-slate-600 dark:text-slate-300">Laut (267)</span></div>
        </div>
      </div>
    `;
    return div;
  };
  legend.addTo(spatialMap);

  renderSpatialMapNodes();
}

function updateMapTheme() {
  if (!spatialMap || !mapTileLayer) return;
  // Basemap OpenStreetMap (OSM) standar konsisten di tema gelap maupun terang
  renderSpatialMapChoropleth();
}

function toggleMapLayer(type) {
  if (type === 'heatmap') {
    showMapHeatmap = !showMapHeatmap;
    const btn = document.getElementById('toggle-layer-heatmap');
    if (btn) {
      btn.classList.toggle('bg-white', showMapHeatmap);
      btn.classList.toggle('dark:bg-slate-900', showMapHeatmap);
      btn.classList.toggle('text-slate-900', showMapHeatmap);
      btn.classList.toggle('dark:text-white', showMapHeatmap);
      btn.classList.toggle('shadow-xs', showMapHeatmap);
      btn.classList.toggle('text-slate-500', !showMapHeatmap);
      btn.classList.toggle('opacity-60', !showMapHeatmap);
    }
    renderSpatialMapChoropleth();
  } else if (type === 'nodes') {
    showMapNodes = !showMapNodes;
    const btn = document.getElementById('toggle-layer-nodes');
    if (btn) {
      btn.classList.toggle('bg-white', showMapNodes);
      btn.classList.toggle('dark:bg-slate-900', showMapNodes);
      btn.classList.toggle('text-slate-900', showMapNodes);
      btn.classList.toggle('dark:text-white', showMapNodes);
      btn.classList.toggle('shadow-xs', showMapNodes);
      btn.classList.toggle('text-slate-500', !showMapNodes);
      btn.classList.toggle('opacity-60', !showMapNodes);
    }
    renderSpatialMapNodes();
  }
}

function setSpatialScaleFilter(scale) {
  currentSpatialScale = scale;
  const select = document.getElementById('select-spatial-scale');
  if (select && select.value !== scale) select.value = scale;
  renderSpatialMapNodes();
}

function renderSpatialMapChoropleth() {
  if (!spatialChoroplethGroup) return;
  spatialChoroplethGroup.clearLayers();

  if (!showMapHeatmap) return;

  const geo = DATA.province_geojson;
  if (!geo || !geo.features) return;

  const sortKey = getHubMetricKey();
  const isPnp = currentMetric === 'pnp';
  const unit = isPnp ? 'penumpang' : 'trip armada';
  const isDark = document.documentElement.classList.contains('dark');

  // 1. Agregasi volume per provinsi dari DATA.spatial_nodes sesuai filter aktif
  const provStats = {};
  let maxProvVol = 0;
  let nationalVol = 0;

  DATA.spatial_nodes.forEach(n => {
    if (currentSpatialModa !== 'ALL' && n.m !== currentSpatialModa) return;
    const pNorm = normalizeProvinceName(n.p);
    if (!pNorm) return;
    if (!provStats[pNorm]) {
      provStats[pNorm] = { vol: 0, count: 0, modas: {} };
    }
    const val = n[sortKey] || 0;
    provStats[pNorm].vol += val;
    provStats[pNorm].count += 1;
    provStats[pNorm].modas[n.m] = (provStats[pNorm].modas[n.m] || 0) + val;
    nationalVol += val;
  });

  Object.values(provStats).forEach(s => {
    if (s.vol > maxProvVol) maxProvVol = s.vol;
  });

  // 2. Render Choropleth GeoJSON Layer
  const geoLayer = L.geoJSON(geo, {
    style: function(feature) {
      const provName = normalizeProvinceName(feature.properties.PROVINSI);
      const stat = provStats[provName] || { vol: 0 };
      const c = getHeatmapColor(stat.vol, maxProvVol, isDark);
      return {
        fillColor: c.color,
        fillOpacity: c.fillOpacity,
        color: isDark ? '#475569' : '#ffffff',
        weight: 1.2,
        dashArray: ''
      };
    },
    onEachFeature: function(feature, layer) {
      const provName = normalizeProvinceName(feature.properties.PROVINSI);
      const stat = provStats[provName] || { vol: 0, count: 0, modas: {} };
      const sharePct = nationalVol > 0 ? (stat.vol / nationalVol * 100).toFixed(1) : '0';

      let domModa = '-';
      let maxMVal = 0;
      if (stat.modas) {
        Object.entries(stat.modas).forEach(([m, v]) => {
          if (v > maxMVal) { maxMVal = v; domModa = m; }
        });
      }

      layer.on('mouseover', function(e) {
        this.setStyle({
          weight: 2.5,
          color: '#1d4ed8',
          fillOpacity: Math.min(0.9, (this.options.fillOpacity || 0.5) + 0.18)
        });
      });
      layer.on('mouseout', function(e) {
        geoLayer.resetStyle(this);
      });

      const tooltipHtml = `
        <div class="p-1 text-xs font-sans space-y-1">
          <div class="font-bold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-700 pb-0.5">${feature.properties.PROVINSI}</div>
          <div class="text-[11px] text-slate-700 dark:text-slate-300">
            Intensitas: <strong class="text-indigo-600 dark:text-indigo-400 font-mono">${numFmt(stat.vol)}</strong> ${unit} (${sharePct}%)
          </div>
          <div class="text-[10px] text-slate-500">
            Simpul: <strong>${stat.count} titik</strong> • Moda Utama: <strong>${domModa}</strong>
          </div>
        </div>
      `;
      layer.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.96 });
    }
  });

  spatialChoroplethGroup.addLayer(geoLayer);
}

function renderSpatialMapNodes() {
  // Render Choropleth Heatmap Wilayah
  renderSpatialMapChoropleth();

  if (!spatialMarkerGroup) return;
  spatialMarkerGroup.clearLayers();

  if (!showMapNodes) return;

  const sortKey = getHubMetricKey();
  const isPnp = currentMetric === 'pnp';

  // 1. Ambil kandidat dengan koordinat dan filter moda aktif
  const pool = DATA.spatial_nodes.filter(n => {
    if (!n.has_coords) return false;
    if (currentSpatialModa !== 'ALL' && n.m !== currentSpatialModa) return false;
    return true;
  });

  // Urutkan simpul dari volume tertinggi ke terendah berdasarkan metrik aktif
  pool.sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0));

  const totalPoolVol = pool.reduce((acc, n) => acc + (n[sortKey] || 0), 0);

  // 2. Filter berdasarkan skala / ranking / pangsa pasar
  let nodes = pool;
  if (currentSpatialScale === 'top10') {
    nodes = pool.slice(0, 10);
  } else if (currentSpatialScale === 'top20') {
    nodes = pool.slice(0, 20);
  } else if (currentSpatialScale === 'top30') {
    nodes = pool.slice(0, 30);
  } else if (currentSpatialScale === 'top50') {
    nodes = pool.slice(0, 50);
  } else if (currentSpatialScale === 'pareto80') {
    let cum = 0;
    const threshold = totalPoolVol * 0.8;
    nodes = [];
    for (const n of pool) {
      nodes.push(n);
      cum += (n[sortKey] || 0);
      if (cum >= threshold) break;
    }
  } else if (currentSpatialScale === 'pareto90') {
    let cum = 0;
    const threshold = totalPoolVol * 0.9;
    nodes = [];
    for (const n of pool) {
      nodes.push(n);
      cum += (n[sortKey] || 0);
      if (cum >= threshold) break;
    }
  }

  const displayedVol = nodes.reduce((acc, n) => acc + (n[sortKey] || 0), 0);
  const sharePct = totalPoolVol > 0 ? (displayedVol / totalPoolVol * 100) : 100;

  // 3. Perbarui teks badge informasi
  const badgeEl = document.getElementById('badge-spatial-count');
  if (badgeEl) {
    const countStr = numFmt(nodes.length);
    const pctStr = decFmt(sharePct, 1);
    if (currentSpatialScale === 'all') {
      badgeEl.innerText = `● ${countStr} Terpetakan (100%)`;
    } else {
      badgeEl.innerText = `● ${countStr} Simpul (${pctStr}% Pangsa)`;
    }
  }

  // 4. Render marker lingkaran Leaflet (ukuran dot rapi dan presisi: min 3.2px, max 8px agar tidak bertumpuk seismik di Jakarta)
  const maxMetricVal = DATA.spatial_nodes.reduce((max, node) => Math.max(max, (node[sortKey] || 0)), 1);
  const isDark = document.documentElement.classList.contains('dark');

  nodes.forEach((n, rankIdx) => {
    const val = n[sortKey] || 0;
    // Ukuran titik proporsional elegan (3.2px s/d 7.5px) agar tidak meluas seperti gempa
    const ratio = Math.min(1, Math.max(0, val / maxMetricVal));
    const minR = 3.2;
    const maxR = 7.5;
    const radius = val > 0 ? (minR + Math.pow(ratio, 0.45) * (maxR - minR)) : 2.5;
    const color = COLOR[n.m] || '#64748b';
    const isTop10 = rankIdx < 10;

    const marker = L.circleMarker([n.lat, n.lon], {
      radius: radius,
      fillColor: color,
      color: isTop10 ? '#f59e0b' : '#ffffff',
      weight: isTop10 ? 1.5 : 0.8,
      opacity: 1.0,
      fillOpacity: 0.92
    });

    // Efek hover interaktif
    marker.on('mouseover', function() {
      this.setStyle({ weight: 2.2, fillOpacity: 1.0, radius: radius + 2.0 });
      this.bringToFront();
    });
    marker.on('mouseout', function() {
      this.setStyle({ weight: isTop10 ? 1.5 : 0.8, fillOpacity: 0.92, radius: radius });
    });

    const rankBadge = rankIdx < 50 
      ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold ${isTop10 ? 'bg-amber-100 text-amber-900 border border-amber-300 dark:bg-amber-950 dark:text-amber-200' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'}">Peringkat #${rankIdx + 1}</span>` 
      : '';
    const shareOfTotal = totalPoolVol > 0 ? decFmt((val / totalPoolVol * 100), 2) + '%' : '-';

    const popupHtml = `
      <div class="p-3 text-xs font-sans space-y-2 max-w-[280px]">
        <div class="flex items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-700 pb-1.5">
          <span class="font-bold text-slate-900 dark:text-white truncate">${n.nama}</span>
          <span class="px-1.5 py-0.2 rounded text-[10px] font-bold text-white shrink-0" style="background-color: ${color}">${n.m}</span>
        </div>
        <div class="flex items-center justify-between text-[11px] text-slate-500">
          <span>${n.p} • Tipe: ${n.tipe}</span>
          ${rankBadge}
        </div>
        <div class="p-2 rounded bg-slate-50 dark:bg-slate-800 space-y-1 text-[11px] font-mono">
          <div class="flex justify-between ${sortKey === 'pnp' ? 'font-bold text-indigo-600 dark:text-indigo-400' : ''}">
            <span>Total Penumpang:</span><span>${numFmt(n.pnp)}</span>
          </div>
          <div class="flex justify-between ${sortKey === 'p_dat' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}">
            <span>↳ Pnp Datang:</span><span>${numFmt(n.p_dat)}</span>
          </div>
          <div class="flex justify-between ${sortKey === 'p_brg' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}">
            <span>↳ Pnp Berangkat:</span><span>${numFmt(n.p_brg)}</span>
          </div>
          <div class="border-t border-slate-200 dark:border-slate-700 pt-1 flex justify-between ${sortKey === 'arm' ? 'font-bold text-indigo-600 dark:text-indigo-400' : ''}">
            <span>Total Armada:</span><span>${numFmt(n.arm)}</span>
          </div>
          <div class="flex justify-between ${sortKey === 'a_dat' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}">
            <span>↳ Armada Datang:</span><span>${numFmt(n.a_dat)}</span>
          </div>
          <div class="flex justify-between ${sortKey === 'a_brg' ? 'font-bold text-indigo-600 dark:text-indigo-400' : 'text-slate-500'}">
            <span>↳ Armada Berangkat:</span><span>${numFmt(n.a_brg)}</span>
          </div>
          <div class="border-t border-slate-200 dark:border-slate-700 pt-1 flex justify-between font-semibold text-emerald-600 dark:text-emerald-400">
            <span>Pangsa terhadap Total:</span><span>${shareOfTotal}</span>
          </div>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    marker.addTo(spatialMarkerGroup);
  });
}

function filterSpatialModa(moda, btn) {
  currentSpatialModa = moda;
  document.querySelectorAll('.map-moda-btn').forEach(b => {
    b.classList.remove('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
    b.classList.add('font-medium', 'text-slate-600', 'dark:text-slate-400');
  });
  btn.classList.add('active', 'font-semibold', 'bg-slate-900', 'dark:bg-slate-100', 'text-white', 'dark:text-slate-900', 'shadow-xs');
  btn.classList.remove('font-medium', 'text-slate-600', 'dark:text-slate-400');
  renderSpatialMapNodes();
}

function resetSpatialMap() {
  if (!spatialMap) return;
  spatialMap.setView([-2.2, 117.5], 5);
}

function toggleMapFullscreen() {
  const card = document.getElementById('spatial-map-card');
  const txt = document.getElementById('txt-map-fs');
  if (!card) return;

  const isFs = card.classList.toggle('fixed');
  card.classList.toggle('inset-0', isFs);
  card.classList.toggle('z-50', isFs);
  card.classList.toggle('p-4', isFs);

  const canvas = document.getElementById('spatialMapCanvas');
  if (canvas) {
    if (isFs) {
      canvas.className = 'w-full h-full rounded-md relative z-10';
      if (txt) txt.innerText = 'Tutup Layar Penuh';
    } else {
      canvas.className = 'w-full h-[calc(100vh-250px)] min-h-[660px] rounded-md relative z-10';
      if (txt) txt.innerText = 'Layar Penuh';
    }
  }

  setTimeout(() => {
    if (spatialMap) spatialMap.invalidateSize();
  }, 150);
}"""

for filename in ['index.html', 'Dashboard_Mobilitas_Nasional_2026.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update const DATA
    pos1 = html.find("const DATA = {")
    pos_numfmt = html.find("const numFmt =", pos1)
    if pos1 == -1 or pos_numfmt == -1:
        raise Exception(f"Cannot find const DATA block in {filename}: {pos1}, {pos_numfmt}")

    # The end of DATA is right before `const numFmt =` (accounting for `;\n`)
    pos_semicolon = html.rfind(";", pos1, pos_numfmt)
    if pos_semicolon == -1:
        raise Exception(f"Cannot find semicolon ending const DATA in {filename}")

    html = html[:pos1] + "const DATA = " + bundle_json_str + ";\n" + html[pos_numfmt:]

    # 2. Update Header description and add Layer Toggle Buttons in #tab-spatial-map
    old_desc = "Sebaran geografis 1.014 simpul transportasi nasional terpetakan di seluruh wilayah Indonesia (ukuran lingkaran proporsional terhadap volume penumpang)"
    new_desc = "Heatmap intensitas mobilitas batas wilayah 38 provinsi terpadu dengan sebaran 1.014 titik simpul transportasi nasional (Udara, KA, Bus, ASDP, dan Laut)"
    html = html.replace(old_desc, new_desc, 1)

    old_toolbar_spot = """              <!-- Map Direction Toggle -->
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="map-dir-tot" onclick="setGlobalDirection('tot')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Dua Arah</button>
                <button id="map-dir-dat" onclick="setGlobalDirection('dat')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Datang</button>
                <button id="map-dir-brg" onclick="setGlobalDirection('brg')" class="px-2 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Berangkat</button>
              </div>"""

    new_toolbar_spot = """              <!-- Map Direction Toggle -->
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="map-dir-tot" onclick="setGlobalDirection('tot')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Dua Arah</button>
                <button id="map-dir-dat" onclick="setGlobalDirection('dat')" class="px-2 py-1 rounded text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all">Datang</button>
                <button id="map-dir-brg" onclick="setGlobalDirection('brg')" class="px-2 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all">Berangkat</button>
              </div>

              <!-- Layer Display Toggles: Heatmap Batas Wilayah & Titik Simpul -->
              <div class="inline-flex rounded-md border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                <button id="toggle-layer-heatmap" onclick="toggleMapLayer('heatmap')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all flex items-center gap-1.5" title="Tampilkan / Sembunyikan Heatmap Batas Wilayah 38 Provinsi">
                  <span class="w-2 h-2 rounded-xs bg-rose-500"></span>
                  <span>Heatmap Wilayah</span>
                </button>
                <button id="toggle-layer-nodes" onclick="toggleMapLayer('nodes')" class="px-2.5 py-1 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs transition-all flex items-center gap-1.5" title="Tampilkan / Sembunyikan Titik Simpul Transportasi">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span>Titik Simpul</span>
                </button>
              </div>"""

    if old_toolbar_spot in html:
        html = html.replace(old_toolbar_spot, new_toolbar_spot, 1)

    # 3. Update spatial map JS block
    m1 = html.find('// TAB 7: LEAFLET SPATIAL MAP CONTROLLER')
    m2 = html.find('// TAB 8: FORECASTING NATARU 2026/2027 CONTROLLER')
    if m1 == -1 or m2 == -1:
        raise Exception(f"Cannot find spatial map JS block markers in {filename}: {m1}, {m2}")

    # Start from `// ---------------------------------------------------------------` right before m1
    start_pos = html.rfind('// ---------------------------------------------------------------', 0, m1)
    end_pos = html.rfind('// ---------------------------------------------------------------', m1, m2)

    html = html[:start_pos] + new_spatial_js + "\n\n" + html[end_pos:]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Successfully updated {filename}")

print("Completed spatial choropleth heatmap implementation!")
