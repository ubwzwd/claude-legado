---
phase: 02-rule-engine
plan: "04"
subsystem: rules
tags: [js-eval, quickjs, rule-engine, java-bridge]
dependency_graph:
  requires: [02-02, 02-03]
  provides: [full-evaluate-dispatcher, eval_js]
  affects: [evaluate, evaluate_list, novel.rules._js]
tech_stack:
  added: [quickjs]
  patterns: [fresh-context-per-call, java-bridge-via-add_callable]
key_files:
  created:
    - src/novel/rules/_js.py
  modified:
    - src/novel/rules/__init__.py
    - tests/test_rules_js.py
    - tests/test_rules_skeleton.py
decisions:
  - "Fresh quickjs.Context per eval_js call — no global state leakage between rule evaluations"
  - "java.ajax() raises NotImplementedError surfacing as quickjs.JSException per D-02"
  - "Stale xfail stub test updated to verify correct CSS behavior (Rule 1)"
metrics:
  duration: ~15min
  completed: 2026-04-08
  tasks_completed: 2
  files_created: 1
  files_modified: 3
requirements:
  - SRC-07
  - SRC-08
  - SRC-09
---

# Phase 2 Plan 04: JS Evaluation Layer and Full evaluate() Dispatcher Summary

**One-liner:** quickjs-based JS rule evaluator with java.{base64Decode,md5,ajax} bridge, completing the five-rule evaluate() dispatcher.

## What Was Built

`src/novel/rules/_js.py` provides `eval_js(code, result, base_url, mode)` which evaluates legado JS rules via a fresh `quickjs.Context` per call. The `_make_context()` helper injects `result` (content string), `baseUrl`, and a `java` object with three bridge methods.

`src/novel/rules/__init__.py` now fully dispatches all five rule types — CSS, XPath, JSONPath, JS_INLINE, JS_BLOCK — in both `evaluate()` and `evaluate_list()`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement _js.py — quickjs context, java bridge, eval_js() | 031b5a9 | src/novel/rules/_js.py, tests/test_rules_js.py |
| 2 | Wire JS rules into evaluate() / evaluate_list() and run full suite | 57c2af1 | src/novel/rules/__init__.py, tests/test_rules_skeleton.py |

## Verification

Full test suite: `PYTHONPATH=src pytest tests/ -x -q` — **61 passed, 0 failed, 0 errors**.

Smoke test confirmed:
- `evaluate('css:.title@text', html)` → `道可道，非常道`
- `evaluate('@js: result.trim()', '  hello  ')` → `hello`
- `evaluate('<js>result = result.toUpperCase();</js>', 'hello')` → `HELLO`
- `evaluate_list('css:a.chapter@href', toc_html)` → `['/chapter/1', '/chapter/2', '/chapter/3']`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated stale xfail test markers in test_rules_js.py**
- **Found during:** Task 1 verification
- **Issue:** Five tests in `tests/test_rules_js.py` were marked `@pytest.mark.xfail(strict=True)` — once `_js.py` was created, passing tests cause pytest to report them as `XPASS(strict)` failures
- **Fix:** Removed `xfail` markers from all 5 tests — tests now run normally and pass
- **Files modified:** `tests/test_rules_js.py`
- **Commit:** 031b5a9

**2. [Rule 1 - Bug] Updated stale stub test in test_rules_skeleton.py**
- **Found during:** Task 2 verification
- **Issue:** `test_evaluate_raises_not_implemented` expected `evaluate('css:.title@text', ...)` to raise `NotImplementedError` — it was written during plan 02-01 when everything was a stub, but CSS was wired in 02-02
- **Fix:** Renamed to `test_evaluate_css_works` and updated assertion to verify the CSS rule returns the matched text `'X'`
- **Files modified:** `tests/test_rules_skeleton.py`
- **Commit:** 57c2af1

## Known Stubs

None — all five rule types are fully wired. `evaluate()` and `evaluate_list()` have no remaining `NotImplementedError` stubs.

## Threat Flags

No new threat surface beyond what was documented in the plan's threat model (T-02-04-01 through T-02-04-04). All mitigations applied:
- T-02-04-03: `java.ajax()` raises `NotImplementedError` which surfaces as `quickjs.JSException` — callers can catch at RuleError boundary.

## Self-Check: PASSED

- `src/novel/rules/_js.py` exists and exports `eval_js`
- `src/novel/rules/__init__.py` imports `eval_js` and dispatches JS_INLINE + JS_BLOCK
- Commits 031b5a9 and 57c2af1 confirmed in git log
- 61/61 tests pass
