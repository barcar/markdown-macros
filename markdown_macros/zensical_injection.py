"""
Zensical compatibility shim.

Zensical parses YAML front matter into a local `meta` dict, strips the YAML
block from the markdown source, and then calls `md.convert(content)`.

Markdown Macros is a Python-Markdown extension running inside that `md`
pipeline, so it needs the parsed front matter to be available on the Markdown
instance (e.g. via `md.front_matter`) before `md.convert()` is called.

Since Zensical currently doesn't pass `meta` into the Markdown instance, we
install a small monkeypatch that wraps `zensical.markdown.render()` and injects
`meta` into `md.front_matter` before calling `md.convert()`.
"""

from __future__ import annotations

from typing import Any


def install_zensical_front_matter_injection() -> bool:
    """
    Monkeypatch `zensical.markdown.render()` to set `md.front_matter = meta`.

    Returns:
        True if the patch was installed (or already installed), else False.
    """

    try:
        import zensical.markdown as zmd
    except Exception:
        return False

    # Avoid double-installing if the extension is imported multiple times.
    if getattr(zmd.render, "_markdown_macros_front_matter_patched", False):
        return True

    try:
        import yaml
        from datetime import date, datetime
        from yaml import SafeLoader

        from markdown import Markdown
        from zensical.compat.autorefs import set_autorefs_page
        from zensical.config import get_config
        from zensical.extensions.links import LinksExtension
        from zensical.extensions.search import SearchExtension
    except Exception:
        return False

    def render(content: str, path: str, url: str) -> dict[str, Any]:
        config = get_config()

        set_autorefs_page(url, path)

        # Initialize Markdown parser
        md = Markdown(
            extensions=config["markdown_extensions"],
            extension_configs=config["mdx_configs"],
        )

        # Register links extension, equivalent to MkDocs' path resolution
        links = LinksExtension(
            use_directory_urls=config["use_directory_urls"], path=path
        )
        links.extendMarkdown(md)

        # Register search extension (extracts text for search indexing)
        search_extension = SearchExtension()
        search_extension.extendMarkdown(md)

        # Extract metadata; Zensical uses YAML because Python-Markdown's metadata
        # parsing is broken/limited in the upstream implementation.
        meta: dict[str, Any] = {}
        if match := zmd.FRONT_MATTER_RE.match(content):
            try:
                loaded = yaml.load(match.group(1), SafeLoader)
                if isinstance(loaded, dict):
                    meta = loaded
                    content = content[match.end() :].lstrip("\n")
                else:
                    meta = {}
            except Exception:  # noqa: BLE001
                meta = {}

        # Inject parsed front matter into the Python-Markdown instance.
        # Our extension can then read `md.front_matter` when it runs.
        md.front_matter = meta if isinstance(meta, dict) else {}

        # Convert Markdown and set nullish metadata to empty string.
        rendered_content = md.convert(content)
        for key, value in meta.items():
            if value is None:
                meta[key] = ""

            # Convert datetime back to ISO format (for now)
            if isinstance(value, (date, datetime)):
                meta[key] = value.isoformat()

        # Obtain search index data, unless page is excluded.
        search_processor = md.postprocessors["search"]
        if meta.get("search", {}).get("exclude", False):
            search_processor.data = []

        return {
            "meta": meta,
            "content": rendered_content,
            "search": search_processor.data,
            "title": "",
            "toc": [zmd._convert_toc(item) for item in getattr(md, "toc_tokens", [])],
        }

    render._markdown_macros_front_matter_patched = True  # type: ignore[attr-defined]

    zmd.render = render
    return True

