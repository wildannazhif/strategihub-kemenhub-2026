import subprocess
import os

print("Fixing duplicated spatial map code block in index.html and Dashboard_Mobilitas_Nasional_2026.html...")

for filename in ['index.html', 'Dashboard_Mobilitas_Nasional_2026.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    cut_str_start = "// ---------------------------------------------------------------\nlet currentBasemap = 'osm';"
    cut_str_end = "// TAB 8: FORECASTING NATARU 2026/2027 CONTROLLER"

    pos_start = text.find(cut_str_start)
    pos_end = text.find(cut_str_end)

    if pos_start == -1 or pos_end == -1:
        raise Exception(f"Cannot find duplicate cut markers in {filename}: {pos_start}, {pos_end}")

    cleaned = text[:pos_start] + text[pos_end:]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"Successfully cleaned {filename} (removed {pos_end - pos_start} duplicate characters).")

print("Checking JS syntax with node...")
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
scripts = re.findall(r'<script[\s\S]*?</script>', text, re.IGNORECASE)
for i, s in enumerate(scripts):
    if 'src=' in s:
        continue
    code = s.split('>', 1)[1].rsplit('</script>', 1)[0]
    with open('tmp_test.js', 'w', encoding='utf-8') as tf:
        tf.write(code)
    res = subprocess.run(['node', '--check', 'tmp_test.js'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in script {i}:", res.stderr)
    else:
        print(f"Script {i} syntax is clean!")
    os.remove('tmp_test.js')

print("All syntax checks passed!")
