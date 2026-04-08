"""replaceRegex post-processing for legado rules (SRC-06)."""
from __future__ import annotations

import re


def apply_replace_regex(text: str, replace_regex: str | None) -> str:
    """Apply a legado replaceRegex chain to text.

    Format: ##pattern1##replacement1##pattern2##replacement2...
    An empty replacement string deletes matched text.
    Returns original text unchanged if replace_regex is empty or None.

    Examples:
        apply_replace_regex('hello   world', '##\\s+## ##') -> 'hello world'
        apply_replace_regex('hello<br>world', '##<br>####')  -> 'helloworld'
    """
    if not replace_regex:
        return text

    parts = replace_regex.split('##')
    # If rule starts with '##', first element is '' — skip it
    if parts and parts[0] == '':
        parts = parts[1:]

    i = 0
    while i + 1 < len(parts):
        pattern = parts[i]
        replacement = parts[i + 1]
        text = re.sub(pattern, replacement, text)
        i += 2

    return text
