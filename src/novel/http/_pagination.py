"""Pagination helpers for multi-page TOC and content chains (HTTP-04, HTTP-05)."""
from __future__ import annotations

from typing import Callable

from novel.rules._templates import apply_url_template


def follow_toc_pages(
    start_url: str,
    fetch_fn: Callable[[str], str],
    eval_fn: Callable[[str, str], str],
    next_url_rule: str,
    base_url: str = '',
) -> list[str]:
    """Fetch all TOC pages following nextTocUrl until empty (HTTP-04, D-10).

    Args:
        start_url: First TOC page URL.
        fetch_fn: Callable that takes a URL and returns raw HTML string.
        eval_fn: Callable that takes (rule, html) and returns the next URL string (or '').
        next_url_rule: The legado rule expression for extracting nextTocUrl from HTML.
        base_url: Base URL for rule evaluation context.

    Returns:
        List of raw HTML strings, one per page.

    Uses a visited-set guard to prevent infinite loops on malformed sources.
    Applies apply_url_template() for {{page}} placeholders per D-12.
    """
    pages: list[str] = []
    current_url: str | None = start_url
    visited: set[str] = set()

    while current_url and current_url not in visited:
        visited.add(current_url)
        html = fetch_fn(current_url)
        pages.append(html)
        next_url = eval_fn(next_url_rule, html)
        if next_url:
            next_url = apply_url_template(next_url, {'page': len(pages) + 1})
            current_url = next_url
        else:
            current_url = None

    return pages


def follow_content_pages(
    start_url: str,
    fetch_fn: Callable[[str], str],
    eval_fn: Callable[[str, str], str],
    next_url_rule: str,
    base_url: str = '',
) -> list[str]:
    """Fetch all content pages following nextContentUrl until empty (HTTP-05, D-11).

    Symmetric to follow_toc_pages. Same visited-set guard and template substitution.
    """
    pages: list[str] = []
    current_url: str | None = start_url
    visited: set[str] = set()

    while current_url and current_url not in visited:
        visited.add(current_url)
        html = fetch_fn(current_url)
        pages.append(html)
        next_url = eval_fn(next_url_rule, html)
        if next_url:
            next_url = apply_url_template(next_url, {'page': len(pages) + 1})
            current_url = next_url
        else:
            current_url = None

    return pages
