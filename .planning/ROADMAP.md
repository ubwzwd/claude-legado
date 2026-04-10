# Roadmap: claude-legado

## Overview

Five phases deliver a working novel reader that camouflages itself as Claude AI output. Phase 1 proves the disguise works with fake data before any real scraping is built. Phase 2 builds the rule engine in isolation so it can be tested against real book source JSON without HTTP. Phase 3 wires the real HTTP layer. Phase 4 connects everything into a working end-to-end read pipeline. Phase 5 hardens the experience for daily use.

## Phases

- [x] **Phase 1: Scaffold, Display, State** - Skill command wired, streaming output looks like Claude, state persists between invocations
- [x] **Phase 2: Rule Engine** - CSS/XPath/JSONPath/JS selectors parse real book source rules correctly
- [ ] **Phase 3: HTTP + Source Loading** - Load book source JSON, fetch real URLs with headers, cookies, and GBK encoding
- [ ] **Phase 4: Read Pipeline** - Full search → TOC → chapter content flow working end-to-end with a real source
- [ ] **Phase 5: Polish** - Error handling, bookshelf UX, and README — daily-use quality

## Phase Details

### Phase 1: Scaffold, Display, State
**Goal**: Users can invoke `/novel` and see convincingly fake Claude-style streaming output, with reading state persisted between invocations
**Depends on**: Nothing (first phase)
**Requirements**: SKILL-01, SKILL-02, SKILL-03, SKILL-04, SKILL-05, SKILL-06, SKILL-07, SKILL-08, DISP-01, DISP-02, DISP-03, DISP-04, DISP-05, DISP-06, DISP-07, STATE-01, STATE-02, STATE-03, STATE-04
**Success Criteria** (what must be TRUE):
  1. `/novel` invoked in a Claude Code session streams hardcoded text character-by-character in a pattern indistinguishable from a real Claude AI response at a glance
  2. CJK characters render at correct double-width with no line overflow or misaligned wrapping
  3. After `/novel next` then closing the session, re-running `/novel` resumes from the correct chapter without re-prompting
  4. All eight subcommands (`/novel`, `next`, `prev`, `search`, `toc`, `shelf`, `use`) are registered and return a coherent (even if stubbed) response
  5. Navigation hint block appears at the end of every chapter output
**Plans**: 3 plans

Plans:
- [x] 01-01: Skill file and Python entry point (`novel.py` + `.claude/commands/novel.md`), argument dispatch for all eight subcommands
- [x] 01-02: Streaming display engine — variable-delay character output, burst chunks, CJK width handling via Rich
- [x] 01-03: State persistence — `~/.claude-legado/state.json`, `shelf.json`, `sources/` directory; resume logic for `/novel` with no args
**UI hint**: yes

### Phase 2: Rule Engine
**Goal**: CSS, XPath, JSONPath, regex, and JS rules from a real legado book source JSON are parsed and evaluated correctly against sample HTML/JSON payloads
**Depends on**: Phase 1
**Requirements**: SRC-01, SRC-02, SRC-03, SRC-04, SRC-05, SRC-06, SRC-07, SRC-08, SRC-09, SRC-10
**Success Criteria** (what must be TRUE):
  1. A real community book source JSON file loads without error and all required fields validate
  2. A CSS selector rule (`css:.title@text`) extracts the expected string from a sample HTML fixture
  3. An XPath rule and a JSONPath rule each extract correct values from their respective fixtures
  4. A `##pattern##replacement` replaceRegex chain transforms a string correctly
  5. An `@js: result.trim()` expression and a `<js>...</js>` block both execute via quickjs with the correct `result` and `baseUrl` context variables
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Bootstrap: rules sub-package skeleton, _errors.py, _detect.py, _source.py (SRC-01, SRC-02), pyproject.toml deps, all Wave 0 test stubs
- [x] 02-02-PLAN.md — Selector engine: _css.py, _xpath.py, _jsonpath.py, evaluate() dispatcher (SRC-03, SRC-04, SRC-05)
- [x] 02-03-PLAN.md — Post-processing: _regex.py (replaceRegex), _templates.py (URL template) (SRC-06, SRC-10)
- [x] 02-04-PLAN.md — JS layer: _js.py (quickjs), evaluate() fully wired for @js: and <js> (SRC-07, SRC-08, SRC-09)

### Phase 3: HTTP + Source Loading
**Goal**: The tool fetches real novel website pages using book source headers and cookies, correctly transcoding GBK responses, and follows multi-page TOC and content chains
**Depends on**: Phase 2
**Requirements**: HTTP-01, HTTP-02, HTTP-03, HTTP-04, HTTP-05
**Success Criteria** (what must be TRUE):
  1. `/novel use <source.json>` loads a real community book source file and confirms it is stored under `~/.claude-legado/sources/`
  2. A GBK-encoded novel site response is fetched and displayed as correct UTF-8 Chinese text
  3. A multi-page TOC (site with `nextTocUrl`) is fully traversed and all chapter links are collected
  4. HTTP headers from the book source `header` field are sent with every request to that source's domain
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — HTTP client + encoding + /novel use: _client.py (headers, fetch, cookie jar), _encoding.py (charset cascade), /novel use command wiring (HTTP-01, HTTP-02, HTTP-03)
- [x] 03-02-PLAN.md — Pagination + ajax wiring: _pagination.py (follow_toc_pages, follow_content_pages), _js.py two-pass ajax injection (HTTP-04, HTTP-05)

### Phase 4: Read Pipeline
**Goal**: A user can search for a book, add it to the shelf, open its TOC, and read a chapter — all against a real live novel source
**Depends on**: Phase 2, Phase 3
**Requirements**: FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05
**Success Criteria** (what must be TRUE):
  1. `/novel search 斗破苍穹` returns a list of book titles and authors fetched from a real source
  2. Selecting a search result adds the book to the shelf and fetches its first TOC page
  3. `/novel toc` displays the full ordered chapter list for the current book
  4. `/novel` (or `/novel next`) streams the content of the current chapter fetched from the real site
  5. Reading position advances correctly after each chapter and persists across invocations
**Plans**: TBD

Plans:
- [x] 04-01: Search flow — build search URL from template, fetch, apply `ruleSearch`, return formatted book list (`FLOW-01`)
- [x] 04-02: Book info + shelf add — fetch detail page, apply `ruleBookInfo`, persist to `shelf.json` with initial TOC fetch (`FLOW-02`, `FLOW-05`)
- [x] 04-03: TOC flow — fetch TOC pages, apply `ruleToc`, collect ordered chapter list, display via `/novel toc` (`FLOW-03`)
- [x] 04-04: Content flow — fetch chapter URL, apply `ruleContent`, clean text, stream via display engine (`FLOW-04`)

### Phase 5: Polish
**Goal**: The tool handles real-world failures gracefully and a new user can install and start reading from the README alone
**Depends on**: Phase 4
**Requirements**: (hardening across all prior requirements — no new v1 reqs)
**Success Criteria** (what must be TRUE):
  1. A network timeout or HTTP error produces a readable message and leaves state intact (no corrupt `state.json`)
  2. A malformed or unsupported book source rule fails with a clear "rule not supported" message rather than a Python traceback
  3. `/novel shelf` shows each book with its title, author, current chapter, and total chapter count
  4. A developer with no prior context can follow the README to install dependencies and read a chapter within five minutes
**Plans**: TBD

Plans:
- [x] 05-01: Error handling hardening — network errors, rule parse failures, missing state, graceful degradation
- [ ] 05-02: Bookshelf UX — `/novel shelf` display with progress, `/novel toc` chapter count and current marker
- [ ] 05-03: README and setup — installation steps, dependency list, example book source, usage walkthrough

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Scaffold, Display, State | 3/3 | Complete | 2026-04-07 |
| 2. Rule Engine | 4/4 | Complete | 2026-04-08 |
| 3. HTTP + Source Loading | 0/2 | Not started | - |
| 4. Read Pipeline | 0/4 | Not started | - |
| 5. Polish | 0/3 | Not started | - |
