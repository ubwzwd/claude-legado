# Phase 3: HTTP + Source Loading - Research

**Researched:** 2026-04-08
**Domain:** Python HTTP client (httpx), encoding detection (charset-normalizer), pagination loops, /novel use command wiring
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Use `httpx` (sync client — `httpx.Client`) as the HTTP library. Already named in PROJECT.md stack. Sync API matches the existing all-sync codebase.
- **D-02:** Add `httpx` to `pyproject.toml` dependencies. No `requests` — httpx is the decision.
- **D-03:** Implement java.ajax() via **two-pass pre-fetch injection**. First pass: run JS with a recording stub that captures any `java.ajax(url)` calls without executing them. Second pass: fetch those URLs with the real httpx client, inject results, re-run JS with real data.
- **D-04:** The pre-fetch mechanism lives in the HTTP module (`src/novel/http/`), not in `_js.py`. The `eval_js()` function in `_js.py` gains an optional `ajax_fetcher: Callable[[str], str] | None` parameter.
- **D-05:** The `_make_context()` function is updated to accept pre-fetched results dict `{url: content}` so it can inject real responses into the quickjs context for the second-pass eval.
- **D-06:** Encoding cascade: (1) parse charset from `Content-Type` header; (2) if absent or unreliable, run charset detection on response bytes; (3) decode with detected encoding, falling back to UTF-8 with `errors='replace'`.
- **D-07:** Use `charset_normalizer.from_bytes()` as the fallback detector (ships with httpx — prefer over chardet to avoid a separate dependency).
- **D-08:** Parse the book source `header` field (JSON string or dict) and pass as headers to every `httpx.Client` request to that source's domain (HTTP-01).
- **D-09:** Per-source cookie jar: instantiate one `httpx.Client` per book source domain, with `follow_redirects=True`. Cookie jar is per-client, so per-source (HTTP-03).
- **D-10:** `follow_toc_pages(start_url, fetch_fn, next_url_field='nextTocUrl') -> list[str]` — loops fetching pages until `nextTocUrl` is empty or absent. Returns list of all raw HTML strings (HTTP-04).
- **D-11:** `follow_content_pages(start_url, fetch_fn, next_url_field='nextContentUrl') -> list[str]` — same pattern for chapter content pages (HTTP-05).
- **D-12:** `nextTocUrl` and `nextContentUrl` values from the book source may contain `{{page}}` template placeholders — apply `apply_url_template()` from `novel.rules._templates` before fetching.
- **D-13:** `/novel use <path>` loads the book source JSON (using existing `load_book_source()` from `novel.rules._source`), copies it to `~/.claude-legado/sources/<filename>`, and sets it as the active source in `state.json`.
- **D-14:** On success, print: source name, base URL, which rule fields are present, and the stored path.
- **D-15:** No connectivity ping in Phase 3. `/novel use` is offline-safe — just parse, validate, persist, and confirm.
- **D-16:** New sub-package `src/novel/http/` with: `_client.py`, `_encoding.py`, `_pagination.py`. Public API: `from novel.http import fetch, follow_toc_pages, follow_content_pages`.

### Claude's Discretion

- Exact `httpx.Client` instantiation pattern (singleton per source or per-call)
- Whether to validate `nextTocUrl`/`nextContentUrl` as legado rules or treat as plain URL templates
- Test fixture strategy for HTTP tests (respx mock or VCR cassettes — prefer respx since httpx is already the client)
- Exact chardet/charset-normalizer call site in `_encoding.py`

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HTTP-01 | Fetch URLs with custom headers from book source `header` field | D-08: parse header field (JSON string or dict), pass to httpx.Client constructor; verified header propagation via respx mock |
| HTTP-02 | Auto-detect and transcode GBK/GB2312 responses to UTF-8 | D-06/D-07: Content-Type header cascade + charset_normalizer.from_bytes() fallback; verified with real GBK bytes |
| HTTP-03 | Cookie jar per book source domain | D-09: one httpx.Client per source domain; httpx.Client.cookies is per-client; verified via tool |
| HTTP-04 | Follow multi-page TOC (`nextTocUrl`) until empty | D-10/D-12: follow loop with visited-set guard; apply_url_template() for {{page}}; loop pattern verified |
| HTTP-05 | Follow multi-page chapter content (`nextContentUrl`) until empty | D-11/D-12: same pattern as HTTP-04; symmetric implementation |
</phase_requirements>

---

## Summary

Phase 3 adds the HTTP transport layer to the existing all-sync Python codebase. The core machinery is `httpx.Client` (already installed, version 0.28.1), `charset-normalizer` for encoding detection (not yet in pyproject.toml), and `respx` for test mocking (not yet in pyproject.toml). All three are available via pip.

The most complex piece is the two-pass java.ajax() injection (D-03 through D-05). This was verified working: a recording stub captures URL calls in the first pass, then a prefetched dict is injected into a fresh quickjs context for the second pass. The existing `_make_context()` and `eval_js()` functions need minimal surgery — an optional `ajax_fetcher` parameter and an optional `prefetched` dict parameter.

The `/novel use` command replaces the current stub in `commands.py`. It reuses `load_book_source()` from `novel.rules._source`, copies the file to `~/.claude-legado/sources/`, and writes the active source path into `state.json`. No HTTP call is made — the command is intentionally offline-safe.

**Primary recommendation:** Build the three sub-modules in dependency order — `_encoding.py` (no deps), `_client.py` (uses encoding), `_pagination.py` (uses client + rules._templates) — then wire `/novel use` in `commands.py` and extend `_js.py` last (ajax injection).

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28.1 | Sync HTTP client with headers, cookies, redirects | Locked decision D-01; already installed system-wide |
| charset-normalizer | 3.4.7 | Encoding detection for GBK/GB2312 responses | Locked decision D-07; avoids chardet dependency; httpx recommends it |
| respx | 0.23.1 | Mock httpx in tests without network | Designed for httpx; supports header assertions; no cassette files needed |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (built-in) re | stdlib | Parse charset from Content-Type header | Always — step 1 of encoding cascade |
| (built-in) json | stdlib | Parse book source `header` field from JSON string | In _client.py header normalization |
| (built-in) shutil / pathlib | stdlib | Copy source file to ~/.claude-legado/sources/ | In /novel use implementation |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| charset-normalizer | chardet | chardet adds a dependency; charset-normalizer is already the httpx recommendation and available |
| respx | pytest-recording (VCR) | VCR requires real network hit to record; respx is inline and httpx-native |
| per-call client | cached per-domain singleton | Singleton complicates test isolation; per-call (or per-request-group) is simpler and verified working |

**Installation (additions to pyproject.toml):**
```bash
pip install charset-normalizer respx
```

**Version verification:** [VERIFIED: pip index versions 2026-04-08]
- httpx 0.28.1 — already installed
- charset-normalizer 3.4.7 — latest available
- respx 0.23.1 — latest available

---

## Architecture Patterns

### Recommended Project Structure

```
src/novel/http/
├── __init__.py          # Public API: fetch, follow_toc_pages, follow_content_pages
├── _client.py           # httpx.Client factory, header parsing, fetch() function
├── _encoding.py         # charset detection and decode_response() function
└── _pagination.py       # follow_toc_pages(), follow_content_pages()
```

The new sub-package follows the exact same convention as `src/novel/rules/` (underscore-prefixed private modules, clean `__init__.py` public surface).

### Pattern 1: Header Normalization

The book source `header` field arrives as either a JSON-encoded string or a plain dict. Always normalize to dict before passing to httpx.

```python
# Source: verified against real legado book source format + json stdlib
import json

def parse_source_headers(header_field) -> dict:
    """Normalize book source header field to plain dict."""
    if not header_field:
        return {}
    if isinstance(header_field, str):
        try:
            parsed = json.loads(header_field)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    if isinstance(header_field, dict):
        return header_field
    return {}
```

[VERIFIED: tested against legado JSON format; json.loads of JSON string produces dict]

### Pattern 2: Encoding Cascade

```python
# Source: verified via charset_normalizer 3.4.7 + re stdlib
import re
from charset_normalizer import from_bytes

def decode_response(content: bytes, content_type: str = '') -> str:
    """Decode response bytes to UTF-8 string using encoding cascade.

    1. Parse charset from Content-Type header.
    2. Fall back to charset_normalizer.from_bytes() detection.
    3. Fall back to UTF-8 with errors='replace'.
    """
    # Step 1: parse Content-Type header
    m = re.search(r'charset=([\\w-]+)', content_type, re.IGNORECASE)
    if m:
        charset = m.group(1).lower()
        try:
            return content.decode(charset)
        except (UnicodeDecodeError, LookupError):
            pass  # fall through to detection

    # Step 2: charset_normalizer detection
    result = from_bytes(content)
    best = result.best()
    if best:
        return str(best)

    # Step 3: UTF-8 fallback
    return content.decode('utf-8', errors='replace')
```

[VERIFIED: charset_normalizer.from_bytes() returns Result; .best() returns Match or None; str(match) gives decoded string — confirmed via testing]

**Critical finding:** `charset_normalizer` detection on short GBK strings (< ~50 chars) may misidentify encoding (detected big5hkscs for 6-char GBK string, correctly detected gb18030 for longer string). The Content-Type header step is critical for reliability — most novel sites declare `charset=gbk` or `charset=gb2312` in their Content-Type. The fallback detection is only for sites that omit the charset declaration.

### Pattern 3: httpx.Client per Source

```python
# Source: verified against httpx 0.28.1 API
import httpx

def make_client(source_headers: dict, timeout: float = 10.0) -> httpx.Client:
    """Create an httpx.Client with source-specific headers and cookie jar.

    Returns a context-manager-compatible client. Caller is responsible
    for closing (use as context manager or call .close()).
    Cookie jar is per-client instance — satisfies HTTP-03.
    """
    return httpx.Client(
        headers=source_headers,
        follow_redirects=True,
        timeout=timeout,
    )
```

[VERIFIED: httpx.Client(headers=..., follow_redirects=True) accepted; cookies are per-client instance (httpx.Cookies); confirmed via tool execution]

The `follow_redirects=False` default in httpx 0.27+ must be overridden — novel sites frequently redirect.

### Pattern 4: Two-Pass Ajax Injection

```python
# Source: verified via quickjs 3.0.1 + patterns from _js.py
# First pass — recording stub captures called URLs
captured: list[str] = []

def recording_ajax(url: str) -> str:
    captured.append(url)
    return ''  # Don't raise — let JS continue

ctx_record = _make_context(result, base_url, ajax_fetcher=recording_ajax)
try:
    ctx_record.eval(code)
except Exception:
    pass  # JS may fail on empty ajax returns; that's expected

# Fetch captured URLs
prefetched = {url: fetch(url, client) for url in captured}

# Second pass — inject real data
ctx_real = _make_context(result, base_url, prefetched=prefetched)
return_val = ctx_real.eval(code)  # or ctx_real.get('result') for block mode
```

[VERIFIED: recording stub + prefetched dict injection confirmed working via tool execution against quickjs 3.0.1]

**Important:** The `_make_context()` signature change must remain backward-compatible. Both new parameters default to `None`, preserving existing behavior (ajax raises JSException when both are None).

### Pattern 5: Pagination Loop

```python
# Source: verified logic pattern via respx mock test
def follow_toc_pages(
    start_url: str,
    fetch_fn,           # Callable[[str], str] — returns raw HTML
    eval_fn,            # Callable[[str, str], str] — evaluates nextTocUrl rule
    next_url_rule: str,
    base_url: str,
) -> list[str]:
    """Fetch all TOC pages, following nextTocUrl until empty.

    Uses visited-set guard to prevent infinite loops on malformed sources.
    Returns list of raw HTML strings (one per page).
    """
    pages: list[str] = []
    current_url = start_url
    visited: set[str] = set()

    while current_url and current_url not in visited:
        visited.add(current_url)
        html = fetch_fn(current_url)
        pages.append(html)
        next_url = eval_fn(next_url_rule, html)
        if next_url:
            next_url = apply_url_template(next_url, {'page': len(pages) + 1})
        current_url = next_url or None

    return pages
```

[VERIFIED: loop logic verified; visited-set prevents infinite loops; apply_url_template integration confirmed from _templates.py]

D-12 notes that `nextTocUrl`/`nextContentUrl` values may contain `{{page}}` placeholders. The `apply_url_template()` from `novel.rules._templates` handles this with no modification needed.

### Pattern 6: /novel use Command

```python
# Source: derived from existing patterns in commands.py, state.py, _source.py
import shutil
from pathlib import Path
from novel.rules._source import load_book_source
from novel.state import load_state, save_state, SOURCES_DIR, ensure_dirs

RULE_FIELDS = ['searchUrl', 'ruleSearch', 'ruleBookInfo', 'ruleToc', 'ruleContent']

def _use_source(args: list[str]) -> None:
    if not args:
        print("Usage: /novel use <path-to-source.json>")
        return
    path = Path(args[0])
    source = load_book_source(path)  # raises ValueError/OSError on failure

    ensure_dirs()
    dest = SOURCES_DIR / path.name
    shutil.copy2(path, dest)

    state = load_state()
    state['source'] = str(dest)
    save_state(state)

    rules_present = [f for f in RULE_FIELDS if source.get(f)]
    rules_absent  = [f for f in RULE_FIELDS if not source.get(f)]

    print(f"Loaded book source:")
    print(f"  Name:  {source['bookSourceName']}")
    print(f"  URL:   {source['bookSourceUrl']}")
    rules_line = ', '.join([f"{f} ✓" for f in rules_present] +
                           [f"{f} —" for f in rules_absent])
    print(f"  Rules: {rules_line}")
    print(f"\nStored: {dest}")
```

[VERIFIED: load_book_source(), save_state(), SOURCES_DIR all confirmed present in existing codebase]

### Anti-Patterns to Avoid

- **Async httpx:** Do not use `httpx.AsyncClient`. The entire codebase is synchronous and there is no event loop. Using async would require restructuring every call site.
- **Short-content charset detection:** Do not rely solely on charset_normalizer for short responses (< 100 bytes). The header cascade is the reliable path — detection is a fallback only.
- **Mutable default headers:** Do not pass a mutable dict as a default argument to make_client(). Always create headers fresh per call.
- **Skipping visited-set in pagination:** Without a visited-set, a malformed source with a self-referential nextTocUrl causes infinite loops. Always guard.
- **String concatenation for URLs:** Never construct next-page URLs by string concatenation. Always use `apply_url_template()` or the raw URL value from rule evaluation.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Encoding detection | Custom byte-sniffing logic | `charset_normalizer.from_bytes()` | Handles BOM, GB18030 superset, statistical analysis — correct in edge cases |
| Cookie handling | Manual Set-Cookie header parsing | `httpx.Client` cookie jar | RFC 6265 compliance, domain scoping, secure flag handling |
| Redirect following | Manual Location header chasing | `httpx.Client(follow_redirects=True)` | Handles relative redirects, loop detection, method preservation |
| HTTP mock in tests | Recording real responses to files | `respx` mock library | No network dependency, reproducible, fast, httpx-native API |
| URL percent-encoding | Manual urllib.parse.quote calls | httpx internal handling | httpx encodes params correctly when passed as dict |

**Key insight:** httpx handles the complex parts of HTTP correctly by default. The only custom logic needed is the encoding cascade (step 1: Content-Type header; step 2: charset_normalizer fallback) because novel sites frequently declare wrong or absent charsets.

---

## Common Pitfalls

### Pitfall 1: Short GBK strings fool charset_normalizer

**What goes wrong:** `charset_normalizer.from_bytes()` misidentifies encoding on responses shorter than ~100 bytes. Tested: a 6-character GBK string was detected as big5hkscs; a 40-character GBK string correctly detected as gb18030.
**Why it happens:** Statistical detection needs sufficient sample size to discriminate between CJK encodings.
**How to avoid:** Always parse Content-Type header first (step 1 of cascade). charset_normalizer is step 2 only. Most novel sites declare charset=gbk or charset=gb2312 explicitly.
**Warning signs:** Garbled output for short responses, or incorrect detection on test fixtures with minimal content.

[VERIFIED: reproduced via tool execution]

### Pitfall 2: httpx follow_redirects is False by default since 0.20+

**What goes wrong:** Requests to novel sites that issue 301/302 redirects return the redirect response, not the destination — `response.status_code == 301` and `response.content` is empty or minimal.
**Why it happens:** httpx changed the default to `follow_redirects=False` in 0.20.0 as a security-conscious default.
**How to avoid:** Always instantiate `httpx.Client(follow_redirects=True)`. This is captured in D-09.
**Warning signs:** Empty or very short response bodies; status codes 301/302 in tests.

[VERIFIED: httpx 0.28.1 — follow_redirects defaults to False per constructor signature]

### Pitfall 3: gb18030 is a superset of GBK — decode with gb18030 is safe for GBK content

**What goes wrong:** Attempting to decode gb18030-detected content with strict 'gbk' codec fails for characters in the gb18030 extension range.
**Why it happens:** gb18030 extends GBK; all GBK bytes are valid gb18030, but not vice versa.
**How to avoid:** If charset_normalizer detects gb18030, use gb18030 for decoding (not gbk). Python's codec handles this correctly — `bytes.decode('gb18030')` works for all GBK content.
**Warning signs:** UnicodeDecodeError when decoding with 'gbk' on content that charset_normalizer detected as 'gb18030'.

[VERIFIED: charset_normalizer detected gb18030 for GBK test bytes; Python gb18030 codec is a superset]

### Pitfall 4: Two-pass ajax — first pass JS may raise on empty return value

**What goes wrong:** If the JS code uses the ajax result immediately (e.g., `JSON.parse(java.ajax(url))`), the recording stub returns `''` and `JSON.parse('')` throws a JS exception. The first-pass context throws before all `java.ajax()` calls are recorded.
**Why it happens:** The recording stub returns empty string to avoid side effects, but JS code that processes the result immediately will fail.
**How to avoid:** Wrap first-pass eval in a try/except. The goal of the first pass is only to capture URLs — a thrown exception after capturing some URLs is acceptable. Use the captured list even if the first pass raises.
**Warning signs:** Test reveals some ajax URLs not captured when JS code chains calls.

[VERIFIED: pattern confirmed via quickjs testing]

### Pitfall 5: /novel use — state['source'] key must be a string path, not a Path object

**What goes wrong:** Storing a `pathlib.Path` object in state dict causes `json.JSONDecodeError` on reload because Path is not JSON-serializable.
**Why it happens:** `save_state()` uses `json.dumps()` which rejects non-serializable types.
**How to avoid:** Always `str(dest)` before storing in state dict. The existing state.py pattern uses `ensure_ascii=False` but does not handle non-serializable types.
**Warning signs:** `TypeError: Object of type PosixPath is not JSON serializable` on save.

[VERIFIED: confirmed by reading state.py — json.dumps with no custom encoder]

---

## Code Examples

### Fetch with source headers (HTTP-01, HTTP-03)

```python
# Source: verified against httpx 0.28.1 API
import httpx
import json

def fetch(url: str, source: dict, timeout: float = 10.0) -> httpx.Response:
    """Fetch a URL using headers and cookie jar from book source."""
    raw_header = source.get('header', {})
    if isinstance(raw_header, str):
        try:
            headers = json.loads(raw_header)
        except json.JSONDecodeError:
            headers = {}
    elif isinstance(raw_header, dict):
        headers = raw_header
    else:
        headers = {}

    with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as client:
        return client.get(url)
```

### Decode GBK response (HTTP-02)

```python
# Source: verified via charset_normalizer 3.4.7 + re stdlib
import re
from charset_normalizer import from_bytes

def decode_response(content: bytes, content_type: str = '') -> str:
    m = re.search(r'charset=([\w-]+)', content_type, re.IGNORECASE)
    if m:
        charset = m.group(1).lower()
        try:
            return content.decode(charset)
        except (UnicodeDecodeError, LookupError):
            pass
    result = from_bytes(content)
    best = result.best()
    if best:
        return str(best)
    return content.decode('utf-8', errors='replace')
```

### respx mock for HTTP tests

```python
# Source: verified against respx 0.23.1 + httpx 0.28.1
import respx
import httpx

def test_fetch_sends_source_headers():
    with respx.mock:
        route = respx.get('https://example.com/toc').mock(
            return_value=httpx.Response(200, text='<html>...</html>')
        )
        response = fetch('https://example.com/toc', source={'header': '{"User-Agent": "test"}'})
        assert route.called
        assert route.calls.last.request.headers['user-agent'] == 'test'
```

### _make_context extension (D-04, D-05)

```python
# Source: verified via quickjs 3.0.1; extends existing _js.py pattern
from __future__ import annotations
from typing import Callable

def _make_context(
    result: str,
    base_url: str,
    ajax_fetcher: Callable[[str], str] | None = None,
    prefetched: dict[str, str] | None = None,
) -> quickjs.Context:
    ctx = quickjs.Context()
    ctx.set('result', result)
    ctx.set('baseUrl', base_url)

    def _base64_decode(s: str) -> str: ...
    def _md5(s: str) -> str: ...

    if ajax_fetcher is not None:
        def _ajax(url: str) -> str:
            return ajax_fetcher(url)
    elif prefetched is not None:
        def _ajax(url: str) -> str:
            return prefetched.get(url, '')
    else:
        def _ajax(url: str) -> str:
            raise NotImplementedError('java.ajax not available until Phase 3')

    ctx.add_callable('_javaBase64Decode', _base64_decode)
    ctx.add_callable('_javaMd5', _md5)
    ctx.add_callable('_javaAjax', _ajax)
    ctx.eval('var java = { base64Decode: _javaBase64Decode, md5: _javaMd5, ajax: _javaAjax };')
    return ctx
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| requests library | httpx | Project init decision | httpx is the project standard; requests not used |
| chardet | charset-normalizer | httpx default since ~2022 | Same API shape; charset-normalizer is maintained by httpx team |
| follow_redirects=True default | follow_redirects=False default | httpx 0.20.0 | Must explicitly set True or all redirects return 30x |
| VCR cassettes | respx inline mock | respx 0.20+ | No file cassettes needed; inline mock is simpler |

**Deprecated/outdated:**
- chardet: Not wrong, but charset-normalizer is the modern replacement with active maintenance and httpx integration.
- Manually setting `httpx.Client.cookies`: Not needed — httpx.Client maintains its own cookie jar automatically across requests.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Book source `header` field arrives as JSON string or dict (not other types) | Pattern 1 | If it can be a list or null-encoded, parse_source_headers() needs more guards |
| A2 | `nextTocUrl` rule evaluation produces a plain URL string (not a legado rule expression requiring further evaluation) | Pattern 5 | If nextTocUrl is itself a legado rule (e.g., `css:a.next@href`), the pagination loop needs to call `evaluate()` not just `apply_url_template()` |
| A3 | Novel sites that use GBK declare it in Content-Type header in the majority of cases | Pitfall 1 | If most sites omit the header, charset_normalizer short-content failures become more common |

---

## Open Questions

1. **Does nextTocUrl produce a plain URL or a legado rule expression?**
   - What we know: D-12 says it may contain `{{page}}` placeholders and calls `apply_url_template()`.
   - What's unclear: Is `nextTocUrl` the raw URL template directly, or the result of evaluating a rule against the current page's HTML?
   - Recommendation: In Phase 3, treat it as a plain URL template (apply_url_template only). Phase 4 will clarify when wiring `ruleToc` evaluation. This is captured as A2 above.

2. **httpx.Client lifecycle — per-call or held open across a session?**
   - What we know: Claude's Discretion area. Per-call is simpler and test-safe. Held-open reuses connections (performance) but complicates isolation.
   - Recommendation: Per-call (one `with httpx.Client() as client:` per fetch call). At the chapter-per-invocation scale of this tool, connection reuse is negligible. Simplicity wins.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| httpx | HTTP client (all HTTP reqs) | ✓ | 0.28.1 | — |
| charset-normalizer | HTTP-02 encoding detection | ✗ (not in pyproject.toml) | 3.4.7 available | — (required, no fallback) |
| respx | Test mocking | ✗ (not in pyproject.toml) | 0.23.1 available | — (required for tests) |
| Python 3.12 | Project minimum | ✓ | 3.12 (system) | — |

**Missing dependencies with no fallback:**
- `charset-normalizer` — must be added to `pyproject.toml` dependencies
- `respx` — must be added to `pyproject.toml` dev/test dependencies (or as a regular dep; project currently has no `[project.optional-dependencies]`)

**Missing dependencies with fallback:**
- None.

[VERIFIED: pip index versions 2026-04-08; system python3 confirmed present]

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in use) |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `PYTHONPATH=src python3 -m pytest tests/test_http*.py -x -q` |
| Full suite command | `PYTHONPATH=src python3 -m pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HTTP-01 | Custom headers sent with every request | unit | `pytest tests/test_http_client.py::test_fetch_sends_source_headers -x` | ❌ Wave 0 |
| HTTP-01 | Header field parsed from JSON string | unit | `pytest tests/test_http_client.py::test_parse_source_headers_json_string -x` | ❌ Wave 0 |
| HTTP-01 | Header field parsed from dict | unit | `pytest tests/test_http_client.py::test_parse_source_headers_dict -x` | ❌ Wave 0 |
| HTTP-02 | GBK response decoded to correct UTF-8 | unit | `pytest tests/test_http_encoding.py::test_decode_gbk_response -x` | ❌ Wave 0 |
| HTTP-02 | Content-Type charset header used first | unit | `pytest tests/test_http_encoding.py::test_decode_uses_content_type_charset -x` | ❌ Wave 0 |
| HTTP-02 | Falls back to charset_normalizer when no header | unit | `pytest tests/test_http_encoding.py::test_decode_fallback_charset_normalizer -x` | ❌ Wave 0 |
| HTTP-02 | UTF-8 replace fallback on undetectable content | unit | `pytest tests/test_http_encoding.py::test_decode_utf8_fallback -x` | ❌ Wave 0 |
| HTTP-03 | Cookie jar is per-client (per-source) | unit | `pytest tests/test_http_client.py::test_cookie_jar_per_client -x` | ❌ Wave 0 |
| HTTP-04 | follow_toc_pages fetches all pages until nextTocUrl empty | unit | `pytest tests/test_http_pagination.py::test_follow_toc_pages_two_pages -x` | ❌ Wave 0 |
| HTTP-04 | follow_toc_pages stops on already-visited URL | unit | `pytest tests/test_http_pagination.py::test_follow_toc_pages_visited_guard -x` | ❌ Wave 0 |
| HTTP-05 | follow_content_pages same pattern as toc | unit | `pytest tests/test_http_pagination.py::test_follow_content_pages -x` | ❌ Wave 0 |
| SKILL-08 | /novel use loads source and stores to sources/ | integration | `pytest tests/test_novel_use.py::test_use_loads_and_persists_source -x` | ❌ Wave 0 |
| SKILL-08 | /novel use prints correct summary output | unit | `pytest tests/test_novel_use.py::test_use_prints_summary -x` | ❌ Wave 0 |
| SKILL-08 | /novel use with no args prints usage | unit | `pytest tests/test_novel_use.py::test_use_no_args -x` | ❌ Wave 0 |
| D-04/D-05 | eval_js ajax_fetcher param wires into context | unit | `pytest tests/test_rules_js.py::test_eval_js_ajax_fetcher -x` | ❌ Wave 0 |
| D-04/D-05 | eval_js prefetched dict injection | unit | `pytest tests/test_rules_js.py::test_eval_js_prefetched -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `PYTHONPATH=src python3 -m pytest tests/ -x -q`
- **Per wave merge:** `PYTHONPATH=src python3 -m pytest tests/ -x -q`
- **Phase gate:** Full suite green (all 61 existing + all new Phase 3 tests) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_http_client.py` — covers HTTP-01, HTTP-03
- [ ] `tests/test_http_encoding.py` — covers HTTP-02
- [ ] `tests/test_http_pagination.py` — covers HTTP-04, HTTP-05
- [ ] `tests/test_novel_use.py` — covers SKILL-08 (/novel use command)
- [ ] Two new test cases in `tests/test_rules_js.py` — covers D-04/D-05 (_make_context extension)

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth in Phase 3 |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A — local CLI tool |
| V5 Input Validation | yes | Validate source JSON before use; validate URL before fetch |
| V6 Cryptography | no | N/A — no crypto in Phase 3 |

### Known Threat Patterns for HTTP client + local file loading

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SSRF via malicious book source URL | Spoofing / Tampering | httpx follows redirects within allowed scope; no mitigation needed at this layer — Phase 5 hardening scope |
| Path traversal in source file copy | Tampering | Use `Path(args[0]).name` (basename only) for dest filename; do not trust full user-supplied path as destination |
| Malformed JSON in source `header` field | Tampering | Wrap json.loads in try/except, return {} on failure |
| Infinite redirect loop | Denial of Service | httpx.Client has `max_redirects=20` default — no extra guard needed |

**Path traversal note:** When copying the source file to `~/.claude-legado/sources/`, use `path.name` (just the filename, not the full path) as the destination filename. Do not use `str(path)` as the dest component — a source file at `../../.bashrc` should copy as `.bashrc` to sources/, not overwrite `~/.bashrc`. [ASSUMED — standard path-copy best practice; not a specific httpx/legado vulnerability]

---

## Sources

### Primary (HIGH confidence)
- httpx 0.28.1 — installed locally; constructor signature verified via `help(httpx.Client.__init__)`
- charset-normalizer 3.4.7 — pip index versions verified; behavior tested via Python REPL
- respx 0.23.1 — pip index versions verified; mock patterns tested via Python REPL
- quickjs 3.0.1 — two-pass ajax injection pattern verified via Python REPL against existing `_js.py`
- Existing codebase — `_source.py`, `_templates.py`, `_js.py`, `state.py`, `commands.py` all read directly

### Secondary (MEDIUM confidence)
- httpx changelog: follow_redirects default changed to False in 0.20.0 [ASSUMED — training knowledge, not re-verified in this session]

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages version-verified via pip, behavior tested locally
- Architecture: HIGH — patterns verified by running actual Python code against installed packages
- Pitfalls: HIGH — encoding pitfall reproduced empirically; redirect pitfall confirmed via API inspection

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (stable ecosystem — httpx/charset-normalizer/respx have slow release cadence)
