---
phase: 2
slug: rule-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already configured in pyproject.toml) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]` |
| **Quick run command** | `PYTHONPATH=src pytest tests/test_rules_*.py -x -q` |
| **Full suite command** | `PYTHONPATH=src pytest -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=src pytest tests/test_rules_*.py -x -q`
- **After every plan wave:** Run `PYTHONPATH=src pytest -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SRC-01 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_source_parser.py::test_load_single -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | SRC-01 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_source_parser.py::test_load_array -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | SRC-02 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_source_parser.py::test_required_fields -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | SRC-02 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_source_parser.py::test_missing_field -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | SRC-03 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_css.py::test_text_attr -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | SRC-03 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_css.py::test_href_attr -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 1 | SRC-03 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_css.py::test_no_match -x` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 1 | SRC-04 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_xpath.py::test_text_node -x` | ❌ W0 | ⬜ pending |
| 02-02-05 | 02 | 1 | SRC-04 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_xpath.py::test_attr_node -x` | ❌ W0 | ⬜ pending |
| 02-02-06 | 02 | 1 | SRC-05 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_jsonpath.py::test_scalar -x` | ❌ W0 | ⬜ pending |
| 02-02-07 | 02 | 1 | SRC-05 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_jsonpath.py::test_array -x` | ❌ W0 | ⬜ pending |
| 02-02-08 | 02 | 1 | SRC-05 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_jsonpath.py::test_no_match -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | SRC-06 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_regex.py::test_single_pair -x` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 2 | SRC-06 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_regex.py::test_chained -x` | ❌ W0 | ⬜ pending |
| 02-03-03 | 03 | 2 | SRC-06 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_regex.py::test_delete -x` | ❌ W0 | ⬜ pending |
| 02-03-04 | 03 | 2 | SRC-10 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_evaluate.py::test_url_template -x` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 2 | SRC-07 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_js.py::test_inline -x` | ❌ W0 | ⬜ pending |
| 02-04-02 | 04 | 2 | SRC-08 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_js.py::test_block -x` | ❌ W0 | ⬜ pending |
| 02-04-03 | 04 | 2 | SRC-09 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_js.py::test_java_base64 -x` | ❌ W0 | ⬜ pending |
| 02-04-04 | 04 | 2 | SRC-09 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_js.py::test_java_md5 -x` | ❌ W0 | ⬜ pending |
| 02-04-05 | 04 | 2 | SRC-09 | — | N/A | unit | `PYTHONPATH=src pytest tests/test_rules_js.py::test_ajax_stub -x` | ❌ W0 | ⬜ pending |
| 02-xx-int | 02–04 | 2 | All | D-09 | RuleError on bad input, not silent failure | integration | `PYTHONPATH=src pytest tests/test_rules_evaluate.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_source_parser.py` — stubs for SRC-01, SRC-02
- [ ] `tests/test_rules_css.py` — stubs for SRC-03
- [ ] `tests/test_rules_xpath.py` — stubs for SRC-04
- [ ] `tests/test_rules_jsonpath.py` — stubs for SRC-05
- [ ] `tests/test_rules_regex.py` — stubs for SRC-06
- [ ] `tests/test_rules_js.py` — stubs for SRC-07, SRC-08, SRC-09
- [ ] `tests/test_rules_evaluate.py` — dispatcher integration + SRC-10 + D-09 RuleError
- [ ] `tests/fixtures/html_title.html` — minimal HTML for CSS/XPath tests
- [ ] `tests/fixtures/toc_list.html` — HTML with list items for multi-select tests
- [ ] `tests/fixtures/book_info.json` — minimal JSON for JSONPath tests
- [ ] `tests/fixtures/book_source.json` — synthetic book source for SRC-01/SRC-02 tests

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
