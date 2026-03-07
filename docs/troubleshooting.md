# Troubleshooting

## Trusted config

The extension loads Python code when you set `module_name` or `modules`: it imports and runs `define_env(env)` from those modules. Only use trusted project roots and module names. If your config (e.g. `zensical.toml` or `mkdocs.yml`) or the content of `main.py` / pluglets can be influenced by untrusted users, they could run arbitrary code. Same as with the MkDocs Macros plugin: treat config and macro modules as trusted.

## Variables or macros not replaced

**Symptom**: You see literal `{{ variable }}` or `{{ macro() }}` in the output.

**Causes**:

1. **Extension not enabled**  
   Ensure `markdown_macros` is in your `markdown_extensions` (Zensical, MkDocs) or in the `extensions` list when calling `markdown.Markdown()` or `markdown.markdown()`.

2. **Wrong extension**  
   You might have only `FrontMatterExtension` (front-matter-only). Jinja2 is handled by `MacrosExtension`. Loading by name as `markdown_macros` uses `MacrosExtension`; for front-matter only you must use `markdown_macros.front_matter:FrontMatterExtension`.

3. **Jinja2 not installed**  
   The macros extension requires `jinja2`. Install it: `pip install jinja2`.

4. **Template error**  
   If Jinja2 raises an exception (e.g. undefined variable, syntax error), the extension catches it and returns the **unchanged** body, so you see raw `{{ ... }}`. Check your build logs for tracebacks.

## Module or macros not found

**Symptom**: Variables from config or front matter work, but macros or variables from your module do not.

**Causes**:

1. **Wrong `project_root`**  
   The extension resolves `module_name` relative to `project_root` (default `"."`). If `main.py` is not under that directory, set `project_root` to the directory that contains `main.py`.

2. **Module has no `define_env`**  
   The module must define a function named exactly `define_env(env)`. If it’s missing or misspelled, the extension will not load any macros or variables from that module.

3. **Import error in module**  
   If importing or running the module fails (e.g. missing dependency), the extension falls back to no macros/filters from that module. Fix the import or run the module in isolation to see the error.

## Front matter not parsed

**Symptom**: `md.Meta` or `md.front_matter` is empty, or variables from the YAML block don’t work.

**Causes**:

1. **Invalid YAML**  
   The block must be valid YAML between the first two `---` lines. Check indentation and colons. If YAML parsing fails, the extension uses an empty dict.

2. **Delimiters**  
   Only `---` at the **start** of the document is supported. The opening line must be `---` (optionally with trailing spaces/newline), then the YAML content, then a closing `---`.

## Zensical: extension not applied

**Symptom**: In Zensical, Markdown is built but no templating or front matter is applied.

**Cause**: If you override `markdown_extensions` in Zensical, you must list **all** extensions you want, including `markdown_macros`. Adding one custom extension can replace the default list. Include `markdown_macros` (and any others you need) explicitly.

## MkDocs: difference from MkDocs Macros plugin

**Symptom**: Something works with the MkDocs Macros **plugin** but not with this extension.

**Explanation**: This package is a **Python-Markdown extension**, not an MkDocs plugin. It does not have access to MkDocs config, current page, or nav. It only:

- Parses YAML front matter and makes it available as template variables and as `md.Meta` / `md.front_matter`
- Runs Jinja2 on the Markdown body with variables, macros, and filters you provide via config and `define_env(env)`

So `env.conf`, `env.config`, `env.page`, and MkDocs-specific variables are **not** available. Use config `variables`, `include_yaml`, and your module for global data, and front matter for page-level data.
