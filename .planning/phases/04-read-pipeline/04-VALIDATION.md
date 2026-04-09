---
phase: 04
slug: read-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `pytest tests/test_04_read_pipeline.py` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~1 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_04_read_pipeline.py`
- **After every plan wave:** Run `pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | FLOW-01 | — | N/A | unit | `pytest tests/test_04_read_pipeline.py -k test_search_flow` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | FLOW-02 | — | N/A | unit | `pytest tests/test_04_read_pipeline.py -k test_book_info_and_add` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 1 | FLOW-03 | — | N/A | unit | `pytest tests/test_04_read_pipeline.py -k test_toc_flow` | ❌ W0 | ⬜ pending |
| 04-04-01 | 04 | 1 | FLOW-04 | — | N/A | unit | `pytest tests/test_04_read_pipeline.py -k test_reading_flow` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_04_read_pipeline.py` — unit tests for Phase 4 covering FLOW-01 to FLOW-05
- [ ] `respx` mock setup in `conftest.py` — intercept network calls for tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real network search | FLOW-01 | Test against dynamic site changes | `/novel search test` using live data |
| Text streaming output | FLOW-04 | Display validation depends on terminal capabilities | Run `python3 -m novel` on a real chapter and verify variable-speed chunks |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
