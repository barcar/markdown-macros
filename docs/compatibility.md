# Compatibility with MkDocs Macros

Markdown Macros aims for **API and option compatibility** with the [MkDocs Macros plugin](https://mkdocs-macros-plugin.readthedocs.io/en/latest/) (variables, macros, filters, `define_env(env)`, and most configuration options), so that the same module and page patterns work in both. It is **not** a full feature-for-feature clone, because it is a **Python-Markdown extension**, not an MkDocs plugin.

## Markdown syntax processing

Processing order matches the plugin:

1. **Front matter** is parsed first (YAML between `---` … `---`). Keys become template variables; the block is stripped from the document.
2. **Jinja2** runs on the **body** only (the rest of the page). Variables, macros, filters, `{% set %}`, `{% if %}`, `{% for %}`, `{% include %}`, etc. behave the same.
3. The **result** is plain Markdown, which is then passed to the rest of the Python-Markdown pipeline (and on to HTML).

So the **markdown syntax processing is compatible**: the same page content (front matter + body with Jinja2) produces the same expanded Markdown. The plugin’s only exception is the **YAML `title` field**: it allows Jinja2 in `title` (e.g. `title: Description of {{ product_name }}`). This extension supports that too: if the front matter `title` value contains `{{` or `{%`, it is rendered with the same Jinja2 context before the body is rendered. Other YAML keys are **not** templated (literals only), same as the plugin.

## What is compatible

| Feature | MkDocs Macros | Markdown Macros |
|--------|----------------|------------------|
| **Jinja2 on Markdown** | ✓ | ✓ |
| **Variables** from config | `extra` in mkdocs.yml | `variables` in extension config |
| **Variables** from YAML files | `include_yaml` | ✓ `include_yaml` (list or key→path dict) |
| **Variables** from Python module | `define_env(env)` → `env.variables` | ✓ same |
| **Variables** from YAML header | ✓ | ✓ (front matter) |
| **Variables** from `{% set %}` in page | ✓ | ✓ (Jinja2) |
| **Macros** | `@env.macro` | ✓ same |
| **Filters** | `@env.filter` | ✓ same |
| **Custom Jinja2 delimiters** | `j2_*` options | ✓ `j2_block_*`, `j2_variable_*`, `j2_comment_*` |
| **Module** (e.g. `main.py`) | `module_name` | ✓ `module_name` + `project_root` |
| **Pluglets** | `modules` (list of package names) | ✓ `modules` |
| **include_dir** | Base dir for `{% include %}` | ✓ `include_dir` |
| **render_by_default** / **render_macros** | Opt-in per page | ✓ same |
| **on_error_fail** | Build fails on template error | ✓ same |
| **on_undefined** | `keep` / `strict` | ✓ same |
| **verbose** | Debug logging | ✓ same (logger `markdown_macros`) |
| **j2_extensions** | Jinja2 extensions list | ✓ same |

So for **typical use** and **advanced options**, the same `define_env(env)`, page syntax, and config options work.

## What is different (MkDocs-only)

These depend on MkDocs and cannot be provided by a Markdown extension:

| Feature | In MkDocs Macros | In Markdown Macros |
|--------|-------------------|---------------------|
| **env.conf** | MkDocs config (e.g. `site_name`) | ✗ not available |
| **env.config** | MkDocs global context | ✗ not available |
| **env.page** | Current page (title, url, etc.) | ✗ not available |
| **env.project_dir** | Docs directory | ✗ use `project_root` for paths only |
| **Hooks** `on_pre_page_macros`, `on_post_page_macros`, `on_post_build` | MkDocs events | ✗ no MkDocs events |

Page-level data in Markdown Macros comes only from **YAML front matter** and from **Jinja2** (`{% set %}`). There is no “current page” object.

## Summary

- **Implemented (MkDocs-Macros–style):** Jinja2 on pages; variables (config, include_yaml list or dict, module, pluglets, front matter, `{% set %}`); macros and filters; `define_env(env)`; one local module + pluglets; `include_dir`; `render_by_default` / `render_macros`; `on_error_fail`; `on_undefined`; `verbose`; `j2_comment_*`; `j2_extensions`.
- **Different by design:** No `env.conf`, `env.config`, `env.page`, or MkDocs hooks.

For Zensical or any Markdown-only pipeline, the extension is **highly compatible** with MkDocs Macros. For MkDocs with env.page, config, or event hooks, use the [MkDocs Macros plugin](https://mkdocs-macros-plugin.readthedocs.io/) itself.
