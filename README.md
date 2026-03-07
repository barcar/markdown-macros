# Markdown Macros

[![Deploy docs to GitHub Pages](https://github.com/barcar/markdown-macros/actions/workflows/pages.yml/badge.svg)](https://github.com/barcar/markdown-macros/actions/workflows/pages.yml)

**Author:** [BarCar](https://github.com/barcar) · **Repository:** [github.com/barcar/markdown-macros](https://github.com/barcar/markdown-macros)

A **Python-Markdown extension** that brings [MkDocs Macros](https://mkdocs-macros-plugin.readthedocs.io/)–style **Jinja2 templating** to any Markdown pipeline: variables (config + YAML front matter), **macros**, and **filters**. Works with [Zensical](https://zensical.org), MkDocs, or plain Python—without the MkDocs plugin.

## Features

- **Variables** from config, YAML front matter, or `include_yaml`
- **Macros and filters** via `define_env(env)` in a Python module (same API as MkDocs Macros)
- **YAML front matter** parsed and exposed as `md.Meta` / `md.front_matter`

## Installation

```bash
pip install markdown-macros-extension
```

Requires: `markdown>=3.4`, `pyyaml>=6.0`, `jinja2>=3.0`.

## Quick example

```python
import markdown
from markdown_macros import MacrosExtension

text = """---
title: My Page
---

# {{ title }}

The answer is {{ 6 * 7 }}.
"""
md = markdown.Markdown(extensions=[MacrosExtension()])
html = md.convert(text)  # title and 42 rendered
```

In Zensical or MkDocs, add `markdown_macros` to your Markdown extensions and optionally set `module_name`, `variables`, `include_yaml`, etc. See the [documentation](https://barcar.github.io/markdown-macros/) for configuration, usage, and the full API.

**Compatibility:** API-aligned with the [MkDocs Macros plugin](https://mkdocs-macros-plugin.readthedocs.io/) (variables, macros, filters, `define_env`); see [Compatibility](https://barcar.github.io/markdown-macros/compatibility/) in the docs.

## Documentation

**Online:** [Documentation](https://barcar.github.io/markdown-macros/) (GitHub Pages).

To build the docs locally:

```bash
pip install -e ".[docs]"
zensical serve
```

## License

MIT License. See [LICENSE](LICENSE).
