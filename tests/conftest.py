import pathlib
import pytest


@pytest.fixture
def tmp_state_dir(tmp_path):
    """Override STATE_DIR to a temp directory for test isolation."""
    try:
        import novel.state as state_mod
        original = state_mod.STATE_DIR
        state_mod.STATE_DIR = tmp_path
        state_mod.STATE_FILE = tmp_path / 'state.json'
        state_mod.SHELF_FILE = tmp_path / 'shelf.json'
        state_mod.SOURCES_DIR = tmp_path / 'sources'
        yield tmp_path
        state_mod.STATE_DIR = original
        state_mod.STATE_FILE = original / 'state.json'
        state_mod.SHELF_FILE = original / 'shelf.json'
        state_mod.SOURCES_DIR = original / 'sources'
    except ImportError:
        # novel.state does not exist yet (Plans 03+), just yield tmp_path
        yield tmp_path
