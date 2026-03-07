# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-03-07

### Fixed

- `pyproject.toml`: use SPDX `license = "MIT"` and remove deprecated license classifier to clear setuptools deprecation warnings in CI/PyPI build

## [0.3.0] - 2026-03-07

### Added

- Tests run in CI before docs deploy; Pages only updates when tests pass
- README badges: PyPI version, Python 3.8+, License MIT

### Changed

- Docs workflow renamed to "Tests and Deploy docs to GitHub Pages" (test job added with `needs: test` on build)

## [0.2.0] - 2026-03-07

### Added

- Documentation built with [Zensical](https://zensical.org) (replacing MkDocs); modern theme, repo link in header
- Changelog and License pages in the docs site; Changelog copied from root in CI for GitHub Pages
- GitHub Actions: deploy docs to GitHub Pages on push to `main`; publish to PyPI on release (version from tag)
- [Dependabot](.github/dependabot.yml) for pip and GitHub Actions (monthly)

### Changed

- PyPI package name **markdown-macros-extension** (install: `pip install markdown-macros-extension`); extension key in config remains `markdown_macros`
- README trimmed to a short overview with link to online docs and compatibility note
- Author and repo set to BarCar / barcar/markdown-macros; MIT License (c) 2026 BarCar

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
