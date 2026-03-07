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

from markdown import Extension
from markdown.preprocessors import Preprocessor

from markdown_macros.utils import FRONT_MATTER_RE, meta_from_dict

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


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
        self.md.Meta.update(meta_from_dict(data))
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
