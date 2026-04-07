"""Book source JSON parser and validator for legado format."""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS: tuple[str, ...] = ('bookSourceUrl', 'bookSourceName')


def load_book_source(path: str | Path) -> dict:
    """Load a legado book source JSON file.

    Accepts either a single source object (dict) or an array of source objects.
    Returns a single source dict (first item if array input).

    Raises:
        ValueError: if the file is empty array, wrong type, or missing required fields.
        json.JSONDecodeError: if the file is not valid JSON.
        OSError: if the file cannot be read.
    """
    text = Path(path).read_text(encoding='utf-8')
    data = json.loads(text)

    if isinstance(data, list):
        if not data:
            raise ValueError('Book source array is empty')
        source = data[0]
    elif isinstance(data, dict):
        source = data
    else:
        raise ValueError(f'Expected dict or list, got {type(data).__name__}')

    for field in REQUIRED_FIELDS:
        if field not in source:
            raise ValueError(f'Missing required field: {field!r}')

    return source
