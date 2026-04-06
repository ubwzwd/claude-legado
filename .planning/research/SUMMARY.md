# Research Summary: claude-legado

**Synthesized:** 2026-04-07
**Sources:** BOOK_SOURCES.md, SKILL_SYSTEM.md, TERMINAL_UI.md, NOVEL_SOURCES.md

---

## Stack Decision

**Python** is the right choice for all components.

| Layer | Choice | Reason |
|-------|--------|--------|
| HTTP | `httpx` (async) or `requests` (sync) | GBK encoding support via `chardet`/`iconv`; mature cookie jar |
| HTML parsing | `lxml` + `cssselect` | CSS and XPath selectors in one library — maps directly to legado rule prefixes |
| JSON | stdlib `json` | Standard |
| JS rules | `quickjs` (python-quickjs) | Lightweight, embeddable, handles `@js:` and `<js>` blocks without a full browser |
| Terminal output | `rich` | Native CJK width handling (`wcwidth`); Live/streaming output; works in Claude's Bash tool stdout |
| Keyboard input | `readchar` | Cross-platform; handles escape sequences for arrow keys; works in raw terminal mode |
| Progress storage | `~/.claude-legado/` JSON files | Simple, no dependencies |

Node.js was considered but rejected: legado book sources use CSS/XPath/JSONPath rules, and Python's `lxml`+`cssselect` handles this more cleanly than Node.js equivalents.

---

## Architecture Decision: Chapter-Per-Invocation

**Critical finding from SKILL_SYSTEM.md:** Claude Code skills run inside the Bash tool. There is no guaranteed PTY ownership or stdin. A persistent TUI session (curses, blessed) is not viable.

**Design consequence:** The `/novel` skill is chapter-per-invocation.

```
/novel                    → show current book + chapter, stream content
/novel search <query>     → search, show results
/novel add <url>          → add book to library
/novel next               → advance to next chapter, stream content
/novel prev               → go back one chapter, stream content
/novel toc                → show chapter list
/novel shelf              → show bookshelf
/novel use <source.json>  → load a book source file
```

State is persisted between invocations in `~/.claude-legado/state.json` (current book, chapter, position).

The streaming/typewriter effect works via `sys.stdout.write()` + `sys.stdout.flush()` — Claude's Bash tool does pass through stdout in real-time.

---

## Camouflage Design

The disguise works through streaming output styled to match Claude Code's response format:

```
◆ Fetching chapter...

  第三章 风云突变

  李云飞看着眼前的剑，心中
  暗想：此人武功深不可测...

  [继续: /novel next  |  目录: /novel toc  |  退出: /novel shelf]
```

Key points:
- Streaming with variable delay: 15-40ms per char, longer pauses at `。！？` (Chinese punctuation)
- Occasional burst chunks (8-15 chars) to mimic real LLM token streaming
- `rich` handles CJK double-width characters automatically — `len()` must NOT be used for line wrapping
- Output uses Rich's `Console` in streaming mode, no alternate screen buffer (keeps scrollback intact)

---

## Legado Book Source Format

A book source is a JSON object with:
- **Metadata**: `bookSourceUrl` (unique key), `bookSourceName`, `header` (HTTP headers JSON string)
- **URL templates**: `searchUrl` (`{{key}}`, `{{page}}`), `exploreUrl`
- **5 rule objects**: `ruleSearch`, `ruleExplore`, `ruleBookInfo`, `ruleToc`, `ruleContent`

### Rule Syntax

All rules use unified syntax: `prefix:selector@attribute##replaceRegex`

| Prefix | Example | Backend |
|--------|---------|---------|
| `css:` | `css:.book-name@text` | cssselect |
| `xpath:` | `xpath://h3/text()` | lxml |
| `$.` / `json:` | `$.data.list` | jsonpath-ng |
| `@js:` | `@js: result.split('\n')[0]` | quickjs |
| (none) | `.book-name@text` | auto-detect |

### JS Execution Context

`@js:` and `<js>...</js>` blocks receive these variables:
- `result` — the current extracted value
- `baseUrl` — the page URL
- `java.ajax(url)` — synchronous HTTP fetch (must be re-implemented as sync wrapper over async)
- `java.base64Decode(s)`, `java.md5(s)`, etc.

### Multi-page handling
- TOC: follow `nextTocUrl` rule until empty
- Content: follow `nextContentUrl` rule until empty

---

## Novel Source Accessibility Tiers

| Tier | Anti-scraping | HTTP needed | Scope |
|------|--------------|-------------|-------|
| A | None / User-Agent only | Plain requests | ✓ In scope (笔趣阁 families) |
| B | Referer + cookie | requests + jar | ✓ In scope |
| C | JS rule logic | requests + quickjs | ✓ In scope |
| D | Cloudflare | Playwright | ✗ Out of scope |
| E | Login required | Auth flow | ✗ Out of scope |

~90% of community free sources fall in Tier A–C.

**GBK encoding:** Many older Chinese novel sites serve GBK/GB2312. Must detect and transcode at HTTP layer using `chardet` + `codecs`.

---

## Key Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `java.ajax()` sync-in-JS incompatibility | HIGH | Implement as async wrapper; inject pre-fetched result into JS context |
| Site HTML structure changes | MEDIUM | Sources are community-maintained; user imports updated sources |
| CJK width bugs in terminal | MEDIUM | Use Rich throughout; never call `len()` on Chinese strings for layout |
| stdout not streaming in Bash tool | LOW | Confirmed: Bash tool passes stdout through; use `flush=True` |
| Domain instability of 笔趣阁 mirrors | HIGH | Ship with source import workflow; don't hardcode URLs |

---

## Phasing Guidance

1. **Phase 1 — Skill scaffold + streaming display**: Skill file, Python script entry point, fake streaming output, state persistence. Validate camouflage works before building the scraper.
2. **Phase 2 — Rule engine**: CSS/XPath/JSON selector parsing, `@js:` execution via quickjs, replaceRegex, URL template substitution.
3. **Phase 3 — HTTP + source loading**: Load `.json` book source files, HTTP fetch with headers/cookies/encoding, GBK transcoding.
4. **Phase 4 — Search + TOC + content flow**: Wire search → bookInfo → TOC → chapter content using rule engine + HTTP layer.
5. **Phase 5 — Library management**: Bookshelf, reading progress, `/novel shelf`, `/novel toc`.

Phase 1 and Phase 2 can be validated independently. Phase 4 depends on Phases 2 and 3.
