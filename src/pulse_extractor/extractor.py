from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import trafilatura
import re

try:
    import markdown as md
except ImportError:
    md = None


def _clean_html(html: str) -> str:
    # Remove common non-content areas by role/class hints
    soup = BeautifulSoup(html, 'lxml')
    for sel in [
        {'role': 'navigation'},
        {'role': 'banner'},
        {'role': 'contentinfo'},
    ]:
        for tag in soup.find_all(attrs=sel):
            tag.decompose()
    # remove obvious nav/footer/header classes
    for cls in ['nav', 'navbar', 'menu', 'footer', 'header', 'breadcrumbs', 'sub-nav', 'sidebar', 'site-header', 'site-footer']:
        for tag in soup.find_all(class_=lambda c: c and cls in c):
            tag.decompose()
    return str(soup)


def extract_page_content(url: str, html: str, content_type: Optional[str] = None) -> Dict[str, Any]:
    # Convert Markdown to HTML if indicated
    raw_html = html
    url_lower = (url or "").lower()
    is_markdown = (content_type and "text/markdown" in content_type) or url_lower.endswith('.md')
    if is_markdown and md is not None:
        try:
            raw_html = md.markdown(html)
        except Exception:
            raw_html = html

    cleaned_html = _clean_html(raw_html)
    text = trafilatura.extract(cleaned_html, include_tables=True, include_formatting=True) or ""

    soup = BeautifulSoup(cleaned_html, 'lxml')
    # Capture hierarchy via headings
    headings = []
    for level in range(1, 6):
        for h in soup.find_all(f'h{level}'):
            title = h.get_text(strip=True)
            if title:
                headings.append({'level': level, 'title': title})

    # Identify main content container (improves help centers like Zendesk/WordPress)
    main_candidates = [
        soup.find('main'),
        soup.find('article'),
        soup.find('div', class_=lambda c: c and ('article-body' in c or 'post-content' in c or 'content' in c)),
        soup.find('section', class_=lambda c: c and ('content' in c or 'article' in c)),
    ]
    main = next((m for m in main_candidates if m), soup)

    # Capture sections: heading followed by sibling text until next heading
    sections = []
    heading_tags = [f'h{i}' for i in range(1, 7)]
    for h in main.find_all(heading_tags):
        title = h.get_text(strip=True)
        if not title:
            continue
        content_parts = []
        for sib in h.next_siblings:
            if getattr(sib, 'name', None) and sib.name in heading_tags:
                break
            if getattr(sib, 'get_text', None):
                txt = sib.get_text(" ", strip=True)
                if txt:
                    content_parts.append(txt)
        body = "\n".join(content_parts)
        if body:
            sections.append({'title': title, 'body': body, 'level': int(h.name[1])})

    # Fallback: if no sections found, create a generic section from paragraphs
    if not sections:
        paras = []
        for p in main.find_all('p')[:6]:
            t = p.get_text(" ", strip=True)
            if t:
                paras.append(t)
        if paras:
            body = "\n".join(paras)
            # Use page title or domain as module name
            page_title = None
            if soup.title and soup.title.get_text():
                page_title = soup.title.get_text(strip=True)
            sections.append({'title': page_title or 'General', 'body': body, 'level': 2})

    return {
        'url': url,
        'text': text,
        'headings': headings,
        'sections': sections,
    }
