import re
import time
import logging
from dataclasses import dataclass
from typing import List, Set, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
import tldextract
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pulse.crawler")


@dataclass
class Page:
    url: str
    html: str
    content_type: Optional[str] = None


def _normalize_url(u: str) -> Optional[str]:
    try:
        parsed = urlparse(u)
        if not parsed.scheme:
            u = "https://" + u
            parsed = urlparse(u)
        if parsed.scheme not in {"http", "https"}:
            return None
        # remove fragments
        return parsed._replace(fragment="").geturl()
    except Exception:
        return None


def _domain(url: str) -> str:
    ext = tldextract.extract(url)
    return ".".join([p for p in [ext.subdomain, ext.domain, ext.suffix] if p])


def _robots_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rfp = RobotFileParser()
        rfp.set_url(robots_url)
        rfp.read()
        return rfp.can_fetch("*", url)
    except Exception:
        return True


HELP_PATTERNS = [
    re.compile(r"help", re.I),
    re.compile(r"support", re.I),
    re.compile(r"docs", re.I),
    re.compile(r"documentation", re.I),
    re.compile(r"knowledge", re.I),
    re.compile(r"hc/en-us", re.I),
]


def _is_relevant_link(href: str) -> bool:
    if not href:
        return False
    href = href.strip()
    if href.startswith("mailto:") or href.startswith("tel:"):
        return False
    if href.endswith(('.pdf', '.zip', '.png', '.jpg', '.jpeg', '.gif')):
        return False
    for pat in HELP_PATTERNS:
        if pat.search(href):
            return True
    # also allow relative links; they will be resolved and checked against domain
    return href.startswith('/')


def _fetch(url: str, timeout: int = 20, retries: int = 2) -> Optional[Tuple[str, Optional[str]]]:
    backoff = 0.6
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "PulseCrawler/1.0"})
            ctype = resp.headers.get("Content-Type", "") if resp is not None else None
            if resp.status_code == 200 and resp.text:
                # Only process textual content
                if ctype and ("text/html" in ctype or "text/plain" in ctype or "text/markdown" in ctype):
                    return resp.text, ctype
                # Fallback: if content-type missing, try using text
                if not ctype:
                    return resp.text, None
                # Non-text types skipped
                logger.debug(f"Skipping non-text content-type: {ctype} for {url}")
                return None
            else:
                logger.debug(f"Non-200 status {resp.status_code if resp else 'N/A'} for {url}")
        except Exception as e:
            logger.debug(f"Fetch error on attempt {attempt} for {url}: {e}")
        if attempt < retries:
            time.sleep(backoff)
            backoff *= 1.5
    return None


def crawl_urls(urls: List[str], max_pages: int = 200, per_domain_limit: int = 150, delay: float = 0.3) -> List[Page]:
    normalized = [u for u in (_normalize_url(u) for u in urls) if u]
    queue: List[str] = []
    visited: Set[str] = set()
    pages: List[Page] = []
    domain_counts: Dict[str, int] = {}

    for u in normalized:
        queue.append(u)

    unlimited_pages = max_pages is None or max_pages <= 0
    unlimited_domain = per_domain_limit is None or per_domain_limit <= 0

    while queue and (unlimited_pages or len(pages) < max_pages):
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        dom = _domain(url)
        count = domain_counts.get(dom, 0)
        if not unlimited_domain and count >= per_domain_limit:
            continue
        if not _robots_allowed(url):
            continue

        fetched = _fetch(url)
        if not fetched:
            continue
        html, content_type = fetched
        pages.append(Page(url=url, html=html, content_type=content_type))
        domain_counts[dom] = count + 1
        logger.info(f"Fetched {url}")

        soup = BeautifulSoup(html, 'lxml')
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if not _is_relevant_link(href):
                continue
            new_url = urljoin(url, href)
            new_dom = _domain(new_url)
            if new_dom != dom:
                # restrict to same domain
                continue
            if new_url not in visited:
                queue.append(new_url)

        time.sleep(delay)

    return pages
