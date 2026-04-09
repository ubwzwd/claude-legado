"""JS rule evaluation for legado rules via quickjs (SRC-07, SRC-08, SRC-09)."""
from __future__ import annotations

import base64
import hashlib
from typing import Callable

import quickjs


def _make_context(
    result: str,
    base_url: str,
    ajax_fetcher: Callable[[str], str] | None = None,
    prefetched: dict[str, str] | None = None,
) -> quickjs.Context:
    """Build a fresh quickjs.Context with result, baseUrl, and java bridge injected.

    Always creates a new context — never reuses. This prevents JS global state leakage
    between separate rule evaluations (~0.1ms overhead per call, verified acceptable).

    Injected JS globals:
        result   — content string (selector output or raw content)
        baseUrl  — base URL for resolving relative links
        java     — object with base64Decode(), md5(), ajax() methods

    java.ajax() behavior depends on parameters:
        - ajax_fetcher provided: calls the fetcher callable (recording mode)
        - prefetched provided: looks up URL in prefetched dict (injection mode)
        - neither: raises NotImplementedError (surfaces as quickjs.JSException)
    """
    ctx = quickjs.Context()

    # Inject content variables
    ctx.set('result', result)
    ctx.set('baseUrl', base_url)

    # Register Java bridge callables
    def _base64_decode(s: str) -> str:
        return base64.b64decode(s).decode('utf-8')

    def _md5(s: str) -> str:
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    if ajax_fetcher is not None:
        def _ajax(url: str) -> str:
            return ajax_fetcher(url)
    elif prefetched is not None:
        def _ajax(url: str) -> str:
            return prefetched.get(url, '')
    else:
        def _ajax(url: str) -> str:
            raise NotImplementedError('java.ajax not available without fetcher')

    ctx.add_callable('_javaBase64Decode', _base64_decode)
    ctx.add_callable('_javaMd5', _md5)
    ctx.add_callable('_javaAjax', _ajax)

    # Build java object in JS — methods reference the injected callables
    ctx.eval('var java = { base64Decode: _javaBase64Decode, md5: _javaMd5, ajax: _javaAjax };')

    return ctx


def eval_js(
    code: str,
    result: str,
    base_url: str,
    mode: str = 'inline',
    ajax_fetcher: Callable[[str], str] | None = None,
    prefetched: dict[str, str] | None = None,
) -> str:
    """Evaluate JS code via a fresh quickjs context.

    mode='inline': code is a single JS expression.
                   The return value of the expression is the result string.
    mode='block':  code is a multi-statement JS block.
                   The block may mutate the 'result' variable.
                   The final value of 'result' is read back after eval.

    Args:
        code:          JS expression or block to evaluate (prefix already stripped by caller)
        result:        Content string injected as JS 'result' global
        base_url:      URL string injected as JS 'baseUrl' global
        mode:          'inline' or 'block'
        ajax_fetcher:  Optional callable for recording/fetching ajax URLs (two-pass mode)
        prefetched:    Optional dict mapping URLs to pre-fetched content (injection mode)

    Returns:
        str — result of JS evaluation, or '' if None

    Raises:
        quickjs.JSException: if JS code raises (includes java.ajax stub NotImplementedError)
    """
    ctx = _make_context(result, base_url, ajax_fetcher=ajax_fetcher, prefetched=prefetched)

    if mode == 'inline':
        ret = ctx.eval(code)
        return str(ret) if ret is not None else ''
    else:  # mode == 'block'
        ctx.eval(code)
        val = ctx.get('result')
        return str(val) if val is not None else ''
