"""Tests for the Macros (Jinja2) extension."""

import markdown
from markdown_macros import MacrosExtension


def test_include_yaml_list(tmp_path):
    """Variables from include_yaml (list of paths) are in context."""
    vars_file = tmp_path / "vars.yaml"
    vars_file.write_text("from_yaml: loaded\nkey2: value2\n", encoding="utf-8")
    text = "Result: {{ from_yaml }} and {{ key2 }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                include_yaml=[str(vars_file)],
                project_root=str(tmp_path),
            )
        ]
    )
    html = md.convert(text)
    assert "loaded" in html
    assert "value2" in html


def test_include_yaml_dict(tmp_path):
    """Variables from include_yaml (dict key→path) are nested under key."""
    data_file = tmp_path / "data.yaml"
    data_file.write_text("nested: value\n", encoding="utf-8")
    text = "Result: {{ data.nested }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                include_yaml={"data": str(data_file)},
                project_root=str(tmp_path),
            )
        ]
    )
    html = md.convert(text)
    assert "value" in html


def test_front_matter_as_variables():
    text = """---
title: My Page
price: 42
---

# {{ title }}

Price is {{ price }}.
"""
    md = markdown.Markdown(extensions=[MacrosExtension()])
    html = md.convert(text)
    assert "My Page" in html
    assert "42" in html
    assert "{{" not in html
    assert md.front_matter["title"] == "My Page"
    assert md.front_matter["price"] == 42


def test_config_variables():
    text = "Unit price: {{ unit_price }}."
    md = markdown.Markdown(
        extensions=[MacrosExtension(variables={"unit_price": 10})]
    )
    html = md.convert(text)
    assert "10" in html
    assert "{{" not in html


def test_no_jinja2_leave_unchanged():
    text = "No variables here."
    md = markdown.Markdown(extensions=[MacrosExtension()])
    html = md.convert(text)
    assert "No variables here" in html


def test_render_by_default_false_skips_without_render_macros():
    text = """---
title: Page
---

# {{ title }}
"""
    md = markdown.Markdown(
        extensions=[MacrosExtension(render_by_default=False)]
    )
    html = md.convert(text)
    # Without render_macros: true, Jinja2 is skipped
    assert "{{ title }}" in html
    assert md.front_matter["title"] == "Page"


def test_render_by_default_false_renders_when_render_macros_true():
    text = """---
title: Page
render_macros: true
---

# {{ title }}
"""
    md = markdown.Markdown(
        extensions=[MacrosExtension(render_by_default=False)]
    )
    html = md.convert(text)
    assert "Page" in html
    assert "{{ title }}" not in html


def test_title_field_jinja2_expansion():
    """MkDocs Macros compatibility: title in front matter can contain Jinja2."""
    text = """---
title: Page for {{ product_name }}
product_name: Widget
---

# {{ title }}

Content.
"""
    md = markdown.Markdown(extensions=[MacrosExtension()])
    html = md.convert(text)
    assert "Page for Widget" in html
    assert md.front_matter["title"] == "Page for Widget"
    assert "{{" not in html


def test_on_undefined_strict_raises():
    import pytest
    text = "Hello {{ missing }}"
    # on_error_fail=True so the UndefinedError propagates
    md = markdown.Markdown(
        extensions=[MacrosExtension(on_undefined="strict", on_error_fail=True)]
    )
    with pytest.raises(Exception):
        md.convert(text)
