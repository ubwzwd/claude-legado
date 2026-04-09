"""HTTP transport layer for claude-legado.

Public API:
    fetch(url, source, timeout) -> (text, response)
    parse_source_headers(header_field) -> dict
    decode_response(content, content_type) -> str
"""
from novel.http._client import fetch, parse_source_headers
from novel.http._encoding import decode_response

__all__ = ['fetch', 'parse_source_headers', 'decode_response']
