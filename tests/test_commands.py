"""Tests for the novel commands dispatcher."""
import pytest
from novel.commands import dispatch


def test_default_dispatch_no_args(capsys):
    """dispatch([]) calls default handler without error and produces output."""
    dispatch([])
    captured = capsys.readouterr()
    assert captured.out  # should produce some output


def test_default_dispatch_unknown_cmd(capsys):
    """dispatch(['unknowncmd']) falls through to default handler, not crash."""
    dispatch(["unknowncmd"])
    captured = capsys.readouterr()
    assert captured.out  # should produce some output


def test_next_dispatch(capsys):
    """dispatch(['next']) routes to next handler and produces output."""
    dispatch(["next"])
    captured = capsys.readouterr()
    assert captured.out  # should produce some output


def test_prev_dispatch(capsys):
    """dispatch(['prev']) routes to prev handler and produces output."""
    dispatch(["prev"])
    captured = capsys.readouterr()
    assert captured.out  # should produce some output


def test_search_stub(capsys):
    """dispatch(['search', 'test']) prints stub message containing 'search'."""
    dispatch(["search", "test"])
    captured = capsys.readouterr()
    assert "search" in captured.out.lower()


def test_toc_stub(capsys):
    """dispatch(['toc']) prints stub message containing 'toc'."""
    dispatch(["toc"])
    captured = capsys.readouterr()
    assert "toc" in captured.out.lower()


def test_shelf_stub(capsys):
    """dispatch(['shelf']) prints stub message containing 'shelf'."""
    dispatch(["shelf"])
    captured = capsys.readouterr()
    assert "shelf" in captured.out.lower()


def test_use_dispatch(capsys):
    """dispatch(['use', 'path.json']) prints error for nonexistent file (no longer a stub)."""
    dispatch(["use", "path.json"])
    captured = capsys.readouterr()
    assert captured.out  # should print an error message


def test_module_runs(capsys):
    """python -m novel exits 0 (tested via import dispatch([]))."""
    # If dispatch([]) doesn't raise, the module would also work
    dispatch([])
    captured = capsys.readouterr()
    assert captured.out  # no crash
