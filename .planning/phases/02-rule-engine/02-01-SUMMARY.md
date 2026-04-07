---
phase: 02-rule-engine
plan: 01
subsystem: rule-engine
tags: [lxml, cssselect, jsonpath-ng, quickjs, pytest, tdd, legado]

# Dependency graph
requires:
  - phase: 01-scaffold-display-state
    provides: src-layout (src/novel/), pytest config, Python 3.12 project structure
provides:
  - novel.rules package with evaluate/evaluate_list stubs (importable by plans 02-02 through 02-04)
  - RuleError exception class for all rule engine errors
  - detect_rule_type() covering all 5 legado rule type prefixes
  - load_book_source() parser accepting single dict or array JSON
  - tests/fixtures/ with html_title.html, toc_list.html, book_info.json, book_source.json
  - Wave 0 XFAIL test stubs for plans 02-02 through 02-04
affects: [02-02-css-xpath, 02-03-jsonpath-js, 02-04-evaluate-dispatch]

# Tech tracking
tech-stack:
  added: [lxml>=6.0, cssselect>=1.4, jsonpath-ng>=1.8, quickjs>=1.19]
  patterns:
    - TDD RED/GREEN: test file written first, implementation follows
    - detect_rule_type() prefix-dispatch pattern for rule type detection
    - REQUIRED_FIELDS tuple + loop for declarative field validation
    - strict=True xfail stubs guarantee stubs fail on NotImplementedError (not silently pass)

key-files:
  created:
    - src/novel/rules/__init__.py
    - src/novel/rules/_errors.py
    - src/novel/rules/_detect.py
    - src/novel/rules/_source.py
    - tests/fixtures/book_source.json
    - tests/fixtures/html_title.html
    - tests/fixtures/toc_list.html
    - tests/fixtures/book_info.json
    - tests/test_rules_skeleton.py
    - tests/test_source_parser.py
    - tests/test_rules_css.py
    - tests/test_rules_xpath.py
    - tests/test_rules_jsonpath.py
    - tests/test_rules_regex.py
    - tests/test_rules_js.py
    - tests/test_rules_evaluate.py
  modified:
    - pyproject.toml

key-decisions:
  - "detect_rule_type() prefix order: xpath: > css: > $./$[ > @js: > <js>...</js> — prevents ambiguity"
  - "XFAIL stubs use strict=True — ensures stubs turn GREEN when implementation is added (not silently pass on wrong code)"
  - "evaluate/evaluate_list remain NotImplementedError stubs — wired in plans 02-02 through 02-04"

patterns-established:
  - "Pattern 1: Rule prefix detection with ordered if-chain (research Pattern 2)"
  - "Pattern 2: REQUIRED_FIELDS tuple + for-loop validator in load_book_source()"
  - "Pattern 3: XFAIL strict=True stub test pattern for Wave 0 pre-creation"

requirements-completed: [SRC-01, SRC-02]

# Metrics
duration: 5min
completed: 2026-04-08
---

# Phase 2 Plan 01: Rules Sub-Package Skeleton Summary

**legado rules package bootstrapped: detect_rule_type() for 5 prefixes, load_book_source() parser, 4 passing source tests, 21 xfail Wave 0 stubs**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-08T00:04:53Z
- **Completed:** 2026-04-08T00:09:58Z
- **Tasks:** 3
- **Files modified:** 17

## Accomplishments

- Created importable `novel.rules` package with `evaluate`, `evaluate_list`, `RuleError` — downstream plans can import immediately
- Implemented `detect_rule_type()` covering all 5 legado rule prefixes (css:, xpath:, $., @js:, <js>...</js>)
- Implemented `load_book_source()` that handles both single-object and array JSON with required-field validation; 4 tests pass
- Created `tests/fixtures/` with 4 synthetic fixture files (no real URLs, no PII — per D-06/D-08)
- Created 6 Wave 0 XFAIL test stubs (21 total tests) for plans 02-02 through 02-04 — each will go GREEN when implementation lands
- Added 4 new dependencies to pyproject.toml: lxml, cssselect, jsonpath-ng, quickjs

## Task Commits

1. **Task 1: Rules sub-package skeleton** - `2224886` (feat)
2. **Task 2: _source.py parser and test_source_parser.py** - `1b95173` (feat)
3. **Task 3: Wave 0 test stubs and fixtures** - `5423d0c` (feat)

## Files Created/Modified

- `pyproject.toml` — Added lxml>=6.0, cssselect>=1.4, jsonpath-ng>=1.8, quickjs>=1.19 to dependencies
- `src/novel/rules/__init__.py` — Public API: evaluate/evaluate_list stubs, RuleError re-export
- `src/novel/rules/_errors.py` — RuleError(rule, cause) exception class
- `src/novel/rules/_detect.py` — RuleType enum + detect_rule_type() with ordered prefix matching
- `src/novel/rules/_source.py` — load_book_source() with array/dict handling and field validation
- `tests/fixtures/book_source.json` — Synthetic legado book source fixture
- `tests/fixtures/html_title.html` — Chinese novel HTML page for CSS/XPath tests
- `tests/fixtures/toc_list.html` — Chapter list HTML for CSS/XPath list tests
- `tests/fixtures/book_info.json` — Nested JSON fixture for JSONPath tests
- `tests/test_rules_skeleton.py` — 10 tests for package structure (all pass)
- `tests/test_source_parser.py` — 4 tests for load_book_source() (all pass)
- `tests/test_rules_css.py` — 3 xfail stubs (CSS evaluator, plan 02-02)
- `tests/test_rules_xpath.py` — 2 xfail stubs (XPath evaluator, plan 02-02)
- `tests/test_rules_jsonpath.py` — 3 xfail stubs (JSONPath evaluator, plan 02-03)
- `tests/test_rules_regex.py` — 3 xfail stubs (regex post-processing, plan 02-03)
- `tests/test_rules_js.py` — 5 xfail stubs (JS evaluator, plan 02-03)
- `tests/test_rules_evaluate.py` — 5 xfail stubs (dispatcher, plan 02-04)

## Decisions Made

- `detect_rule_type()` uses ordered prefix check (xpath: before css: before $.) to prevent ambiguity; exact research Pattern 2
- `strict=True` on all XFAIL stubs — ensures they cannot silently pass; they will XPASS (go GREEN) only when implementation is correct
- `evaluate()`/`evaluate_list()` remain `NotImplementedError` stubs in `__init__.py` — wired in plans 02-02 through 02-04 as promised

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns beyond those in the plan's threat model. `load_book_source()` reads caller-controlled paths (T-02-01-01 accepted). `json.JSONDecodeError` propagates to caller for malformed JSON (T-02-01-03 mitigated). All fixture data is synthetic (T-02-01-02 complied).

## Known Stubs

The following stubs are intentional and tracked for downstream plans:

| File | Stub | Resolved by |
|------|------|-------------|
| `src/novel/rules/__init__.py` | `evaluate()` → NotImplementedError | plan 02-04 |
| `src/novel/rules/__init__.py` | `evaluate_list()` → NotImplementedError | plan 02-04 |

These stubs are required architecture — they provide the import surface while downstream plans implement the logic.

## Self-Check: PASSED

All files verified present on disk. All 3 task commits verified in git log.

| Check | Result |
|-------|--------|
| src/novel/rules/__init__.py | FOUND |
| src/novel/rules/_errors.py | FOUND |
| src/novel/rules/_detect.py | FOUND |
| src/novel/rules/_source.py | FOUND |
| tests/fixtures/book_source.json | FOUND |
| tests/fixtures/html_title.html | FOUND |
| tests/test_source_parser.py | FOUND |
| commit 2224886 (Task 1) | FOUND |
| commit 1b95173 (Task 2) | FOUND |
| commit 5423d0c (Task 3) | FOUND |
