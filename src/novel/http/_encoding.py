"""Charset detection and decode cascade for HTTP responses (HTTP-02, D-06, D-07)."""
from __future__ import annotations

import re


def decode_response(content: bytes, content_type: str = '') -> str:
    """Decode HTTP response bytes to a Python string.

    Three-step cascade:
        1. Parse charset from Content-Type header (e.g. 'text/html; charset=gbk')
        2. Detect charset via charset_normalizer library
        3. Fall back to UTF-8 with replacement characters

    Args:
        content: Raw response bytes.
        content_type: Value of the Content-Type HTTP header (may be empty).

    Returns:
        Decoded string.
    """
    # Step 1: Content-Type charset header
    match = re.search(r'charset=([\w-]+)', content_type, re.IGNORECASE)
    if match:
        charset = match.group(1)
        try:
            return content.decode(charset)
        except (UnicodeDecodeError, LookupError):
            pass  # fall through to step 2

    # Step 2: charset_normalizer detection
    from charset_normalizer import from_bytes
    result = from_bytes(content)
    best = result.best()
    if best is not None:
        return str(best)

    # Step 3: UTF-8 with replacement characters
    return content.decode('utf-8', errors='replace')
