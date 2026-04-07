"""Subcommand dispatcher for the /novel CLI tool."""
from __future__ import annotations


def _stream_current() -> None:
    """Placeholder for streaming current chapter. Plan 02 replaces with real streaming."""
    print("Reading current chapter...")


def _advance(direction: int) -> None:
    """Placeholder for advancing to next/prev chapter. Plan 02 replaces with real logic."""
    if direction > 0:
        print("Advancing to next chapter...")
    else:
        print("Going to previous chapter...")


_RECOGNIZED = {"next", "prev", "search", "toc", "shelf", "use"}


def dispatch(args: list[str]) -> None:
    """Route subcommand args to the correct handler.

    Args:
        args: Argument list (typically sys.argv[1:]).
              Empty args or unrecognized first arg → default handler (_stream_current).
    """
    cmd = args[0] if args else None

    if cmd == "next":
        _advance(+1)
    elif cmd == "prev":
        _advance(-1)
    elif cmd == "search":
        print("search: not yet implemented -- available in Phase 4")
    elif cmd == "toc":
        print("toc: not yet implemented -- available in Phase 4")
    elif cmd == "shelf":
        print("shelf: not yet implemented -- available in Phase 5")
    elif cmd == "use":
        print("use: not yet implemented -- available in Phase 3")
    else:
        # No args or unrecognized command → default (stream current chapter)
        _stream_current()
