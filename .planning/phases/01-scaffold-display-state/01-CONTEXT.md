# Phase 1: Scaffold, Display, State - Context

**Gathered:** 2026-04-07 (discuss mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the `/novel` Claude Code skill and make it stream convincingly fake Claude-style output, with reading state persisted between invocations. Uses **hardcoded fake data only** — no real scraping, no HTTP, no rule engine. The goal is to validate the camouflage looks real before Phase 2+ builds the actual book source engine.

Subcommands `search`, `toc`, `shelf`, `use` return stubbed responses in this phase.

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- **D-01:** `src/novel/` Python package (src-layout). Entry point at `src/novel/__main__.py` or equivalent so `python -m novel` works.
- **D-02:** Skill file lives at `.claude/commands/novel.md`. Invokes via `cd /path/to/repo && python -m novel $ARGUMENTS` in a Bash block.
- **D-03:** No separate `novel.py` at root — keep the package structure clean from day one so Phase 2+ rule engine modules land naturally inside `src/novel/`.

### Camouflage Framing
- **D-04:** Prepend a short italicized fake reasoning block before chapter text begins. Mimics Claude's extended thinking mode. Example: `*Analyzing the chapter structure and preparing the response...*` (or similar Chinese-context phrasing).
- **D-05:** After the fake reasoning block, stream chapter content character-by-character using DISP-02/DISP-03 timing (15–40ms per char, longer pauses at `。！？`, occasional 8–15 char bursts).
- **D-06:** No fake prompt echo or Q&A framing — the reasoning block + streaming text is sufficient camouflage.

### Fake Hardcoded Content
- **D-07:** Ship 3 fake chapters of actual Chinese web novel prose (public-domain or generated content that reads like xianxia/wuxia). Enough for next/prev navigation and state persistence to be meaningfully testable.
- **D-08:** Fake book metadata: title, author, and chapter list are all hardcoded. The "current book" is auto-loaded so `/novel` works with no prior shelf setup.
- **D-09:** Chapter content is long enough to look like a real chapter at a glance (≥500 Chinese characters per chapter).

### Streaming Display Engine
- **D-10:** Use `rich.console.Console` in live/streaming mode (no alternate screen, scrollback preserved — DISP-05).
- **D-11:** CJK double-width: rely on Rich's built-in wcwidth handling. No manual width math — Rich handles this correctly when the console width is queried from the terminal.
- **D-12:** Chapter header (number + title) printed before content starts (DISP-06). Navigation hint block printed after content ends (DISP-07).

### State Persistence
- **D-13:** State file at `~/.claude-legado/state.json`. Bookshelf at `~/.claude-legado/shelf.json`. Sources directory at `~/.claude-legado/sources/`.
- **D-14:** `/novel` with no args resumes from last saved position. If state is empty, auto-loads the hardcoded fake book and starts at chapter 1.
- **D-15:** State written after each chapter display (not interactively mid-chapter — chapter-per-invocation design).

### Stubbed Subcommands
- **D-16:** `search`, `toc`, `shelf`, `use` each print a one-line stub message (e.g., "search: not yet implemented — available in Phase 4") rather than erroring out. All eight subcommands must be registered (SKILL-05 through SKILL-08).

### Claude's Discretion
- Exact wording of the fake reasoning block
- Whether to use `time.sleep` or `asyncio` for streaming delays (prefer sync for Phase 1 simplicity)
- Packaging details (`pyproject.toml` vs `setup.py`, exact package layout within `src/novel/`)
- Whether to add a `requirements.txt` or go straight to `pyproject.toml`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements are fully captured in REQUIREMENTS.md and the decisions above.

### Requirements file (MANDATORY READ)
- `.planning/REQUIREMENTS.md` — Full v1 requirement list; Phase 1 covers SKILL-01 through SKILL-08, DISP-01 through DISP-07, STATE-01 through STATE-04

### Project decisions
- `.planning/PROJECT.md` §Key Decisions — Python stack (rich, httpx, lxml+cssselect, quickjs), chapter-per-invocation design, Phase 1 fake-data rationale

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — repo has no source files yet. `src/novel/` package must be created from scratch.

### Established Patterns
- `.claude/` directory exists with `settings.local.json` — skill file goes in `.claude/commands/novel.md` (commands, not skills).
- Python stack decided at project init: `rich` for display, `httpx` for HTTP (Phase 3+), no other dependencies needed in Phase 1.

### Integration Points
- Claude Code invokes the skill via the Bash tool. The skill file must be self-contained and not require any interactive stdin.
- `~/.claude-legado/` is the user-level storage directory; the package must create it on first run if absent.

</code_context>

<specifics>
## Specific Ideas

- Fake reasoning block should feel like Claude introspecting on the "request" — something like `*正在准备章节内容...*` or `*Retrieving chapter content from source...*` works. Keep it short (1–2 lines).
- The streaming feel is the primary camouflage — the reasoning block adds authenticity but the character-by-character output is what sells it.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-scaffold-display-state*
*Context gathered: 2026-04-07*
