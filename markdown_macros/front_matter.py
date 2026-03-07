"""
YAML Front Matter preprocessor for Python-Markdown.

Strips the leading --- YAML --- block from the source and stores parsed data
in md.Meta (Python-Markdown style: lowercase keys, list-of-strings values)
and md.front_matter (full parsed dict for nested structures).

Compatible with Zensical and MkDocs Macros: runs only at the Markdown layer;
no Jinja2 or plugin logic. When MkDocs Macros is used, it can consume
page-level metadata; this extension ensures front matter is available as md.Meta
for the rest of the pipeline.
"""

import re
from markdown import Extension
from markdown.preprocessors import Preprocessor

try:
    import yaml
except ImportError:
    yaml = None

# Match --- at start of document, then content until next --- (YAML style only for now)
FRONT_MATTER_RE = re.compile(
    r"^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n",
    re.MULTILINE,
)


def _meta_from_dict(data):
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


class FrontMatterPreprocessor(Preprocessor):
    """Preprocessor that strips YAML front matter and stores it on the Markdown instance."""

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, lines):
        text = "\n".join(lines)
        match = FRONT_MATTER_RE.match(text)
        if not match:
            # Ensure Meta and front_matter exist for downstream (e.g. themes, MkDocs)
            if not hasattr(self.md, "Meta") or self.md.Meta is None:
                self.md.Meta = {}
            if not hasattr(self.md, "front_matter") or self.md.front_matter is None:
                self.md.front_matter = {}
            return lines

        raw_block = match.group(1).strip()
        if yaml is not None:
            try:
                data = yaml.safe_load(raw_block)
                if data is None:
                    data = {}
                if not isinstance(data, dict):
                    data = {"content": data}
            except Exception:
                data = {}
        else:
            data = {}

        # Expose for Python-Markdown and downstream (e.g. MkDocs page.meta)
        self.md.Meta = getattr(self.md, "Meta", None) or {}
        self.md.Meta.update(_meta_from_dict(data))
        # Full structure for themes/plugins that expect nested data
        self.md.front_matter = data

        # Return remaining markdown (without the front matter block)
        rest = text[match.end() :]
        return rest.split("\n")


class FrontMatterExtension(Extension):
    """Python-Markdown extension that parses YAML front matter and exposes it as md.Meta and md.front_matter."""

    def __init__(self, **kwargs):
        # No config options; declare empty config so base Extension.setConfig behaves correctly.
        self.config = {}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(
            FrontMatterPreprocessor(md, self.getConfigs()),
            "front_matter",
            priority=25,  # Run early, before most other preprocessors (higher = first)
        )


def make_extension(**kwargs):
    return FrontMatterExtension(**kwargs)
