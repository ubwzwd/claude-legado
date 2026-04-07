"""Streaming display engine for claude-legado.

Renders novel chapters as convincing Claude-like output:
- Fake reasoning preamble
- Chapter header via Rich
- Character-by-character streaming with variable delays and burst chunks
- Navigation hints via Rich
"""
from __future__ import annotations

import random
import sys
import time

from rich.console import Console

PAUSE_LONG = 0.15    # sentence-end: 。！？
PAUSE_MED = 0.06     # clause-end: ，、；
DELAY_MIN = 0.015    # 15ms base min
DELAY_MAX = 0.040    # 40ms base max
BURST_PROB = 0.15    # 15% chance of burst
BURST_MIN = 8
BURST_MAX = 15


def _char_delay(ch: str) -> float:
    """Return delay in seconds for a given character."""
    if ch in '。！？':
        return PAUSE_LONG
    if ch in '，、；':
        return PAUSE_MED
    return random.uniform(DELAY_MIN, DELAY_MAX)


def stream_text(text: str) -> None:
    """Stream text to stdout character-by-character with variable delays.

    Uses sys.stdout.write + flush (not print or Rich Console) for precise
    character-level control. Occasionally emits burst chunks to mimic
    Claude's response cadence.
    """
    i = 0
    while i < len(text):
        # Burst chunk: 15% chance if enough characters remain
        if (
            random.random() < BURST_PROB
            and i + BURST_MIN < len(text)
        ):
            chunk_size = random.randint(BURST_MIN, BURST_MAX)
            chunk_size = min(chunk_size, len(text) - i)
            sys.stdout.write(text[i:i + chunk_size])
            sys.stdout.flush()
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            i += chunk_size
        else:
            ch = text[i]
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(_char_delay(ch))
            i += 1
    sys.stdout.write('\n')
    sys.stdout.flush()


def print_reasoning_preamble() -> None:
    """Print a fake Claude-style reasoning preamble."""
    console = Console(markup=True, highlight=False)
    console.print("[italic dim]*Analyzing the request and preparing response...*[/italic dim]\n")


def print_chapter_header(chapter_num: int, title: str) -> None:
    """Print a bold chapter header."""
    console = Console(markup=True, highlight=False)
    console.print(f"\n[bold]第{chapter_num}章  {title}[/bold]\n")


def print_nav_hints(chapter_index: int, total: int) -> None:
    """Print navigation hints after chapter content."""
    console = Console(markup=True, highlight=False)
    hints = []
    if chapter_index < total - 1:
        hints.append("[dim]/novel next[/dim] -- 下一章")
    if chapter_index > 0:
        hints.append("[dim]/novel prev[/dim] -- 上一章")
    hints.append("[dim]/novel toc[/dim] -- 目录")
    console.print("\n  " + "   |   ".join(hints))


def stream_chapter(
    chapter_num: int,
    title: str,
    content: str,
    chapter_index: int,
    total: int,
) -> None:
    """Stream a full chapter with preamble, header, content, and nav hints.

    This is the main entry point used by commands.py.
    """
    print_reasoning_preamble()
    print_chapter_header(chapter_num, title)
    stream_text(content)
    print_nav_hints(chapter_index, total)
