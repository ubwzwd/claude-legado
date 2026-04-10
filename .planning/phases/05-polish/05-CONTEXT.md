# Phase 05: Polish - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Hardening the tool for daily use—graceful error handling, improving `/novel shelf` and `/novel toc` UX, and adding a comprehensive README.

</domain>

<decisions>
## Implementation Decisions

### Error Presentation
- **D-01:** Claude Disguise: Errors regarding network/rules should print a fake streaming Claude apology (e.g. "*Claude is having trouble reaching the source context...*"), keeping the camouflage intact instead of spilling a standard CLI traceback.

### Shelf Information Density
- **D-02:** With progress: `/novel shelf` shows the book along with reading progress (e.g. `[ID] Title - Author (Chapter 42 / 1000)`).

### TOC Navigation Marker
- **D-03:** Current chapter marker: Highlight the active chapter when calling `/novel toc` (e.g., `-> [42] Chapter 42`) so the reader knows exactly where they are.

### Out-of-the-box Experience
- **D-04:** Require manual setup: Ensure the repository remains clean by requiring users to find and load their own source first before reading. No default JSON source is provided.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements file
- `.planning/REQUIREMENTS.md` — Hardening across all prior requirements (Phase 5).

### Project decisions
- `.planning/PROJECT.md` §Key Decisions — Python stack (rich, httpx), sync design.
-(`.planning/STATE.md`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Established Patterns
- `RuleError` explicitly raised from rule engine layer: Any HTTP or Rule evaluation errors propagate up explicitly and should be caught at the command handler level to format as a "Claude disguised" message.
- Sync architecture constraint.
- Chapter-per-invocation (no interactive TUI navigation loop holding process alive) — all actions must be command-line arguments.

### Integration Points
- Connecting `commands.py` error handling logic to the display engine (`novel.display.stream_output` or similar) rather than letting Python terminate with an unhandled exception traceback.
- Modifying `shelf` formatting in `commands.py` while ensuring it pulls progress from `state.json`.

</code_context>

<specifics>
## Specific Ideas

- Error fake streaming message must be convincing (e.g., "*Claude encountered an issue with the source context...*").

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-polish*
*Context gathered: 2026-04-10*
