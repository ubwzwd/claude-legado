"""CSS selector evaluation for legado rules (SRC-03)."""
from __future__ import annotations

import lxml.html
import lxml.etree


def eval_css(rule_body: str, html: str) -> str:
    """Evaluate a CSS rule body (after 'css:' prefix is stripped by caller).

    rule_body format: 'selector@attribute' or 'selector'
    - @text  -> element.text_content() (all descendant text)
    - @{attr} -> element.get(attr, '')
    - no @   -> outer HTML of first matched element as string
    No match -> return ''
    """
    if '@' in rule_body:
        selector, attr = rule_body.rsplit('@', 1)
    else:
        selector, attr = rule_body, None

    tree = lxml.html.fromstring(html)
    elements = tree.cssselect(selector)
    if not elements:
        return ''

    el = elements[0]
    if attr == 'text':
        return el.text_content()
    elif attr is None or attr == 'html':
        return lxml.etree.tostring(el, encoding='unicode', method='html')
    else:
        return el.get(attr, '')


def eval_css_list(rule_body: str, html: str) -> list[str]:
    """Evaluate a CSS rule body and return ALL matches (used by evaluate_list).

    Returns list of strings using the same @attribute/text/html extraction logic.
    Returns [] if no elements match.
    """
    if '@' in rule_body:
        selector, attr = rule_body.rsplit('@', 1)
    else:
        selector, attr = rule_body, None

    tree = lxml.html.fromstring(html)
    elements = tree.cssselect(selector)
    if not elements:
        return []

    results = []
    for el in elements:
        if attr == 'text':
            results.append(el.text_content())
        elif attr is None or attr == 'html':
            results.append(lxml.etree.tostring(el, encoding='unicode', method='html'))
        else:
            results.append(el.get(attr, ''))
    return results
