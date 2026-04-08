"""Tests for replaceRegex post-processing (SRC-06)."""
from __future__ import annotations

import pytest


def test_single_pair():
    """##\\s+## ## collapses whitespace to single space."""
    from novel.rules._regex import apply_replace_regex
    result = apply_replace_regex('hello   world', '##\\s+## ##')
    assert result == 'hello world'


def test_chained():
    """Two chained replace pairs both apply in sequence."""
    from novel.rules._regex import apply_replace_regex
    result = apply_replace_regex('abc123def', '##[0-9]+####[a-z]+##X##')
    assert result == 'X'


def test_delete():
    """Empty replacement deletes matched text."""
    from novel.rules._regex import apply_replace_regex
    result = apply_replace_regex('hello<br>world', '##<br>####')
    assert result == 'helloworld'
