import json
import sys
from pathlib import Path

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
    out_path = out_dir / "four_sites_small.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {out_path}")
