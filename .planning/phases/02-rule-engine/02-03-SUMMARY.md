---
phase: 02-rule-engine
plan: 03
subsystem: rules
tags: [regex, templates, string-processing, legado]
dependency_graph:
  requires: [02-01]
  provides: [apply_replace_regex, apply_url_template]
  affects: [phase-04-callers]
tech_stack:
  added: []
  patterns: [stdlib-re, replaceRegex-chain, url-template-substitution]
key_files:
  created:
    - src/novel/rules/_regex.py
    - src/novel/rules/_templates.py
  modified:
    - tests/test_rules_regex.py
    - tests/test_rules_evaluate.py
decisions:
  - test_chained assertion corrected from 'XXX' to 'X' — regex chain ##[0-9]+####[a-z]+##X## yields 'X' not 'XXX' (digits stripped first leaving 'abcdef', then [a-z]+ replaces entire run with 'X')
metrics:
  duration: ~5min
  completed: 2026-04-08
  tasks_completed: 1
  files_created: 2
  files_modified: 2
---

# Phase 02 Plan 03: Regex Chain Processor and URL Template Substitution Summary

**One-liner:** stdlib-only replaceRegex chain processor and {{key}} URL template substitution using Python re.sub.

## What Was Built

Two standalone string-processing utility modules for the legado rule engine:

- `src/novel/rules/_regex.py` — `apply_replace_regex(text, replace_regex) -> str` implements the legado `##pattern##replacement` chain format where each pair is applied sequentially; empty replacement deletes matched text; empty/None replace_regex returns input unchanged.

- `src/novel/rules/_templates.py` — `apply_url_template(template, params) -> str` replaces `{{key}}` placeholders with values from a params dict; unknown keys are left unchanged as `{{key}}`.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement _regex.py and _templates.py (TDD) | 8e0efc3 | src/novel/rules/_regex.py, src/novel/rules/_templates.py, tests/test_rules_regex.py, tests/test_rules_evaluate.py |

## Test Results

```
PYTHONPATH=src pytest tests/test_rules_regex.py tests/test_rules_evaluate.py::test_url_template -x -q
4 passed in 0.01s
```

- `test_single_pair` — `##\s+## ##` collapses whitespace: PASS
- `test_chained` — two chained pairs applied in sequence: PASS
- `test_delete` — empty replacement deletes matched text: PASS
- `test_url_template` — `{{key}}` substitution with unknown key left intact: PASS

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test_chained assertion in test_rules_regex.py**
- **Found during:** Task 1 (plan pre-identified this in the `<behavior>` section)
- **Issue:** The stub in plan 02-01 asserted `result == 'XXX'` for `apply_replace_regex('abc123def', '##[0-9]+####[a-z]+##X##')`. The correct result is `'X'`: first pair strips digits yielding `'abcdef'`, second pair replaces the entire `[a-z]+` run with `'X'` yielding `'X'`.
- **Fix:** Changed assertion from `'XXX'` to `'X'` and removed `xfail` markers from all three regex tests.
- **Files modified:** `tests/test_rules_regex.py`
- **Commit:** 8e0efc3

## Known Stubs

None — both functions are fully implemented with no placeholder data or hardcoded values.

## Threat Flags

No new security-relevant surface beyond what is documented in the plan's threat model (T-02-03-01, T-02-03-02). Both threats accepted: regex patterns come from user-curated book source JSON, not attacker-controlled input.

## Self-Check: PASSED

- [x] `src/novel/rules/_regex.py` exists
- [x] `src/novel/rules/_templates.py` exists
- [x] Commit 8e0efc3 exists in git log
- [x] 4 tests pass
