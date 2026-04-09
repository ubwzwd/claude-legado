---
phase: 03-http-source-loading
plan: 01
subsystem: http
tags: [http, encoding, source-loading]
requires: [rules/_source.py, state.py]
provides: [http/_client.py, http/_encoding.py]
affects: [commands.py]
tech_stack:
  added: [httpx, charset-normalizer, respx]
  patterns: [per-call httpx.Client, 3-step charset cascade, basename-only copy]
key_files:
  created:
    - src/novel/http/__init__.py
    - src/novel/http/_client.py
    - src/novel/http/_encoding.py
    - tests/test_http_client.py
    - tests/test_http_encoding.py
    - tests/test_novel_use.py
  modified:
    - pyproject.toml
    - src/novel/commands.py
    - tests/test_commands.py
key_decisions:
  - "Per-call httpx.Client (context manager) — no persistent session object, matches legado's per-source-domain model"
  - "Lazy import charset_normalizer inside decode_response — avoids import-time cost for non-encoding paths"
  - "Updated test_use_stub -> test_use_dispatch since /novel use is no longer a stub"
requirements_completed: [HTTP-01, HTTP-02, HTTP-03]
duration: "7 min"
completed: "2026-04-09"
---

# Phase 03 Plan 01: HTTP Client + Encoding + /novel use Summary

HTTP transport foundation with source-aware headers, GBK encoding cascade, and working `/novel use` command.

## Duration

Started: 2026-04-09T17:51:45Z
Ended: 2026-04-09T17:58:35Z
Duration: ~7 min
Tasks: 2 | Files: 9 (6 created, 3 modified)

## What Was Built

### Task 1: HTTP Client and Encoding Sub-Package
- `src/novel/http/_client.py`: `parse_source_headers()` normalizes JSON string/dict header fields; `fetch()` creates per-call `httpx.Client` with custom headers, `follow_redirects=True`, configurable timeout, and charset-aware decoding
- `src/novel/http/_encoding.py`: `decode_response()` implements 3-step charset cascade — Content-Type charset header → charset_normalizer detection → UTF-8 replace fallback
- `pyproject.toml`: Added httpx>=0.28, charset-normalizer>=3.3, respx>=0.21
- 12 tests pass (7 client, 5 encoding)

### Task 2: Wire /novel use Command
- `src/novel/commands.py`: New `_use_source()` function loads source JSON via `load_book_source()`, copies to `~/.claude-legado/sources/` using basename-only destination (T-03-01 path traversal mitigation), sets `state['source']` as string path, prints summary with source name/URL/rule field presence
- Removed `'use'` from `STUB_COMMANDS`, dispatch routes to `_use_source(args[1:])`
- 5 new tests pass, updated 1 existing test
- Full suite: 78 tests green (61 existing + 17 new)

## Deviations from Plan

**[Rule 1 - Bug] Monkeypatch SOURCES_DIR on commands module** — Found during: Task 2 test | Issue: `SOURCES_DIR` imported at module level in `commands.py` meant monkeypatching `novel.state.SOURCES_DIR` didn't affect the already-imported reference | Fix: Added `monkeypatch.setattr(cmd_mod, 'SOURCES_DIR', sources_dir)` in test fixture | Verification: All 5 use tests pass

**Total deviations:** 1 auto-fixed (1 bug fix). **Impact:** Minimal — test-only fix, no production code change.

## Issues Encountered

None.

## Next

Ready for Plan 03-02: Pagination + ajax wiring (Wave 2).

## Self-Check: PASSED
- [x] src/novel/http/__init__.py exists
- [x] src/novel/http/_client.py exists with `def fetch(`
- [x] src/novel/http/_encoding.py exists with `def decode_response(`
- [x] tests/test_http_client.py exists with 7 tests
- [x] tests/test_http_encoding.py exists with 5 tests
- [x] tests/test_novel_use.py exists with 5 tests
- [x] git log shows commits for 03-01
- [x] Full suite 78 tests pass
