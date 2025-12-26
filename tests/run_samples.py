import json
import sys
from pathlib import Path
import argparse

# Ensure project root is on sys.path when running this file directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from module_extractor import run

# Reduced to 2 stable sources for initial validation
SAMPLES = [
    "https://wordpress.org/documentation/",
    "https://www.chargebee.com/docs/2.0/",
]

if __name__ == "__main__":
    # Small crawl limits for quick correctness checks (configurable)
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=6)
    parser.add_argument("--per-domain-limit", type=int, default=5)
    args = parser.parse_args()

    result = run(SAMPLES, max_pages=args.max_pages, per_domain_limit=args.per_domain_limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))
