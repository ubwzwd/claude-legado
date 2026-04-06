# Legado Book Source Format — Deep Research

**Project:** claude-legado
**Researched:** 2026-04-06
**Overall confidence:** MEDIUM-HIGH
**Sources:** legado GitHub source code (BookSource.kt, BookSourcePart.kt, RuleBook.kt, AnalyzeUrl.kt, AnalyzeRule.kt, JsExtensions.kt), community documentation at legado.aoaostar.com, gitee mirror documentation

---

## 1. What a Book Source Is

A legado 书源 (book source) is a JSON object (or array of them) describing how to scrape one novel website. It encodes:

- How to build a search URL from a query string
- How to parse search results into a list of books with metadata
- How to find and parse a book's chapter list (目录)
- How to fetch and extract the text content of one chapter (正文)
- How to discover book metadata (cover, author, intro, category)

The format is purely declarative except for optional embedded JavaScript snippets. The legado Android app interprets these rules. This project re-implements that interpreter in TypeScript/Node.js.

---

## 2. Top-Level JSON Structure

A single book source is a JSON object. Collections are JSON arrays of these objects.

### 2.1 All Top-Level Fields

```json
{
  "bookSourceUrl":        "https://example.com",
  "bookSourceName":       "示例书源",
  "bookSourceGroup":      "小说",
  "bookSourceType":       0,
  "bookSourceComment":    "备注说明",
  "enabled":              true,
  "enabledExplore":       true,
  "enabledCookieJar":     false,
  "header":               "{\"User-Agent\": \"Mozilla/5.0\"}",
  "loginUrl":             "",
  "loginUi":              "",
  "loginCheckJs":         "",
  "respondTime":          180000,
  "weight":               0,
  "customOrder":          0,
  "lastUpdateTime":       1700000000000,
  "concurrentRate":       "",
  "variableComment":      "",

  "searchUrl":            "https://example.com/search?q={{key}}&page={{page}}",
  "exploreUrl":           "https://example.com/explore/{{page}}",

  "ruleSearch":           { ... },
  "ruleExplore":          { ... },
  "ruleBookInfo":         { ... },
  "ruleToc":              { ... },
  "ruleContent":          { ... }
}
```

### 2.2 Field Reference

#### Identity / Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bookSourceUrl` | string | YES | The base URL of the source website. Acts as the unique key/ID for the source. |
| `bookSourceName` | string | YES | Display name shown in the app's source list. |
| `bookSourceGroup` | string | NO | Comma-separated group tags, e.g. `"小说,精品"`. Used for filtering. |
| `bookSourceType` | int | YES | Source type: `0` = novel/text, `1` = audio book, `2` = image (manga), `3` = file. |
| `bookSourceComment` | string | NO | Freeform notes, author attribution, change log. |
| `enabled` | bool | NO | Whether this source is active. Default `true`. |
| `enabledExplore` | bool | NO | Whether the discover/browse (发现) feature is enabled. Default `true`. |
| `enabledCookieJar` | bool | NO | If `true`, legado manages a cookie jar for this domain. |
| `header` | string | NO | JSON string of HTTP headers to include in every request from this source. |
| `loginUrl` | string | NO | URL for a login page or login POST endpoint. |
| `loginUi` | string | NO | JSON describing login form fields for the app's UI. |
| `loginCheckJs` | string | NO | JS snippet that checks if user is currently logged in. |
| `respondTime` | long | NO | Expected response time in ms (used for timeout tuning). |
| `weight` | int | NO | Sort weight — higher weight sources appear first. |
| `customOrder` | int | NO | Manual sort order override. |
| `lastUpdateTime` | long | NO | Unix timestamp in ms of last source edit. |
| `concurrentRate` | string | NO | Rate limiting: e.g. `"2,1000"` means max 2 requests per 1000ms. |
| `variableComment` | string | NO | Documentation for variables this source stores/expects. |

#### URL Pattern Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `searchUrl` | string | CONDITIONALLY | URL template for search. Required if the source supports search. |
| `exploreUrl` | string | NO | Newline-separated list of discover/browse URL entries (with optional display labels). |

#### Rule Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ruleSearch` | object | NO | Rules for parsing search result pages. |
| `ruleExplore` | object | NO | Rules for parsing explore/discover pages (same structure as ruleSearch). |
| `ruleBookInfo` | object | NO | Rules for parsing a book detail/info page. |
| `ruleToc` | object | NO | Rules for parsing the table of contents (chapter list). |
| `ruleContent` | object | NO | Rules for fetching and extracting chapter body text. |

---

## 3. URL Template Syntax

### 3.1 searchUrl

The `searchUrl` field supports a mini-template language.

```
https://example.com/search?q={{key}}&page={{page}}
```

**Available variables:**

| Variable | Description |
|----------|-------------|
| `{{key}}` | The search keyword (URL-encoded by default) |
| `{{page}}` | Current page number (starts at 1) |
| `{{key<>}}` | Search keyword NOT URL-encoded |

**POST requests:** Use `@POST` prefix or a body separator.

```
https://example.com/api/search,@POST,{"keyword":"{{key}}","page":{{page}}}
```

Or with the `<webQuery>` body syntax:

```
https://example.com/search
<webQuery>
keyword={{key}}&page={{page}}
```

**Pagination:** legado auto-increments `{{page}}` when the user requests more results.

### 3.2 exploreUrl

`exploreUrl` is a newline-separated list. Each line is one "shelf" or category:

```
书单::https://example.com/list/1
排行榜::https://example.com/rank
更新::https://example.com/update/{{page}}
```

Format per line: `[display_label::]url`. The `::` separator is optional; if absent, the URL is the label too. The URL may contain `{{page}}`.

### 3.3 URL Template Variables (General Rules)

Throughout all rule fields, URLs can reference the source variable store:

- `{{variable_name}}` — substitutes a stored variable
- `@js:` prefix — the entire string is a JS expression that returns the URL
- `<js>...</js>` tag — inline JS block inside the URL string

---

## 4. Rule Objects

Each of `ruleSearch`, `ruleExplore`, `ruleBookInfo`, `ruleToc`, `ruleContent` is an object with specific fields. All rule fields within these objects are **rule strings** — they follow a common rule syntax described in Section 5.

### 4.1 ruleSearch / ruleExplore

These two share the same structure. They describe how to parse a list of book cards from a search results page or an explore page.

```json
{
  "bookList":    "css:ul.result-list > li",
  "name":        "css:h3.title",
  "author":      "css:span.author",
  "kind":        "css:span.category",
  "intro":       "css:p.desc",
  "coverUrl":    "css:img@src",
  "wordCount":   "css:span.words",
  "lastChapter": "css:span.last-chapter",
  "bookUrl":     "css:a@href"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `bookList` | YES | Rule to select the list of book items from the page. This is a **list rule** — it returns a collection of nodes, one per book. All other fields are evaluated in the context of each node. |
| `name` | YES | Book title. |
| `author` | NO | Author name. |
| `kind` | NO | Genre/category tags. Comma-separated if multiple. |
| `intro` | NO | Book synopsis/description. |
| `coverUrl` | NO | Cover image URL. |
| `wordCount` | NO | Total word count string. |
| `lastChapter` | NO | Name of the most recently updated chapter. |
| `bookUrl` | YES | URL of the book's detail/info page. This is what legado follows to fetch the full book info and then the TOC. |

### 4.2 ruleBookInfo

Describes how to extract metadata from a book's detail page.

```json
{
  "init":        "",
  "name":        "css:h1.book-title",
  "author":      "css:span.author-name",
  "coverUrl":    "css:div.cover img@src",
  "intro":       "css:div.intro",
  "kind":        "css:span.tag",
  "wordCount":   "",
  "lastChapter": "css:div.last-chapter a",
  "updateTime":  "css:span.update-time",
  "tocUrl":      "css:a.chapter-list@href",
  "canReName":   false
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `init` | NO | A URL or JS expression that pre-fetches additional data (e.g. an API call) before the info rules run. Result is stored and accessible. |
| `name` | NO | Book title (may already be known from search; overrides if present). |
| `author` | NO | Author. |
| `coverUrl` | NO | Cover image absolute URL. |
| `intro` | NO | Synopsis. May be multi-line. |
| `kind` | NO | Genre/category. |
| `wordCount` | NO | Word count. |
| `lastChapter` | NO | Latest chapter name. |
| `updateTime` | NO | Last update timestamp string. |
| `tocUrl` | NO | URL of the chapter list page, if different from `bookUrl`. If empty, legado uses `bookUrl` for TOC too. |
| `canReName` | bool | Whether users can rename the book. |

### 4.3 ruleToc

Describes how to parse the table of contents (chapter list).

```json
{
  "chapterList":  "css:ul.chapter-list > li",
  "chapterName":  "css:a",
  "chapterUrl":   "css:a@href",
  "isVip":        "",
  "isPay":        "",
  "updateTime":   "",
  "nextTocUrl":   ""
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `chapterList` | YES | List rule — selects all chapter items. |
| `chapterName` | YES | Chapter title from each list item. |
| `chapterUrl` | YES | URL of the chapter content page from each list item. |
| `isVip` | NO | Rule that returns truthy if the chapter is behind a paywall. |
| `isPay` | NO | Rule that returns truthy if the user has paid for this chapter. |
| `updateTime` | NO | Chapter publish/update time. |
| `nextTocUrl` | NO | Rule to find a "next page" URL for multi-page chapter lists. legado follows this recursively until empty/null. |

### 4.4 ruleContent

Describes how to extract chapter text from a chapter page.

```json
{
  "content":       "css:div#chapter-content",
  "nextContentUrl": "",
  "webJs":         "",
  "sourceRegex":   "",
  "replaceRegex":  "",
  "imageStyle":    "",
  "payAction":     ""
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `content` | YES | Rule to extract the chapter body text (or HTML). |
| `nextContentUrl` | NO | Rule to find the URL of the next page, if chapter spans multiple pages. legado recursively fetches and appends. |
| `webJs` | NO | JavaScript to inject/run in a WebView before extracting content. Used when normal HTTP fetch can't get the content (JS-rendered sites). |
| `sourceRegex` | NO | Regex pattern to narrow which part of the raw page is processed. Applied before content rule. |
| `replaceRegex` | NO | Regex substitution applied to the extracted text. Format: `pattern##replacement` or just `pattern` (replaces with empty). Newline-separated for multiple. |
| `imageStyle` | NO | Styles for embedded images (mainly for manga sources). |
| `payAction` | NO | JS snippet for initiating a payment flow. |

---

## 5. Rule Syntax — The Core Language

Every rule string in legado (whether `bookList`, `content`, `chapterUrl`, etc.) follows a common syntax. The `AnalyzeRule` class in legado interprets these.

### 5.1 Rule Type Prefixes

A rule string starts with an optional prefix declaring which engine to use:

| Prefix | Engine | Example |
|--------|--------|---------|
| `css:` | CSS selector (JSoup) | `css:div.title` |
| `xpath:` or `//` | XPath | `xpath://div[@class="title"]` or `//div[@class="title"]` |
| `json:` or `$.` | JSONPath | `json:$.data.list` or `$.data.list` |
| `@css:` | CSS selector on already-selected node | `@css:a` |
| `@xpath:` | XPath on already-selected node | — |
| `@json:` | JSONPath on already-selected node | — |
| (none) | Default: JSoup/CSS auto-detect, or plain text | `div.title` |
| `@js:` | JavaScript expression (single expression) | `@js:result.replace(/\s/g,'')` |
| `<js>...</js>` | JavaScript block | See section 7 |
| `:` prefix | Shorthand for regex | (rare) |

**Auto-detection when no prefix:** If the source URL returns JSON, the default rule type is JSONPath. If it returns HTML, the default is CSS/JSoup.

### 5.2 Attribute Extraction

After a CSS/XPath selector selects an element, you append `@attr` to extract an attribute:

```
css:a.chapter-link@href      → extracts href attribute
css:img.cover@src            → extracts src attribute
css:meta[property="og:url"]@content   → extracts content attribute
```

**Special attribute names:**

| Syntax | Meaning |
|--------|---------|
| `@href` | The `href` attribute |
| `@src` | The `src` attribute |
| `@text` | The visible text content (default if no @attr) |
| `@html` | The full inner HTML |
| `@textNodes` | Only direct text nodes (not text from children) |
| `@all` | All text, including hidden elements |
| `@value` | The `value` attribute |
| `@data-xxx` | Any `data-` attribute |

### 5.3 Chaining Rules

Rules can be chained with `@` between steps (not the same `@` as attribute extraction — context determines which):

```
css:div.book-info@css:span.author@text
```

This selects `div.book-info`, then within it selects `span.author`, then extracts text. In practice, the `@` chain is used for nested selections.

For JSONPath: chaining uses `.` natively. `$.result[0].name` is a full JSONPath expression.

### 5.4 Regex Post-Processing

After a selector extracts a value, you can apply regex via `##`:

```
css:span.chapter-num##第(\d+)章
```

If the regex has a capture group, the first capture group becomes the result. If no capture group, the full match is returned.

Multiple transforms: separate with `\n` (actual newline in the JSON string, written as `\\n` in JSON):

```
css:div.content##<[^>]+>\n##\\s{2,}## 
```

This strips HTML tags, then collapses multiple whitespace.

### 5.5 List Rules vs Value Rules

**List rules** (used in `bookList`, `chapterList`): Return multiple nodes. The result is a collection. In CSS/XPath this is natural (a selector may match N elements). In JSONPath, use array paths (`$.data[*]`).

**Value rules** (used in `name`, `content`, etc.): Applied to each item in the list, return a single string.

### 5.6 URL Completion

When a rule extracts a URL (e.g. `bookUrl`, `chapterUrl`, `coverUrl`), legado automatically completes relative URLs using the base URL of the source or the current page. Rules do not need to manually add the domain.

---

## 6. JSONPath Support

When the source returns JSON (API-based sources), rules use JSONPath.

### 6.1 Basic JSONPath

```
$.data.books[*].title       → all book titles in an array
$.data.books                → the books array itself (for bookList)
$.code                      → top-level field
$[0].name                   → first element name
```

### 6.2 Filters

```
$.data[?(@.type=="novel")]  → filter by field value
```

### 6.3 Combined with Regex

```
$.data.content##<br>## \n
```

Extracts `content` field then replaces `<br>` with newline.

---

## 7. JavaScript Execution in Rules

Legado supports embedded JavaScript in rules. This is a critical feature for complex sources.

### 7.1 Syntax Forms

**Form 1: `@js:` prefix (expression)**

The rule is a JavaScript expression. The result of the expression becomes the rule output.

```
@js:result.trim().replace(/\s{2,}/g, '\n')
```

**Form 2: `<js>...</js>` block**

Used when you need multi-statement JavaScript. The last evaluated expression (or explicit `return`) is the output.

```
<js>
var arr = result.split('\n');
arr.filter(function(x){ return x.trim() !== ''; }).join('\n');
</js>
```

**Form 3: Mixed — selector then JS**

```
css:div#content<js>result.replace(/<[^>]+>/g, '')</js>
```

The CSS selector runs first, puts result in `result`, then JS transforms it.

### 7.2 JavaScript Context Variables

Inside any JS snippet, these variables are pre-injected:

| Variable | Type | Description |
|----------|------|-------------|
| `result` | string/object | Output of the preceding selector step (or the full page content if no selector) |
| `baseUrl` | string | The URL of the current page being processed |
| `book` | object | The current Book object with fields: `name`, `author`, `bookUrl`, `tocUrl`, `coverUrl`, `intro`, `kind`, `wordCount`, `lastChapter`, `updateTime`, `variable` |
| `source` | object | The current BookSource object (read-only access to source metadata) |
| `chapter` | object | (In content rules) The current BookChapter with `url`, `title`, `index`, `variable` |
| `cookie` | object | Cookie helper — `cookie.getCookie(url)`, `cookie.setCookie(url, value)` |
| `cache` | object | Key-value cache — `cache.get(key)`, `cache.put(key, value, ms)` |
| `java` | object | Bridge to Java/Android utilities |

### 7.3 JsExtensions — The `java` Object API

The `java` object provides utilities from the Android app. For a Node.js reimplementation, these must be re-implemented:

| Method | Signature | Description |
|--------|-----------|-------------|
| `java.ajax(url)` | `(url: string) → string` | Synchronous HTTP GET, returns body |
| `java.ajax(url, header)` | `(url: string, header: string) → string` | GET with extra headers (JSON string) |
| `java.ajaxAll(urls)` | `(urls: string[]) → string[]` | Fetch multiple URLs in parallel |
| `java.post(url, body, header)` | → string | HTTP POST |
| `java.base64Decode(str)` | → string | Base64 decode |
| `java.base64Encode(str)` | → string | Base64 encode |
| `java.base64DecodeToByteArray(str)` | → byte[] | Base64 to bytes |
| `java.md5Encode(str)` | → string | MD5 hash (lowercase hex) |
| `java.md5Encode16(str)` | → string | 16-char MD5 |
| `java.hexDecodeStr(str)` | → string | Hex decode to string |
| `java.hexEncode(str)` | → string | Hex encode |
| `java.timeFormat(ms)` | → string | Format Unix ms as date string |
| `java.timeFormat(ms, pattern)` | → string | Format with pattern like `yyyy-MM-dd` |
| `java.getVariable(key)` | → string | Get from source variable store |
| `java.putVariable(key, val)` | — | Put to source variable store |
| `java.getBookVariable(key)` | → string | Get from per-book variable store |
| `java.putBookVariable(key, val)` | — | Put to per-book variable store |
| `java.getChapterVariable(key)` | → string | Get from per-chapter variable store |
| `java.putChapterVariable(key, val)` | — | Put to per-chapter variable store |
| `java.getCookie(domain)` | → string | Get stored cookie for domain |
| `java.setCookie(domain, cookie)` | — | Store cookie for domain |
| `java.aesDecodeArgsBase64Str(data, mode, key, iv)` | → string | AES decrypt |
| `java.aesEncodeToBase64Str(data, mode, key, iv)` | → string | AES encrypt |
| `java.encodeURI(str)` | → string | URI encode |
| `java.encodeURIComponent(str)` | → string | URI component encode |
| `java.getString(str)` | → string | Coerce to string |
| `java.formatHtml(html)` | → string | Normalize HTML |

**Note for this project:** The `java.ajax()` calls inside JS rules create an async challenge. In the legado Android app these are blocking. In Node.js, the JS interpreter must handle these as async operations. This is a significant implementation complexity.

### 7.4 crypto-js Availability

Legado bundles `crypto-js` inside the Rhino JS engine. Sources may use:

```javascript
var CryptoJS = require('crypto-js');
var encrypted = CryptoJS.AES.decrypt(result, key);
```

For the Node.js reimplementation, `crypto-js` npm package covers this.

### 7.5 Common JS Patterns

**Pattern: Fetch an API in JS and return structured result**

```javascript
// In searchUrl
@js:
var page = {{page}};
var url = 'https://api.example.com/search?q={{key}}&p=' + page;
url
```

**Pattern: Parse JSON response in content rule**

```javascript
// content rule
@js:
var obj = JSON.parse(result);
obj.data.content.replace(/<[^>]+>/g, '')
```

**Pattern: Compute a signed URL (anti-scraping)**

```javascript
@js:
var ts = Date.now();
var sign = java.md5Encode('secret' + ts + '{{key}}');
'https://api.example.com/search?q={{key}}&ts=' + ts + '&sign=' + sign
```

---

## 8. Search Flow — End to End

### 8.1 Input → Output

**Input:** search keyword string (e.g. `"斗破苍穹"`)

**Steps:**

1. **Build URL:** Substitute `{{key}}` (URL-encoded) and `{{page}}` (= 1) into `searchUrl`. If `searchUrl` starts with `@js:`, evaluate the JS to get the URL.

2. **HTTP request:** GET (or POST if specified) the URL. Send `header` values. Manage cookies if `enabledCookieJar` is true.

3. **Select book list:** Apply `ruleSearch.bookList` to the response body. This yields N nodes (HTML elements or JSON sub-objects).

4. **Extract fields:** For each node, apply all `ruleSearch` sub-rules (`name`, `author`, `bookUrl`, etc.) to extract strings.

5. **Return:** A list of `SearchBook` objects with the extracted fields.

**Output:** `SearchBook[]` — each with `name`, `author`, `bookUrl`, `coverUrl`, `kind`, `intro`, `lastChapter`, `wordCount`.

### 8.2 Pagination

- Caller increments `{{page}}` and repeats from step 1.
- No pagination state is managed server-side; legado is stateless per-request.

---

## 9. Book Info Flow

After a search result is tapped (or a `bookUrl` followed):

1. **HTTP GET** `bookUrl` (with source headers).
2. If `ruleBookInfo.init` is set, evaluate it — it may fetch additional data.
3. Apply `ruleBookInfo` sub-rules to extract `name`, `author`, `coverUrl`, `intro`, `kind`, `updateTime`, `lastChapter`.
4. Determine `tocUrl`: if `ruleBookInfo.tocUrl` rule yields a value, use that; otherwise use `bookUrl` as the TOC URL.
5. Return enriched `Book` object.

---

## 10. Chapter List (TOC) Flow

**Input:** `tocUrl` (from book info step, or `bookUrl`)

**Steps:**

1. **HTTP GET** `tocUrl`.
2. Apply `ruleToc.chapterList` to select all chapter nodes.
3. For each node: apply `chapterName` and `chapterUrl` rules.
4. Check `ruleToc.nextTocUrl` — if it yields a non-empty URL, fetch that page and append more chapters. Repeat until `nextTocUrl` is empty.
5. Return `BookChapter[]` — ordered list with `title` and `url`.

**Multi-page TOC:** Many Chinese novel sites paginate their chapter lists (e.g. 1000 chapters split across 5 pages). The `nextTocUrl` rule handles this by pointing to the next page URL.

---

## 11. Chapter Content Flow

**Input:** `chapterUrl` (one chapter URL from the TOC)

**Steps:**

1. **HTTP GET** `chapterUrl` (with headers, cookies).
2. If `ruleContent.sourceRegex` is set, trim the response to only the matched region.
3. Apply `ruleContent.content` rule to extract the raw content string.
4. If `ruleContent.nextContentUrl` is non-empty, fetch that URL, extract content, append. Repeat.
5. Apply `ruleContent.replaceRegex` transformations to clean up the text.
6. Return final content string.

**Multi-page chapters:** Some sites split one chapter into multiple pages. `nextContentUrl` handles this.

---

## 12. Variable Storage

Legado provides a three-tier variable store accessible in JS:

| Scope | JS access | Persists |
|-------|-----------|----------|
| Source-level | `java.getVariable(key)` / `java.putVariable(key, val)` | Until source is modified |
| Book-level | `java.getBookVariable(key)` / `java.putBookVariable(key, val)` | Per book, across sessions |
| Chapter-level | `java.getChapterVariable(key)` / `java.putChapterVariable(key, val)` | Per chapter fetch |

Also accessible via `book.variable` (JSON string on the book object) and `chapter.variable`.

---

## 13. HTTP / Request Details

### 13.1 Header Format

`header` field is a JSON string:

```json
"{\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\", \"Referer\": \"https://example.com/\"}"
```

Individual request URLs can also carry headers using the format:

```
https://example.com/api,{"User-Agent":"custom"}
```

Or more explicitly with the legado URL syntax:

```
url,{headers},{body}
```

### 13.2 POST Requests

POST is triggered by appending `,@POST,<body>` to the URL string, or by using `<webQuery>` blocks.

```
https://example.com/api/search,@POST,{"keyword":"{{key}}","page":{{page}}}
```

The body can be:
- JSON string (`{...}`)
- Form data (`key=value&key2=value2`)

Content-Type is inferred from the body format or set via the `header` field.

### 13.3 Encoding

URL-encoded variables use `{{key}}` (encoded). Raw/unencoded uses `{{key<>}}` or `{{key,urlencode}}`.

Character encoding of response pages: legado auto-detects charset from HTTP headers and HTML meta tags. GBK/GB2312 is common for older Chinese novel sites.

---

## 14. Content Type Handling

### 14.1 HTML Sources

Most sources. Response is parsed with JSoup. CSS selectors and XPath are available. Line breaks in content are typically `<br>` or `<p>` tags.

**Typical content cleaning needed:**
- Strip ads: `replaceRegex` with patterns like `本章[^章]*广告[^。]*。##`
- Normalize whitespace: `\s{2,}## ` or `&nbsp;## `
- Remove HTML tags remaining after extraction: `<[^>]+>## `

### 14.2 JSON API Sources

Response body is raw JSON. Rules use JSONPath. No HTML parsing needed. Content is often pre-cleaned.

### 14.3 Mixed Sources

Some sources serve HTML pages that embed JSON in `<script>` tags. Extract the JSON with a JS rule, then parse:

```javascript
@js:
var m = result.match(/window\.__DATA__\s*=\s*({.*?});/s);
var data = JSON.parse(m[1]);
data.content
```

---

## 15. replaceRegex Syntax

`replaceRegex` is newline-separated list of replacement rules. Each line: `pattern##replacement`.

```
<[^>]+>##
&nbsp;## 
\n{3,}##\n\n
^\s+##
```

- Pattern is a Java regex (not JS regex). Java regex flavor: `\d`, `\s`, `(?i)` for case-insensitive, etc.
- If `##replacement` is omitted, replacement is empty string (deletion).
- Capture groups in replacement: `$1`, `$2`.
- The pattern is applied to the full content string (not line by line) unless anchored.

---

## 16. Complete Working Example — Simple HTML Source

This example is representative of a typical free Chinese novel aggregator.

```json
{
  "bookSourceUrl": "https://www.biquge.biz",
  "bookSourceName": "笔趣阁BIZ",
  "bookSourceGroup": "小说",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "header": "{\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0\"}",
  "searchUrl": "https://www.biquge.biz/search.php?keyword={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "css:div.bookbox",
    "name": "css:div.bookinfo h4 a",
    "author": "css:div.bookinfo p:nth-child(2)",
    "kind": "css:div.bookinfo p:nth-child(3)",
    "intro": "css:div.bookinfo p.intro",
    "coverUrl": "css:img.bookImg@src",
    "lastChapter": "css:div.bookinfo p.update a",
    "bookUrl": "css:div.bookinfo h4 a@href"
  },
  "ruleBookInfo": {
    "name": "css:h1#bookTitle",
    "author": "css:a#bookAuthor",
    "coverUrl": "css:div#bookSummary img@src",
    "intro": "css:p#bookSummaryText",
    "kind": "css:span.red a",
    "lastChapter": "css:a#bookLastChapter",
    "tocUrl": "css:a#bookLastChapter@href"
  },
  "ruleToc": {
    "chapterList": "css:ul#chapterList > li",
    "chapterName": "css:a",
    "chapterUrl": "css:a@href",
    "nextTocUrl": ""
  },
  "ruleContent": {
    "content": "css:div#chapterContent",
    "nextContentUrl": "",
    "replaceRegex": "<[^>]+>##\n&nbsp;## \n天才一秒记住本站地址.*?\\n##\n看小说app.*?\\n##"
  }
}
```

---

## 17. Complete Working Example — JSON API Source

```json
{
  "bookSourceUrl": "https://api.novel-example.com",
  "bookSourceName": "API示例源",
  "bookSourceGroup": "小说,API",
  "bookSourceType": 0,
  "enabled": true,
  "header": "{\"User-Agent\":\"okhttp/4.9.0\", \"Content-Type\":\"application/json\"}",
  "searchUrl": "https://api.novel-example.com/search?kw={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "$.data.list",
    "name": "$.title",
    "author": "$.author",
    "kind": "$.category",
    "intro": "$.intro",
    "coverUrl": "$.cover",
    "lastChapter": "$.lastChapter",
    "bookUrl": "$.bookId##^##https://api.novel-example.com/book/"
  },
  "ruleBookInfo": {
    "name": "$.data.title",
    "author": "$.data.author",
    "coverUrl": "$.data.cover",
    "intro": "$.data.description",
    "kind": "$.data.tags",
    "lastChapter": "$.data.lastChapter.name",
    "tocUrl": "@js:'https://api.novel-example.com/toc?bookId=' + book.bookUrl.split('/').pop() + '&page=1'"
  },
  "ruleToc": {
    "chapterList": "$.data.chapters",
    "chapterName": "$.title",
    "chapterUrl": "@js:'https://api.novel-example.com/chapter?id=' + result.id",
    "nextTocUrl": "@js:$.data.hasNext ? 'https://api.novel-example.com/toc?bookId={{bookId}}&page=' + ($.data.page + 1) : ''"
  },
  "ruleContent": {
    "content": "$.data.content",
    "replaceRegex": "<br\\s*/?>##\n"
  }
}
```

---

## 18. Common Pitfalls in Rule Writing

### Relative vs Absolute URLs

Rule extracts `/book/123` but needs `https://example.com/book/123`. Legado handles this automatically by completing relative URLs against the current page's base URL. The reimplementation must do the same.

### GBK Encoding

Many Chinese novel sites serve GBK/GB2312 encoded pages. The HTTP client must detect and transcode to UTF-8 before rule processing. Legado uses OkHttp which handles this. In Node.js, use `iconv-lite` with charset detection from HTTP headers (`Content-Type: text/html; charset=gbk`) or HTML `<meta charset="gbk">`.

### Dynamic/JS-Rendered Content

Sites that render content via JavaScript are unsupported by simple HTTP fetch. The `webJs` field in `ruleContent` is intended for this but requires a headless browser (legado uses Android WebView). For the CLI reimplementation, skip sources requiring `webJs` or add a `puppeteer` fallback.

### Anti-Scraping

Many sources require:
- A realistic `User-Agent`
- `Referer` header matching the site
- Cookie session management
- Rate limiting (`concurrentRate` field)

Sources often break when the site changes its HTML structure. This is normal — community sources are constantly updated.

---

## 19. Source Type Values

| Value | Meaning | Notes |
|-------|---------|-------|
| `0` | Novel/text | Standard novel source |
| `1` | Audio book | Not needed for this project |
| `2` | Image/manga | CSS rules still apply, but content is image URLs |
| `3` | File | Direct file download |

For this project (text novels), only `bookSourceType: 0` sources are needed.

---

## 20. exploreUrl Format Details

```
书单::https://example.com/list?type=1
排行榜::https://example.com/rank/{{page}}
完结小说::https://example.com/finish/{{page}}
```

Each newline is a separate "shelf". Format: `[name::]url`. When displayed in the app, the `name` part appears as a category label in the Discover tab.

For the CLI project, `exploreUrl` provides "browse by category" functionality — useful for discovery without a specific search term.

---

## 21. Summary of Required vs Optional Fields for Minimal Viable Source

To implement a source that supports search, TOC, and content reading (the three critical flows):

### Minimum required:

```json
{
  "bookSourceUrl": "...",      ← Required: unique ID
  "bookSourceName": "...",     ← Required: display
  "bookSourceType": 0,         ← Required: 0 for novels
  "searchUrl": "...",          ← Required for search
  "ruleSearch": {
    "bookList": "...",         ← Required
    "name": "...",             ← Required
    "bookUrl": "..."           ← Required
  },
  "ruleToc": {
    "chapterList": "...",      ← Required
    "chapterName": "...",      ← Required
    "chapterUrl": "..."        ← Required
  },
  "ruleContent": {
    "content": "..."           ← Required
  }
}
```

Everything else is enhancement. `ruleBookInfo` is optional but improves metadata quality. `ruleExplore` is optional (browse feature). `exploreUrl` is optional (browse feature).

---

## 22. Implementation Notes for This Project (Node.js/TypeScript)

### What Must Be Reimplemented

1. **URL template substitution** — `{{key}}`, `{{page}}`, variable references
2. **HTTP client** — with header support, cookie jar (per-source), GBK transcoding, rate limiting
3. **CSS selector engine** — use `cheerio` (Node.js JSoup equivalent)
4. **XPath engine** — use `xpath` + `xmldom` packages, or `cheerio-xpath`
5. **JSONPath engine** — use `jsonpath-plus` or `jsonpath`
6. **JavaScript engine** — use Node.js `vm` module (or `vm2` for isolation) with pre-injected context variables
7. **`java` object** — stub/implement all `java.*` methods used by sources
8. **URL completion** — resolve relative URLs against base URL (Node.js `new URL(rel, base)`)
9. **replaceRegex** — apply Java-compatible regex (Node.js regex is close but not identical)
10. **Rule chain parser** — parse `css:selector@attr##regex` syntax
11. **Multi-page TOC** — follow `nextTocUrl` recursively
12. **Multi-page content** — follow `nextContentUrl` recursively

### What Can Be Skipped (Out of Scope)

- `webJs` / WebView rendering (legado-specific, requires browser)
- `loginUrl` / `loginUi` (auth support)
- `bookSourceType` 1, 2, 3 (audio, manga, file)
- `enabledCookieJar` advanced session management (basic cookie support is enough)
- `payAction` (paid content)
- `concurrentRate` (can implement as simple delay if needed)

### Recommended npm Packages

| Need | Package | Notes |
|------|---------|-------|
| HTML parsing / CSS selectors | `cheerio` | Drop-in JSoup equivalent |
| XPath | `xpath` + `xmldom` | Or `cheerio-xpath` |
| JSONPath | `jsonpath-plus` | More complete than `jsonpath` |
| HTTP client | `axios` or `got` | Both support custom headers |
| GBK encoding | `iconv-lite` | + `charset` for detection |
| JS sandbox | `vm2` or Node `vm` | For running `@js:` snippets |
| Crypto (for sources) | `crypto-js` | Many sources use CryptoJS |
| URL resolution | built-in `URL` | `new URL(relative, base)` |

---

## 23. Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| Top-level JSON fields | HIGH | From BookSource.kt entity class — all @ColumnInfo fields |
| Rule object structures | HIGH | From RuleBook.kt data class fields |
| Rule syntax (CSS/XPath/JSON/regex) | HIGH | From AnalyzeRule.kt parsing logic |
| `java.*` method list | MEDIUM | From JsExtensions.kt — may be incomplete for edge methods |
| URL template syntax | HIGH | Documented in multiple community wikis |
| replaceRegex behavior | MEDIUM | Java regex vs JS regex subtleties not fully verified |
| JS context variables | MEDIUM | Context injection documented in source but some edge cases unclear |
| exploreUrl format | MEDIUM | Less documented; inferred from source code |
| Actual scraping behavior for live sites | LOW | Sites change; examples may be stale |

---

## 24. References

- Legado GitHub: https://github.com/gedoor/legado
- BookSource.kt: `app/src/main/java/io/legado/app/data/entities/BookSource.kt`
- RuleBook.kt: `app/src/main/java/io/legado/app/data/entities/rule/RuleBook.kt`
- AnalyzeRule.kt: `app/src/main/java/io/legado/app/help/book/rule/AnalyzeRule.kt`
- JsExtensions.kt: `app/src/main/java/io/legado/app/help/book/rule/JsExtensions.kt`
- AnalyzeUrl.kt: `app/src/main/java/io/legado/app/model/analyzeRule/AnalyzeUrl.kt`
- Community book source repository: https://github.com/gedoor/MyBookshelf
- Legado rule documentation wiki: https://github.com/gedoor/legado/wiki

**Note:** All technical details in this document are based on training knowledge of the legado codebase as of mid-2025. The legado project is actively maintained and rule syntax may have minor additions in later versions. Verify against the actual source code before implementing edge cases.
