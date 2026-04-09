---
phase: 03-http-source-loading
plan: 02
subsystem: http, rules
tags: [pagination, ajax, js-engine]
requires: [http/_client.py, rules/_templates.py]
provides: [http/_pagination.py]
affects: [rules/_js.py]
tech_stack:
  added: []
  patterns: [visited-set pagination guard, two-pass ajax injection, callable injection via quickjs]
key_files:
  created:
    - src/novel/http/_pagination.py
    - tests/test_http_pagination.py
  modified:
    - src/novel/http/__init__.py
    - src/novel/rules/_js.py
    - tests/test_rules_js.py
key_decisions:
  - "Symmetric follow_toc_pages/follow_content_pages functions — same logic, separate names for clarity"
  - "ajax_fetcher and prefetched are mutually exclusive modes — fetcher takes precedence if both provided"
requirements_completed: [HTTP-04, HTTP-05]
duration: "4 min"
completed: "2026-04-09"
---

# Phase 03 Plan 02: Pagination + Ajax Wiring Summary

Multi-page TOC/content pagination loops and two-pass ajax injection for the JS engine.

## Duration

Started: 2026-04-09T17:59:39Z
Ended: 2026-04-09T18:03:10Z
Duration: ~4 min
Tasks: 2 | Files: 5 (2 created, 3 modified)

## What Was Built

### Task 1: Pagination Helpers
- `src/novel/http/_pagination.py`: `follow_toc_pages()` and `follow_content_pages()` traverse pagination chains using `fetch_fn` and `eval_fn` callables
- Both use visited-set guard to prevent infinite loops on self-referential URLs (T-03-06)
- `apply_url_template()` handles `{{page}}` placeholders in next URLs (D-12)
- Updated `http/__init__.py` with new exports
- 6 pagination tests pass

### Task 2: Two-Pass Ajax Injection
- Extended `_make_context()` with `ajax_fetcher` and `prefetched` optional parameters
- `ajax_fetcher` mode: recording callable invoked when `java.ajax()` called in JS (pass 1 — URL capture)
- `prefetched` mode: dict lookup returns pre-fetched content when `java.ajax()` called (pass 2 — injection)
- Backward compatible: without either parameter, `java.ajax()` still raises `NotImplementedError` → `JSException`
- Extended `eval_js()` to forward both parameters through to `_make_context()`
- 3 new tests pass (recording, injection, backward compat), all 8 JS tests green

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next

Phase 03 complete, ready for verification.

## Self-Check: PASSED
- [x] src/novel/http/_pagination.py exists with `def follow_toc_pages(`
- [x] src/novel/http/_pagination.py contains `visited: set[str] = set()`
- [x] src/novel/http/_pagination.py contains `apply_url_template(`
- [x] src/novel/rules/_js.py contains `ajax_fetcher: Callable`
- [x] src/novel/rules/_js.py contains `prefetched: dict`
- [x] tests/test_http_pagination.py contains 6 tests
- [x] tests/test_rules_js.py contains 8 tests (5 existing + 3 new)
- [x] git log shows commits for 03-02
- [x] Full suite 87 tests pass
