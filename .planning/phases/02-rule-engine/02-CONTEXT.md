# Phase 2: Rule Engine - Context

**Gathered:** 2026-04-07 (discuss mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Parse and evaluate CSS/XPath/JSONPath/regex/JS rules extracted from legado book source JSON. **Pure rule engine — no HTTP, no UI, no networking.** Phase 3 wires HTTP; Phase 4 wires the full read pipeline. Phase 2 must be fully testable against in-memory HTML/JSON fixtures.

The JS layer (`@js:` / `<js>`) is included in Phase 2. The `java.ajax()` bridge is stubbed out (not callable) — HTTP injection is finalized in Phase 3.

</domain>

<decisions>
## Implementation Decisions

### quickjs Binding
- **D-01:** Use the `quickjs` PyPI package (`pip install quickjs`). API: `quickjs.Context()`, `ctx.eval()`. Lightweight, well-maintained CPython binding to QuickJS.
- **D-02:** `java.ajax()` is stubbed in Phase 2 — inject a no-op callable that raises `NotImplementedError("java.ajax not available until Phase 3")`. This satisfies SRC-09 context injection without any HTTP dependency.

### Rule API Shape
- **D-03:** Public API is a single `evaluate(rule: str, content: str | dict, base_url: str = '') -> str` function in `src/novel/rules/__init__.py`. Auto-detects rule type from prefix (`css:`, `xpath:`, `$`, `@js:`, `<js>`). Returns a string.
- **D-04:** Module lives at `src/novel/rules/` (sub-package, not a flat file) — complex enough to warrant internal splitting: `_css.py`, `_xpath.py`, `_jsonpath.py`, `_regex.py`, `_js.py`, `_detect.py`.
- **D-05:** Phase 3/4 callers use: `from novel.rules import evaluate`. No class instantiation required at call site.

### Test Fixtures
- **D-06:** Synthetic minimal fixtures committed to `tests/fixtures/`. Hand-crafted HTML/JSON strings targeting specific rule types. No real book source files in repo — avoids URL rot and legal gray areas.
- **D-07:** Each fixture file is small and focused: `html_title.html`, `toc_list.html`, `book_info.json`, etc. One fixture per rule type being tested.
- **D-08:** Book source JSON parser tests use a hand-crafted synthetic book source object (all required fields present, representative values). Not a real scraped source.

### Rule Failure Behavior
- **D-09:** Failed rule evaluation raises `RuleError(rule: str, cause: Exception)` — a custom exception defined in `src/novel/rules/_errors.py`. Never returns empty string silently.
- **D-10:** Phase 3/4 callers catch `RuleError` explicitly. Phase 5 adds user-facing error messages on top. This keeps the rule engine honest and makes debugging straightforward.

### Claude's Discretion
- Internal sub-module split within `src/novel/rules/` (how many files, exact naming)
- replaceRegex chain parsing implementation detail (regex split on `##`)
- URL template substitution implementation (`{{key}}` substitution via str.format or re.sub)
- Exact `quickjs.Context` setup pattern (one context per evaluate call vs module-level singleton)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements (MANDATORY)
- `.planning/REQUIREMENTS.md` — Phase 2 covers SRC-01 through SRC-10. Read the full spec for each requirement before planning tasks.

### Project decisions
- `.planning/PROJECT.md` §Key Decisions — Python stack confirmation (lxml+cssselect, quickjs, jsonpath-ng), chapter-per-invocation design, Phase 2 rationale (rule engine in isolation before HTTP)

### Phase 1 context (for integration awareness)
- `.planning/phases/01-scaffold-display-state/01-CONTEXT.md` — src/novel/ package layout, state file paths, established patterns

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/novel/state.py` — atomic write pattern (`tmp + Path.replace()`) — rule engine test helpers may want the same pattern if writing fixture output
- `src/novel/__main__.py` → `commands.py` dispatch pattern — Phase 4 will route `use`, `search`, `toc` through the rule engine

### Established Patterns
- Flat module files for simple concerns (`display.py`, `state.py`, `commands.py`) — rule engine is complex enough to warrant a sub-package (`src/novel/rules/`)
- No class instantiation at call site — commands call module-level functions directly. Rule engine API follows the same pattern (`evaluate()` not `RuleEngine().evaluate()`)
- `src/novel/data/` sub-directory already exists (fake book data) — `src/novel/rules/` follows the same sub-package convention

### Integration Points
- Phase 3 will import `from novel.rules import evaluate` and pass fetched HTML/JSON as content
- Phase 4 uses evaluate for `ruleSearch`, `ruleBookInfo`, `ruleToc`, `ruleContent` field values
- `java.ajax()` stub in Phase 2 must be swappable for a real async-compatible implementation in Phase 3 without changing the quickjs context setup

</code_context>

<specifics>
## Specific Ideas

- STATE.md notes HIGH risk on `java.ajax()` sync-in-JS. Decision: stub with `NotImplementedError` in Phase 2, implement as pre-fetch injection in Phase 3 (caller fetches the URL, injects result into JS context before eval).
- `evaluate()` signature takes `content: str | dict` — str for HTML (CSS/XPath rules), dict for JSON (JSONPath rules). Auto-detection of content type can use `isinstance` check.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-rule-engine*
*Context gathered: 2026-04-07*
