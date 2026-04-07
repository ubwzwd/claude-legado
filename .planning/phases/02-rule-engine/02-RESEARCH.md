# Phase 2: Rule Engine - Research

**Researched:** 2026-04-07
**Domain:** legado rule parsing — CSS/XPath/JSONPath/regex/JS evaluation in Python
**Confidence:** HIGH (all library APIs verified by running code against installed packages)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Use `quickjs` PyPI package (`pip install quickjs`). API: `quickjs.Context()`, `ctx.eval()`.
- **D-02:** `java.ajax()` stubbed in Phase 2 with `NotImplementedError("java.ajax not available until Phase 3")`.
- **D-03:** Public API is `evaluate(rule: str, content: str | dict, base_url: str = '') -> str` in `src/novel/rules/__init__.py`. Auto-detects rule type from prefix.
- **D-04:** Sub-package `src/novel/rules/` with internal modules: `_css.py`, `_xpath.py`, `_jsonpath.py`, `_regex.py`, `_js.py`, `_detect.py`.
- **D-05:** Phase 3/4 callers use `from novel.rules import evaluate`. No class instantiation at call site.
- **D-06:** Synthetic minimal fixtures in `tests/fixtures/`. No real book source files.
- **D-07:** Small focused fixture files: `html_title.html`, `toc_list.html`, `book_info.json`, etc.
- **D-08:** Book source JSON parser tests use hand-crafted synthetic source object.
- **D-09:** Failed rule evaluation raises `RuleError(rule: str, cause: Exception)` from `src/novel/rules/_errors.py`.
- **D-10:** Phase 3/4 callers catch `RuleError` explicitly.

### Claude's Discretion

- Internal sub-module split within `src/novel/rules/` (how many files, exact naming)
- replaceRegex chain parsing implementation (regex split on `##`)
- URL template substitution (`{{key}}` via `re.sub`)
- Exact `quickjs.Context` setup pattern (one context per evaluate call vs singleton)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SRC-01 | Parse legado book source JSON (single object or array) | §Standard Stack, §Architecture Patterns (BookSource dataclass), §Code Examples (JSON loading) |
| SRC-02 | Validate required fields (`bookSourceUrl`, `bookSourceName`, rule objects) | §Architecture Patterns (Validation logic), §Code Examples (required field check) |
| SRC-03 | CSS selector rules (`css:selector@attribute`) | §Legado Rule Syntax, §lxml+cssselect API, §Code Examples |
| SRC-04 | XPath rules (`xpath://path/text()`) | §Legado Rule Syntax, §lxml XPath API, §Code Examples |
| SRC-05 | JSONPath rules (`$.path.to.field`) | §Legado Rule Syntax, §jsonpath-ng API, §Code Examples |
| SRC-06 | `replaceRegex` post-processing (`##pattern##replacement`) | §Legado Rule Syntax (replaceRegex), §Code Examples |
| SRC-07 | `@js:` inline JS expressions via quickjs | §Legado Rule Syntax (JS), §quickjs API, §Code Examples |
| SRC-08 | `<js>...</js>` block JS via quickjs | §Legado Rule Syntax (JS), §quickjs API, §Code Examples |
| SRC-09 | JS context provides `result`, `baseUrl`, `java.base64Decode()`, `java.md5()` | §quickjs API (java bridge), §Code Examples |
| SRC-10 | URL template substitution (`{{key}}`, `{{page}}`) | §Legado Rule Syntax (URL template), §Code Examples |

</phase_requirements>

---

## Summary

Phase 2 builds a pure rule evaluation engine for legado book source rules — no HTTP, no UI. All four selector types (CSS, XPath, JSONPath, JS) evaluate against in-memory HTML strings or Python dicts. The replaceRegex post-processor and URL template substitution complete the surface area.

All library APIs were verified by running code in the project's Python 3.12 environment (packages installed fresh). `quickjs 1.19.4`, `lxml 6.0.2`, `cssselect 1.4.0`, `jsonpath-ng 1.8.0` are current as of the research date. `ctx.set()` and `ctx.add_callable()` are the correct injection methods for quickjs — `globalThis` attribute assignment raises `AttributeError` on `_quickjs.Object`.

**Primary recommendation:** One `quickjs.Context()` per `evaluate()` call. 1000 context creations take ~118ms total, so per-call overhead is negligible. Eliminates all state leakage risk between rule evaluations. For the `<js>` block pattern, inject `result` via `ctx.set()`, run the block, then read back via `ctx.get('result')` rather than relying on the eval return value.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| lxml | 6.0.2 | HTML/XML parsing and XPath evaluation | De-facto standard for lxml-based scraping; fastest Python HTML parser |
| cssselect | 1.4.0 | CSS selector translation to XPath (used by lxml) | Required companion to `lxml.cssselect()` |
| jsonpath-ng | 1.8.0 | JSONPath expression evaluation | Most maintained JSONPath library; has `jsonpath_ng.ext` for filter expressions |
| quickjs | 1.19.4 | Embedded JS runtime via QuickJS binding | Lightweight CPython binding, no Node.js dependency, agreed in D-01 |

[VERIFIED: npm registry / pip install output — installed versions confirmed 2026-04-07]

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| re (stdlib) | — | replaceRegex chain application | All regex post-processing — no external dep needed |
| hashlib (stdlib) | — | MD5 for `java.md5()` implementation | Built-in — no external dep |
| base64 (stdlib) | — | base64 for `java.base64Decode()` | Built-in — no external dep |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| lxml.html.fromstring | BeautifulSoup | lxml is faster; cssselect integrates natively; BS4 adds a dependency |
| jsonpath-ng | jsonpath2 | jsonpath-ng is more maintained; has ext module for filter support |
| quickjs | js2py | quickjs is ~10x faster; js2py has poor ES6 support |
| re.sub per step | re.compile + sub | compile helps for repeated patterns; not worth caching in this phase |

**Installation:**
```bash
pip install lxml cssselect jsonpath-ng quickjs
```

**Version verification:** [VERIFIED: pip install output 2026-04-07]
- quickjs 1.19.4
- lxml 6.0.2
- cssselect 1.4.0
- jsonpath-ng 1.8.0

---

## Legado Rule Syntax

[ASSUMED — synthesized from training knowledge of legado format + community sources. Pattern shapes confirmed consistent with the test fixtures used in verification.]

### CSS Rules (SRC-03)

Format: `css:SELECTOR@ATTRIBUTE`

| Syntax | Meaning |
|--------|---------|
| `css:.title@text` | CSS selector `.title`, extract full text content (including child element text) |
| `css:a.chapter@href` | CSS selector `a.chapter`, extract `href` attribute |
| `css:img.cover@src` | CSS selector `img.cover`, extract `src` attribute |
| `css:div.content` | CSS selector, no `@` suffix — returns inner HTML as string |
| `css:#list dd a@href` | Descendant combinator — first match's `href` |

`@text` maps to `element.text_content()` (includes all descendant text).
Any other `@attribute` maps to `element.get(attribute, '')`.
No `@` suffix returns the serialized outer HTML of the first matched element.
No match returns `''` (empty string).

### XPath Rules (SRC-04)

Format: `xpath:XPATH_EXPRESSION`

The prefix `xpath:` is stripped; the remainder is passed directly to `tree.xpath()`.

| Syntax | Meaning |
|--------|---------|
| `xpath://h1/text()` | All text nodes of `h1` elements |
| `xpath://a[@class='chapter']/@href` | `href` attributes of matching anchors |
| `xpath://div[@id='content']/p/text()` | Text in all `p` inside `#content` |

`tree.xpath()` always returns a list. Convention: join with `''` (for text) or take `[0]` for a single URL. Empty list returns `''`.

### JSONPath Rules (SRC-05)

Format: `$.path.to.field` (no prefix required — detected by `$.` or `$[` start)

| Syntax | Meaning |
|--------|---------|
| `$.book.title` | Scalar field |
| `$.books[*].name` | All names in a books array |
| `$.data[0].url` | First item's url |

Use `jsonpath_ng.parse(expr).find(data)`. Returns list of `DatumInContext` objects. Access value via `.value`. Empty list → no match → return `''`.

For filter expressions (`[?(@.status == "free")]`), import `jsonpath_ng.ext.parse` instead of `jsonpath_ng.parse`. [VERIFIED: tested in Python 2026-04-07]

### replaceRegex (SRC-06)

Format: `##PATTERN##REPLACEMENT` (chained: `##P1##R1##P2##R2...`)

The `replaceRegex` field in a rule object is a separate string from the selector rule. After the selector extracts content, the replaceRegex is applied as a post-processing step.

Split logic:
```
rule.split('##') -> ['', 'P1', 'R1', 'P2', 'R2']  # starts with ##
```
Skip the leading empty element. Apply `re.sub(P, R, text)` in pairs sequentially. Empty replacement = delete matched text. [VERIFIED: tested 2026-04-07]

### JS Rules (SRC-07, SRC-08)

| Format | Trigger | Context |
|--------|---------|---------|
| `@js: expression` | Starts with `@js:` | Strip prefix, eval expression, return value is the result |
| `<js>code</js>` | Starts with `<js>`, contains `</js>` | Extract code between tags, inject `result` before eval, read `result` back after eval |

For `@js:` inline: `ctx.set('result', content)` then `return_val = ctx.eval(expression)`. Use `return_val` directly.

For `<js>` block: `ctx.set('result', content)` then `ctx.eval(code_block)` then `final = ctx.get('result')`. The block modifies `result` in place.

### JS Context (SRC-09)

Variables injected before any JS eval:
- `result` — the selector output (or raw content if no preceding selector)
- `baseUrl` — base URL string for resolving relative links

`java` object with methods:
- `java.base64Decode(str)` — decodes base64 → UTF-8 string
- `java.md5(str)` — returns hex MD5 of UTF-8 encoded string
- `java.ajax(url)` — raises `NotImplementedError` in Phase 2

`java.ajax` must be wired through `ctx.add_callable('_javaAjax', ajax_stub)` then `ctx.eval('java.ajax = _javaAjax;')` after building the `java` object.

### URL Templates (SRC-10)

Format: `{{key}}` in URL strings

| Template variable | Typical usage |
|-------------------|---------------|
| `{{searchKey}}` | Search query string |
| `{{page}}` | Pagination index (integer) |
| `{{bookUrl}}` | Book detail page URL |

Implementation: `re.sub(r'\{\{(\w+)\}\}', lambda m: str(params.get(m.group(1), m.group(0))), template)`. Unknown keys are left as-is (not replaced). [VERIFIED: tested 2026-04-07]

### Book Source JSON Format (SRC-01, SRC-02)

[ASSUMED — legado community format. Structure verified consistent with code tests.]

Required fields: `bookSourceUrl` (str), `bookSourceName` (str).

Optional but expected rule objects: `ruleSearch`, `ruleBookInfo`, `ruleToc`, `ruleContent`.

Each rule object is a dict with string values that are rule expressions.

`bookSourceType: 0` = text novel (the only type this project supports in v1).

Single source: JSON object. Multiple sources: JSON array of objects.

---

## Architecture Patterns

### Recommended Project Structure

```
src/novel/
├── rules/
│   ├── __init__.py       # Public API: evaluate(), evaluate_list()
│   ├── _detect.py        # Rule type detection: detect_rule_type(rule) -> RuleType
│   ├── _errors.py        # RuleError(rule, cause) exception class
│   ├── _css.py           # eval_css(rule_body, html_str) -> str
│   ├── _xpath.py         # eval_xpath(expr, html_str) -> str
│   ├── _jsonpath.py      # eval_jsonpath(expr, data) -> str
│   ├── _regex.py         # apply_replace_regex(text, replace_regex) -> str
│   └── _js.py            # eval_js(code, result, base_url, mode) -> str
tests/
├── fixtures/
│   ├── html_title.html   # Simple HTML with book title
│   ├── toc_list.html     # HTML with chapter list and next-page link
│   ├── content.html      # HTML with chapter text content
│   ├── book_info.json    # JSON book info dict
│   ├── search_results.json  # JSON search results array
│   └── source_minimal.json  # Minimal valid book source JSON
├── test_rules_css.py
├── test_rules_xpath.py
├── test_rules_jsonpath.py
├── test_rules_regex.py
├── test_rules_js.py
├── test_rules_detect.py
├── test_rules_evaluate.py  # Integration: evaluate() dispatcher
└── test_source_parser.py   # SRC-01, SRC-02
```

### Pattern 1: Public `evaluate()` Dispatcher

```python
# src/novel/rules/__init__.py
# Source: verified design from CONTEXT.md + library testing 2026-04-07

from novel.rules._detect import detect_rule_type, RuleType
from novel.rules._css import eval_css
from novel.rules._xpath import eval_xpath
from novel.rules._jsonpath import eval_jsonpath
from novel.rules._js import eval_js
from novel.rules._errors import RuleError


def evaluate(rule: str, content: str | dict, base_url: str = '') -> str:
    """Evaluate a legado rule against content. Returns str result.

    Raises:
        RuleError: if rule evaluation fails for any reason.
    """
    rule_type, rule_body = detect_rule_type(rule)
    try:
        if rule_type == RuleType.CSS:
            return eval_css(rule_body, content)
        elif rule_type == RuleType.XPATH:
            return eval_xpath(rule_body, content)
        elif rule_type == RuleType.JSONPATH:
            return eval_jsonpath(rule, content)
        elif rule_type == RuleType.JS_INLINE:
            return eval_js(rule_body, content, base_url, mode='inline')
        elif rule_type == RuleType.JS_BLOCK:
            return eval_js(rule_body, content, base_url, mode='block')
        else:
            raise ValueError(f'Unknown rule type for: {rule!r}')
    except RuleError:
        raise
    except Exception as cause:
        raise RuleError(rule, cause) from cause
```

### Pattern 2: Rule Type Detection

```python
# src/novel/rules/_detect.py
# Source: verified behavior from rule syntax testing 2026-04-07

import enum

class RuleType(enum.Enum):
    CSS = 'css'
    XPATH = 'xpath'
    JSONPATH = 'jsonpath'
    JS_INLINE = 'js_inline'
    JS_BLOCK = 'js_block'


def detect_rule_type(rule: str) -> tuple[RuleType, str]:
    """Return (RuleType, rule_body) where rule_body has prefix stripped."""
    rule = rule.strip()
    if rule.startswith('xpath:'):
        return RuleType.XPATH, rule[len('xpath:'):]
    if rule.startswith('css:'):
        return RuleType.CSS, rule[len('css:'):]
    if rule.startswith('$.') or rule.startswith('$['):
        return RuleType.JSONPATH, rule  # jsonpath-ng wants the full $ expression
    if rule.startswith('@js:'):
        return RuleType.JS_INLINE, rule[len('@js:'):].strip()
    if rule.startswith('<js>') and '</js>' in rule:
        code = rule[len('<js>'):rule.index('</js>')]
        return RuleType.JS_BLOCK, code
    raise ValueError(f'Cannot detect rule type: {rule!r}')
```

**Detection order matters:** `xpath:` and `css:` before JSONPath (in case a JSONPath somehow starts with css-like text — unlikely but explicit ordering is safe). JS block before JS inline (both start with different tokens so order doesn't matter, but be consistent).

### Pattern 3: CSS Evaluation

```python
# src/novel/rules/_css.py
# Source: VERIFIED by running against lxml 6.0.2 + cssselect 1.4.0

import lxml.html
import lxml.etree


def eval_css(rule_body: str, html: str) -> str:
    """Evaluate a CSS rule body (after stripping 'css:' prefix).

    rule_body format: 'selector@attribute' or 'selector'
    - @text -> element.text_content()
    - @{attr} -> element.get(attr, '')
    - no @ -> outer HTML of first match
    """
    if '@' in rule_body:
        selector, attr = rule_body.rsplit('@', 1)
    else:
        selector, attr = rule_body, None

    tree = lxml.html.fromstring(html)
    elements = tree.cssselect(selector)
    if not elements:
        return ''

    el = elements[0]
    if attr == 'text':
        return el.text_content()
    elif attr is None or attr == 'html':
        return lxml.etree.tostring(el, encoding='unicode', method='html')
    else:
        return el.get(attr, '')
```

### Pattern 4: XPath Evaluation

```python
# src/novel/rules/_xpath.py
# Source: VERIFIED by running against lxml 6.0.2

import lxml.html


def eval_xpath(expr: str, html: str) -> str:
    """Evaluate XPath expression against HTML string.

    Returns first result for attribute/text() selectors.
    Joins multiple text() results with empty string.
    """
    tree = lxml.html.fromstring(html)
    results = tree.xpath(expr)
    if not results:
        return ''
    if isinstance(results[0], str):
        # text() or @attribute results — join all
        return ''.join(results)
    # Element results — take first, serialize
    import lxml.etree
    return lxml.etree.tostring(results[0], encoding='unicode', method='html')
```

### Pattern 5: JSONPath Evaluation

```python
# src/novel/rules/_jsonpath.py
# Source: VERIFIED against jsonpath-ng 1.8.0

from jsonpath_ng import parse as jpath_parse


def eval_jsonpath(expr: str, data: dict | list) -> str:
    """Evaluate JSONPath expression against a Python dict/list.

    Returns first match as string, or '' if no match.
    """
    matches = jpath_parse(expr).find(data)
    if not matches:
        return ''
    return str(matches[0].value)
```

Note: for filter expressions (`[?(@.field == value)]`), use `jsonpath_ng.ext.parse` instead. In Phase 2, start with `jsonpath_ng.parse` and add ext fallback only if needed. [VERIFIED: both APIs available in 1.8.0]

### Pattern 6: replaceRegex Application

```python
# src/novel/rules/_regex.py
# Source: VERIFIED — split/apply logic tested 2026-04-07

import re


def apply_replace_regex(text: str, replace_regex: str) -> str:
    """Apply legado replaceRegex chain to text.

    Format: ##pattern1##replacement1##pattern2##replacement2...
    Empty replacement = delete matched text.
    Returns original text if replace_regex is empty or None.
    """
    if not replace_regex:
        return text

    parts = replace_regex.split('##')
    # If rule starts with ##, first element is '' — skip it
    if parts and parts[0] == '':
        parts = parts[1:]

    i = 0
    while i + 1 < len(parts):
        pattern = parts[i]
        replacement = parts[i + 1]
        text = re.sub(pattern, replacement, text)
        i += 2

    return text
```

### Pattern 7: JS Evaluation

```python
# src/novel/rules/_js.py
# Source: VERIFIED against quickjs 1.19.4

import base64
import hashlib
import quickjs


def _make_context(result: str, base_url: str) -> quickjs.Context:
    """Build a fresh quickjs context with result, baseUrl, and java bridge."""
    ctx = quickjs.Context()

    # Inject content variables
    ctx.set('result', result)
    ctx.set('baseUrl', base_url)

    # Register Java bridge callables
    def _base64_decode(s: str) -> str:
        return base64.b64decode(s).decode('utf-8')

    def _md5(s: str) -> str:
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def _ajax_stub(url: str) -> str:
        raise NotImplementedError('java.ajax not available until Phase 3')

    ctx.add_callable('_javaBase64Decode', _base64_decode)
    ctx.add_callable('_javaMd5', _md5)
    ctx.add_callable('_javaAjax', _ajax_stub)

    # Build java object in JS
    ctx.eval('var java = { base64Decode: _javaBase64Decode, md5: _javaMd5, ajax: _javaAjax };')

    return ctx


def eval_js(code: str, result: str, base_url: str, mode: str = 'inline') -> str:
    """Evaluate JS code via quickjs.

    mode='inline': code is a single expression; return value is the result.
    mode='block': code is a multi-line block; reads result variable after eval.
    """
    ctx = _make_context(result, base_url)

    if mode == 'inline':
        ret = ctx.eval(code)
        return str(ret) if ret is not None else ''
    else:
        ctx.eval(code)
        val = ctx.get('result')
        return str(val) if val is not None else ''
```

**Key insight:** New `quickjs.Context()` per call (not a module-level singleton). 1000 context creations take ~118ms; per-chapter performance is negligible. Avoids all JS global state leakage between rule evaluations. [VERIFIED: benchmarked 2026-04-07]

### Pattern 8: RuleError Exception

```python
# src/novel/rules/_errors.py

class RuleError(Exception):
    """Raised when a legado rule fails to evaluate.

    Attributes:
        rule: the raw rule string that caused the failure
        cause: the underlying exception
    """

    def __init__(self, rule: str, cause: Exception) -> None:
        self.rule = rule
        self.cause = cause
        super().__init__(f'Rule evaluation failed: {rule!r} — {cause}')
```

### Pattern 9: URL Template Substitution

```python
# Can live in src/novel/rules/_templates.py or inline in __init__.py

import re


def apply_url_template(template: str, params: dict) -> str:
    """Replace {{key}} placeholders in a URL template.

    Unknown keys are left as-is (not replaced).
    """
    def replace(m: re.Match) -> str:
        key = m.group(1)
        return str(params[key]) if key in params else m.group(0)

    return re.sub(r'\{\{(\w+)\}\}', replace, template)
```

[VERIFIED: tested 2026-04-07]

### Pattern 10: Book Source Parser (SRC-01, SRC-02)

```python
# src/novel/rules/_source.py  (or src/novel/source.py — Claude's discretion)

import json
from pathlib import Path

REQUIRED_FIELDS = ('bookSourceUrl', 'bookSourceName')


def load_book_source(path: str | Path) -> dict:
    """Load a legado book source JSON file.

    Accepts either a single source object or an array.
    Returns a single source dict (first item if array).
    Raises ValueError for missing required fields.
    """
    text = Path(path).read_text(encoding='utf-8')
    data = json.loads(text)

    if isinstance(data, list):
        if not data:
            raise ValueError('Book source array is empty')
        source = data[0]
    elif isinstance(data, dict):
        source = data
    else:
        raise ValueError(f'Expected dict or list, got {type(data).__name__}')

    for field in REQUIRED_FIELDS:
        if field not in source:
            raise ValueError(f'Missing required field: {field!r}')

    return source
```

### Anti-Patterns to Avoid

- **Module-level quickjs.Context singleton:** Any JS rule that sets a global variable will pollute subsequent evaluations. Always create a new context per `evaluate()` call.
- **globalThis attribute assignment for injection:** `ctx.globalThis.result = 'x'` raises `AttributeError` on `_quickjs.Object`. Use `ctx.set('result', value)` instead. [VERIFIED: tested 2026-04-07]
- **Catching `quickjs.JSException` only:** Python exceptions from `add_callable` callbacks (e.g., `java.ajax` raising `NotImplementedError`) surface as `quickjs.JSException` with message `"Python call failed."`. Wrap the entire `eval_js()` in a broad try/except and convert to `RuleError`. [VERIFIED: tested 2026-04-07]
- **Using `lxml.html.fragment_fromstring` for full pages:** Use `lxml.html.fromstring()` for all HTML — it handles both fragments and full documents correctly. XPath with `//` works from the returned element in both cases.
- **Splitting replaceRegex on a fixed number of `##`:** Use `.split('##')` and skip leading empty element — handles arbitrary chain lengths.
- **Replacing `{{key}}` via str.format_map:** URLs often contain `{0}`, `{1}`, or lone `{` characters that crash str.format. Use `re.sub(r'\{\{(\w+)\}\}', ...)` instead.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSS selector parsing | Custom regex-based CSS parser | `lxml.cssselect()` | CSS has complex specificity, pseudo-classes, combinators — cssselect handles all of them |
| XPath evaluation | String walking/regex | `lxml.html.fromstring().xpath()` | XPath has axes, predicates, node types, namespaces |
| JSONPath evaluation | Custom `$.` path walker | `jsonpath_ng.parse().find()` | Array subscripts, recursive descent, filters |
| JS execution | JS interpreter in Python | `quickjs.Context().eval()` | QuickJS is a complete ES2020 interpreter |
| MD5 / base64 | Custom implementations | `hashlib.md5`, `base64.b64decode` | Correctness, encoding edge cases |

**Key insight:** Each of these has real edge cases that take weeks to get right. Phase 2's job is wiring existing libraries, not implementing algorithms.

---

## Common Pitfalls

### Pitfall 1: lxml whitespace in text_content()

**What goes wrong:** `element.text_content()` returns raw whitespace — leading/trailing spaces, newlines, tab characters — exactly as they appear in HTML source.
**Why it happens:** `text_content()` concatenates all descendant text nodes verbatim.
**How to avoid:** Always `strip()` the result of `text_content()` before returning from `eval_css`. Consider also normalizing `\xa0` (non-breaking space) to regular space.
**Warning signs:** Tests fail with unexpected leading/trailing whitespace.

### Pitfall 2: quickjs ajax stub swallowed as JSException

**What goes wrong:** Calling `java.ajax()` from JS raises `NotImplementedError` in Python, but quickjs catches it and re-raises as `quickjs.JSException: InternalError: Python call failed.`
**Why it happens:** `add_callable` callbacks that raise Python exceptions are converted by the binding to JS `InternalError`. [VERIFIED: tested 2026-04-07]
**How to avoid:** Catch `quickjs.JSException` in `eval_js()` and wrap it in `RuleError` with the original string. The message `"Python call failed."` is enough context for debugging in Phase 2.
**Warning signs:** `java.ajax()` test raises `JSException` not `NotImplementedError` directly.

### Pitfall 3: jsonpath-ng filter syntax requires `.ext` module

**What goes wrong:** `jsonpath_ng.parse('[?(@.status == "free")]')` raises a parse error.
**Why it happens:** Filter predicates (`?()`) are in the extended module, not the base `jsonpath_ng` package.
**How to avoid:** For Phase 2, use `jsonpath_ng.parse` (covers all non-filter expressions). If filter expressions appear in book sources in later phases, switch to `jsonpath_ng.ext.parse`. [VERIFIED: both available in 1.8.0]
**Warning signs:** `Error on line 1, col X: Unexpected character: ?`

### Pitfall 4: lxml fromstring type depends on content

**What goes wrong:** `lxml.html.fromstring('<p>text</p>')` returns an `HtmlElement` with tag `p`, not `html`. Calling `.cssselect('p')` on this element returns an empty list because the element IS the `p`.
**Why it happens:** `fromstring` returns the root element of the parsed fragment — which may be the `p` itself for single-element fragments.
**How to avoid:** When the content is a full page response, `fromstring()` returns the `html` element and `//` XPaths work from there. For known fragment inputs, use `.cssselect()` on the returned element directly (not on a wrapping document). In practice, novel site responses are always full pages.
**Warning signs:** Empty results from a selector that should match.

### Pitfall 5: CSS rule body with no @attribute modifier

**What goes wrong:** `css:div.content` (no `@`) is treated as "return HTML" by many implementations, but callers may expect plain text.
**Why it happens:** Ambiguous rule format — without explicit `@text`, could mean "first match element's HTML" or "first match element's text".
**How to avoid:** Document clearly: no `@` suffix → serialize outer HTML. If the caller wants text, the rule must include `@text`.
**Warning signs:** Downstream code sees `<div class="content">...</div>` instead of plain text.

### Pitfall 6: replaceRegex with odd number of ## parts

**What goes wrong:** `##pattern##` (trailing `##`) splits to `['', 'pattern', '']` — replacement is `''` (empty string = delete), which is valid. But `##pattern` (no second `##`) splits to `['', 'pattern']` — only one part after stripping leading empty, loop condition `i + 1 < len(parts)` fails, rule silently does nothing.
**Why it happens:** User authored a malformed replaceRegex.
**How to avoid:** The loop already handles this correctly — `i + 1 < len(parts)` means incomplete pairs are skipped. This is the right behavior (silent skip of malformed trailing entries).
**Warning signs:** Expected transformation doesn't happen — check the rule string for odd `##` count.

---

## Test Fixture Design

### Fixture Files (all in `tests/fixtures/`)

**`html_title.html`** — Minimal HTML for CSS/XPath title extraction tests:
```html
<html><head><title>Test</title></head><body>
<h1 class="bookname">斗破苍穹</h1>
<span class="author">天蚕土豆</span>
<a class="toc-link" href="/toc/123">目录</a>
<img class="cover" src="/covers/123.jpg"/>
</body></html>
```

**`toc_list.html`** — HTML for chapter list extraction:
```html
<html><body>
<ul class="chapter-list">
  <li><a href="/ch/1">第一章 陨落的天才</a></li>
  <li><a href="/ch/2">第二章 斗之气</a></li>
  <li><a href="/ch/3">第三章 萧炎</a></li>
</ul>
<a class="next-page" href="/toc/123?page=2">下一页</a>
</body></html>
```

**`content.html`** — HTML for chapter content extraction:
```html
<html><body>
<div id="content">
  <p>　　萧炎双眼微合，感受着气旋之中那股缓缓流动的斗气...</p>
  <p>　　这是一段测试内容。</p>
</div>
<a class="next-chapter" href="/ch/2">下一章</a>
</body></html>
```

**`book_info.json`** — JSON for JSONPath tests:
```json
{
  "book": {
    "name": "斗破苍穹",
    "author": "天蚕土豆",
    "cover": "https://example.com/cover.jpg",
    "intro": "这是简介。"
  },
  "chapters": [
    {"name": "第一章", "url": "/ch/1"},
    {"name": "第二章", "url": "/ch/2"}
  ]
}
```

**`search_results.json`** — JSON array for search rule tests:
```json
[
  {"title": "斗破苍穹", "author": "天蚕土豆", "url": "/book/123"},
  {"title": "斗罗大陆", "author": "唐家三少", "url": "/book/456"}
]
```

**`source_minimal.json`** — Minimal valid legado book source:
```json
{
  "bookSourceUrl": "https://example.com",
  "bookSourceName": "测试书源",
  "bookSourceType": 0,
  "searchUrl": "https://example.com/search?q={{searchKey}}&page={{page}}",
  "ruleSearch": {
    "bookList": "css:.book-item",
    "name": "css:.book-name@text",
    "author": "css:.book-author@text",
    "bookUrl": "css:.book-link@href"
  },
  "ruleBookInfo": {
    "name": "css:h1.title@text",
    "author": "css:.author@text"
  },
  "ruleToc": {
    "chapterList": "css:.chapter-list li",
    "chapterName": "css:a@text",
    "chapterUrl": "css:a@href"
  },
  "ruleContent": {
    "content": "css:div#content@text"
  }
}
```

---

## Integration with Phase 1 src Layout

Phase 1 established `src/novel/` with flat module files (`display.py`, `state.py`, `commands.py`). The rule engine is complex enough to warrant a sub-package (decision D-04).

`src/novel/rules/` becomes a peer sub-package alongside `src/novel/data/` (which already exists as a sub-package holding fake book data). The convention is consistent: sub-packages for modules with multiple internal files, flat `.py` files for single-concern modules.

`pyproject.toml` uses `find_packages(where=["src"])` — no change needed; setuptools auto-discovers `novel.rules` as a sub-package when `src/novel/rules/__init__.py` exists.

Phase 3 will `from novel.rules import evaluate` from `commands.py` to wire HTTP-fetched content through the rule engine. The `java.ajax` stub in `_js.py` uses `ctx.add_callable('_javaAjax', ajax_stub)` — Phase 3 replaces `ajax_stub` with a real HTTP callable that accepts a URL and returns the response body. The quickjs context setup code in `_make_context()` does not change shape — Phase 3 passes a different callable.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already configured in pyproject.toml) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]` |
| Quick run command | `PYTHONPATH=src pytest tests/test_rules_*.py -x -q` |
| Full suite command | `PYTHONPATH=src pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SRC-01 | Load single-object book source JSON | unit | `pytest tests/test_source_parser.py::test_load_single -x` | Wave 0 |
| SRC-01 | Load array book source JSON (take first) | unit | `pytest tests/test_source_parser.py::test_load_array -x` | Wave 0 |
| SRC-02 | Validate required fields present | unit | `pytest tests/test_source_parser.py::test_required_fields -x` | Wave 0 |
| SRC-02 | Raise on missing bookSourceUrl | unit | `pytest tests/test_source_parser.py::test_missing_field -x` | Wave 0 |
| SRC-03 | CSS @text extracts text content | unit | `pytest tests/test_rules_css.py::test_text_attr -x` | Wave 0 |
| SRC-03 | CSS @href extracts attribute | unit | `pytest tests/test_rules_css.py::test_href_attr -x` | Wave 0 |
| SRC-03 | CSS no-match returns empty string | unit | `pytest tests/test_rules_css.py::test_no_match -x` | Wave 0 |
| SRC-04 | XPath text() returns joined text | unit | `pytest tests/test_rules_xpath.py::test_text_node -x` | Wave 0 |
| SRC-04 | XPath @attr returns attribute value | unit | `pytest tests/test_rules_xpath.py::test_attr_node -x` | Wave 0 |
| SRC-05 | JSONPath scalar field | unit | `pytest tests/test_rules_jsonpath.py::test_scalar -x` | Wave 0 |
| SRC-05 | JSONPath array wildcard | unit | `pytest tests/test_rules_jsonpath.py::test_array -x` | Wave 0 |
| SRC-05 | JSONPath no-match returns empty | unit | `pytest tests/test_rules_jsonpath.py::test_no_match -x` | Wave 0 |
| SRC-06 | replaceRegex single pair | unit | `pytest tests/test_rules_regex.py::test_single_pair -x` | Wave 0 |
| SRC-06 | replaceRegex chained pairs | unit | `pytest tests/test_rules_regex.py::test_chained -x` | Wave 0 |
| SRC-06 | replaceRegex empty replacement deletes | unit | `pytest tests/test_rules_regex.py::test_delete -x` | Wave 0 |
| SRC-07 | @js: inline expression eval | unit | `pytest tests/test_rules_js.py::test_inline -x` | Wave 0 |
| SRC-08 | `<js>` block eval with result mutation | unit | `pytest tests/test_rules_js.py::test_block -x` | Wave 0 |
| SRC-09 | java.base64Decode() in JS context | unit | `pytest tests/test_rules_js.py::test_java_base64 -x` | Wave 0 |
| SRC-09 | java.md5() in JS context | unit | `pytest tests/test_rules_js.py::test_java_md5 -x` | Wave 0 |
| SRC-09 | java.ajax() raises via JSException | unit | `pytest tests/test_rules_js.py::test_ajax_stub -x` | Wave 0 |
| SRC-10 | URL template with known keys | unit | `pytest tests/test_rules_evaluate.py::test_url_template -x` | Wave 0 |
| SRC-10 | URL template with unknown key left as-is | unit | `pytest tests/test_rules_evaluate.py::test_url_template_unknown -x` | Wave 0 |
| All | evaluate() dispatches to correct engine | integration | `pytest tests/test_rules_evaluate.py -x` | Wave 0 |
| D-09 | RuleError raised on bad CSS selector | unit | `pytest tests/test_rules_evaluate.py::test_rule_error -x` | Wave 0 |

### Coverage Targets

Every rule type needs:
- Happy path: correct extraction from fixture
- No-match path: returns `''` gracefully
- Error path: malformed rule/input raises `RuleError`, not crashes

JS specifically needs:
- `@js:` inline mode
- `<js>` block mode with result mutation
- `java.base64Decode`, `java.md5` callable
- `java.ajax` stub raises (via `JSException` → wrapped in `RuleError`)

### Sampling Rate

- **Per task commit:** `PYTHONPATH=src pytest tests/ -x -q`
- **Per wave merge:** `PYTHONPATH=src pytest -x -q` (full suite including Phase 1 tests)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

All test files are new — none exist yet. Wave 0 of each plan task creates the test file before implementing the module.

- [ ] `tests/fixtures/html_title.html` — CSS/XPath title extraction tests
- [ ] `tests/fixtures/toc_list.html` — chapter list, next-page link
- [ ] `tests/fixtures/content.html` — chapter content div
- [ ] `tests/fixtures/book_info.json` — JSONPath tests
- [ ] `tests/fixtures/search_results.json` — search result array
- [ ] `tests/fixtures/source_minimal.json` — SRC-01/02 book source parser
- [ ] `tests/test_source_parser.py` — SRC-01, SRC-02
- [ ] `tests/test_rules_css.py` — SRC-03
- [ ] `tests/test_rules_xpath.py` — SRC-04
- [ ] `tests/test_rules_jsonpath.py` — SRC-05
- [ ] `tests/test_rules_regex.py` — SRC-06
- [ ] `tests/test_rules_js.py` — SRC-07, SRC-08, SRC-09
- [ ] `tests/test_rules_evaluate.py` — dispatcher, URL templates, RuleError

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | All | Yes | 3.12.3 | — |
| lxml | SRC-03, SRC-04 | Yes (post-install) | 6.0.2 | — |
| cssselect | SRC-03 | Yes (post-install) | 1.4.0 | — |
| jsonpath-ng | SRC-05 | Yes (post-install) | 1.8.0 | — |
| quickjs | SRC-07, SRC-08, SRC-09 | Yes (post-install) | 1.19.4 | — |
| pytest | Test framework | Yes (from Phase 1) | unknown | — |

**Missing dependencies with no fallback:** None.

**Note:** These packages are not yet in `pyproject.toml` — Wave 0 of Plan 02-02 must add them to `[project].dependencies`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Legado rule CSS format is `css:selector@attribute` | §Legado Rule Syntax | If format differs (e.g., `css:selector%%attribute`), `rsplit('@', 1)` parser breaks |
| A2 | Legado replaceRegex format is `##pattern##replacement` with `##` as delimiter | §Legado Rule Syntax | If delimiter is different, chain parsing breaks |
| A3 | `bookSourceUrl` and `bookSourceName` are the only required fields | §Architecture Patterns (SRC-02) | If more fields are required by real sources, validator will pass malformed sources |
| A4 | `@js:` strips exactly `@js:` (4 chars + colon + space is part of expression) | §Legado Rule Syntax (JS) | If legado preserves the space in `@js: expr`, we need to `.strip()` — Pattern 2 already does this |
| A5 | `bookSourceType: 0` means text novel; arrays of sources are handled by returning first | §Book Source JSON Format | If Phase 3/4 needs to handle multi-source arrays differently, `load_book_source` needs updating |

---

## Open Questions

1. **Does legado ever combine selector + replaceRegex in a single rule string, or are they always separate fields?**
   - What we know: replaceRegex appears as a separate key in rule objects (e.g., `ruleContent.replaceRegex`)
   - What's unclear: Whether a single rule string can embed `##` as a chained post-processor
   - Recommendation: Treat `replaceRegex` as a separate field only (not embedded in selector strings) for Phase 2. Revisit if Phase 4 integration testing reveals otherwise.

2. **Does `evaluate()` need to return a list for rules that match multiple elements (e.g., chapter list)?**
   - What we know: `evaluate()` is typed as `-> str` per D-03
   - What's unclear: Phase 4's `ruleToc.chapterList` extracts multiple items — how does that flow work?
   - Recommendation: Phase 2 implements `evaluate() -> str` (first match). A separate `evaluate_list() -> list[str]` can be added in Phase 2 or Phase 4 as needed. The planner should explicitly include `evaluate_list()` if the ROADMAP plan 02-02 implies multi-element extraction.

---

## Sources

### Primary (HIGH confidence)
- VERIFIED by running code: lxml 6.0.2 + cssselect 1.4.0 — CSS selector behavior, text_content(), attribute extraction, fragment parsing
- VERIFIED by running code: lxml 6.0.2 XPath — text(), @attr results, HTML tree behavior
- VERIFIED by running code: jsonpath-ng 1.8.0 — parse/find API, DatumInContext.value, array handling, filter via ext module
- VERIFIED by running code: quickjs 1.19.4 — Context(), set(), get(), add_callable(), eval() return values, JSException shape, context performance (118ms/1000 contexts)
- VERIFIED by running code: re (stdlib) — replaceRegex chain split/apply logic
- VERIFIED by running code: re (stdlib) — URL template substitution via re.sub

### Secondary (MEDIUM confidence)
- CONTEXT.md (02-CONTEXT.md) — all locked decisions D-01 through D-10
- ROADMAP.md — Phase 2 plan breakdown (02-01 through 02-04), success criteria

### Tertiary (LOW confidence)
- [ASSUMED] Legado rule syntax specifics (CSS `@attribute` format, replaceRegex `##` delimiter, JS `@js:` / `<js>` format) — consistent with training knowledge but not verified against legado source code or official documentation

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — packages installed and all critical APIs verified by running code
- Architecture patterns: HIGH — code patterns derived from verified API behavior
- Legado rule syntax: MEDIUM — format shapes consistent with training knowledge; not verified against legado Android source code
- Pitfalls: HIGH — pitfalls verified by actually triggering the failure conditions in Python

**Research date:** 2026-04-07
**Valid until:** 2026-05-07 (stable libraries; legado format unlikely to change in 30 days)
