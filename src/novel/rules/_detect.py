"""Rule type detection for legado rule strings."""
from __future__ import annotations

import enum


class RuleType(enum.Enum):
    CSS = 'css'
    XPATH = 'xpath'
    JSONPATH = 'jsonpath'
    JS_INLINE = 'js_inline'
    JS_BLOCK = 'js_block'


def detect_rule_type(rule: str) -> tuple[RuleType, str]:
    """Return (RuleType, rule_body) where rule_body has the prefix stripped.

    Detection order: xpath: → css: → JSONPath ($./$[) → @js: → <js>...</js>
    Raises ValueError if no rule type can be detected.
    """
    rule = rule.strip()
    if rule.startswith('xpath:'):
        return RuleType.XPATH, rule[len('xpath:'):]
    if rule.startswith('css:'):
        return RuleType.CSS, rule[len('css:'):]
    if rule.startswith('$.') or rule.startswith('$['):
        return RuleType.JSONPATH, rule  # jsonpath-ng wants the full $ expression
    if rule.startswith('@js:'):
        return RuleType.JS_INLINE, rule[len('@js:'):].strip()
    if rule.startswith('<js>') and '</js>' in rule:
        code = rule[len('<js>'):rule.index('</js>')]
        return RuleType.JS_BLOCK, code
    raise ValueError(f'Cannot detect rule type: {rule!r}')
