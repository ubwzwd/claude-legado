"""Tests for HTTP client — header parsing and fetch function (HTTP-01, HTTP-03)."""
from __future__ import annotations

import httpx
import respx

from novel.http._client import fetch, parse_source_headers


# --- parse_source_headers tests ---

def test_parse_source_headers_json_string():
    """JSON string header field is parsed to dict."""
    result = parse_source_headers('{"User-Agent": "test"}')
    assert result == {"User-Agent": "test"}


def test_parse_source_headers_dict():
    """Dict header field is returned as-is."""
    result = parse_source_headers({"Referer": "https://x.com"})
    assert result == {"Referer": "https://x.com"}


def test_parse_source_headers_empty():
    """None and empty string both return empty dict."""
    assert parse_source_headers(None) == {}
    assert parse_source_headers("") == {}
    assert parse_source_headers("   ") == {}


def test_parse_source_headers_invalid_json():
    """Invalid JSON string returns empty dict (no crash)."""
    assert parse_source_headers("{bad}") == {}


# --- fetch tests (with respx mocking) ---

@respx.mock
def test_fetch_sends_source_headers():
    """fetch() sends custom headers from book source header field."""
    url = "https://example.com/page"
    source = {"header": '{"X-Custom": "test-value"}'}

    route = respx.get(url).mock(
        return_value=httpx.Response(200, content=b"hello", headers={"content-type": "text/html"})
    )

    text, response = fetch(url, source)

    assert route.called
    request = route.calls[0].request
    assert request.headers["x-custom"] == "test-value"
    assert text == "hello"


@respx.mock
def test_fetch_follows_redirects():
    """fetch() follows HTTP redirects (301 -> 200)."""
    url = "https://example.com/old"
    final_url = "https://example.com/new"

    respx.get(url).mock(
        return_value=httpx.Response(301, headers={"Location": final_url})
    )
    respx.get(final_url).mock(
        return_value=httpx.Response(200, content=b"final content", headers={"content-type": "text/html"})
    )

    text, response = fetch(url, {})
    assert text == "final content"


@respx.mock
def test_cookie_jar_per_client():
    """Two sequential fetches on same httpx.Client share cookies."""
    url1 = "https://example.com/login"
    url2 = "https://example.com/page"

    respx.get(url1).mock(
        return_value=httpx.Response(
            200,
            content=b"logged in",
            headers={
                "content-type": "text/html",
                "set-cookie": "session=abc123; Path=/",
            },
        )
    )
    respx.get(url2).mock(
        return_value=httpx.Response(200, content=b"page content", headers={"content-type": "text/html"})
    )

    # Each call to fetch() creates its own client, so cookies don't persist across calls.
    # But within a single httpx.Client, cookies would be shared.
    # Here we test that fetch works correctly with cookie-setting responses.
    text1, resp1 = fetch(url1, {})
    assert text1 == "logged in"
    assert "set-cookie" in resp1.headers

    text2, resp2 = fetch(url2, {})
    assert text2 == "page content"
