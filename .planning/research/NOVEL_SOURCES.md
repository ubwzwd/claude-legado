# Novel Sources Research: Chinese Web Novel Ecosystem

**Domain:** Chinese web novel scraping and legado book source format
**Researched:** 2026-04-06
**Overall confidence:** MEDIUM — Training knowledge (cutoff Aug 2025). Network tools unavailable for live verification. Flagged where live validation is critical.

---

## 1. Major Free Chinese Novel Websites

### Tier 1: Large Traffic, Partially Free

**起点中文网 (qidian.com)**
- Owned by Tencent (阅文集团 / China Literature)
- Business model: VIP chapters behind paywall; first ~100 chapters often free; "免费区" (free zone) exists with fully free novels
- Anti-scraping: Aggressive. Cloudflare, JS fingerprinting, token-based chapter URLs, rotating selectors
- API: No public API. Mobile app uses private signed API (HTTPS + token). Reverse-engineered endpoints exist but rotate
- Accessibility: LOW for scraping without heavy tooling
- Confidence: HIGH (well-documented in community)

**番茄小说 (fanqienovel.com / 字节跳动 ByteDance)**
- Fully free model, ByteDance-owned
- Large catalog including exclusives
- Anti-scraping: Moderate. Uses JS obfuscation, some Cloudflare, chapter content split across multiple API calls with signed tokens
- API: Private app API partially reverse-engineered by community. JSON responses. Some legado sources target their API directly
- Accessibility: MEDIUM — plain HTTP possible for some endpoints but tokens required
- Confidence: MEDIUM (community sources exist, behavior may have changed)

**七猫免费小说 (qimao.com)**
- Fully free, ad-supported
- Good catalog of popular titles
- Anti-scraping: Light to moderate. Some JS rendering required for pagination
- API: Mobile app uses JSON API, partially accessible without auth for free chapters
- Accessibility: MEDIUM-HIGH
- Confidence: MEDIUM

**笔趣阁 / 笔趣看 (multiple mirror domains)**
- Not a single site — a brand name copied across hundreds of mirror sites (biquge.*, biqukan.*, biqugse.*, etc.)
- Fully free, ad-heavy, SEO scraper farms
- Anti-scraping: Very light. Usually plain HTML, minimal JS, no auth required
- API: None — pure HTML scraping
- Accessibility: HIGH (easiest to scrape)
- Note: Domain stability is poor — mirrors appear and disappear. The legado community constantly updates 笔趣阁 sources to track live mirrors
- Confidence: HIGH

**书旗小说 (shuqi.com) — also 书旗免费版**
- Owned by Alibaba
- Mixed free/paid
- Anti-scraping: Moderate. Some Cloudflare, user-agent checking
- Accessibility: MEDIUM
- Confidence: MEDIUM

**起点免费 / 免费小说区**
- 起点 has a dedicated free section at different URL paths; distinct from the main paid site
- Easier to access than paid 起点 chapters
- Anti-scraping: Moderate (same domain infrastructure as paid)
- Confidence: MEDIUM

### Tier 2: Mid-Size Free Sites (Common in legado community sources)

| Site | Domain Pattern | Model | JS Required | Notes |
|------|---------------|-------|-------------|-------|
| 顶点小说 | ddxsku.com / variants | Free | No | HTML, popular legado target |
| 一秒钟小说 | 1miaoshu.com variants | Free | No | Simple HTML |
| 新笔趣阁 | xbqg variants | Free | No | 笔趣阁 family |
| 飞卢小说 | faloo.com | Mixed | Light | More structured HTML |
| 起点轻小说 | qingkan.com | Free | Light | Light novels |
| 精华书阁 | various | Free | No | Pure HTML |
| 掌阅 (zhangyue.com) | Paid-primary | Paid | Heavy | Not worth targeting |

Confidence for Tier 2: MEDIUM — site availability changes frequently, this reflects community knowledge as of 2025.

---

## 2. Legado Book Source Format (书源)

### What a Book Source Is

A legado 书源 (book source) is a JSON object describing scraping rules for one website. The legado Android app interprets these rules using a built-in rule engine. The community maintains shared repositories of thousands of sources.

### JSON Structure (HIGH confidence — from legado source code and docs)

```json
{
  "bookSourceUrl": "https://example.com",
  "bookSourceName": "示例小说网",
  "bookSourceType": 0,
  "bookSourceGroup": "免费",
  "enabled": true,
  "enabledExplore": true,
  "header": "{\n  \"User-Agent\": \"Mozilla/5.0...\",\n  \"Referer\": \"https://example.com\"\n}",
  "loginUrl": "",
  "loginCheckJs": "",
  "bookUrlPattern": "",
  "searchUrl": "https://example.com/search?q={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": ".search-result .item",
    "name": ".title",
    "author": ".author",
    "bookUrl": "a@href",
    "coverUrl": "img@src",
    "intro": ".desc",
    "kind": ".tag",
    "lastChapter": ".last-chap"
  },
  "ruleBookInfo": {
    "init": "",
    "name": "h1.book-title",
    "author": ".author-name",
    "coverUrl": ".cover img@src",
    "intro": "#intro",
    "kind": ".tag",
    "lastChapter": ".last-chapter",
    "tocUrl": ".chapter-list@href"
  },
  "ruleToc": {
    "chapterList": "#chapter-list li",
    "chapterName": "a",
    "chapterUrl": "a@href",
    "nextTocUrl": ".next-page@href"
  },
  "ruleContent": {
    "content": "#content",
    "nextContentUrl": "",
    "webJs": "",
    "sourceRegex": "",
    "replaceRegex": ""
  }
}
```

### Rule Syntax (HIGH confidence)

Legado uses a custom rule language. Key constructs:

- **CSS selectors**: `div.class`, `#id`, standard CSS
- **XPath**: `//div[@class='content']` — prefix with `//` or use `@xpath:`
- **JSONPath**: `$.data.list[*]` — for JSON API responses
- **Attribute extraction**: `tag@attribute` e.g. `a@href`, `img@src`
- **Regex**: `##regex` appended to rule
- **JS execution**: `<js>...</js>` blocks for arbitrary JavaScript
- **String interpolation**: `{{key}}` for search terms, `{{page}}` for pagination
- **PUT/POST**: Search URL supports `@POST:` prefix and `{body}` template

### JS Execution in Book Sources

Legado runs JS rules in an embedded JavaScript engine (Rhino in older versions, moving toward V8-based). This means:

- `<js>` blocks can manipulate the fetched HTML/JSON before rule extraction
- Can do string manipulation, base64 decode, XOR decryption
- Can call `java.xxx` bridge methods for HTTP requests from within JS
- Used for: decrypting obfuscated content, computing signed tokens, parsing non-standard formats

Example JS rule (content decryption pattern seen in community sources):
```javascript
<js>
  var content = result;
  // XOR decrypt with hardcoded key
  var key = 12345;
  var decoded = '';
  for (var i = 0; i < content.length; i++) {
    decoded += String.fromCharCode(content.charCodeAt(i) ^ key);
  }
  decoded
</js>
```

### Header Injection

The `header` field (JSON string) allows custom HTTP headers per source:
- `User-Agent` spoofing (mobile UA strings common)
- `Referer` headers to pass hotlink checks
- `Cookie` injection for sites requiring session cookies
- `X-Requested-With` for AJAX-style requests

---

## 3. Anti-Scraping Measures by Site Type

### Plain HTML Sites (笔趣阁 family, 顶点, etc.)

**Measures encountered:**
- User-agent checking (solved with browser UA in header)
- Referer checking (solved with header injection)
- Simple rate limiting (solved with delays between requests)
- IP blocking for high-frequency scrapers

**Countermeasures needed:** Plain HTTP with correct headers. No JS rendering required.

**Confidence:** HIGH

### Mid-tier free sites (七猫, 番茄 web)

**Measures encountered:**
- Cloudflare Bot Management (CF challenge pages — `cf_clearance` cookie required)
- JavaScript-rendered content (chapter text loaded via AJAX after initial page load)
- Token/signature parameters in API calls (timestamp + HMAC-signed params)
- Dynamic CSS class names (obfuscated selectors that rotate)

**Countermeasures:**
- CF clearance: Requires headless browser + FlareSolverr or similar once; store cookie
- AJAX content: Can often be replicated with direct API calls once endpoint is identified
- Tokens: Some are time-based and can be computed; others require JS execution

**Confidence:** MEDIUM

### Major platforms (起点, 书旗 Alibaba-owned)

**Measures encountered:**
- Heavy Cloudflare (CF Enterprise tier on some)
- App-only content delivery (chapters only available through signed API + device fingerprint)
- Encrypted chapter content (content XOR/AES encrypted, key derived from device/account)
- CAPTCHA on search
- Account binding (chapters require login session)

**Countermeasures:** Extremely difficult without maintaining signed mobile app sessions. Not practical for a CLI tool without auth.

**Confidence:** HIGH (these are not viable targets for this project)

---

## 4. Public APIs and Official Reading APIs

**Verdict:** No major Chinese novel platform offers a public developer API for content access. (HIGH confidence)

**Known partial exceptions:**
- 番茄小说 web API: Some endpoints are called without authentication on the web version, discoverable via browser devtools. These have been reverse-engineered by the legado community. However ByteDance actively patches these.
- 七猫 mobile API: JSON-based, partially accessible, but signing keys rotate
- 起点 内容开放平台: Exists (open.qidian.com) but is for publishing/analytics, NOT reading content via API

**Practical conclusion:** All viable sources scrape HTML or reverse-engineer private mobile APIs. There are no sanctioned programmatic reading APIs.

---

## 5. HTTP Libraries Recommendation

### Python

**Primary: `httpx` (async)**
- Native async/await support — important for reading multiple chapters without blocking
- HTTP/2 support (some sites prefer it)
- Clean API similar to `requests`
- Built-in timeout, retry, connection pooling
- `pip install httpx`

**Alternative: `requests` (sync)**
- Simpler if async not needed
- Vast ecosystem (requests-cache, requests-html)
- Slower for multiple sequential requests
- Good for prototyping and simple sources

**For JS-rendering sites: `playwright` (Python)**
- Full browser automation
- Can handle Cloudflare, CAPTCHAs (manual solve flow), cookie extraction
- Heavy dependency — only use when needed
- `pip install playwright && playwright install chromium`

**HTML parsing: `beautifulsoup4` + `lxml`**
- Industry standard for HTML scraping
- `pip install beautifulsoup4 lxml`
- CSS selectors via `bs4.select()`, XPath via `lxml.etree`

**JSON: stdlib `json` module — no extra dep needed**

**Recommended stack for this project:**
```
httpx[http2]     # async HTTP client
beautifulsoup4   # HTML parsing
lxml             # fast XML/HTML parser backend for bs4
jsonpath-ng      # JSONPath for JSON API responses
```

### Node.js (if chosen instead)

**`axios`** — mature, promise-based, good interceptor system  
**`undici`** — faster, Node native, lower overhead  
**`playwright`** — for JS-rendering  
**`cheerio`** — jQuery-style HTML parsing (no JS execution)  
**`node-html-parser`** — faster, less feature-rich alternative to cheerio  

---

## 6. JS Rendering Requirements

### Do most sources need a headless browser?

**No — for the viable free sources, plain HTTP is sufficient.** (MEDIUM-HIGH confidence)

The pattern in the legado community:
- ~70% of community book sources target plain-HTML sites (笔趣阁 family, mid-tier free sites)
- ~20% use JSON API calls (番茄, 七猫 mobile APIs) — plain HTTP with correct headers
- ~10% use JS execution within the legado rule engine for content decryption/manipulation — but this is JS logic applied to already-fetched content, not JS-rendered pages

For the legado-compatible CLI tool:
- The `<js>` blocks in book sources run JavaScript **on already-fetched content** to post-process it
- This is not headless browser rendering — it's a sandboxed JS eval for data transformation
- The tool needs a JS engine (not a browser) to execute these rules

**Headless browser requirement:**
- Only needed for Cloudflare-protected sites
- Not needed for any of the recommended Tier 1 free sources (番茄 web, 七猫, 笔趣阁)
- For this project, headless browser support should be out of scope initially; treat CF-protected sources as incompatible

### Implementing the `<js>` rule engine

The legado `<js>` rule blocks need a JavaScript runtime, not a browser:
- **Node.js**: Can eval JS natively — if the tool is Node-based this is trivial
- **Python + `execjs`**: `pip install PyExecJS` — runs JS via Node.js subprocess
- **Python + `js2py`**: Pure Python JS interpreter — limited ES6 support, may fail on complex sources
- **Python + `quickjs`**: `pip install quickjs` — embeds QuickJS engine (ES2020 support, fast, no Node dependency)
- **Recommendation: `quickjs` for Python** — best balance of compatibility and self-containment

---

## 7. Typical Response Formats

### Plain HTML (most common for free sites)

```html
<html>
  <div id="content">
    第一章 content text here...
    <p>paragraph one</p>
    <p>paragraph two</p>
  </div>
</html>
```

- Ads often embedded within content `<div>` — need regex cleanup rules
- Chapter navigation via `<a>` links to next/prev chapter URLs
- Content sometimes split across multiple pages (pagination)
- legado `ruleContent.replaceRegex` handles ad/junk text removal

### JSON API (番茄, 七猫, mid-tier apps)

```json
{
  "code": 0,
  "data": {
    "chapterId": "123456",
    "title": "第一章 开始",
    "content": "章节内容...",
    "nextChapterId": "123457"
  }
}
```

- Content may be base64 encoded
- Content may be split into multiple segments (`content_items` array)
- Pagination via `nextChapterId` or `cursor` parameters

### Mixed (HTML page + embedded JSON)

Some sites embed chapter data in a `<script>` tag as JSON within the HTML page:
```html
<script>
window.__INITIAL_STATE__ = {"chapter": {"content": "...", ...}}
</script>
```
- legado `<js>` rules handle extracting this with `JSON.parse()`

---

## 8. Community Book Source Repositories

The legado community maintains several public GitHub repositories of book sources:

**Primary community sources:**
- `gedoor/legado` — official app, includes some example sources
- `XIU2/yuedu` — large curated collection (数百个高质量书源)
- Various QQ group and Telegram channel shared sources (not in public git)

**Source format notes from community practice:**
- Sources are distributed as JSON arrays (list of source objects)
- Sources expire frequently — site structure changes break selectors
- "有效源" (valid/working sources) vs "失效源" (broken sources) is a constant maintenance concern
- The community tags sources by: free/paid, content type, language, reliability

**Most stable source targets (historically):**
1. 笔趣阁 mirror sites — extremely simple HTML, most commonly maintained
2. 番茄小说 web — ByteDance maintains consistent API structure (breaks less often)
3. 顶点小说 — stable HTML structure
4. 七猫 web — moderate stability

---

## 9. Legal and ToS Considerations

**Disclaimer: This is general information, not legal advice.**

### Chinese Law Context

- Chinese copyright law (著作权法) protects novel content
- Web scraping itself is not explicitly illegal in China, but ToS violations are contractual
- Platforms' ToS universally prohibit automated access and content scraping
- Free novel content is still copyright-protected; "free to read" ≠ "free to redistribute"

### ToS Posture of Major Sites

| Platform | Prohibits Scraping | Enforces Legally | Notes |
|----------|-------------------|-----------------|-------|
| 起点/阅文 | Yes | Actively | Has sued aggregator sites |
| 番茄/ByteDance | Yes | Moderate | Mainly blocks technically |
| 七猫 | Yes | Light | Technical blocking only |
| 笔趣阁 mirrors | Unclear | No | Many are themselves piracy sites |

### Practical Considerations for This Project

- Personal use (reading for oneself) is the gray area where enforcement is nearly zero
- The legado app itself has been available for years without legal challenge — it's a reader, not a redistributor
- This CLI tool, like legado, is a reader that fetches content for personal display
- **Key risk mitigation:** Don't cache/store/redistribute content; fetch-on-demand only
- Paid content is explicitly out of scope (per PROJECT.md) — reduces exposure significantly
- The real legal risk is redistribution at scale, not personal reading

### Confidence: MEDIUM — based on observed enforcement patterns as of 2025, not legal analysis

---

## 10. Implementing the legado Rule Engine in Python/Node.js

This is the core technical challenge for this project.

### Rule Types to Implement

| Rule Type | Example | Implementation |
|-----------|---------|----------------|
| CSS selector | `div#content p` | `bs4.select()` or cheerio |
| XPath | `//div[@id='content']` | `lxml.etree` |
| JSONPath | `$.data.content` | `jsonpath-ng` |
| Attribute extract | `a@href` | Post-processing after selector |
| Regex | `##(\d+)` | `re` module |
| JS block | `<js>result.trim()</js>` | `quickjs` or Node eval |
| Concat | `name@@author` | String join |
| Negative | `@!` | Filter out matching elements |

### Variable System

Legado rules use these variables accessible in JS blocks:
- `result` — current extracted value (string/array)
- `baseUrl` — current page URL
- `java.getString(key)` — access stored variables
- `java.put(key, value)` — store variables for cross-rule use

### HTTP Request Handling

The rule engine drives HTTP requests through:
1. `searchUrl` — first request, fills `{{key}}` and `{{page}}`
2. `ruleBookInfo.init` — optional secondary request for book info page
3. `ruleToc.nextTocUrl` — pagination of chapter list
4. `ruleContent.nextContentUrl` — pagination within a chapter

For Python implementation:
- Use `httpx.AsyncClient` with session persistence (cookies, headers)
- Apply source's `header` JSON to every request in session
- Handle `@POST:` prefix by switching to POST method

---

## 11. Recommended Approach for This Project

### Use Plain HTTP for All Sources

Do not attempt headless browser support initially. Focus on:
1. Plain HTML sources (笔趣阁, 顶点, etc.)
2. JSON API sources (番茄 web API, 七猫 API)
3. JS-in-rule sources (content processed after fetch, not browser-rendered)

This covers ~90% of actively-maintained free community sources.

### Source Compatibility Tier

| Tier | Description | Support |
|------|-------------|---------|
| A | Plain HTML, no auth, no JS rendering | Full support |
| B | JSON API, no auth | Full support |
| C | Requires `<js>` rule execution | Support with QuickJS |
| D | Requires Cloudflare clearance | Out of scope |
| E | Requires account login | Out of scope (per PROJECT.md) |

### Starter Sources to Test Against

Target these for initial development (most stable, most common in community):

1. Any live 笔趣阁 mirror (e.g., `www.biquge.biz` or current mirror) — plain HTML, Tier A
2. 番茄小说 web (`fanqienovel.com`) — JSON API, Tier B
3. 顶点小说 (`www.ddxsku.com`) — plain HTML, Tier A

---

## Sources and Confidence

This research is based on:
- Training knowledge of legado's open-source codebase (GitHub: gedoor/legado)
- Training knowledge of the Chinese novel community book source ecosystem (XIU2/yuedu, legado forums)
- General knowledge of Chinese novel platform anti-scraping behaviors

**Network verification was not possible** (WebSearch and WebFetch tools unavailable in this environment). All findings should be validated against:
- Current legado wiki: https://github.com/gedoor/legado/wiki
- Current community sources: https://github.com/XIU2/yuedu
- Live site behavior testing with actual HTTP clients

**Confidence summary:**

| Area | Level | Reason |
|------|-------|--------|
| Legado JSON format/rules | HIGH | Open-source, well-documented, stable spec |
| Site availability/accessibility | MEDIUM | Sites change frequently; reflect 2024-2025 patterns |
| Anti-scraping specifics | MEDIUM | Patterns are consistent but implementation details drift |
| JS rule engine mechanics | HIGH | From legado Kotlin source code, stable |
| Public API existence | HIGH | Definitively no public APIs exist |
| Legal considerations | MEDIUM | Based on observed patterns, not legal research |
| HTTP library recommendations | HIGH | Stable ecosystem choices |
