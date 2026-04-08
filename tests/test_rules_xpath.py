"""Tests for XPath rule evaluation (SRC-04)."""
from __future__ import annotations

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures'
HTML_TITLE = (FIXTURES / 'html_title.html').read_text(encoding='utf-8')


def test_text_node():
    """xpath://h1/text() returns the text of h1."""
    from novel.rules._xpath import eval_xpath
    result = eval_xpath('//h1/text()', HTML_TITLE)
    assert result == '道可道，非常道'


def test_attr_node():
    """xpath://img[@class='cover']/@src returns src attribute."""
    from novel.rules._xpath import eval_xpath
    result = eval_xpath("//img[@class='cover']/@src", HTML_TITLE)
    assert result == 'https://example.com/cover.jpg'
