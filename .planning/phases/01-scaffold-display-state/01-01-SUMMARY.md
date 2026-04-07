---
phase: 01-scaffold-display-state
plan: 01
subsystem: cli
tags: [python, setuptools, pytest, rich, src-layout, dispatcher, claude-code-skill]

requires: []
provides:
  - python -m novel entry point with 8-subcommand dispatcher
  - pyproject.toml src-layout package config (claude-legado)
  - .claude/commands/novel.md Claude Code skill file
  - test suite for all dispatch paths (9 tests)
  - tests/conftest.py with tmp_state_dir fixture for Plan 03
affects: [01-02, 01-03, 02-scraping, 03-book-source, 04-search, 05-shelf]

tech-stack:
  added: [rich>=13.7, setuptools>=61.0, pytest]
  patterns:
    - src-layout (src/novel/) for clean module boundaries
    - Subcommand dispatcher pattern with explicit routing table
    - TDD: RED (failing tests) then GREEN (implementation) workflow

key-files:
  created:
    - pyproject.toml
    - src/novel/__init__.py
    - src/novel/__main__.py
    - src/novel/commands.py
    - .claude/commands/novel.md
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_commands.py
    - .gitignore
  modified: []

key-decisions:
  - "src-layout (src/novel/) keeps package clean for Phase 2+ rule engine modules"
  - "dispatch() falls through to _stream_current() for unknown/no args — never errors"
  - "Stub commands print 'not yet implemented -- available in Phase N' with specific phase refs"
  - "conftest tmp_state_dir fixture uses try/except to allow graceful load before novel.state exists"

patterns-established:
  - "dispatch(args: list[str]) -> None is the canonical entry point for all subcommands"
  - "Unknown args fall through to default (stream current), never raise"
  - "PYTHONPATH=src python -m novel is the canonical invocation in skill file"

requirements-completed: [SKILL-01, SKILL-02, SKILL-03, SKILL-04, SKILL-05, SKILL-06, SKILL-07, SKILL-08]

duration: 15min
completed: 2026-04-07
---

# Phase 1 Plan 01: Package Scaffold, Dispatcher, Skill File Summary

**Python src-layout package with 8-subcommand CLI dispatcher, Claude Code /novel skill file, and full pytest suite — all 9 dispatch tests green**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-07T00:00:00Z
- **Completed:** 2026-04-07T00:15:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 9 created

## Accomplishments

- src-layout Python package (`src/novel/`) installable via `pip install -e .`
- `dispatch(args)` routes all 8 subcommands: default, next, prev, search, toc, shelf, use
- `.claude/commands/novel.md` skill file wires Claude Code `/novel` to `python -m novel $ARGUMENTS`
- 9 pytest tests covering all dispatch paths — all pass
- `conftest.py` with `tmp_state_dir` fixture (lazy import, future-safe for Plan 03)
- `.gitignore` for build artifacts and pycache

## Task Commits

1. **Task 1: Package scaffold, dispatcher, skill file, tests** - `45e8f6a` (feat)

## Files Created/Modified

- `pyproject.toml` — Package config with src-layout, rich dependency, pytest config
- `src/novel/__init__.py` — Package marker
- `src/novel/__main__.py` — Entry point importing `dispatch` from `novel.commands`
- `src/novel/commands.py` — `dispatch()` with all 8 subcommand routes and stubs
- `.claude/commands/novel.md` — Claude Code skill file using `python -m novel $ARGUMENTS`
- `tests/__init__.py` — Test package marker
- `tests/conftest.py` — `tmp_state_dir` fixture with lazy novel.state import
- `tests/test_commands.py` — 9 tests for dispatch routing
- `.gitignore` — Excludes egg-info, pycache, dist, build

## Decisions Made

- Used `try/except ImportError` in conftest for `novel.state` so test collection never fails before Plan 03 exists
- Stub messages include specific phase numbers ("available in Phase 4") as per D-16
- `_advance(direction: int)` uses int sign to distinguish next/prev, keeping routing code lean
- Added `.gitignore` (deviation Rule 2 — necessary for clean repo operation)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added .gitignore for build artifacts**
- **Found during:** Task 1 (after pip install -e .)
- **Issue:** `pip install -e .` generates `src/claude_legado.egg-info/` and `__pycache__/` directories that would appear as untracked files
- **Fix:** Created `.gitignore` with standard Python exclusions
- **Files modified:** `.gitignore`
- **Verification:** `git status` shows no untracked build artifacts
- **Committed in:** 45e8f6a (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical)
**Impact on plan:** Required for clean repo state, no scope creep.

## Issues Encountered

- System Python pip required `--break-system-packages` flag (WSL2 Ubuntu environment) — resolved with flag, package installed successfully.

## Known Stubs

| Stub | File | Line | Reason |
|------|------|------|--------|
| `_stream_current()` prints "Reading current chapter..." | `src/novel/commands.py` | 9 | Placeholder — Plan 02 replaces with real rich streaming |
| `_advance()` prints simple text | `src/novel/commands.py` | 14-18 | Placeholder — Plan 02 replaces with state-aware navigation |
| search stub message | `src/novel/commands.py` | 32 | Intentional — Phase 4 feature |
| toc stub message | `src/novel/commands.py` | 34 | Intentional — Phase 4 feature |
| shelf stub message | `src/novel/commands.py` | 36 | Intentional — Phase 5 feature |
| use stub message | `src/novel/commands.py` | 38 | Intentional — Phase 3 feature |

All stubs are intentional per plan specification. This plan's goal is dispatcher wiring, not content rendering. Plans 02 and 03 resolve the _stream_current and _advance stubs.

## Next Phase Readiness

- `python -m novel` and all 8 subcommands functional — Plans 02 and 03 can import and extend `commands.py`
- `tests/conftest.py` `tmp_state_dir` fixture ready for Plan 03 state tests
- Package installable and importable — no setup required for parallel worktree agents

---
*Phase: 01-scaffold-display-state*
*Completed: 2026-04-07*
