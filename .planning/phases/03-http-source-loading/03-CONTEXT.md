# Phase 3: HTTP + Source Loading - Context

**Gathered:** 2026-04-08 (discuss mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Fetch real novel website pages using book source headers and cookies, transcode GBK/GB2312 responses to UTF-8, and follow multi-page TOC and content chains. Wire `/novel use` to actually load and persist a book source file. No read pipeline yet — that is Phase 4.

Requirements: HTTP-01 through HTTP-05.

</domain>

<decisions>
## Implementation Decisions

### HTTP Client
- **D-01:** Use `httpx` (sync client — `httpx.Client`) as the HTTP library. Already named in PROJECT.md stack. Sync API matches the existing all-sync codebase. `charset-normalizer` ships with httpx as a bonus.
- **D-02:** Add `httpx` to `pyproject.toml` dependencies. No `requests` — httpx is the decision.

### java.ajax() Wiring
- **D-03:** Implement java.ajax() via **two-pass pre-fetch injection**. First pass: run JS with a recording stub that captures any `java.ajax(url)` calls without executing them. Second pass: fetch those URLs with the real httpx client, inject results, re-run JS with real data. This keeps HTTP logic out of `_js.py` and isolates the JS eval layer from direct HTTP calls.
- **D-04:** The pre-fetch mechanism lives in the HTTP module (`src/novel/http/`), not in `_js.py`. The `eval_js()` function in `_js.py` gains an optional `ajax_fetcher: Callable[[str], str] | None` parameter. If None (default), ajax calls raise the existing stub error. If provided, it is used for pre-fetch injection.
- **D-05:** The `_make_context()` function is updated to accept pre-fetched results dict `{url: content}` so it can inject real responses into the quickjs context for the second-pass eval.

### Encoding Detection
- **D-06:** Encoding cascade: (1) parse charset from `Content-Type` header; (2) if absent or unreliable, run `chardet.detect()` on response bytes; (3) decode with detected encoding, falling back to UTF-8 with `errors='replace'`. Most robust — handles sites that lie about their encoding.
- **D-07:** Add `chardet` to `pyproject.toml` dependencies (or use `charset-normalizer` which ships with httpx — prefer `charset-normalizer` to avoid a separate dependency). Use `charset_normalizer.from_bytes()` as the fallback detector.

### Custom Headers and Cookie Jar
- **D-08:** Parse the book source `header` field (JSON string or dict) and pass as headers to every `httpx.Client` request to that source's domain (HTTP-01).
- **D-09:** Per-source cookie jar: instantiate one `httpx.Client` per book source domain, with `follow_redirects=True`. Cookie jar is per-client, so per-source (HTTP-03).

### Pagination Helpers
- **D-10:** `follow_toc_pages(start_url, fetch_fn, next_url_field='nextTocUrl') -> list[str]` — loops fetching pages until `nextTocUrl` is empty or absent. Returns list of all raw HTML strings (HTTP-04).
- **D-11:** `follow_content_pages(start_url, fetch_fn, next_url_field='nextContentUrl') -> list[str]` — same pattern for chapter content pages (HTTP-05).
- **D-12:** `nextTocUrl` and `nextContentUrl` values from the book source may contain `{{page}}` template placeholders — apply `apply_url_template()` from `novel.rules._templates` before fetching.

### /novel use Command
- **D-13:** `/novel use <path>` loads the book source JSON (using existing `load_book_source()` from `novel.rules._source`), copies it to `~/.claude-legado/sources/<filename>`, and sets it as the active source in `state.json`.
- **D-14:** On success, print: source name, base URL, which rule fields are present (searchUrl, ruleSearch, ruleToc, ruleContent), and the stored path. Example:
  ```
  Loaded book source:
    Name:  笔趣阁
    URL:   https://www.biquge.com.cn
    Rules: searchUrl, ruleSearch, ruleToc, ruleContent ✓

  Stored: ~/.claude-legado/sources/biquge.json
  ```
- **D-15:** No connectivity ping in Phase 3. `/novel use` is offline-safe — just parse, validate, persist, and confirm.

### Module Structure
- **D-16:** New sub-package `src/novel/http/` with: `_client.py` (httpx client factory, header parsing, cookie jar), `_encoding.py` (charset detection and decoding), `_pagination.py` (nextTocUrl/nextContentUrl follow loops). Public API: `from novel.http import fetch, follow_toc_pages, follow_content_pages`.

### Claude's Discretion
- Exact `httpx.Client` instantiation pattern (singleton per source or per-call)
- Whether to validate `nextTocUrl`/`nextContentUrl` as legado rules or treat as plain URL templates
- Test fixture strategy for HTTP tests (respx mock or VCR cassettes — prefer respx since httpx is already the client)
- Exact chardet/charset-normalizer call site in `_encoding.py`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements (MANDATORY)
- `.planning/REQUIREMENTS.md` — Phase 3 covers HTTP-01 through HTTP-05. Read the full spec for each requirement.

### Project decisions
- `.planning/PROJECT.md` §Key Decisions — Python stack (httpx confirmed), sync design, chapter-per-invocation constraint
- `.planning/STATE.md` §Accumulated Context/Decisions — Phase 2 decisions on quickjs context, `java.ajax()` stub design, and the HIGH-risk note on ajax sync-in-JS

### Phase 2 context (for _js.py integration)
- `.planning/phases/02-rule-engine/02-CONTEXT.md` — D-02 (ajax stub design), D-03 (evaluate() API shape), established quickjs context pattern that Phase 3 extends

### Phase 1 context (for /novel use wiring)
- `.planning/phases/01-scaffold-display-state/01-CONTEXT.md` — D-13 (state file paths), D-16 (stub message style), commands.py dispatch pattern that Phase 3 replaces for the `use` subcommand

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/novel/rules/_source.py` — `load_book_source(path)`: parses legado JSON, validates required fields. Phase 3 `/novel use` calls this directly.
- `src/novel/rules/_templates.py` — `apply_url_template(template, params)`: `{{key}}` substitution for URL construction. Used by pagination helpers for `nextTocUrl`/`nextContentUrl`.
- `src/novel/rules/_js.py` — `_make_context()` and `eval_js()`: must be extended with optional `ajax_fetcher` parameter and pre-fetched results dict. The two-pass injection lands here.
- `src/novel/state.py` — atomic write pattern (`tmp + Path.replace()`). HTTP module's source persistence follows same pattern.
- `src/novel/commands.py` — `dispatch()`: `use` branch currently prints a stub. Phase 3 replaces it with real `_use_source()` implementation.

### Established Patterns
- All-sync execution — no `asyncio`, no `async def`. The httpx sync client (`httpx.Client`, not `httpx.AsyncClient`) matches this.
- Sub-package per concern: `src/novel/rules/`, `src/novel/data/` — new `src/novel/http/` follows the same convention.
- Module-level functions, no class instantiation at call site — `fetch(url, source)` not `HTTPClient(source).fetch(url)`.
- Fresh context per eval call (from `_js.py`) — `httpx.Client` can be instantiated per-call or shared per source; either works with sync design.

### Integration Points
- `_js.py:_make_context()` → Phase 3 adds `ajax_fetcher` optional param and pre-fetched results injection
- `commands.py:dispatch()` → `use` branch wired to `src/novel/http/_client.py` via a new `_use_source()` function
- Phase 4 will call `from novel.http import fetch, follow_toc_pages, follow_content_pages` — design the public API surface with Phase 4 in mind

</code_context>

<specifics>
## Specific Ideas

- Two-pass ajax: first pass uses a recording stub that captures URLs without fetching; second pass injects pre-fetched content back into the quickjs context. This keeps `_js.py` clean — HTTP logic stays in `src/novel/http/`.
- `/novel use` output should be informative but not verbose — list which rule fields are present (e.g., `ruleSearch ✓ / ruleToc ✓ / ruleContent ✓ / ruleBookInfo —`) so the user can immediately see if a source supports all flows.
- chardet vs charset-normalizer: prefer `charset_normalizer` since it ships with httpx. Avoids adding `chardet` as a separate dependency.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-http-source-loading*
*Context gathered: 2026-04-08*
