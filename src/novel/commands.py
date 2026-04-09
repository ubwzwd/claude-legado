"""Subcommand dispatcher for the /novel CLI tool."""
from __future__ import annotations

import json
import shutil
import urllib.parse
from pathlib import Path

from novel.display import stream_chapter
from novel.state import ensure_dirs, load_state, save_state, SOURCES_DIR, save_search_cache, load_search_cache, load_shelf, save_shelf, set_active_book
from novel.data.fake_book import FAKE_BOOK, get_fake_chapter
from novel.rules._source import load_book_source
from novel.http import fetch, follow_toc_pages
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


def _add_book(args: list[str]) -> None:
    """Implement /novel add <index>."""
    if not args:
        print('Usage: /novel add <index>')
        return
        
    try:
        index = int(args[0])
    except ValueError:
        print('Index must be an integer.')
        return
        
    cache = load_search_cache()
    if index < 1 or index > len(cache):
        print('Invalid index.')
        return
        
    book = cache[index - 1]
    
    state = load_state()
    source_path_str = state.get('source')
    if not source_path_str or source_path_str == 'builtin':
         print('No active source to fetch book info.')
         return
         
    try:
         source = load_book_source(Path(source_path_str))
    except (ValueError, json.JSONDecodeError, OSError) as e:
         print(f'Error loading source: {e}')
         return
         
    book_url = book.get('bookUrl')
    if not book_url:
         print('No book URL found in search cache for this book.')
         return
         
    book_url = urllib.parse.urljoin(source['bookSourceUrl'], book_url)

    try:
         content, _ = fetch(book_url, source)
    except Exception as e:
         print(f'Error fetching book info: {e}')
         return
         
    rule_intro = source.get('ruleBookInfoIntro', '')
    if rule_intro:
        intro_val = evaluate(rule_intro, content)
        if isinstance(intro_val, list) and intro_val:
             book['intro'] = str(intro_val[0]).strip()
        else:
             book['intro'] = str(intro_val).strip() if intro_val else '[No intro extracted]'
    else:
        book['intro'] = '[No intro extracted]'

    shelf = load_shelf()
    shelf.append(book)
    save_shelf(shelf)
    print(f"Added '{book['name']}' to shelf.")


def _list_shelf() -> None:
    """Implement /novel shelf."""
    shelf = load_shelf()
    if not shelf:
        print('Shelf is empty.')
        return
        
    state = load_state()
    current_book_id = state.get('current_book')
        
    for i, book in enumerate(shelf, start=1):
        name = book.get('name', '[No name extracted]')
        author = book.get('author', '[No author extracted]')
        # Just use name as pseudo ID for active marker since we don't have proper IDs yet
        active_marker = "*" if current_book_id == name else " "
        print(f"[{i}]{active_marker} {name} - {author}")


def _show_toc(args: list[str]) -> None:
    """Implement /novel toc <page>."""
    state = load_state()
    current_book_id = state.get('current_book')
    if not current_book_id or current_book_id == 'fake-book-01':
        print("No active book selected.")
        return
        
    shelf = load_shelf()
    book = None
    for item in shelf:
        if item.get('name') == current_book_id:
            book = item
            break
            
    if not book:
        print("Active book not found in shelf.")
        return
        
    source_path_str = state.get('source')
    if not source_path_str or source_path_str == 'builtin':
         print('No active source to fetch TOC.')
         return
         
    try:
         source = load_book_source(Path(source_path_str))
    except Exception as e:
         print(f'Error loading source: {e}')
         return
         
    toc_url = book.get('tocUrl') or book.get('bookUrl')
    if not toc_url:
         print("Book has no TOC URL or Book URL.")
         return
         
    toc_url = urllib.parse.urljoin(source['bookSourceUrl'], toc_url)
         
    rule_next_toc = source.get('ruleTocNextUrl', '')
    
    pages_html = follow_toc_pages(
        start_url=toc_url,
        fetch_fn=lambda u: fetch(urllib.parse.urljoin(source['bookSourceUrl'], u), source)[0],
        eval_fn=lambda r, h: str(evaluate(r, h) or ''),
        next_url_rule=rule_next_toc
    )
    
    rule_toc = source.get('ruleToc')
    if not rule_toc:
        print("Source missing ruleToc.")
        return
        
    rule_toc_name = source.get('ruleTocName', '')
    rule_toc_url = source.get('ruleTocUrl', '')
    
    chapters = []
    
    for page_html in pages_html:
        items = evaluate_list(rule_toc, page_html)
        for item in items:
            name = str(evaluate(rule_toc_name, item) or '').strip() if rule_toc_name else ''
            url = evaluate(rule_toc_url, item) if rule_toc_url else ''
            if isinstance(url, list) and url:
                url = str(url[0]).strip()
            else:
                url = str(url or '').strip()
                
            chapters.append({'name': name, 'url': url})
            
    # Cache chapters
    book['chapters'] = chapters
    save_shelf(shelf)
    
    if not chapters:
        print("No chapters found in TOC.")
        return
        
    page = 1
    if args:
        try:
            page = int(args[0])
        except ValueError:
             print("Page must be an integer.")
             return
             
    per_page = 50
    total_pages = (len(chapters) + per_page - 1) // per_page
    
    if page < 1 or page > total_pages:
        if total_pages > 0:
             print(f"Invalid page. TOC has {total_pages} pages.")
        return
        
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(chapters))
    
    print(f"TOC for '{book.get('name', 'Unknown')}' (Page {page}/{total_pages}):")
    for i in range(start_idx, end_idx):
        ch = chapters[i]
        print(f"[{i + 1}] {ch.get('name', '[No Name]')}")


def _info_book() -> None:
    """Implement /novel info."""
    state = load_state()
    current_book_id = state.get('current_book')
    if not current_book_id or current_book_id == 'fake-book-01':
        if current_book_id == 'fake-book-01':
            print("Title: " + FAKE_BOOK['title'])
            print("Author: " + FAKE_BOOK['author'])
            print("Intro: " + FAKE_BOOK['intro'])
        else:
            print("No active book selected.")
        return
        
    shelf = load_shelf()
    for book in shelf:
        if book.get('name') == current_book_id:
            print(f"Title:  {book.get('name', '[No Name]')}")
            print(f"Author: {book.get('author', '[No Author]')}")
            print(f"\nIntro:\n{book.get('intro', '[No Intro]')}")
            return
            
    print("Active book not found in shelf.")


def _read_book(args: list[str]) -> None:
    """Implement /novel read <index>."""
    if not args:
        print("Usage: /novel read <index>")
        return
        
    try:
        index = int(args[0])
    except ValueError:
        print("Index must be an integer.")
        return
        
    shelf = load_shelf()
    if index < 1 or index > len(shelf):
        print("Invalid shelf index.")
        return
        
    book = shelf[index - 1]
    name = book.get('name')
    if not name:
        print("Cannot read book: Book name is missing in shelf data.")
        return
        
    set_active_book(name)
    print(f"Now reading: {name}")


_RECOGNIZED = {"next", "prev", "search", "toc", "shelf", "use", "add", "info", "read"}


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
    elif cmd == "add":
        _add_book(args[1:])
    elif cmd == "info":
        _info_book()
    elif cmd == "read":
        _read_book(args[1:])
    elif cmd == "toc":
        _show_toc(args[1:])
    elif cmd == "shelf":
        _list_shelf()
    elif cmd == "use":
        _use_source(args[1:])
    else:
        # No args or unrecognized command -> default (stream current chapter)
        _stream_current()
