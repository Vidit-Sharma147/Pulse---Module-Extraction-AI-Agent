from typing import List, Dict, Any


def to_output_list(modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Ensure consistent keys and order
    result = []
    for m in modules:
        result.append({
            'module': m.get('module'),
            'Description': m.get('Description'),
            'Submodules': m.get('Submodules', {}),
            'confidence': round(float(m.get('confidence', 0.5)), 3),
        })
    return result
