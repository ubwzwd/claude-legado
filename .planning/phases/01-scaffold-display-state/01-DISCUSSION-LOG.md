# Phase 1: Scaffold, Display, State - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in 01-CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-07
**Phase:** 01-scaffold-display-state
**Mode:** discuss
**Areas discussed:** Camouflage framing, Skill invocation structure, Hardcoded fake content, Project layout

## Gray Areas Presented

| Area | Options Offered | Selected |
|------|----------------|----------|
| Camouflage framing | Plain streaming only / Fake reasoning block / Fake prompt echo | Fake reasoning block before content |
| Skill invocation | `python novel.py` at root / `python -m novel` package / inline heredoc | `python -m novel` with `src/novel/` package |
| Hardcoded fake content | 3 Chinese chapters / 1 placeholder chapter / 10+ chapters | 3 short Chinese chapters, real novel feel |
| Project layout | `novel.py` at root / `src/novel/` package / `novel/` at root | `src/novel/` package + `.claude/commands/novel.md` |

## Corrections Made

No corrections — all selections were first-pass choices.

## Carrying Forward

From project-level decisions (STATE.md + PROJECT.md):
- Python stack: rich, httpx, lxml+cssselect, quickjs (decided at project init)
- Chapter-per-invocation design: no TUI, no stdin
- Phase 1 uses hardcoded/fake data to validate camouflage before any scraping is built
