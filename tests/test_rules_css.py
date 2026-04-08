"""Tests for CSS selector rule evaluation (SRC-03)."""
from __future__ import annotations

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures'
HTML_TITLE = (FIXTURES / 'html_title.html').read_text(encoding='utf-8')


def test_text_attr():
    """css:.title@text extracts text content of .title element."""
    from novel.rules._css import eval_css
    result = eval_css('.title@text', HTML_TITLE)
    assert result == '道可道，非常道'


def test_href_attr():
    """css:a.chapter@href extracts href from first .chapter anchor."""
    from novel.rules._css import eval_css
    toc_html = (FIXTURES / 'toc_list.html').read_text(encoding='utf-8')
    result = eval_css('a.chapter@href', toc_html)
    assert result == '/chapter/1'


def test_no_match():
    """css with no match returns empty string (not RuleError)."""
    from novel.rules._css import eval_css
    result = eval_css('.nonexistent@text', HTML_TITLE)
    assert result == ''
