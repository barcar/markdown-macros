"""
Shared utilities for front matter and macros extensions.
"""

import re

# Match --- at start of document, then content until next --- (YAML-style front matter)
FRONT_MATTER_RE = re.compile(
    r"^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n",
    re.MULTILINE,
)


def meta_from_dict(data):
    """Convert parsed YAML dict to Python-Markdown Meta format: lowercase keys, list values."""
    meta = {}
    if not isinstance(data, dict):
        return meta
    for key, value in data.items():
        k = key.lower().strip()
        if isinstance(value, list):
            meta[k] = [str(v) for v in value]
        elif value is None:
            meta[k] = [""]
        else:
            meta[k] = [str(value)]
    return meta
