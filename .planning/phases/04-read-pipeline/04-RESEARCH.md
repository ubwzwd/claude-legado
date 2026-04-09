# Phase 04: Read Pipeline - Research

## Objective
Identify how to wire the existing rule engine and HTTP layer into a fully synchronous search, shelf, and read pipeline.

## Implementation Patterns & Findings
- **Search flow (`/novel search`)**: Fetch the search page using the searchUrl (after replacing `{{key}}`). Evaluate the response with `ruleSearch`, which should return a list of books. We need a way to store this short-lived cache (e.g. `state.py: save_search_cache`).
- **Shelf additions (`/novel add`)**: Pick from the search cache. Need to fetch book info using `ruleBookInfo` where applicable, save intro/author into the shelf (`shelf.json` via `state.py: save_shelf`), and fetch the initial TOC so chapters are ready to read.
- **TOC handling (`/novel toc`)**: Use `novel.http.follow_toc_pages()` + `novel.rules.evaluate_list` under `ruleToc` to extract the chapter URLs and titles. We need to truncate output to chunks (e.g., 50 at a time) and paginate based on the command argument per D-04.
- **Reading (`/novel` and `/novel next`)**: Needs to fetch the chapter URL, use `novel.rules.evaluate` against `ruleContent`, and return text. Pass string chunks to `display.stream_chapter()`. 
- **Book Info (`/novel info`)**: Fetch the book detail page, use `ruleBookInfo`, and display the introduction clearly, rather than cramming it in `novel add`.

## Validation Architecture
- Testing will require `respx` to mock out `httpx` HTTP requests for search, TOC, and chapter fetching to isolate unit tests from actual network requests.
- We need tests to ensure the read stream saves progress first before streaming (D-10) and handles CJK text gracefully.
- Validate `shelf.json` state updates properly during shelf modifications.

## Integration & Dependencies
- `novel.commands` will be completely overhauled to remove fake data stubs and plug in real components (`novel.http.fetch`, `novel.rules.evaluate`, `novel.rules.evaluate_list`).
- `novel.state` will need new functions: `load_shelf()`, `save_shelf()`, `load_search_cache()`, `save_search_cache()`.

## Missing Data & Error Handling
- Per D-09: If a rule engine extract fails for an optional field (like intro), fallback to `[No intro extracted]`. Wrap `evaluate(...)` with a fallback mechanism or catch `RuleError`.
- Per D-10: State updates (progress saving) must trigger **before** the stream engine begins outputting characters so Ctrl+C interruptions don't cause lost progress.

## RESEARCH COMPLETE
