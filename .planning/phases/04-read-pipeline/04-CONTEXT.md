# Phase 04: Read Pipeline - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

End-to-end search and read flow integrating the rule engine and HTTP layer. Wiring up `/novel search`, `/novel add`, `/novel info`, `/novel toc`, `/novel next` to deliver a complete reading experience from search to reading, within a command-line environment mimicking Claude.

</domain>

<decisions>
## Implementation Decisions

### Search & Add Workflow
- **D-01:** `/novel search <query>` saves a short-lived cache state with the search results.
- **D-02:** `/novel add <index>` picks a result from the search cache to add to the shelf.

### Book Info Display
- **D-03:** Book details (intro, author) are viewed via a dedicated `/novel info` command rather than printing automatically upon adding to the shelf.

### TOC Handling
- **D-04:** Paginates chapter lists via `/novel toc <page_number>` (e.g., 50 chapters per page) instead of dumping thousands of chapters at once.

### Content Fetching & Navigation
- **D-05:** Fetches chapters strictly on-demand (keeping the stack simple and synchronous), honoring the Phase 3 stack decisions.

### Shelf Management
- **D-06:** `/novel shelf` lists saved books with index IDs.
- **D-07:** `/novel read <id>` makes a book from the shelf the active one.

### Search Results Formatting
- **D-08:** Display `[index] Title - Author - name of the book source` in the search results list.

### Missing Data Fallback
- **D-09:** If the rule engine fails to extract an optional field, display a clear placeholder like `[No intro extracted]`.

### Save Progress Triggers
- **D-10:** Save reading progress *before* streaming starts. This ensures that if the user Ctrl+C's midway, they will land on the current/new chapter next time they type `/novel`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements file (MANDATORY READ)
- `.planning/REQUIREMENTS.md` — Full v1 requirement list; Phase 4 covers FLOW-01 through FLOW-05.

### Project decisions
- `.planning/PROJECT.md` §Key Decisions — Python stack (httpx confirmed, sync design).
- `.planning/STATE.md` — State management using `~/.claude-legado/state.json` and `~/.claude-legado/shelf.json`.

### Phase Contexts
- `.planning/phases/02-rule-engine/02-CONTEXT.md` — `evaluate()` API.
- `.planning/phases/03-http-source-loading/03-CONTEXT.md` — `fetch()`, `follow_toc_pages()` HTTP APIs.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/novel/commands.py` — Location for wiring the actual command paths over the stub implementations.
- `src/novel/state.py` — `load_state()`, `save_state()` available for progress and cache management.

### Established Patterns
- Chapter-per-invocation (no interactive TUI navigation loop holding process alive) — all actions must be command-line arguments.
- Sync architecture constraint.

### Integration Points
- Connecting `commands.py` functions to HTTP fetchers (`novel.http`) and the parsed rule engine (`novel.rules`).

</code_context>

<specifics>
## Specific Ideas

- No interactive standard-in menus due to Claude Code bash tool constraints. All user interaction is single-shot via arguments.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-read-pipeline*
*Context gathered: 2026-04-10*
