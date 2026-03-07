# Markdown Macros

**A Python-Markdown extension that brings MkDocs-Macros–style Jinja2 templating to any Markdown pipeline.**

Markdown Macros is a [Python-Markdown](https://python-markdown.github.io/) extension. It treats Markdown pages as **Jinja2 templates**, so you can use **variables**, **macros** (callable functions), and **filters** in your content. It works with [Zensical](https://zensical.org), MkDocs, or any tool that uses Python-Markdown—without requiring the MkDocs Macros *plugin*.

## Getting started

### Definition

Markdown Macros does one thing:

**Transform the Markdown source with Jinja2** before the rest of the pipeline runs:

- Use **variables** from configuration, YAML front matter, or external YAML files.
- Call **macros** (Python functions) from your templates.
- Use **filters** to format or transform values.

The result is plain Markdown, which is then converted to HTML as usual.

### Simple example

A Markdown page can contain a variable:

```markdown
The unit price of our product is {{ unit_price }} EUR.
```

In your config (e.g. Zensical or MkDocs), set the variable and enable the extension:

```toml
# zensical.toml
[project.markdown_extensions.markdown_macros]
variables = { unit_price = 10 }
```

Or in Python:

```python
md = markdown.Markdown(extensions=[
    MacrosExtension(variables={"unit_price": 10})
])
html = md.convert(text)
```

The page is rendered as:

```markdown
The unit price of our product is 10 EUR.
```

Markdown then converts that to HTML as usual.

### Full example

Use a variable and a **macro** (function) in the page:

```markdown
---
units: 50
---

The unit price is {{ unit_price }} EUR.
The sale price of {{ units }} units is {{ price(unit_price, units) }} EUR.
```

Define the macro in a Python module (`main.py`):

```python
def define_env(env):
    env.variables["unit_price"] = 10

    @env.macro
    def price(unit_price, no):
        return unit_price * no
```

Enable the extension with `module_name="main"`. The page becomes:

```markdown
The unit price is 10 EUR.
The sale price of 50 units is 500 EUR.
```

### Variables

Variables are available in templates as `{{ name }}`. They can come from:

| Source | Scope | How |
|--------|--------|-----|
| **Extension config** | Global | `variables` option in your Markdown extension config |
| **YAML files** | Global | `include_yaml` option (list of file paths) |
| **Python module** | Global | `define_env(env)` in your module: `env.variables["key"] = value` |
| **YAML front matter** | Page | `---` … `---` block at the top of the page |
| **Template** | Page | `{% set variable = value %}` in the page |

Page-level (front matter, `{% set %}`) overrides global variables.

### Create your own macros and filters

**Macros** are Python functions you call in the template, e.g. `{{ price(10, 5) }}`.

**Filters** transform a value with the pipe syntax, e.g. `{{ text \| upper }}`.

Create a module (e.g. `main.py`) with a `define_env(env)` function and register them:

```python
def define_env(env):
    @env.macro
    def greeting(name):
        return f"Hello, {name}!"

    @env.filter
    def double(n):
        return 2 * (int(n) if isinstance(n, str) and n.isdigit() else n)
```

Then in Markdown:

```markdown
{{ greeting("World") }}
{{ 21 | double }} is 42.
```

See [Writing modules](writing-modules.md) for the full API.

## What Markdown Macros is not

- **Not an MkDocs plugin** – It is a Python-Markdown extension. You add it under `markdown_extensions`, not under `plugins`. It works with MkDocs, Zensical, or any Markdown-based stack.
- **Not for HTML themes** – The Jinja2 in Markdown Macros runs on the **Markdown content** only. Theme or site-level Jinja2 (e.g. MkDocs theme templates) is separate.

## Compatibility

The extension is **highly compatible** with the [MkDocs Macros plugin](https://mkdocs-macros-plugin.readthedocs.io/en/latest/): same API (variables, macros, filters, `define_env(env)`), same options (pluglets, include_dir, render_by_default, on_error_fail, on_undefined, etc.). Only MkDocs-specific features (e.g. `env.page`, `env.conf`, MkDocs hooks) are unavailable. See [Compatibility with MkDocs Macros](compatibility.md) for details.

## Next steps

- [Installation](installation.md) – Install and enable the extension
- [Configuration](configuration.md) – All extension options
- [Writing modules](writing-modules.md) – `define_env(env)` in detail
- [Usage](usage.md) – Zensical, MkDocs, and plain Python
