"""Streaming display engine for the /novel skill.

Makes novel text appear like Claude AI output by streaming characters one-by-one
with variable delays that mimic natural LLM token generation.
"""
from __future__ import annotations

import random
import sys
import time

# Timing constants
PAUSE_LONG = 0.15     # sentence-end: 。！？
PAUSE_MED = 0.06      # clause-end: ，、；
DELAY_MIN = 0.015     # 15ms base min
DELAY_MAX = 0.040     # 40ms base max
BURST_PROB = 0.15     # 15% chance of burst
BURST_MIN = 8
BURST_MAX = 15


def _char_delay(ch: str) -> float:
    """Return the sleep duration after emitting character ch.

    Args:
        ch: Single character to determine delay for.

    Returns:
        PAUSE_LONG for sentence-end punctuation,
        PAUSE_MED for clause-end punctuation,
        random uniform in [DELAY_MIN, DELAY_MAX] otherwise.
    """
    if ch in "。！？":
        return PAUSE_LONG
    if ch in "，、；":
        return PAUSE_MED
    return random.uniform(DELAY_MIN, DELAY_MAX)


def stream_text(text: str) -> None:
    """Stream text character-by-character to stdout with variable delays.

    Occasionally emits burst chunks of 8-15 characters for realism.
    After all characters are written, emits a newline.

    Args:
        text: The text content to stream.
    """
    i = 0
    length = len(text)
    while i < length:
        # Attempt burst with probability BURST_PROB if enough chars remain
        if random.random() < BURST_PROB and i + BURST_MIN < length:
            chunk_size = random.randint(BURST_MIN, BURST_MAX)
            chunk = text[i:i + chunk_size]
            sys.stdout.write(chunk)
            sys.stdout.flush()
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            i += chunk_size
        else:
            ch = text[i]
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(_char_delay(ch))
            i += 1
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_reasoning_preamble() -> None:
    """Print a fake 'thinking' preamble styled as Claude reasoning output.

    Creates a Console instance inside the function to avoid Rich detecting
    test environments at module import time.
    """
    from rich.console import Console

    console = Console(markup=True, highlight=False)
    console.print("[italic dim]*Analyzing the request and preparing response...*[/italic dim]\n")


def print_chapter_header(chapter_num: int, title: str) -> None:
    """Print a chapter header with number and title using Rich bold markup.

    Args:
        chapter_num: The 1-based chapter number to display.
        title: The chapter title string.
    """
    from rich.console import Console

    console = Console(markup=True, highlight=False)
    console.print(f"\n[bold]第{chapter_num}章  {title}[/bold]\n")


def print_nav_hints(chapter_index: int, total: int) -> None:
    """Print navigation hints appropriate for the current chapter position.

    Always shows /novel toc. Shows /novel next if not last chapter.
    Shows /novel prev if not first chapter.

    Args:
        chapter_index: 0-based index of the current chapter.
        total: Total number of chapters.
    """
    from rich.console import Console

    hints: list[str] = []
    if chapter_index < total - 1:
        hints.append("[dim]/novel next[/dim] -- 下一章")
    if chapter_index > 0:
        hints.append("[dim]/novel prev[/dim] -- 上一章")
    hints.append("[dim]/novel toc[/dim] -- 目录")

    console = Console(markup=True, highlight=False)
    console.print("\n  " + "   |   ".join(hints))


def stream_chapter(
    chapter_num: int,
    title: str,
    content: str,
    chapter_index: int,
    total: int,
) -> None:
    """Stream a complete chapter with preamble, header, content, and nav hints.

    This is the main entry point that Plan 03 will wire into commands.py.

    Args:
        chapter_num: 1-based chapter number for display.
        title: Chapter title string.
        content: Full chapter text to stream.
        chapter_index: 0-based index for navigation hint calculation.
        total: Total chapters for navigation hint calculation.
    """
    print_reasoning_preamble()
    print_chapter_header(chapter_num, title)
    stream_text(content)
    print_nav_hints(chapter_index, total)


def stream_error(msg: str) -> None:
    """Print an error message styled as Claude reasoning output.

    Args:
        msg: The error message to display.
    """
    from rich.console import Console

    console = Console(markup=True, highlight=False)
    console.print(f"[italic dim]*Claude encountered an issue: {msg}*[/italic dim]\n")
