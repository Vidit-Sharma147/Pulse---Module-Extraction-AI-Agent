from typing import List, Dict, Any
from collections import defaultdict
import math


def _score_description(text: str) -> float:
    # Simple confidence based on length and sentence count
    length = len(text)
    sentences = text.count('.') + text.count('!') + text.count('?')
    if length < 80:
        return 0.4
    base = min(1.0, math.log10(length + 10) / 3.0)
    bonus = min(0.3, sentences * 0.03)
    return min(1.0, 0.5 + base + bonus)


def _summarize(body: str, max_chars: int = 320) -> str:
    # Extractive: take leading sentences until limit
    parts = []
    for sent in body.split('. '):
        if sum(len(p) for p in parts) + len(sent) + 1 > max_chars:
            break
        parts.append(sent.strip())
    summary = '. '.join(parts).strip()
    if summary and not summary.endswith('.'):
        summary += '.'
    return summary


def infer_structure(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Group by top-level sections (h1/h2 as modules), submodules under h3/h4
    modules_map: Dict[str, Dict[str, Any]] = {}

    for page in pages:
        for sec in page.get('sections', []):
            lvl = sec.get('level', 3)
            title = sec.get('title', '').strip()
            body = sec.get('body', '').strip()
            if not title:
                continue
            if lvl <= 2:
                # module candidate
                desc = _summarize(body) if body else ''
                conf = _score_description(desc) if desc else 0.45
                mod = modules_map.get(title)
                if not mod:
                    modules_map[title] = {
                        'module': title,
                        'Description': desc or title,
                        'Submodules': {},
                        'confidence': conf,
                    }
                else:
                    # merge: prefer longer description
                    if len(desc) > len(mod.get('Description', '')):
                        mod['Description'] = desc
                        mod['confidence'] = max(mod.get('confidence', 0.5), conf)
            elif 3 <= lvl <= 4:
                # submodule under the nearest previous module title on this page or a generic bucket
                # heuristic: use the first h1/h2 seen earlier on this page
                parent_title = None
                for s2 in page.get('sections', []):
                    if s2 is sec:
                        break
                    if s2.get('level', 3) <= 2:
                        parent_title = s2.get('title')
                if not parent_title:
                    parent_title = 'General'
                    if parent_title not in modules_map:
                        modules_map[parent_title] = {
                            'module': parent_title,
                            'Description': 'General documentation topics',
                            'Submodules': {},
                            'confidence': 0.5,
                        }
                mod = modules_map.setdefault(parent_title, {
                    'module': parent_title,
                    'Description': 'Documentation module',
                    'Submodules': {},
                    'confidence': 0.5,
                })
                sm_desc = _summarize(body) if body else ''
                sm_conf = _score_description(sm_desc) if sm_desc else 0.4
                # prefer longer description if duplicate submodule title
                existing = mod['Submodules'].get(title)
                if not existing or len(sm_desc) > len(existing):
                    mod['Submodules'][title] = sm_desc or title
                    mod['confidence'] = max(mod['confidence'], sm_conf)
            else:
                # deeper levels ignored or folded into nearest submodule
                pass

    # Convert map to list
    modules = list(modules_map.values())
    # Basic post-processing: remove empty submodules and trim
    for m in modules:
        if not m['Submodules']:
            m['Submodules'] = {}
        if not m['Description']:
            m['Description'] = m['module']
    return modules
