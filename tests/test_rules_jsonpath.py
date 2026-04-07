"""Tests for JSONPath rule evaluation (SRC-05)."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures'
BOOK_INFO = json.loads((FIXTURES / 'book_info.json').read_text(encoding='utf-8'))


@pytest.mark.xfail(reason='jsonpath eval not yet implemented', strict=True)
def test_scalar():
    """$.book.title returns the book title as a string."""
    from novel.rules._jsonpath import eval_jsonpath
    result = eval_jsonpath('$.book.title', BOOK_INFO)
    assert result == '斗破苍穹'


@pytest.mark.xfail(reason='jsonpath eval not yet implemented', strict=True)
def test_array():
    """$.chapters[0].name returns first chapter name."""
    from novel.rules._jsonpath import eval_jsonpath
    result = eval_jsonpath('$.chapters[0].name', BOOK_INFO)
    assert result == '第一章 陨落的天才'


@pytest.mark.xfail(reason='jsonpath eval not yet implemented', strict=True)
def test_no_match():
    """Non-matching JSONPath expression returns empty string."""
    from novel.rules._jsonpath import eval_jsonpath
    result = eval_jsonpath('$.nonexistent.field', BOOK_INFO)
    assert result == ''
