"""JSONPath rule evaluation for legado rules (SRC-05)."""
from __future__ import annotations

import json
from jsonpath_ng import parse as jpath_parse


def eval_jsonpath(expr: str, data: dict | list | str) -> str:
    """Evaluate JSONPath expression against a Python dict/list.

    Returns first match as str, or '' if no match.
    Uses jsonpath_ng.parse() (not .ext) — sufficient for Phase 2 filter-free expressions.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return ''
            
    matches = jpath_parse(expr).find(data)
    if not matches:
        return ''
    return str(matches[0].value)


def eval_jsonpath_list(expr: str, data: dict | list | str) -> list[str]:
    """Evaluate JSONPath expression and return ALL matches (used by evaluate_list).

    Returns list of str values. Returns [] if no match.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []
            
    matches = jpath_parse(expr).find(data)
    if not matches:
        return []
        
    # Return actual objects if it's a dict or list for evaluate_list inside evaluate_list
    return [m.value for m in matches]
