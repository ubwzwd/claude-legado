# Requirements: claude-legado

**Defined:** 2026-04-07
**Core Value:** Read Chinese web novels in Claude Code, looking indistinguishable from real AI work

## v1 Requirements

### Skill Interface

- [ ] **SKILL-01**: Claude Code skill file at `.claude/commands/novel.md` triggers `/novel` command
- [ ] **SKILL-02**: `/novel` with no args streams current chapter (or prompts to pick a book if shelf empty)
- [ ] **SKILL-03**: `/novel next` advances to next chapter and streams content
- [ ] **SKILL-04**: `/novel prev` goes back one chapter and streams content
- [ ] **SKILL-05**: `/novel search <query>` searches current book source and shows results
- [ ] **SKILL-06**: `/novel toc` shows chapter list for current book
- [ ] **SKILL-07**: `/novel shelf` shows all saved books with reading progress
- [ ] **SKILL-08**: `/novel use <path>` loads a book source JSON file

### Streaming Display

- [ ] **DISP-01**: Chapter content streams character-by-character mimicking Claude AI response output
- [ ] **DISP-02**: Variable delay per character (15-40ms base, longer pauses at `。！？`)
- [ ] **DISP-03**: Occasional burst chunks (8-15 chars) to mimic real LLM token streaming
- [ ] **DISP-04**: CJK double-width characters handled correctly (no overflow, no misaligned lines)
- [ ] **DISP-05**: Output uses Rich Console in streaming mode — no alternate screen buffer (scrollback preserved)
- [ ] **DISP-06**: Chapter header shown before content (chapter number + title)
- [ ] **DISP-07**: Navigation hint shown at end of each chapter (`/novel next`, `/novel toc`, etc.)

### State Persistence

- [ ] **STATE-01**: Reading state persisted to `~/.claude-legado/state.json` (current book, chapter index, source)
- [ ] **STATE-02**: `/novel` with no args resumes from last saved position automatically
- [ ] **STATE-03**: Bookshelf persisted to `~/.claude-legado/shelf.json` (list of added books)
- [ ] **STATE-04**: Loaded book sources persisted to `~/.claude-legado/sources/`

### Book Source Engine

- [ ] **SRC-01**: Parse legado book source JSON format (single object or array)
- [ ] **SRC-02**: Validate required fields (`bookSourceUrl`, `bookSourceName`, rule objects)
- [ ] **SRC-03**: Support CSS selector rules (`css:selector@attribute`)
- [ ] **SRC-04**: Support XPath rules (`xpath://path/text()`)
- [ ] **SRC-05**: Support JSONPath rules (`$.path.to.field`)
- [ ] **SRC-06**: Support `replaceRegex` post-processing (`##pattern##replacement`)
- [ ] **SRC-07**: Support `@js:` inline JS expressions via quickjs engine
- [ ] **SRC-08**: Support `<js>...</js>` block JS via quickjs engine
- [ ] **SRC-09**: JS context provides `result`, `baseUrl`, `java.base64Decode()`, `java.md5()`
- [ ] **SRC-10**: URL template substitution (`{{key}}`, `{{page}}`)

### HTTP Layer

- [ ] **HTTP-01**: Fetch URLs with custom headers from book source `header` field
- [ ] **HTTP-02**: Auto-detect and transcode GBK/GB2312 responses to UTF-8
- [ ] **HTTP-03**: Cookie jar per book source domain
- [ ] **HTTP-04**: Follow multi-page TOC (`nextTocUrl`) until empty
- [ ] **HTTP-05**: Follow multi-page chapter content (`nextContentUrl`) until empty

### Search + Read Flow

- [ ] **FLOW-01**: Search: build search URL from template → fetch → parse `ruleSearch` → return book list
- [ ] **FLOW-02**: Book info: fetch book detail page → parse `ruleBookInfo` → extract title/author/cover/intro
- [ ] **FLOW-03**: TOC: fetch TOC page → parse `ruleToc` → return ordered chapter list with URLs
- [ ] **FLOW-04**: Content: fetch chapter URL → parse `ruleContent` → return clean text
- [ ] **FLOW-05**: Add book from search result to shelf with first TOC fetch

## v2 Requirements

### Enhanced Display

- **DISP-V2-01**: Configurable streaming speed (slow/normal/fast)
- **DISP-V2-02**: Color themes (default dark, light mode)
- **DISP-V2-03**: Font width detection warning when CJK glyphs missing

### Source Management

- **SRC-V2-01**: Import multiple sources from a JSON array file
- **SRC-V2-02**: List and switch between loaded sources (`/novel sources`)
- **SRC-V2-03**: Test a source's connectivity and rule validity

### Explore / Browse

- **FLOW-V2-01**: `/novel explore` — browse featured books from source's `exploreUrl`

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cloudflare-protected sources (Tier D) | Requires Playwright/headless browser — enormous complexity |
| Login-required sources (Tier E) | Auth flow adds scope without serving the core use case |
| Audio book sources (`bookSourceType: 1`) | Text-only v1 |
| Manga/image sources (`bookSourceType: 2`) | Terminal can't render images usefully |
| Real-time sync with legado Android app | Different platform entirely |
| Interactive keyboard nav within a chapter | No stdin in Claude Code's Bash tool |
| Search across multiple sources simultaneously | Complexity/v2 |
| Web UI or GUI | Terminal only |
| Writing/downloading chapters for offline use | Not the use case |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SKILL-01..08 | Phase 1 | Pending |
| DISP-01..07 | Phase 1 | Pending |
| STATE-01..04 | Phase 1 | Pending |
| SRC-01..10 | Phase 2 | Pending |
| HTTP-01..05 | Phase 3 | Pending |
| FLOW-01..05 | Phase 4 | Pending |
| (all prior) | Phase 5 | Pending (hardening — no new reqs) |

**Coverage:**
- v1 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0 ✓
- Phase 5 applies hardening across all prior requirements (no new v1 reqs)

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-07 after roadmap creation*
