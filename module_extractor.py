import argparse
import json
from typing import List

from src.pulse_extractor.crawler import crawl_urls
from src.pulse_extractor.extractor import extract_page_content
from src.pulse_extractor.inference import infer_structure
from src.pulse_extractor.output import to_output_list
from src.pulse_extractor.cache import configure_cache


def run(urls: List[str], max_pages: int = 200, per_domain_limit: int = 150, delay: float = 0.3):
    configure_cache()
    pages = crawl_urls(urls, max_pages=max_pages, per_domain_limit=per_domain_limit, delay=delay)
    contents = [extract_page_content(p.url, p.html, getattr(p, 'content_type', None)) for p in pages]
    modules = infer_structure(contents)
    return to_output_list(modules)


def main():
    parser = argparse.ArgumentParser(description="Pulse - Module Extraction CLI")
    parser.add_argument("--urls", nargs="+", required=True, help="One or more documentation URLs")
    parser.add_argument("--max-pages", type=int, default=0, help="Maximum pages across sources (0 for unlimited)")
    parser.add_argument("--per-domain-limit", type=int, default=0, help="Max pages per domain (0 for unlimited)")
    parser.add_argument("--delay", type=float, default=0.3, help="Crawler throttle delay between requests (seconds)")
    args = parser.parse_args()

    result = run(args.urls, max_pages=args.max_pages, per_domain_limit=args.per_domain_limit, delay=args.delay)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
