---
phase: 01-scaffold-display-state
plan: 02
subsystem: display
tags: [python, rich, streaming, cjk, xianxia, sys.stdout, pytest, tdd]

requires:
  - phase: 01-01
    provides: src-layout package structure, commands.py dispatcher stubs that Plan 03 will wire to display.stream_chapter()

provides:
  - stream_chapter() entry point for Plan 03 to wire into commands.py
  - Character-level streaming engine with variable timing (DELAY_MIN/MAX/PAUSE_LONG/PAUSE_MED/BURST_PROB)
  - Rich-based header, nav hints, and reasoning preamble output functions
  - 3 hardcoded xianxia chapters (834/849/907 CJK chars each) for Phase 1 navigation and state testing
  - test suite: 8 display tests covering timing, CJK width, structural output

affects: [01-03, 02-scraping, 03-book-source]

tech-stack:
  added: []
  patterns:
    - "sys.stdout.write + sys.stdout.flush for character streaming (NOT print/Rich Console)"
    - "Rich Console created per-function (not module-level) to avoid test env detection"
    - "TDD: RED (failing import) then GREEN (all 8 pass) workflow"
    - "CJK width delegated to rich.cells.cell_len (no manual wcwidth math)"

key-files:
  created:
    - src/novel/display.py
    - src/novel/data/__init__.py
    - src/novel/data/fake_book.py
    - tests/test_display.py
  modified: []

key-decisions:
  - "Console created inside each function, not at module level — avoids Rich detecting pytest as non-TTY before we can monkeypatch"
  - "Burst chunks advance index by chunk_size (>= BURST_MIN=8) — loop always terminates (T-02-03 DoS mitigation)"
  - "stream_text uses sys.stdout.write not print — allows monkeypatching sys.stdout in tests"
  - "Fake book authored as original generated xianxia prose — no copyright concern"

patterns-established:
  - "stream_chapter(chapter_num, title, content, chapter_index, total) is the Plan 03 wiring contract"
  - "FAKE_BOOK dict with title/author/chapters keys; each chapter has title/content"
  - "get_fake_chapter(index) returns None on out-of-range (defensive accessor pattern)"

requirements-completed: [DISP-01, DISP-02, DISP-03, DISP-04, DISP-05, DISP-06, DISP-07]

duration: 3min
completed: 2026-04-07
---

# Phase 1 Plan 02: Streaming Display Engine and Fake Book Data Summary

**Character-streaming display engine with variable CJK-aware delays, Rich headers/hints/preamble, and 3 xianxia chapters (2590 total CJK chars) for camouflage validation**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-04-07T01:43:30Z
- **Completed:** 2026-04-07T01:47:03Z
- **Tasks:** 2 (Task 1 TDD: RED + GREEN commits; Task 2: single commit)
- **Files modified:** 4 created

## Accomplishments

- `display.py` streams characters one-by-one via `sys.stdout.write`/`flush` with PAUSE_LONG=0.15 at 。！？, PAUSE_MED=0.06 at ，、；, and random 15–40ms otherwise; 15% burst probability
- Rich Console per-function pattern (not module-level) keeps tests clean without TTY detection issues
- `stream_chapter()` is the Plan 03 wiring contract: calls preamble → header → stream_text → nav hints in sequence
- 3 original xianxia chapters of 太虚剑典: 834/849/907 CJK chars respectively, with natural punctuation for timing variation
- 8 pytest tests all passing; 17 total tests across Plans 01+02 all green

## Task Commits

1. **Task 1 RED: Failing display tests** - `00a5e67` (test)
2. **Task 1 GREEN: Display engine implementation** - `a5bb2ee` (feat)
3. **Task 2: Fake book data (3 chapters)** - `50c6e88` (feat)

## Files Created/Modified

- `src/novel/display.py` — Streaming engine with _char_delay, stream_text (burst logic), print_reasoning_preamble, print_chapter_header, print_nav_hints, stream_chapter
- `src/novel/data/__init__.py` — Empty package marker
- `src/novel/data/fake_book.py` — FAKE_BOOK dict with 3 chapters + get_fake_chapter(index) accessor
- `tests/test_display.py` — 8 tests: stream_text content+newline, char delays (3 ranges), CJK width, header/hints/preamble output

## Decisions Made

- Console created inside each function rather than at module level: avoids pytest's non-TTY environment causing Rich to suppress output before monkeypatching has a chance to run
- `stream_text` uses `sys.stdout.write` not `print` or `Console.print`: enables clean monkeypatching of sys.stdout in tests
- Loop index `i` always advances by >= 1 (single char) or >= BURST_MIN=8 (burst), satisfying T-02-03 DoS mitigation

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None in files created by this plan. (Pre-existing stubs in `commands.py` from Plan 01 are Plan 03's responsibility.)

## Threat Flags

None - no new trust boundaries or network endpoints introduced. All content is hardcoded; sys.stdout output only.

## Next Phase Readiness

- `stream_chapter(chapter_num, title, content, chapter_index, total)` is ready for Plan 03 to wire into `commands.py`
- `get_fake_chapter(index)` accessor ready for state-based chapter lookup in Plan 03
- All 17 tests green; no blockers for Plan 03

## Self-Check: PASSED

All files exist and all commit hashes verified:
- `src/novel/display.py` — FOUND
- `src/novel/data/__init__.py` — FOUND
- `src/novel/data/fake_book.py` — FOUND
- `tests/test_display.py` — FOUND
- `.planning/phases/01-scaffold-display-state/01-02-SUMMARY.md` — FOUND
- Commit `00a5e67` (RED tests) — FOUND
- Commit `a5bb2ee` (GREEN impl) — FOUND
- Commit `50c6e88` (fake book data) — FOUND

---
*Phase: 01-scaffold-display-state*
*Completed: 2026-04-07*
