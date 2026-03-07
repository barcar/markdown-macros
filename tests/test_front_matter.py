"""Tests for the Front Matter extension."""

import markdown
from markdown_macros import FrontMatterExtension


def test_parses_yaml_front_matter():
    text = """---
title: My Page
description: A short summary
tags:
  - blog
  - docs
---

# Hello

Content here.
"""
    md = markdown.Markdown(extensions=[FrontMatterExtension()])
    html = md.convert(text)

    assert "title" in md.Meta
    assert md.Meta["title"] == ["My Page"]
    assert md.Meta["description"] == ["A short summary"]
    assert md.Meta["tags"] == ["blog", "docs"]

    assert md.front_matter["title"] == "My Page"
    assert md.front_matter["description"] == "A short summary"
    assert md.front_matter["tags"] == ["blog", "docs"]

    assert "<h1>Hello</h1>" in html
    assert "---" not in html
    assert "title:" not in html


def test_no_front_matter():
    text = "# No front matter\n\nJust content."
    md = markdown.Markdown(extensions=[FrontMatterExtension()])
    html = md.convert(text)

    assert getattr(md, "Meta", {}) == {} or md.Meta == {}
    assert getattr(md, "front_matter", {}) == {} or md.front_matter == {}
    assert "<h1>No front matter</h1>" in html


def test_front_matter_extension_alone_sets_meta_and_front_matter():
    """FrontMatterExtension only: no Jinja2; md.Meta and md.front_matter are set."""
    text = """---
title: Solo
count: 1
---

# Body
"""
    md = markdown.Markdown(extensions=[FrontMatterExtension()])
    html = md.convert(text)
    assert md.Meta.get("title") == ["Solo"]
    assert md.Meta.get("count") == ["1"]
    assert md.front_matter.get("title") == "Solo"
    assert md.front_matter.get("count") == 1
    assert "Body" in html


def test_extension_by_name():
    text = """---
key: value
---

Body.
"""
    html = markdown.markdown(text, extensions=["markdown_macros"])
    # Extension runs when loaded by name; we can't easily get md.Meta from markdown()
    # so just ensure no crash and body is present
    assert "Body" in html
