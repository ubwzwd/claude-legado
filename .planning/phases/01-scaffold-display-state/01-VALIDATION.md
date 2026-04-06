---
phase: 1
slug: scaffold-display-state
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-07
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — Wave 0 installs |
| **Quick run command** | `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -x -q` |
| **Full suite command** | `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -x -q`
- **After every plan wave:** Run `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-01 | 1 | SKILL-01 | — | N/A | unit | `pytest tests/test_commands.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01-01 | 1 | SKILL-02 | — | N/A | unit | `pytest tests/test_commands.py::test_default_dispatch -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01-01 | 1 | SKILL-03 | — | N/A | unit | `pytest tests/test_commands.py::test_next_dispatch -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01-01 | 1 | SKILL-04 | — | N/A | unit | `pytest tests/test_commands.py::test_prev_dispatch -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01-01 | 1 | SKILL-05,06,07,08 | — | N/A | unit | `pytest tests/test_commands.py::test_stub_commands -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 01-02 | 2 | DISP-01,03 | — | N/A | smoke | `pytest tests/test_display.py::test_stream_text_output -x` | ❌ W0 | ⬜ pending |
| 1-02-02 | 01-02 | 2 | DISP-02 | — | N/A | unit | `pytest tests/test_display.py::test_char_delay -x` | ❌ W0 | ⬜ pending |
| 1-02-03 | 01-02 | 2 | DISP-04 | — | N/A | unit | `pytest tests/test_display.py::test_cjk_width -x` | ❌ W0 | ⬜ pending |
| 1-02-04 | 01-02 | 2 | DISP-06,07 | — | N/A | unit | `pytest tests/test_display.py::test_header_and_hints -x` | ❌ W0 | ⬜ pending |
| 1-02-05 | 01-02 | 2 | DISP-05 | — | N/A | manual | n/a — visual check | manual-only | ⬜ pending |
| 1-03-01 | 01-03 | 2 | STATE-01 | — | N/A | unit | `pytest tests/test_state.py::test_save_state -x` | ❌ W0 | ⬜ pending |
| 1-03-02 | 01-03 | 2 | STATE-02 | — | N/A | unit | `pytest tests/test_state.py::test_load_state_missing -x` | ❌ W0 | ⬜ pending |
| 1-03-03 | 01-03 | 2 | STATE-02 | — | N/A | unit | `pytest tests/test_state.py::test_load_state_exists -x` | ❌ W0 | ⬜ pending |
| 1-03-04 | 01-03 | 2 | STATE-03 | — | N/A | unit | `pytest tests/test_state.py::test_shelf_init -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — package marker
- [ ] `tests/test_commands.py` — covers SKILL-02 through SKILL-08 dispatch stubs
- [ ] `tests/test_display.py` — covers DISP-02, DISP-04, DISP-01/03 smoke, DISP-06/07
- [ ] `tests/test_state.py` — covers STATE-01 through STATE-04
- [ ] `tests/conftest.py` — shared fixture: temp directory for `~/.claude-legado/` (override `STATE_DIR` to a tmp path)
- [ ] `pyproject.toml` — `[tool.pytest.ini_options]` block with `testpaths = ["tests"]`
- [ ] `pip install -e .` — required before pytest can import `novel`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Streaming output is visually indistinguishable from Claude AI response at a glance | DISP-01, DISP-05 | Subjective visual quality; timing perception cannot be automated | `/novel` in a Claude Code session; observe stream cadence, burst pattern, pauses |
| CJK text renders without line overflow or misalignment in terminal | DISP-04, DISP-05 | Terminal rendering depends on font and terminal emulator settings | `/novel` with CJK chapter active; resize terminal to 80 cols; verify no overflow |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
