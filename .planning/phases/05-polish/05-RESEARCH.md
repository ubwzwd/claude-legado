# Phase 05 Research: Polish

## Objective
Answer: "What do I need to know to PLAN this phase well?" focusing on error handling, bookshelf UX, and preventing default payloads.

## Findings

### 1. Error Presentation (D-01)
- **Current State**: Exceptions during source loading, network fetching, and rule evaluation are either caught and dumped via `print(f"Error: {e}")` (e.g., in `_fetch_and_stream`, `_search_books`, `_use_source`) or sometimes uncaught during rule evaluation loop.
- **Action Needed**: 
  - Need a new function in `novel.display`, e.g., `stream_error(msg: str) -> None`, that prints the error message mimicking Claude's thinking style (e.g. `[italic dim]*Claude is having trouble reaching the source context: {msg}*[/italic dim]`).
  - Update `commands.py` error handling blocks to use `stream_error`.
  - Ensure `_fetch_and_stream` catches `novel.rules._errors.RuleError` and HTTP exceptions.

### 2. Shelf Information Density (D-02)
- **Current State**: `state.json` tracks a global `chapter_index` which is reset to 0 every time a different book is activated in `set_active_book`. `shelf.json` stores books but without their respective reading progress.
- **Action Needed**:
  - `_fetch_and_stream` must update `book['chapter_index']` in `shelf.json` whenever progress is made, in addition to `state.json`.
  - `set_active_book(book_id)` in `state.py` should initialize `state['chapter_index']` to the saved index from `shelf.json` rather than hardcoding `0`.
  - Modify `_list_shelf` in `commands.py` to display `total_chapters = len(book.get('chapters', []))` and `curr_chapter = book.get('chapter_index', 0) + 1` alongside the book info.

### 3. TOC Navigation Marker (D-03)
- **Current State**: `_show_toc` just lists chapter segments.
- **Action Needed**: Modify `_show_toc` loop to check if `i == state['chapter_index']` and prepend `-> ` and highlight the line to clearly show the user's active chapter.

### 4. Remove Builtin Fallback (D-04)
- **Current State**: `_bootstrap_state` forces `FAKE_BOOK` loading.
- **Action Needed**: Let `state.json` start empty. If the user invokes `/novel` with no active book, stream a fake Claude message instructing them to use a source instead of falling back to `fake_book.py`. Also consider removing `fake_book.py` entirely if it's no longer used.

### 5. Setup & Documentation
- **Action Needed**: Create a top-level `README.md` providing standard setup instructions (`pip install -e .`), a sample source JSON reference, and CLI commands breakdown.

## Verification Architecture
- **Errors**: Run invalid sources and timeout domains, check that the output matches Claude disguises.
- **State**: Switch between books using `/novel read <idx>` and confirm chapter state is not overwritten to 0. 

## RESEARCH COMPLETE
