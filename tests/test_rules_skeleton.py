"""TDD RED tests for rules sub-package skeleton (Task 1)."""
from __future__ import annotations

import pytest


def test_evaluate_importable():
    """evaluate() is importable from novel.rules."""
    from novel.rules import evaluate
    assert callable(evaluate)


def test_evaluate_list_importable():
    """evaluate_list() is importable from novel.rules."""
    from novel.rules import evaluate_list
    assert callable(evaluate_list)


def test_evaluate_css_works():
    """evaluate() dispatches CSS rule and returns matched text."""
    from novel.rules import evaluate
    result = evaluate('css:.title@text', '<h1 class="title">X</h1>')
    assert result == 'X'


def test_rule_error_str():
    """RuleError(rule, cause) str contains both rule and cause message."""
    from novel.rules import RuleError
    err = RuleError('css:.title', ValueError('no match'))
    s = str(err)
    assert 'css:.title' in s
    assert 'no match' in s


def test_detect_css():
    """detect_rule_type('css:.t@text') returns (RuleType.CSS, '.t@text')."""
    from novel.rules._detect import detect_rule_type, RuleType
    rt, body = detect_rule_type('css:.t@text')
    assert rt == RuleType.CSS
    assert body == '.t@text'


def test_detect_xpath():
    """detect_rule_type('xpath://h1/text()') returns (RuleType.XPATH, '//h1/text()')."""
    from novel.rules._detect import detect_rule_type, RuleType
    rt, body = detect_rule_type('xpath://h1/text()')
    assert rt == RuleType.XPATH
    assert body == '//h1/text()'


def test_detect_jsonpath():
    """detect_rule_type('$.book.title') returns (RuleType.JSONPATH, '$.book.title')."""
    from novel.rules._detect import detect_rule_type, RuleType
    rt, body = detect_rule_type('$.book.title')
    assert rt == RuleType.JSONPATH
    assert body == '$.book.title'


def test_detect_js_inline():
    """detect_rule_type('@js: result.trim()') returns (RuleType.JS_INLINE, 'result.trim()')."""
    from novel.rules._detect import detect_rule_type, RuleType
    rt, body = detect_rule_type('@js: result.trim()')
    assert rt == RuleType.JS_INLINE
    assert body == 'result.trim()'


def test_detect_js_block():
    """detect_rule_type('<js>result = result.trim();</js>') returns (RuleType.JS_BLOCK, ...)."""
    from novel.rules._detect import detect_rule_type, RuleType
    rt, body = detect_rule_type('<js>result = result.trim();</js>')
    assert rt == RuleType.JS_BLOCK
    assert body == 'result = result.trim();'


def test_detect_unknown_raises():
    """detect_rule_type('unknown') raises ValueError."""
    from novel.rules._detect import detect_rule_type
    with pytest.raises(ValueError):
        detect_rule_type('unknown')
