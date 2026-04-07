"""State and shelf persistence with atomic write for claude-legado."""
from __future__ import annotations

import json
import pathlib

STATE_DIR: pathlib.Path = pathlib.Path.home() / '.claude-legado'
STATE_FILE: pathlib.Path = STATE_DIR / 'state.json'
SHELF_FILE: pathlib.Path = STATE_DIR / 'shelf.json'
SOURCES_DIR: pathlib.Path = STATE_DIR / 'sources'

DEFAULT_STATE: dict = {
    'current_book': None,
    'chapter_index': 0,
    'source': None,
}


def ensure_dirs() -> None:
    """Create STATE_DIR and SOURCES_DIR if they do not exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    """Load state from STATE_FILE. Returns DEFAULT_STATE on missing or corrupt file."""
    ensure_dirs()
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_STATE)


def save_state(state: dict) -> None:
    """Atomically write state dict to STATE_FILE (tmp + rename)."""
    ensure_dirs()
    tmp = STATE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(STATE_FILE)


def load_shelf() -> list:
    """Load shelf from SHELF_FILE. Returns empty list on missing or corrupt file."""
    ensure_dirs()
    if not SHELF_FILE.exists():
        return []
    try:
        return json.loads(SHELF_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return []


def save_shelf(shelf: list) -> None:
    """Atomically write shelf list to SHELF_FILE (tmp + rename)."""
    ensure_dirs()
    tmp = SHELF_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(shelf, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(SHELF_FILE)
