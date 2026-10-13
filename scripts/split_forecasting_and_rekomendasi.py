import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Sidebar
    old_sidebar_btn = """          <!-- TAB 8: FORECASTING NATARU 2026/2027 -->
          <button onclick="switchTab('tab-forecasting', 'Proyeksi & Prediksi Nataru 2026/2027', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
            <span class="truncate font-semibold text-indigo-700 dark:text-indigo-400">Proyeksi Nataru 2026</span>
          </button>"""

    new_sidebar_btns = """          <!-- TAB 8: FORECASTING NATARU 2026/2027 -->
          <button onclick="switchTab('tab-forecasting', 'Proyeksi & Prediksi Nataru 2026/2027', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
            <span class="truncate font-semibold text-indigo-700 dark:text-indigo-400">Forecasting</span>
          </button>

          <!-- TAB 9: REKOMENDASI PENAMBAHAN ARMADA (1.010 SIMPUL) -->
          <button onclick="switchTab('tab-rekomendasi', 'Rekomendasi Penambahan Armada (1.010 Simpul)', this)" class="nav-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent transition-all text-left">
            <span class="w-1.5 h-1.5 rounded-full bg-violet-600 shrink-0"></span>
            <span class="truncate font-semibold text-violet-700 dark:text-violet-400">Rekomendasi</span>
          </button>"""

    if old_sidebar_btn not in content:
        raise Exception(f"Cannot find old_sidebar_btn in {filename}")
    content = content.replace(old_sidebar_btn, new_sidebar_btns, 1)

    # 2. Extract and swap sections
    simpul_marker = "<!-- Section: Interactive Per-Prasarana / Simpul Simulation Panel -->"
    fc_tbl_marker = "<!-- Table: Daily Forecast Detail (100 Days) -->"
    tentang_marker = "<!-- ========================================================= -->\n      <!-- TAB 9: INFORMASI, METODOLOGI & KAMUS RUMUS DASHBOARD"
    
    pos_simpul = content.find(simpul_marker)
    pos_fc_tbl = content.find(fc_tbl_marker)
    pos_tentang = content.find(tentang_marker)
    
    if pos_simpul == -1 or pos_fc_tbl == -1 or pos_tentang == -1:
        raise Exception(f"Cannot find content markers in {filename}: {pos_simpul}, {pos_fc_tbl}, {pos_tentang}")

    # Section before simpul
    prefix = content[:pos_simpul]
    
    # Simpul section HTML
    simpul_html = content[pos_simpul:pos_fc_tbl].strip()
    
    # Forecast table HTML (from pos_fc_tbl to end of tab-forecasting)
    between_fc_and_tentang = content[pos_fc_tbl:pos_tentang]
    
    # In between_fc_and_tentang, find the closing `</div>\n\n      </div>`
    end_tab_fc_match = re.search(r'</div>\s*</div>\s*$', between_fc_and_tentang.strip())
    if not end_tab_fc_match:
        raise Exception(f"Cannot find closing divs in between_fc_and_tentang in {filename}")
    
    # Strip the last `</div>` which closes tab-forecasting
    last_div_idx = between_fc_and_tentang.rfind('</div>')
    second_last_div_idx = between_fc_and_tentang[:last_div_idx].rfind('</div>')
    
    fc_tbl_html = between_fc_and_tentang[:second_last_div_idx + 6].strip()
    suffix = content[pos_tentang:]

    # Build new tab structure
    new_content_block = f"""{fc_tbl_html}

      </div>

      <!-- ========================================================= -->
      <!-- TAB 9: REKOMENDASI PENAMBAHAN ARMADA (1.010 SIMPUL)        -->
      <!-- ========================================================= -->
      <div id="tab-rekomendasi" class="tab-content hidden space-y-5">
        
        {simpul_html}

      </div>

      """

    content = prefix + new_content_block + suffix

    # 3. Update switchTab JavaScript
    old_switch_tab = """    if (targetId === 'tab-forecasting') {
      renderForecastWorkspace();
    }
    if (targetId === 'tab-tentang-data') {"""

    new_switch_tab = """    if (targetId === 'tab-forecasting') {
      renderForecastWorkspace();
    }
    if (targetId === 'tab-rekomendasi') {
      renderSimpulSimulation();
    }
    if (targetId === 'tab-tentang-data') {"""

    if old_switch_tab not in content:
        raise Exception(f"Cannot find old_switch_tab in {filename}")
    content = content.replace(old_switch_tab, new_switch_tab, 1)

    # 4. In updateDashboardMetricAndDirection, ensure renderSimpulSimulation() is called
    old_update_metric = """  // 10. Update Tab 7 (Leaflet Spatial Map)
  renderSpatialMapNodes();
}"""

    new_update_metric = """  // 10. Update Tab 7 (Leaflet Spatial Map)
  renderSpatialMapNodes();

  // 11. Update Tab 9 (Rekomendasi Simpul)
  renderSimpulSimulation();
}"""

    if old_update_metric in content:
        content = content.replace(old_update_metric, new_update_metric, 1)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully processed {filename}")

process_file('index.html')
process_file('Dashboard_Mobilitas_Nasional_2026.html')
print("All files updated successfully.")
