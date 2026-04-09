"""Subcommand dispatcher for the /novel CLI tool."""
from __future__ import annotations

import json
import shutil
import urllib.parse
from pathlib import Path

from novel.display import stream_chapter
from novel.state import ensure_dirs, load_state, save_state, SOURCES_DIR, save_search_cache
from novel.data.fake_book import FAKE_BOOK, get_fake_chapter
from novel.rules._source import load_book_source
from novel.http import fetch
from novel.rules import evaluate_list, evaluate

STUB_COMMANDS = {
    'search': 'search: not yet implemented -- available in Phase 4',
    'toc':    'toc: not yet implemented -- available in Phase 4',
    'shelf':  'shelf: not yet implemented -- available in Phase 5',
}


def _bootstrap_state(state: dict) -> dict:
    """If no book is loaded, auto-load the builtin fake book at chapter 0."""
    if state['current_book'] is None:
        state['current_book'] = FAKE_BOOK['title']
        state['chapter_index'] = 0
        state['source'] = 'builtin'
    return state


def _stream_current() -> None:
    """Load state, stream the current chapter, save state."""
    state = load_state()
    state = _bootstrap_state(state)
    chapter = get_fake_chapter(state['chapter_index'])
    if chapter is None:
        print("No more chapters. Use /novel prev to go back.")
        return
    total = len(FAKE_BOOK['chapters'])
    stream_chapter(
        chapter_num=state['chapter_index'] + 1,
        title=chapter['title'],
        content=chapter['content'],
        chapter_index=state['chapter_index'],
        total=total,
    )
    save_state(state)


def _advance(delta: int) -> None:
    """Advance chapter_index by delta (+1 for next, -1 for prev), stream, save."""
    state = load_state()
    state = _bootstrap_state(state)
    new_index = state['chapter_index'] + delta
    total = len(FAKE_BOOK['chapters'])
    if new_index < 0:
        print("Already at the first chapter.")
        return
    if new_index >= total:
        print("Already at the last chapter.")
        return
    state['chapter_index'] = new_index
    chapter = get_fake_chapter(new_index)
    stream_chapter(
        chapter_num=new_index + 1,
        title=chapter['title'],
        content=chapter['content'],
        chapter_index=new_index,
        total=total,
    )
    save_state(state)


def _use_source(args: list[str]) -> None:
    """Load a book source JSON file, copy to sources dir, and set as active.

    Args:
        args: Argument list — first element is the path to a source JSON file.
    """
    if not args:
        print('Usage: /novel use <path-to-source.json>')
        return

    path = Path(args[0])

    try:
        source = load_book_source(path)
    except (ValueError, json.JSONDecodeError, OSError) as e:
        print(f'Error loading source: {e}')
        return

    ensure_dirs()

    # Use path.name (basename only) for path traversal safety (T-03-01)
    dest = SOURCES_DIR / path.name
    shutil.copy2(path, dest)

    state = load_state()
    state['source'] = str(dest)  # Store as string, not Path (Pitfall 5)
    save_state(state)

    # Print summary (D-14)
    RULE_FIELDS = ['searchUrl', 'ruleSearch', 'ruleBookInfo', 'ruleToc', 'ruleContent']
    rules_present = [f for f in RULE_FIELDS if source.get(f)]
    rules_absent = [f for f in RULE_FIELDS if not source.get(f)]
    print('Loaded book source:')
    print(f"  Name:  {source['bookSourceName']}")
    print(f"  URL:   {source['bookSourceUrl']}")
    rules_line = ', '.join([f'{f} ✓' for f in rules_present] + [f'{f} —' for f in rules_absent])
    print(f'  Rules: {rules_line}')
    print(f'\nStored: {dest}')


def _search_books(args: list[str]) -> None:
    """Implement /novel search <query>."""
    if not args:
        print('Usage: /novel search <query>')
        return

    query = ' '.join(args)
    state = load_state()
    source_path_str = state.get('source')

    if not source_path_str or source_path_str == 'builtin':
        print('No active source. Use /novel use <path-to-source.json> first.')
        return

    try:
        source = load_book_source(Path(source_path_str))
    except (ValueError, json.JSONDecodeError, OSError) as e:
        print(f'Error loading source: {e}')
        return

    search_url_template = source.get('searchUrl')
    if not search_url_template:
        print('Active source does not support searching (no searchUrl).')
        return

    # Build URL (D-01)
    url = search_url_template.replace('{{key}}', urllib.parse.quote(query))
    url = url.replace('{{page}}', '1')

    try:
        content, _ = fetch(url, source)
    except Exception as e:
        print(f'Error fetching search results: {e}')
        return

    rule_search = source.get('ruleSearch')
    if not rule_search:
        print('Active source does not have ruleSearch.')
        return

    try:
        items = evaluate_list(rule_search, content)
    except Exception as e:
        print(f'Error evaluating search rules: {e}')
        return

    books = []
    source_name = source.get('bookSourceName', 'Unknown Source')

    for item in items:
        # Evaluate only if rule is present (to avoid generic error from empty rule string)
        rule_name = source.get('ruleSearchName', '')
        name = str(evaluate(rule_name, item) or '') if rule_name else ''
        
        rule_author = source.get('ruleSearchAuthor', '')
        author = str(evaluate(rule_author, item) or '') if rule_author else ''
        
        rule_bookurl = source.get('ruleBookUrl', '')
        bookUrl = evaluate(rule_bookurl, item) if rule_bookurl else ''
        if isinstance(bookUrl, list) and bookUrl:
            bookUrl = bookUrl[0]
        else:
            bookUrl = str(bookUrl or '')

        rule_coverurl = source.get('ruleSearchCoverUrl', '')
        coverUrl = evaluate(rule_coverurl, item) if rule_coverurl else ''
        if isinstance(coverUrl, list) and coverUrl:
             coverUrl = coverUrl[0]
        else:
             coverUrl = str(coverUrl or '')
             
        rule_note = source.get('ruleSearchNote', '')
        intro = evaluate(rule_note, item) if rule_note else ''
        if isinstance(intro, list) and intro:
             intro = intro[0]
        else:
             intro = str(intro or '')

        books.append({
            'name': name.strip() if name else '',
            'author': author.strip() if author else '',
            'bookUrl': bookUrl.strip() if bookUrl else '',
            'coverUrl': coverUrl.strip() if coverUrl else '',
            'intro': intro.strip() if intro else '',
            'origin_source_id': source_name
        })

    save_search_cache(books)

    if not books:
        print('No results found.')
        return

    for i, book in enumerate(books, start=1):
        name = book['name'] or '[No name extracted]'
        author = book['author'] or '[No author extracted]'
        print(f"[{i}] {name} - {author} - {source_name}")


_RECOGNIZED = {"next", "prev", "search", "toc", "shelf", "use"}


def dispatch(args: list[str]) -> None:
    """Route subcommand args to the correct handler.

    Args:
        args: Argument list (typically sys.argv[1:]).
              Empty args or unrecognized first arg -> default handler (_stream_current).
    """
    cmd = args[0] if args else None

    if cmd == "next":
        _advance(+1)
    elif cmd == "prev":
        _advance(-1)
    elif cmd == "search":
        _search_books(args[1:])
    elif cmd == "toc":
        print(STUB_COMMANDS['toc'])
    elif cmd == "shelf":
        print(STUB_COMMANDS['shelf'])
    elif cmd == "use":
        _use_source(args[1:])
    else:
        # No args or unrecognized command -> default (stream current chapter)
        _stream_current()
