"""HTTP client factory, header parsing, and fetch function (HTTP-01, HTTP-03, D-01, D-08, D-09)."""
from __future__ import annotations

import json

import httpx

from novel.http._encoding import decode_response


def parse_source_headers(header_field) -> dict:
    """Normalize a legado book source header field to a dict.

    Handles:
        - None or empty string -> {}
        - JSON string -> parsed dict (or {} on invalid JSON)
        - dict -> returned as-is
        - Other types -> {}

    Args:
        header_field: The 'header' value from a book source dict.

    Returns:
        dict of HTTP headers to send.
    """
    if header_field is None:
        return {}
    if isinstance(header_field, dict):
        return header_field
    if isinstance(header_field, str):
        if not header_field.strip():
            return {}
        try:
            parsed = json.loads(header_field)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def fetch(url: str, source: dict, timeout: float = 10.0) -> tuple[str, httpx.Response]:
    """Fetch a URL with book source headers and decode the response.

    Creates a fresh httpx.Client per call with:
        - Custom headers from the source's 'header' field
        - follow_redirects=True
        - Configurable timeout

    Args:
        url: The URL to fetch.
        source: Book source dict containing optional 'header' field.
        timeout: Request timeout in seconds (default 10.0).

    Returns:
        Tuple of (decoded_text, httpx.Response).
    """
    headers = parse_source_headers(source.get('header', {}))
    with httpx.Client(
        headers=headers,
        follow_redirects=True,
        timeout=timeout,
    ) as client:
        response = client.get(url)
        content_type = response.headers.get('content-type', '')
        text = decode_response(response.content, content_type)
        return text, response
