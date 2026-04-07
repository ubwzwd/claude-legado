"""Tests for book source JSON parser (SRC-01, SRC-02)."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures'


def test_load_single(tmp_path):
    """SRC-01: load_book_source accepts a single JSON object."""
    from novel.rules._source import load_book_source
    source_file = tmp_path / 'source.json'
    source_file.write_text(
        json.dumps({'bookSourceUrl': 'https://example.com', 'bookSourceName': '测试书源'}),
        encoding='utf-8',
    )
    result = load_book_source(source_file)
    assert result['bookSourceUrl'] == 'https://example.com'
    assert result['bookSourceName'] == '测试书源'


def test_load_array(tmp_path):
    """SRC-01: load_book_source accepts a JSON array and returns first element."""
    from novel.rules._source import load_book_source
    source_file = tmp_path / 'sources.json'
    source_file.write_text(
        json.dumps([
            {'bookSourceUrl': 'https://example.com', 'bookSourceName': '测试书源'},
            {'bookSourceUrl': 'https://other.com', 'bookSourceName': '其他书源'},
        ]),
        encoding='utf-8',
    )
    result = load_book_source(source_file)
    assert result['bookSourceUrl'] == 'https://example.com'
    assert result['bookSourceName'] == '测试书源'


def test_required_fields():
    """SRC-02: fixture book_source.json contains all required fields."""
    from novel.rules._source import load_book_source
    result = load_book_source(FIXTURES / 'book_source.json')
    assert 'bookSourceUrl' in result
    assert 'bookSourceName' in result


def test_missing_field(tmp_path):
    """SRC-02: load_book_source raises ValueError for missing bookSourceUrl."""
    from novel.rules._source import load_book_source
    source_file = tmp_path / 'bad.json'
    source_file.write_text(
        json.dumps({'bookSourceName': '测试书源'}),
        encoding='utf-8',
    )
    with pytest.raises(ValueError, match='bookSourceUrl'):
        load_book_source(source_file)
