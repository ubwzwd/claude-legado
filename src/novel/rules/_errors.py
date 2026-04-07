"""Custom exceptions for the rule engine."""
from __future__ import annotations


class RuleError(Exception):
    """Raised when a legado rule fails to evaluate.

    Attributes:
        rule: the raw rule string that caused the failure
        cause: the underlying exception
    """

    def __init__(self, rule: str, cause: Exception) -> None:
        self.rule = rule
        self.cause = cause
        super().__init__(f'Rule evaluation failed: {rule!r} — {cause}')
