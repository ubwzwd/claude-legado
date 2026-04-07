"""Tests for novel.state persistence layer (Plan 03)."""
from __future__ import annotations

import json
import pathlib

import pytest


def test_ensure_dirs_creates_state_dir(tmp_state_dir):
    """ensure_dirs() creates STATE_DIR when it does not exist."""
    import novel.state as state_mod
    subdir = tmp_state_dir / 'subtest'
    state_mod.STATE_DIR = subdir
    state_mod.STATE_FILE = subdir / 'state.json'
    state_mod.SHELF_FILE = subdir / 'shelf.json'
    state_mod.SOURCES_DIR = subdir / 'sources'

    assert not subdir.exists()
    state_mod.ensure_dirs()
    assert subdir.is_dir()


def test_ensure_dirs_creates_sources_dir(tmp_state_dir):
    """ensure_dirs() creates SOURCES_DIR (a subdirectory) when it does not exist."""
    import novel.state as state_mod
    sources = tmp_state_dir / 'sources'
    assert not sources.exists()
    state_mod.ensure_dirs()
    assert sources.is_dir()


def test_save_state_writes_valid_json(tmp_state_dir):
    """save_state writes a valid JSON file that can be read back and parsed."""
    import novel.state as state_mod
    data = {'current_book': 'Test Book', 'chapter_index': 2, 'source': 'builtin'}
    state_mod.save_state(data)
    raw = state_mod.STATE_FILE.read_text(encoding='utf-8')
    parsed = json.loads(raw)
    assert parsed == data


def test_load_state_returns_default_when_no_file(tmp_state_dir):
    """load_state returns DEFAULT_STATE when no state.json exists."""
    import novel.state as state_mod
    assert not state_mod.STATE_FILE.exists()
    result = state_mod.load_state()
    assert result == state_mod.DEFAULT_STATE


def test_load_state_returns_saved_data(tmp_state_dir):
    """load_state returns the previously saved data after save_state."""
    import novel.state as state_mod
    data = {'current_book': 'My Novel', 'chapter_index': 5, 'source': 'builtin'}
    state_mod.save_state(data)
    result = state_mod.load_state()
    assert result == data


def test_load_state_returns_default_on_invalid_json(tmp_state_dir):
    """load_state returns DEFAULT_STATE when state.json contains invalid JSON."""
    import novel.state as state_mod
    state_mod.STATE_FILE.write_text('not valid json!!!', encoding='utf-8')
    result = state_mod.load_state()
    assert result == state_mod.DEFAULT_STATE


def test_save_state_atomic_write_no_tmp_remaining(tmp_state_dir):
    """save_state uses atomic write: no .tmp file remains after completion."""
    import novel.state as state_mod
    data = {'current_book': None, 'chapter_index': 0, 'source': None}
    state_mod.save_state(data)
    tmp_file = state_mod.STATE_FILE.with_suffix('.tmp')
    assert not tmp_file.exists(), ".tmp file should not remain after atomic rename"
    assert state_mod.STATE_FILE.exists(), "state.json should exist after save"


def test_shelf_json_initialized_empty_list(tmp_state_dir):
    """shelf.json is accessible as an empty list via load_shelf when missing."""
    import novel.state as state_mod
    assert not state_mod.SHELF_FILE.exists()
    result = state_mod.load_shelf()
    assert result == []


def test_sources_dir_is_directory(tmp_state_dir):
    """SOURCES_DIR is created as a directory by ensure_dirs."""
    import novel.state as state_mod
    state_mod.ensure_dirs()
    assert state_mod.SOURCES_DIR.is_dir()
