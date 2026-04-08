"""Public API for the legado rule engine.

Usage:
    from novel.rules import evaluate, evaluate_list, RuleError

evaluate(rule, content, base_url='') -> str
    Auto-detects rule type from prefix and dispatches to the correct evaluator.
    Returns first match as str. Raises RuleError on failure.

evaluate_list(rule, content, base_url='') -> list[str]
    Same detection and dispatch but returns ALL matches as a list.
    Used by Phase 4 TOC and search flows that need multiple items.
"""
from __future__ import annotations

from novel.rules._detect import detect_rule_type, RuleType
from novel.rules._errors import RuleError
from novel.rules._css import eval_css, eval_css_list
from novel.rules._xpath import eval_xpath, eval_xpath_list
from novel.rules._jsonpath import eval_jsonpath, eval_jsonpath_list
from novel.rules._js import eval_js


def evaluate(rule: str, content: str | dict, base_url: str = '') -> str:
    """Evaluate a legado rule against content. Returns first match as str.

    Supported rule prefixes:
        css:SELECTOR@ATTR  — CSS selector (SRC-03)
        xpath:EXPR         — XPath expression (SRC-04)
        $.path.to.field    — JSONPath expression (SRC-05)
        @js: expression    — Inline JS via quickjs (SRC-07, wired in plan 02-04)
        <js>code</js>      — JS block via quickjs (SRC-08, wired in plan 02-04)

    Raises:
        RuleError: if rule evaluation fails for any reason (D-09).
    """
    try:
        rule_type, rule_body = detect_rule_type(rule)
    except ValueError as cause:
        raise RuleError(rule, cause) from cause

    try:
        if rule_type == RuleType.CSS:
            return eval_css(rule_body, content)
        elif rule_type == RuleType.XPATH:
            return eval_xpath(rule_body, content)
        elif rule_type == RuleType.JSONPATH:
            return eval_jsonpath(rule, content)
        elif rule_type == RuleType.JS_INLINE:
            return eval_js(rule_body, str(content) if not isinstance(content, str) else content, base_url, mode='inline')
        elif rule_type == RuleType.JS_BLOCK:
            return eval_js(rule_body, str(content) if not isinstance(content, str) else content, base_url, mode='block')
        else:
            raise ValueError(f'Unknown rule type: {rule_type!r}')
    except RuleError:
        raise
    except Exception as cause:
        raise RuleError(rule, cause) from cause


def evaluate_list(rule: str, content: str | dict, base_url: str = '') -> list[str]:
    """Evaluate a legado rule and return ALL matches as a list.

    Used by Phase 4 callers that need multiple results (TOC chapter list, search results).

    Raises:
        RuleError: if rule evaluation fails for any reason (D-09).
    """
    try:
        rule_type, rule_body = detect_rule_type(rule)
    except ValueError as cause:
        raise RuleError(rule, cause) from cause

    try:
        if rule_type == RuleType.CSS:
            return eval_css_list(rule_body, content)
        elif rule_type == RuleType.XPATH:
            return eval_xpath_list(rule_body, content)
        elif rule_type == RuleType.JSONPATH:
            return eval_jsonpath_list(rule, content)
        elif rule_type == RuleType.JS_INLINE:
            result = eval_js(rule_body, str(content) if not isinstance(content, str) else content, base_url, mode='inline')
            return [result]
        elif rule_type == RuleType.JS_BLOCK:
            result = eval_js(rule_body, str(content) if not isinstance(content, str) else content, base_url, mode='block')
            return [result]
        else:
            raise ValueError(f'Unknown rule type: {rule_type!r}')
    except RuleError:
        raise
    except Exception as cause:
        raise RuleError(rule, cause) from cause


__all__ = ['evaluate', 'evaluate_list', 'RuleError']
