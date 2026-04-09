"""Tests for /novel use command — source loading and persistence."""
from __future__ import annotations

import json

import pytest


@pytest.fixture
def tmp_state(tmp_path, monkeypatch):
    """Redirect all novel.state paths to tmp_path for isolation."""
    import novel.state as state_mod
    import novel.commands as cmd_mod

    state_dir = tmp_path / 'claude-legado'
    state_dir.mkdir()
    sources_dir = state_dir / 'sources'
    sources_dir.mkdir()

    monkeypatch.setattr(state_mod, 'STATE_DIR', state_dir)
    monkeypatch.setattr(state_mod, 'STATE_FILE', state_dir / 'state.json')
    monkeypatch.setattr(state_mod, 'SHELF_FILE', state_dir / 'shelf.json')
    monkeypatch.setattr(state_mod, 'SOURCES_DIR', sources_dir)
    # Also patch the imported reference in commands.py
    monkeypatch.setattr(cmd_mod, 'SOURCES_DIR', sources_dir)

    return {'state_dir': state_dir, 'sources_dir': sources_dir}


@pytest.fixture
def source_file(tmp_path):
    """Create a minimal valid source JSON file."""
    data = {
        'bookSourceUrl': 'https://example.com',
        'bookSourceName': 'Test Source',
        'ruleSearch': {'bookList': 'css:.book'},
        'ruleToc': {'chapterList': 'css:.chapter'},
    }
    path = tmp_path / 'test_source.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


def test_use_loads_and_persists_source(tmp_state, source_file):
    """_use_source() copies source to SOURCES_DIR and sets state['source']."""
    from novel.commands import _use_source
    import novel.state as state_mod

    _use_source([str(source_file)])

    # File copied to sources dir
    dest = tmp_state['sources_dir'] / source_file.name
    assert dest.exists()

    # State updated with source path as string
    state = state_mod.load_state()
    assert state['source'] == str(dest)


def test_use_prints_summary(tmp_state, source_file, capsys):
    """_use_source() prints source name, URL, and rule field presence."""
    from novel.commands import _use_source

    _use_source([str(source_file)])

    output = capsys.readouterr().out
    assert 'Test Source' in output
    assert 'https://example.com' in output
    assert 'ruleSearch' in output
    assert 'ruleToc' in output


def test_use_no_args(capsys):
    """_use_source([]) prints usage message."""
    from novel.commands import _use_source

    _use_source([])

    output = capsys.readouterr().out
    assert 'Usage' in output


def test_use_invalid_file(tmp_state, capsys):
    """_use_source(['nonexistent.json']) prints error, does not crash."""
    from novel.commands import _use_source

    _use_source(['nonexistent.json'])

    output = capsys.readouterr().out
    assert output.strip()  # Something was printed (error message)


def test_use_path_traversal_safe(tmp_state, tmp_path):
    """Source file at any path copies as basename only to SOURCES_DIR."""
    import novel.state as state_mod

    # Create source in a nested directory
    nested = tmp_path / 'deep' / 'nested'
    nested.mkdir(parents=True)
    data = {
        'bookSourceUrl': 'https://evil.com',
        'bookSourceName': 'Evil Source',
    }
    evil_path = nested / 'evil.json'
    evil_path.write_text(json.dumps(data), encoding='utf-8')

    from novel.commands import _use_source
    _use_source([str(evil_path)])

    # File should be copied as just 'evil.json' inside SOURCES_DIR
    dest = tmp_state['sources_dir'] / 'evil.json'
    assert dest.exists()

    # No path traversal — only basename used
    state = state_mod.load_state()
    assert state['source'] == str(dest)
    assert '..' not in state['source']
