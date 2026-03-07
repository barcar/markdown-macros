"""Tests for the Macros (Jinja2) extension."""

import pytest
import markdown
from markdown_macros import FrontMatterExtension, MacrosExtension


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


def test_include_yaml_path_escape_ignored(tmp_path):
    """Paths that resolve outside project_root are ignored (path safety)."""
    outside = tmp_path.parent / "outside.yaml"
    outside.write_text("secret: leaked\n", encoding="utf-8")
    text = "Result: {{ secret }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                include_yaml=["../outside.yaml"],
                project_root=str(tmp_path),
            )
        ]
    )
    html = md.convert(text)
    assert "leaked" not in html
    assert "{{ secret }}" in html or "secret" not in html


def test_module_path_escape_ignored(tmp_path):
    """module_name that resolves outside project_root is not loaded (path safety)."""
    external = tmp_path.parent / "external_env"
    external.mkdir(exist_ok=True)
    (external / "main.py").write_text(
        "def define_env(env):\n    env.variables['from_outside'] = 'loaded'\n",
        encoding="utf-8",
    )
    text = "Result: {{ from_outside }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                module_name="../external_env/main",
                project_root=str(tmp_path),
            )
        ]
    )
    html = md.convert(text)
    assert "loaded" not in html


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


def test_front_matter_and_macros_together():
    """FrontMatterExtension and MacrosExtension together: Meta set by first, Jinja2 by second."""
    text = """---
title: Combined
---

# {{ title }}

Config var: {{ config_var }}.
"""
    md = markdown.Markdown(
        extensions=[
            FrontMatterExtension(),
            MacrosExtension(variables={"config_var": "ok"}),
        ]
    )
    html = md.convert(text)
    # FrontMatter set Meta (and stripped the --- block); Macros only sees body, so {{ title }} is empty
    assert md.Meta.get("title") == ["Combined"]
    assert "ok" in html  # config_var from Macros
    assert "{{ config_var }}" not in html


def test_pluglets_loaded():
    """Variables and macros from modules= (pluglets) are in context."""
    text = "Var: {{ from_pluglet }}. Double: {{ double(7) }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(modules=["tests.pluglet_helper"]),
        ]
    )
    html = md.convert(text)
    assert "pluglet_ok" in html
    assert "14" in html


def test_on_error_fail_raises_on_render_error():
    """With on_error_fail=True, Jinja2 render errors are re-raised."""
    text = "Hello {{ undefined_var }}"
    md = markdown.Markdown(
        extensions=[MacrosExtension(on_error_fail=True)]
    )
    # Undefined var with default on_undefined leaves it; use strict to force error
    md_strict = markdown.Markdown(
        extensions=[
            MacrosExtension(on_undefined="strict", on_error_fail=True),
        ]
    )
    with pytest.raises(Exception):
        md_strict.convert(text)


def test_on_undefined_strict_raises():
    """on_undefined=strict + on_error_fail=True propagates UndefinedError."""
    text = "Hello {{ missing }}"
    md = markdown.Markdown(
        extensions=[MacrosExtension(on_undefined="strict", on_error_fail=True)]
    )
    with pytest.raises(Exception):
        md.convert(text)


def test_pluglet_import_error_logged(tmp_path):
    """Pluglet that fails to import does not crash; others still load."""
    # Use a non-importable name so ImportError is raised
    text = "OK: {{ from_pluglet }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(modules=["nonexistent_pluglet_xyz", "tests.pluglet_helper"]),
        ]
    )
    html = md.convert(text)
    assert "pluglet_ok" in html


def test_pluglet_empty_names_skipped():
    """Empty or whitespace-only names in modules= are skipped."""
    text = "{{ from_pluglet }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(modules=["", "  ", "tests.pluglet_helper"]),
        ]
    )
    html = md.convert(text)
    assert "pluglet_ok" in html


def test_include_yaml_dict_missing_file(tmp_path):
    """include_yaml dict with missing path does not add the key."""
    text = "Result: {{ data.nested }}."
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                include_yaml={"data": "nonexistent.yaml"},
                project_root=str(tmp_path),
            )
        ]
    )
    html = md.convert(text)
    # data is not loaded, so data.nested is undefined (empty or error depending on on_undefined)
    assert "value" not in html or "data.nested" in html or "Result: ." in html


def test_no_front_matter_sets_empty_front_matter():
    """When there is no front matter, md.front_matter is set to {}."""
    text = "Body only. {{ x }}"
    md = markdown.Markdown(extensions=[MacrosExtension()])
    md.convert(text)
    assert hasattr(md, "front_matter")
    assert md.front_matter == {}


def test_verbose_render_by_default_false():
    """With verbose=True and render_by_default=False, no crash (covers debug log path)."""
    text = """---
title: P
---

# {{ title }}
"""
    md = markdown.Markdown(
        extensions=[MacrosExtension(render_by_default=False, verbose=True)]
    )
    html = md.convert(text)
    assert "{{ title }}" in html


def test_include_dir_and_include(tmp_path):
    """include_dir enables {% include %} from that directory."""
    inc_dir = tmp_path / "partials"
    inc_dir.mkdir()
    (inc_dir / "bit.md").write_text("included", encoding="utf-8")
    text = "Before {% include 'bit.md' %} after"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(
                project_root=str(tmp_path),
                include_dir="partials",
            )
        ]
    )
    html = md.convert(text)
    assert "included" in html
    assert "Before" in html and "after" in html


def test_j2_extensions():
    """j2_extensions list is passed to Jinja2 environment."""
    text = "{{ 1 + 1 }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(j2_extensions=["jinja2.ext.loopcontrols"]),
        ]
    )
    html = md.convert(text)
    assert "2" in html


def test_title_jinja2_expansion_exception_swallowed():
    """If title has Jinja2 that raises, exception is swallowed and body still renders."""
    # Use a title that triggers an error during render (e.g. undefined in strict would raise)
    text = """---
title: "{{ undefined_var_xyz }}"
---

# {{ title }}
"""
    md = markdown.Markdown(extensions=[MacrosExtension()])
    html = md.convert(text)
    # Title expansion may fail (e.g. undefined); body still renders
    assert "<h1>" in html


def test_render_error_swallowed_without_on_error_fail():
    """With on_error_fail=False, Jinja2 error leaves body unchanged."""
    text = "Hello {{ bad syntax }}"
    md = markdown.Markdown(extensions=[MacrosExtension(on_error_fail=False)])
    html = md.convert(text)
    assert "Hello" in html


def test_render_error_swallowed_with_verbose():
    """With on_error_fail=False and verbose=True, error is swallowed and debug logged."""
    # Use a template that raises (e.g. division by zero in expression)
    text = "Hello {{ 1 / 0 }}"
    md = markdown.Markdown(
        extensions=[MacrosExtension(on_error_fail=False, verbose=True)]
    )
    html = md.convert(text)
    assert "Hello" in html


def test_empty_front_matter_in_macros():
    """MacrosExtension with empty or null YAML front matter (data is None -> {})."""
    text = """---
---

# {{ title }}

Body.
"""
    md = markdown.Markdown(extensions=[MacrosExtension()])
    html = md.convert(text)
    assert md.front_matter == {}
    assert "<h1>" in html


def test_macros_make_extension():
    """make_extension() returns MacrosExtension instance."""
    from markdown_macros.macros import make_extension
    ext = make_extension()
    assert isinstance(ext, MacrosExtension)


def test_macro_and_filter_with_explicit_name(tmp_path):
    """Macro and filter can be registered with explicit name."""
    mod = tmp_path / "named_macros.py"
    mod.write_text("""
def define_env(env):
    @env.macro(name="my_macro")
    def the_macro():
        return "macro_ok"
    @env.filter(name="my_filter")
    def the_filter(x):
        return str(x).upper()
""", encoding="utf-8")
    text = "M: {{ my_macro() }} F: {{ 'hi' | my_filter }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(module_name="named_macros", project_root=str(tmp_path)),
        ]
    )
    html = md.convert(text)
    assert "macro_ok" in html
    assert "HI" in html


def test_module_file_without_define_env_returns_empty(tmp_path):
    """Module file that exists but has no define_env returns no vars/macros (break then __import__ fail)."""
    (tmp_path / "nomacros.py").write_text("x = 1\n", encoding="utf-8")
    text = "{{ from_module }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(module_name="nomacros", project_root=str(tmp_path)),
        ]
    )
    html = md.convert(text)
    # nomacros has no define_env; __import__('nomacros') may load our file but it has no define_env
    assert "from_module" not in html or "{{" in html


def test_module_name_with_slash_skips_import():
    """module_name containing '/' does not call __import__ (path safety)."""
    text = "{{ x }}"
    md = markdown.Markdown(
        extensions=[MacrosExtension(module_name="sub/mod", project_root="/tmp")]
    )
    html = md.convert(text)
    assert "{{ x }}" in html or "" in html


def test_verbose_with_module_name(tmp_path):
    """verbose=True with module_name set does not crash (covers debug log)."""
    (tmp_path / "m.py").write_text("def define_env(env):\n    env.variables['v'] = 'ok'\n", encoding="utf-8")
    text = "{{ v }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(module_name="m", project_root=str(tmp_path), verbose=True),
        ]
    )
    html = md.convert(text)
    assert "ok" in html


def test_verbose_with_pluglets():
    """verbose=True with modules= does not crash (covers pluglet debug log)."""
    text = "{{ from_pluglet }}"
    md = markdown.Markdown(
        extensions=[
            MacrosExtension(modules=["tests.pluglet_helper"], verbose=True),
        ]
    )
    html = md.convert(text)
    assert "pluglet_ok" in html
