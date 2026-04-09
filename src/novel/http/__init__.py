"""HTTP transport layer for claude-legado.

Public API:
    fetch(url, source, timeout) -> (text, response)
    parse_source_headers(header_field) -> dict
    decode_response(content, content_type) -> str
    follow_toc_pages(start_url, fetch_fn, eval_fn, next_url_rule) -> list[str]
    follow_content_pages(start_url, fetch_fn, eval_fn, next_url_rule) -> list[str]
"""
from novel.http._client import fetch, parse_source_headers
from novel.http._encoding import decode_response
from novel.http._pagination import follow_toc_pages, follow_content_pages

__all__ = [
    'fetch', 'parse_source_headers', 'decode_response',
    'follow_toc_pages', 'follow_content_pages',
]
