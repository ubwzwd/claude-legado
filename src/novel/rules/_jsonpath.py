"""JSONPath rule evaluation for legado rules (SRC-05)."""
from __future__ import annotations

from jsonpath_ng import parse as jpath_parse


def eval_jsonpath(expr: str, data: dict | list) -> str:
    """Evaluate JSONPath expression against a Python dict/list.

    Returns first match as str, or '' if no match.
    Uses jsonpath_ng.parse() (not .ext) — sufficient for Phase 2 filter-free expressions.
    """
    matches = jpath_parse(expr).find(data)
    if not matches:
        return ''
    return str(matches[0].value)


def eval_jsonpath_list(expr: str, data: dict | list) -> list[str]:
    """Evaluate JSONPath expression and return ALL matches (used by evaluate_list).

    Returns list of str values. Returns [] if no match.
    """
    matches = jpath_parse(expr).find(data)
    if not matches:
        return []
    return [str(m.value) for m in matches]
