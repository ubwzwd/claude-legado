"""Tests for the streaming display engine (display.py)."""
from __future__ import annotations

import io
import sys

import pytest


def test_stream_text_writes_content_and_newline(monkeypatch):
    """stream_text('abc') writes 'abc' + newline to stdout."""
    import time
    monkeypatch.setattr(time, "sleep", lambda _: None)

    from novel.display import stream_text

    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    stream_text("abc")
    result = output.getvalue()
    assert "abc" in result
    assert result.endswith("\n")


def test_char_delay_normal_range():
    """_char_delay returns value in [0.015, 0.040] for normal characters."""
    from novel.display import _char_delay

    for ch in "普通字母abcABC123":
        delay = _char_delay(ch)
        assert 0.015 <= delay <= 0.040, f"Expected [0.015, 0.040] for '{ch}', got {delay}"


def test_char_delay_sentence_end_punctuation():
    """_char_delay returns 0.15 for sentence-ending punctuation 。！？."""
    from novel.display import _char_delay

    for ch in "。！？":
        delay = _char_delay(ch)
        assert delay == 0.15, f"Expected 0.15 for '{ch}', got {delay}"


def test_char_delay_clause_punctuation():
    """_char_delay returns 0.06 for clause punctuation ，、；."""
    from novel.display import _char_delay

    for ch in "，、；":
        delay = _char_delay(ch)
        assert delay == 0.06, f"Expected 0.06 for '{ch}', got {delay}"


def test_cjk_width():
    """CJK characters have double width via rich.cells.cell_len."""
    from rich.cells import cell_len

    assert cell_len("你") == 2
    assert cell_len("你好") == 4


def test_print_chapter_header_contains_title(monkeypatch, capsys):
    """print_chapter_header writes output containing the chapter title."""
    from novel.display import print_chapter_header

    print_chapter_header(1, "初入宗门")
    captured = capsys.readouterr()
    assert "初入宗门" in captured.out


def test_print_nav_hints_contains_next_command(monkeypatch, capsys):
    """print_nav_hints writes output containing '/novel next'."""
    from novel.display import print_nav_hints

    # chapter_index=0, total=3 — should have next but not prev
    print_nav_hints(0, 3)
    captured = capsys.readouterr()
    assert "/novel next" in captured.out


def test_print_reasoning_preamble_contains_text(monkeypatch, capsys):
    """print_reasoning_preamble writes output containing italicized preamble text."""
    from novel.display import print_reasoning_preamble

    print_reasoning_preamble()
    captured = capsys.readouterr()
    # The preamble should contain some indication of analyzing/preparing
    assert "Analyzing" in captured.out or "analyzing" in captured.out or "preparing" in captured.out
