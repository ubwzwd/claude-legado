"""Tests for multi-page pagination helpers (HTTP-04, HTTP-05)."""
from __future__ import annotations

from novel.http._pagination import follow_toc_pages, follow_content_pages


def test_follow_toc_pages_single_page():
    """Single-page TOC: eval_fn returns '' -> returns [html1]."""
    html_map = {'https://example.com/toc': '<html>TOC page 1</html>'}
    fetch_fn = lambda url: html_map[url]
    eval_fn = lambda rule, html: ''

    result = follow_toc_pages(
        start_url='https://example.com/toc',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    assert result == ['<html>TOC page 1</html>']


def test_follow_toc_pages_two_pages():
    """Two-page TOC: eval_fn returns second URL on first call, '' on second."""
    html_map = {
        'https://example.com/toc/1': '<html>TOC page 1</html>',
        'https://example.com/toc/2': '<html>TOC page 2</html>',
    }
    fetch_fn = lambda url: html_map[url]

    next_urls = iter(['https://example.com/toc/2', ''])
    eval_fn = lambda rule, html: next(next_urls)

    result = follow_toc_pages(
        start_url='https://example.com/toc/1',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    assert result == ['<html>TOC page 1</html>', '<html>TOC page 2</html>']


def test_follow_toc_pages_visited_guard():
    """Cycle detection: eval_fn returns the start URL again -> stops, no infinite loop."""
    html_map = {'https://example.com/toc': '<html>TOC page 1</html>'}
    fetch_fn = lambda url: html_map[url]
    # Always returns the same URL (would cause infinite loop without guard)
    eval_fn = lambda rule, html: 'https://example.com/toc'

    result = follow_toc_pages(
        start_url='https://example.com/toc',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    assert result == ['<html>TOC page 1</html>']


def test_follow_toc_pages_template_substitution():
    """URL template with {{page}} is resolved by apply_url_template."""
    html_map = {
        'https://example.com/toc/1': '<html>TOC 1</html>',
        'https://example.com/toc/2': '<html>TOC 2</html>',
    }
    fetch_fn = lambda url: html_map[url]

    next_urls = iter(['https://example.com/toc/{{page}}', ''])
    eval_fn = lambda rule, html: next(next_urls)

    result = follow_toc_pages(
        start_url='https://example.com/toc/1',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    # {{page}} should be replaced with 2 (len(pages) + 1 after first page)
    assert result == ['<html>TOC 1</html>', '<html>TOC 2</html>']


def test_follow_content_pages():
    """Multi-page content: follows nextContentUrl chain."""
    html_map = {
        'https://example.com/ch1/1': '<p>Part 1</p>',
        'https://example.com/ch1/2': '<p>Part 2</p>',
        'https://example.com/ch1/3': '<p>Part 3</p>',
    }
    fetch_fn = lambda url: html_map[url]

    next_urls = iter([
        'https://example.com/ch1/2',
        'https://example.com/ch1/3',
        '',
    ])
    eval_fn = lambda rule, html: next(next_urls)

    result = follow_content_pages(
        start_url='https://example.com/ch1/1',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    assert result == ['<p>Part 1</p>', '<p>Part 2</p>', '<p>Part 3</p>']


def test_follow_content_pages_single():
    """Single-page content with no next URL -> returns [html1]."""
    fetch_fn = lambda url: '<p>Full chapter</p>'
    eval_fn = lambda rule, html: ''

    result = follow_content_pages(
        start_url='https://example.com/chapter',
        fetch_fn=fetch_fn,
        eval_fn=eval_fn,
        next_url_rule='css:.next@href',
    )
    assert result == ['<p>Full chapter</p>']
