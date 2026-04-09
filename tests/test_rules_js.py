"""Tests for JS rule evaluation (SRC-07, SRC-08, SRC-09)."""
from __future__ import annotations

import pytest


def test_inline():
    """@js: inline expression: result.trim() trims the content string."""
    from novel.rules._js import eval_js
    result = eval_js('result.trim()', '  hello world  ', '', mode='inline')
    assert result == 'hello world'


def test_block():
    """<js> block: modifying result variable persists after eval."""
    from novel.rules._js import eval_js
    code = 'result = result.toUpperCase();'
    result = eval_js(code, 'hello', '', mode='block')
    assert result == 'HELLO'


def test_java_base64():
    """java.base64Decode() decodes base64 correctly."""
    from novel.rules._js import eval_js
    import base64
    encoded = base64.b64encode('测试'.encode('utf-8')).decode('ascii')
    result = eval_js(f'java.base64Decode("{encoded}")', '', '', mode='inline')
    assert result == '测试'


def test_java_md5():
    """java.md5() returns hex MD5 of input string."""
    from novel.rules._js import eval_js
    import hashlib
    expected = hashlib.md5('hello'.encode('utf-8')).hexdigest()
    result = eval_js('java.md5("hello")', '', '', mode='inline')
    assert result == expected


def test_ajax_stub():
    """java.ajax() raises JSException wrapping NotImplementedError (D-02)."""
    import quickjs
    from novel.rules._js import eval_js
    with pytest.raises(quickjs.JSException):
        eval_js('java.ajax("https://example.com")', '', '', mode='inline')


def test_eval_js_ajax_fetcher_recording():
    """ajax_fetcher callable is invoked when java.ajax() is called in JS."""
    from novel.rules._js import eval_js
    captured = []
    def recorder(url):
        captured.append(url)
        return ''
    eval_js('java.ajax("https://example.com/data")', '', '', mode='inline', ajax_fetcher=recorder)
    assert captured == ['https://example.com/data']


def test_eval_js_prefetched_injection():
    """prefetched dict provides content for java.ajax() calls."""
    from novel.rules._js import eval_js
    pre = {'https://example.com/data': '{"title":"Test"}'}
    result = eval_js(
        'java.ajax("https://example.com/data")',
        '', '', mode='inline',
        prefetched=pre,
    )
    assert result == '{"title":"Test"}'


def test_eval_js_ajax_backward_compat():
    """Without ajax_fetcher or prefetched, java.ajax() still raises JSException."""
    import quickjs
    from novel.rules._js import eval_js
    with pytest.raises(quickjs.JSException):
        eval_js('java.ajax("https://example.com")', '', '', mode='inline')

