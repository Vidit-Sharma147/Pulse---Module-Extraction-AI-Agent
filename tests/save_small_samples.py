import json
from pathlib import Path
import sys

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from module_extractor import run

SAMPLES = [
    "https://wordpress.org/documentation/",
    "https://www.chargebee.com/docs/2.0/",
]

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parents[1] / "samples"
    out_dir.mkdir(exist_ok=True)
    result = run(SAMPLES, max_pages=6, per_domain_limit=5)
    out_path = out_dir / "two_sites_small.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {out_path}")
