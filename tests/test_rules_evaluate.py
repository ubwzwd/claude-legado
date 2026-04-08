"""Integration tests for evaluate() dispatcher + URL template (SRC-10, D-09)."""
from __future__ import annotations

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures'


def test_css_dispatch():
    """evaluate() with css: prefix dispatches to CSS evaluator."""
    from novel.rules import evaluate
    html = (FIXTURES / 'html_title.html').read_text(encoding='utf-8')
    result = evaluate('css:.title@text', html)
    assert result == '道可道，非常道'


def test_xpath_dispatch():
    """evaluate() with xpath: prefix dispatches to XPath evaluator."""
    from novel.rules import evaluate
    html = (FIXTURES / 'html_title.html').read_text(encoding='utf-8')
    result = evaluate('xpath://h1/text()', html)
    assert result == '道可道，非常道'


def test_jsonpath_dispatch():
    """evaluate() with $. prefix dispatches to JSONPath evaluator."""
    import json
    from novel.rules import evaluate
    data = json.loads((FIXTURES / 'book_info.json').read_text(encoding='utf-8'))
    result = evaluate('$.book.title', data)
    assert result == '斗破苍穹'


def test_rule_error_on_bad_rule():
    """evaluate() raises RuleError (not ValueError) for unrecognized rule type (D-09)."""
    from novel.rules import evaluate, RuleError
    with pytest.raises(RuleError):
        evaluate('NOTARULE', '<html/>')


def test_url_template():
    """apply_url_template replaces {{searchKey}} and leaves unknown keys intact."""
    from novel.rules._templates import apply_url_template
    url = apply_url_template(
        'https://example.com/search?q={{searchKey}}&p={{page}}&x={{unknown}}',
        {'searchKey': '斗破苍穹', 'page': 1},
    )
    assert url == 'https://example.com/search?q=斗破苍穹&p=1&x={{unknown}}'
