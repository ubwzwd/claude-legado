---
phase: 3
slug: http-source-loading
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already in use) |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `PYTHONPATH=src python3 -m pytest tests/test_http*.py -x -q` |
| **Full suite command** | `PYTHONPATH=src python3 -m pytest -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=src python3 -m pytest tests/ -x -q`
- **After every plan wave:** Run `PYTHONPATH=src python3 -m pytest -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green (all 61 existing + all new Phase 3 tests)
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | HTTP-01 | T-03-01 | `Path(args[0]).name` used for dest filename | unit | `pytest tests/test_http_client.py::test_fetch_sends_source_headers -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | HTTP-01 | — | N/A | unit | `pytest tests/test_http_client.py::test_parse_source_headers_json_string -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | HTTP-01 | — | N/A | unit | `pytest tests/test_http_client.py::test_parse_source_headers_dict -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | HTTP-03 | — | N/A | unit | `pytest tests/test_http_client.py::test_cookie_jar_per_client -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | HTTP-02 | — | N/A | unit | `pytest tests/test_http_encoding.py::test_decode_gbk_response -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | HTTP-02 | — | N/A | unit | `pytest tests/test_http_encoding.py::test_decode_uses_content_type_charset -x` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 1 | HTTP-02 | — | N/A | unit | `pytest tests/test_http_encoding.py::test_decode_fallback_charset_normalizer -x` | ❌ W0 | ⬜ pending |
| 03-02-04 | 02 | 1 | HTTP-02 | — | N/A | unit | `pytest tests/test_http_encoding.py::test_decode_utf8_fallback -x` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | HTTP-04 | — | N/A | unit | `pytest tests/test_http_pagination.py::test_follow_toc_pages_two_pages -x` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 2 | HTTP-04 | — | N/A | unit | `pytest tests/test_http_pagination.py::test_follow_toc_pages_visited_guard -x` | ❌ W0 | ⬜ pending |
| 03-03-03 | 03 | 2 | HTTP-05 | — | N/A | unit | `pytest tests/test_http_pagination.py::test_follow_content_pages -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | HTTP-01 | T-03-02 | Path traversal: basename-only dest for source copy | integration | `pytest tests/test_novel_use.py::test_use_loads_and_persists_source -x` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | HTTP-01 | — | N/A | unit | `pytest tests/test_novel_use.py::test_use_prints_summary -x` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | HTTP-01 | — | N/A | unit | `pytest tests/test_novel_use.py::test_use_no_args -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_http_client.py` — stubs for HTTP-01, HTTP-03
- [ ] `tests/test_http_encoding.py` — stubs for HTTP-02
- [ ] `tests/test_http_pagination.py` — stubs for HTTP-04, HTTP-05
- [ ] `tests/test_novel_use.py` — stubs for SKILL-08 (/novel use command)
- [ ] Two new test cases in `tests/test_rules_js.py` — stubs for D-04/D-05 (_make_context extension)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real GBK novel site fetched end-to-end | HTTP-02 | Requires live network; test environments mock HTTP | Run `/novel use <real_source.json>` against a known GBK site, confirm Chinese text displays correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
