# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-07

### Added

- **MacrosExtension**: MkDocs-Macros–style Jinja2 templating for Python-Markdown
  - Variables from config, YAML front matter, `include_yaml` (list or key→path dict), and `define_env(env)` modules
  - Macros and filters via `define_env(env)` (`@env.macro`, `@env.filter`)
  - YAML front matter parsed and exposed as `md.Meta` and `md.front_matter`
  - Jinja2 in the `title` front matter field (plugin compatibility)
- **FrontMatterExtension**: YAML front matter only (no Jinja2), for lighter use
- Config options: `variables`, `module_name`, `modules` (pluglets), `include_yaml`, `include_dir`, `project_root`, `render_by_default`, `on_error_fail`, `on_undefined`, `verbose`, `j2_*` delimiters, `j2_extensions`
- Entry point `markdown_macros` under `markdown.extensions` for `extensions=['markdown_macros']`
- Documentation (docs/) with Zensical: installation, configuration, writing modules, usage, compatibility, troubleshooting
- Tests for front matter, variables, render_by_default, title expansion, on_undefined strict

### Compatibility

- API and options aligned with [MkDocs Macros](https://mkdocs-macros-plugin.readthedocs.io/) plugin; same markdown syntax processing and title-field exception. MkDocs-only features (`env.page`, `env.conf`, hooks) are not available.
