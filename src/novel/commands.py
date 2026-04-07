"""Subcommand dispatcher for the /novel CLI tool."""
from __future__ import annotations

from novel.display import stream_chapter
from novel.state import load_state, save_state
from novel.data.fake_book import FAKE_BOOK, get_fake_chapter

STUB_COMMANDS = {
    'search': 'search: not yet implemented -- available in Phase 4',
    'toc':    'toc: not yet implemented -- available in Phase 4',
    'shelf':  'shelf: not yet implemented -- available in Phase 5',
    'use':    'use: not yet implemented -- available in Phase 3',
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
        print(STUB_COMMANDS['search'])
    elif cmd == "toc":
        print(STUB_COMMANDS['toc'])
    elif cmd == "shelf":
        print(STUB_COMMANDS['shelf'])
    elif cmd == "use":
        print(STUB_COMMANDS['use'])
    else:
        # No args or unrecognized command -> default (stream current chapter)
        _stream_current()
