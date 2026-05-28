#!/usr/bin/env python3

import subprocess
import re
import sys
import pandas as pd
from pathlib import Path

# ==========================
# INPUT VALIDATION
# ==========================

if len(sys.argv) != 3:
    print("Usage: extract_cis_controls.py <CIS_Benchmark.pdf> <output.xlsx>")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
output_xlsx = sys.argv[2]

if not pdf_path.exists():
    print(f"PDF not found: {pdf_path}")
    sys.exit(1)

# ==========================
# STEP 1: EXTRACT PDF TEXT
# ==========================

try:
    text = subprocess.check_output(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        universal_newlines=True
    )
except subprocess.CalledProcessError:
    print("Failed to extract text from PDF")
    sys.exit(1)

# ==========================
# STEP 2: PARSE CONTROLS
# Pattern example:
# 6.2.4.8 Ensure audit tools mode is configured (Automated)
# ==========================

pattern = re.compile(
    r'^\s*(\d+(?:\.\d+)+)\s+(.+?\(Automated\))\s*$',
    re.MULTILINE
)

controls = []
seen = set()

for match in pattern.findall(text):
    control_id = match[0].strip()
    control_name = match[1].strip()

    # Avoid duplicates caused by headers/footers
    if control_id not in seen:
        seen.add(control_id)
        controls.append({
            "Control ID": control_id,
            "Control Name": control_name
        })

# ==========================
# STEP 3: EXPORT TO EXCEL
# ==========================

df = pd.DataFrame(controls)
df.sort_values("Control ID", inplace=True)

df.to_excel(output_xlsx, index=False, engine="openpyxl")

print(f"Extraction completed")
print(f"Total controls extracted: {len(df)}")
print(f"Excel report created: {output_xlsx}")
