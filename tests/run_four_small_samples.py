# Quick-run (PowerShell):
# Open PowerShell in the project root, then run:
# python -m venv .venv
# .venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# python tests\run_four_small_samples.py

import json
import sys
from pathlib import Path
import csv
import io
import yaml

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from module_extractor import run

SAMPLES = [
    "https://wordpress.org/documentation/",
    "https://www.chargebee.com/docs/2.0/",
    "https://support.neo.space/hc/en-us",
    "https://help.zluri.com/",
]

if __name__ == "__main__":
    result = run(SAMPLES, max_pages=8, per_domain_limit=4, delay=0.3)
    out_dir = ROOT / "samples"
    out_dir.mkdir(exist_ok=True)
    # JSON
    json_path = out_dir / "four_sites_small.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved JSON: {json_path}")

    # CSV (flatten submodules)
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(["module", "description", "submodule", "sub_description", "confidence"])
    for m in result:
        mod = m.get("module", "")
        desc = m.get("Description", "")
        conf = m.get("confidence", "")
        subs = m.get("Submodules", {}) or {}
        if subs:
            for sm_name, sm_desc in subs.items():
                writer.writerow([mod, desc, sm_name, sm_desc, conf])
        else:
            writer.writerow([mod, desc, "", "", conf])
    csv_path = out_dir / "four_sites_small.csv"
    csv_path.write_text(csv_buf.getvalue(), encoding="utf-8")
    print(f"Saved CSV: {csv_path}")

    # YAML
    yaml_str = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    yaml_path = out_dir / "four_sites_small.yaml"
    yaml_path.write_text(yaml_str, encoding="utf-8")
    print(f"Saved YAML: {yaml_path}")
