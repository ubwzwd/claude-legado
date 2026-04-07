"""Public API for the legado rule engine."""
from __future__ import annotations

from novel.rules._detect import detect_rule_type, RuleType
from novel.rules._errors import RuleError


def evaluate(rule: str, content: str | dict, base_url: str = '') -> str:
    """Evaluate a legado rule against content. Returns str result.

    Raises:
        RuleError: if rule evaluation fails for any reason.
    """
    raise NotImplementedError('evaluate() not yet wired — implemented in plans 02-02 through 02-04')


def evaluate_list(rule: str, content: str | dict, base_url: str = '') -> list[str]:
    """Evaluate a legado rule and return all matches as a list.

    Used by Phase 4 callers that need multiple results (e.g. TOC chapter list).

    Raises:
        RuleError: if rule evaluation fails for any reason.
    """
    raise NotImplementedError('evaluate_list() not yet wired — implemented in plans 02-02 through 02-04')


__all__ = ['evaluate', 'evaluate_list', 'RuleError']
