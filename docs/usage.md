# Usage

How to use Markdown Macros in different environments.

## Zensical

[Zensical](https://zensical.org) uses Python-Markdown under the hood. Add the extension in `zensical.toml`:

```toml
[project]
site_name = "My Site"

[project.markdown_extensions.markdown_macros]
module_name = "main"
variables = { unit_price = 10 }
```

If you define a custom `markdown_extensions` list, include `markdown_macros` in it; Zensical does not add it by default.

Your `main.py` (or the module name you set) should live in the project root (next to `zensical.toml`). Use `project_root` if your config or module is elsewhere. For opt-in rendering (only render when front matter has `render_macros: true`), set `render_by_default = false`. For `{% include 'snippet.md' %}`, set `include_dir = "snippets"` (or another directory relative to `project_root`).

## MkDocs

Add the extension under `markdown_extensions` in `mkdocs.yml` (not under `plugins`):

```yaml
markdown_extensions:
  - markdown_macros:
      module_name: main
      variables:
        unit_price: 10
      include_yaml:
        - data/vars.yaml
```

Place `main.py` in the project root (next to `mkdocs.yml`). The extension runs during Markdown conversion; it does not replace the MkDocs Macros **plugin**. If you use both, the plugin runs in the MkDocs layer and this extension in the Markdown layer—you can use this extension in setups where the plugin is not available (e.g. Zensical).

## Plain Python

Use Python-Markdown and pass the extension by name or by class:

```python
import markdown
from markdown_macros import MacrosExtension

text = """---
title: My Page
---

# {{ title }}

The answer is {{ 6 * 7 }}.
"""

# By name (no options)
md = markdown.Markdown(extensions=["markdown_macros"])
html = md.convert(text)

# By class (with options)
md = markdown.Markdown(extensions=[
    MacrosExtension(
        variables={"unit_price": 10},
        module_name="main",
        project_root="/path/to/project",
    )
])
html = md.convert(text)

# Access front matter after conversion
print(md.Meta)
print(md.front_matter)
```

After conversion, `md.Meta` holds the front matter in Python-Markdown’s format (lowercase keys, list values), and `md.front_matter` holds the raw parsed YAML dict.

## Front matter only

If you don’t need Jinja2 and only want YAML front matter parsed and exposed:

```python
from markdown_macros import FrontMatterExtension

md = markdown.Markdown(extensions=[FrontMatterExtension()])
html = md.convert(text)
# md.Meta, md.front_matter are set; no template rendering
```

In config, use the full module path:

```yaml
# mkdocs.yml
markdown_extensions:
  - markdown_macros.front_matter:FrontMatterExtension
```
