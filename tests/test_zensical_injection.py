from __future__ import annotations

import re
import sys
import types
from datetime import date

import pytest

from markdown_macros.zensical_injection import install_zensical_front_matter_injection


def _stub_zensical_modules(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    """
    Create a minimal fake `zensical` module hierarchy in `sys.modules`.

    The goal is to let `install_zensical_front_matter_injection()` import and
    patch `zensical.markdown.render()` without depending on Zensical internals.
    """

    # --- zensical.markdown
    zmarkdown = types.ModuleType("zensical.markdown")
    zmarkdown._patched = False

    # Copy Zensical's front matter regex shape (only needs to match our test input).
    zmarkdown.FRONT_MATTER_RE = re.compile(
        r"^-{3}[ \r\t]*?\n(.*?\r?\n)(?:\.{3}|-{3})[ \r\t]*\n",
        re.UNICODE | re.DOTALL,
    )

    def _convert_toc(item):  # noqa: ANN001 - test stub
        return {"id": str(item)}

    zmarkdown._convert_toc = _convert_toc

    def original_render(content: str, path: str, url: str):  # noqa: ARG001
        raise AssertionError("original_render should be replaced by the shim")

    zmarkdown.render = original_render

    # --- zensical.compat.autorefs
    zcompat = types.ModuleType("zensical.compat")
    autorefs = types.ModuleType("zensical.compat.autorefs")

    def set_autorefs_page(url: str, path: str):  # noqa: ARG001
        return None

    autorefs.set_autorefs_page = set_autorefs_page
    sys.modules["zensical.compat"] = zcompat
    sys.modules["zensical.compat.autorefs"] = autorefs

    # --- zensical.config
    zconfig = types.ModuleType("zensical.config")
    zconfig.get_config = lambda: {  # noqa: E731
        "markdown_extensions": [],
        "mdx_configs": {},
        "use_directory_urls": True,
    }

    sys.modules["zensical.config"] = zconfig

    # --- zensical.extensions.links
    zext = types.ModuleType("zensical.extensions")
    zlinks = types.ModuleType("zensical.extensions.links")

    class LinksExtension:  # noqa: D101 - test stub
        def __init__(self, use_directory_urls: bool, path: str):  # noqa: ARG002
            self.use_directory_urls = use_directory_urls
            self.path = path

        def extendMarkdown(self, md):  # noqa: N803 - matches API
            return None

    zlinks.LinksExtension = LinksExtension
    sys.modules["zensical.extensions"] = zext
    sys.modules["zensical.extensions.links"] = zlinks

    # --- zensical.extensions.search
    zsearch = types.ModuleType("zensical.extensions.search")

    from markdown.postprocessors import Postprocessor

    class SearchProcessor(Postprocessor):
        def __init__(self, md):  # noqa: ANN001
            super().__init__(md)
            self.data = [{"dummy": True}]

        def run(self, html: str) -> str:  # noqa: ANN001
            return html

    class SearchExtension:  # noqa: D101 - test stub
        def extendMarkdown(self, md):  # noqa: N803 - matches API
            md.postprocessors.register(SearchProcessor(md), "search", 0)

    zsearch.SearchExtension = SearchExtension
    sys.modules["zensical.extensions.search"] = zsearch

    # --- root module `zensical`
    zensical = types.ModuleType("zensical")
    sys.modules["zensical"] = zensical
    sys.modules["zensical.markdown"] = zmarkdown

    # Ensure our fake modules are returned / usable by imports.
    monkeypatch.setitem(sys.modules, "zensical", zensical)
    monkeypatch.setitem(sys.modules, "zensical.markdown", zmarkdown)

    return zmarkdown


def test_install_patches_render_and_injects_front_matter(monkeypatch: pytest.MonkeyPatch):
    zmarkdown = _stub_zensical_modules(monkeypatch)

    assert install_zensical_front_matter_injection() is True
    assert getattr(zmarkdown.render, "_markdown_macros_front_matter_patched", False) is True

    content = """---\nfoo: bar\ntitle: null\nwhen: 2020-01-01\nsearch:\n  exclude: true\n---\n\n# Heading\n"""
    res = zmarkdown.render(content, path="docs/x.md", url="https://example.com/x.html")

    # front matter extraction
    assert res["meta"]["foo"] == "bar"
    assert res["meta"]["title"] == ""

    # datetime conversion depends on PyYAML resolver, but it should at least serialize as ISO string
    assert isinstance(res["meta"]["when"], str)
    assert res["meta"]["search"]["exclude"] is True

    # wrapper forces search index to empty when excluded
    assert res["search"] == []


def test_install_is_idempotent(monkeypatch: pytest.MonkeyPatch):
    zmarkdown = _stub_zensical_modules(monkeypatch)

    assert install_zensical_front_matter_injection() is True
    first = zmarkdown.render

    assert install_zensical_front_matter_injection() is True
    assert zmarkdown.render is first


def test_render_handles_non_dict_front_matter(monkeypatch: pytest.MonkeyPatch):
    zmarkdown = _stub_zensical_modules(monkeypatch)
    assert install_zensical_front_matter_injection() is True

    # YAML scalar front matter -> meta should become {}
    content = """---\nhello\n---\n\n# Body\n"""
    res = zmarkdown.render(content, path="docs/x.md", url="https://example.com/x.html")
    assert res["meta"] == {}


def test_install_returns_false_if_zensical_markdown_import_fails(
    monkeypatch: pytest.MonkeyPatch,
):
    # Force `import zensical.markdown` to fail by making `zensical` a non-package.
    dummy_zensical = types.ModuleType("zensical")
    monkeypatch.setitem(sys.modules, "zensical", dummy_zensical)
    monkeypatch.delitem(sys.modules, "zensical.markdown", raising=False)

    assert install_zensical_front_matter_injection() is False


def test_install_returns_false_if_python_markdown_dependency_missing(
    monkeypatch: pytest.MonkeyPatch,
):
    _stub_zensical_modules(monkeypatch)

    # Make `from markdown import Markdown` fail by shadowing the module.
    dummy_markdown = types.ModuleType("markdown")
    monkeypatch.setitem(sys.modules, "markdown", dummy_markdown)

    assert install_zensical_front_matter_injection() is False


def test_render_handles_yaml_parse_error(monkeypatch: pytest.MonkeyPatch):
    zmarkdown = _stub_zensical_modules(monkeypatch)
    assert install_zensical_front_matter_injection() is True

    # Tabs are invalid indentation for YAML and should trigger a YAML parse error.
    content = """---\n\tbad: tab\n---\n\n# Body\n"""
    res = zmarkdown.render(content, path="docs/x.md", url="https://example.com/x.html")
    assert res["meta"] == {}

