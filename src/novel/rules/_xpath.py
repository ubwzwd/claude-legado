"""XPath rule evaluation for legado rules (SRC-04)."""
from __future__ import annotations

import lxml.html
import lxml.etree


def eval_xpath(expr: str, html: str) -> str:
    """Evaluate XPath expression against HTML string.

    Returns first result for attribute/@attr and text() selectors (joins all text nodes).
    Returns serialized HTML for element results.
    Returns '' for empty result list.
    """
    tree = lxml.html.fromstring(html)
    results = tree.xpath(expr)
    if not results:
        return ''
    if isinstance(results[0], str):
        # text() or @attribute results — join all matches
        return ''.join(results)
    # Element result — serialize first element as HTML
    return lxml.etree.tostring(results[0], encoding='unicode', method='html')


def eval_xpath_list(expr: str, html: str) -> list[str]:
    """Evaluate XPath expression and return ALL matches (used by evaluate_list).

    Returns list of strings. Returns [] for empty result.
    """
    tree = lxml.html.fromstring(html)
    results = tree.xpath(expr)
    if not results:
        return []
    if results and isinstance(results[0], str):
        return list(results)
    return [lxml.etree.tostring(el, encoding='unicode', method='html') for el in results]
