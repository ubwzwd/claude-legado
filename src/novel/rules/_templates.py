"""URL template substitution for legado rule templates (SRC-10)."""
from __future__ import annotations

import re


def apply_url_template(template: str, params: dict) -> str:
    """Replace {{key}} placeholders in a URL template string.

    Unknown keys (not present in params) are left unchanged as '{{key}'.
    Values are converted to str via str().

    Examples:
        apply_url_template('https://example.com/search?q={{searchKey}}&p={{page}}',
                           {'searchKey': '斗破苍穹', 'page': 1})
        -> 'https://example.com/search?q=斗破苍穹&p=1'

        apply_url_template('https://example.com/{{unknown}}', {})
        -> 'https://example.com/{{unknown}}'
    """
    def replace(m: re.Match) -> str:
        key = m.group(1)
        return str(params[key]) if key in params else m.group(0)

    return re.sub(r'\{\{(\w+)\}\}', replace, template)
