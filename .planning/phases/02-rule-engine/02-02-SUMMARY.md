---
phase: 02-rule-engine
plan: 02
subsystem: rule-engine
tags: [css, xpath, jsonpath, lxml, cssselect, jsonpath-ng, evaluate, dispatcher]
dependency_graph:
  requires: [02-01]
  provides: [02-03, 02-04]
  affects: []
tech_stack:
  added: [lxml+cssselect (CSS selector evaluation), jsonpath-ng (JSONPath evaluation)]
  patterns: [rule-type dispatcher, selector@attr extraction, graceful empty-string fallback]
key_files:
  created:
    - src/novel/rules/_css.py
    - src/novel/rules/_xpath.py
    - src/novel/rules/_jsonpath.py
  modified:
    - src/novel/rules/__init__.py
    - tests/test_rules_css.py
    - tests/test_rules_xpath.py
    - tests/test_rules_jsonpath.py
    - tests/test_rules_evaluate.py
decisions:
  - "eval_jsonpath passes full rule (with $ prefix) not rule_body — jsonpath-ng requires the full $ expression"
  - "evaluate_list for JS types raises NotImplementedError pending plan 02-04 (not RuleError)"
  - "xfail markers removed from selector and dispatcher tests as implementation now live"
metrics:
  duration: 3m
  completed_date: "2026-04-08"
  tasks_completed: 2
  files_changed: 7
---

# Phase 02 Plan 02: CSS/XPath/JSONPath Selector Evaluators Summary

CSS+XPath via lxml and JSONPath via jsonpath-ng wired into evaluate()/evaluate_list() dispatcher with RuleError wrapping for all failures.

## What Was Built

Three selector evaluators plus an updated dispatcher:

- `_css.py`: `eval_css(rule_body, html) -> str` and `eval_css_list(rule_body, html) -> list[str]` using lxml+cssselect. Parses `selector@attr` format where `@text` extracts text_content(), `@{attr}` extracts element attribute, and no `@` returns serialized outer HTML.

- `_xpath.py`: `eval_xpath(expr, html) -> str` and `eval_xpath_list(expr, html) -> list[str]` using lxml. Joins text() and @attribute string results; serializes element results as HTML.

- `_jsonpath.py`: `eval_jsonpath(expr, data) -> str` and `eval_jsonpath_list(expr, data) -> list[str]` using jsonpath-ng. Returns first/all matches as str; returns `''`/`[]` for no-match without raising.

- `__init__.py`: `evaluate()` and `evaluate_list()` now dispatch to the three evaluators by `RuleType`. `ValueError` from `detect_rule_type()` is caught and re-raised as `RuleError` (D-09 requirement). JS types remain `NotImplementedError` pending plan 02-04.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement _css.py, _xpath.py, _jsonpath.py | 7778917 | _css.py, _xpath.py, _jsonpath.py (created); test_rules_css.py, test_rules_xpath.py, test_rules_jsonpath.py (xfail removed) |
| 2 | Wire evaluate() and evaluate_list() in __init__.py | a5aa929 | __init__.py (updated); test_rules_evaluate.py (xfail removed from 4 tests) |

## Verification

- 8 selector tests (3 CSS + 2 XPath + 3 JSONPath): all pass
- 4 dispatcher tests (css_dispatch, xpath_dispatch, jsonpath_dispatch, rule_error_on_bad_rule): all pass
- test_url_template remains xfail (plan 02-03 scope)
- JS/regex tests remain xfail (plan 02-04 scope)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed xfail markers from tests after implementation**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** Tests were marked `xfail(strict=True)`. After implementing the evaluators, pytest reported these as XPASS(strict) failures because xfail tests that unexpectedly pass are treated as test failures.
- **Fix:** Removed `@pytest.mark.xfail` decorators from 8 selector tests and 4 dispatcher tests (keeping `test_url_template` xfail as it targets plan 02-03).
- **Files modified:** tests/test_rules_css.py, tests/test_rules_xpath.py, tests/test_rules_jsonpath.py, tests/test_rules_evaluate.py
- **Commit:** 7778917 (selector tests), a5aa929 (evaluate tests)

## Known Stubs

None — all implemented functions are fully wired. JS_INLINE and JS_BLOCK in evaluate()/evaluate_list() raise `NotImplementedError` intentionally; this is documented in the plan as wired in plan 02-04.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. lxml.html.fromstring() on untrusted HTML is accepted for Phase 2 (test fixtures only); Phase 5 will add size limits per T-02-02-01.

## Self-Check: PASSED

- src/novel/rules/_css.py: FOUND
- src/novel/rules/_xpath.py: FOUND
- src/novel/rules/_jsonpath.py: FOUND
- src/novel/rules/__init__.py: MODIFIED (verified via git diff)
- Commit 7778917: FOUND (git log confirms)
- Commit a5aa929: FOUND (git log confirms)
