# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-03-07

### Added

- CI: test job runs pytest with coverage (`--cov=markdown_macros --cov-fail-under=95`)
- Python 3.13 classifier in `pyproject.toml`
- Shared `markdown_macros.utils`: `FRONT_MATTER_RE` and `meta_from_dict()` (deduplicated from front_matter and macros)
- Tests for path safety, utils, front matter edge cases (empty/null/scalar/malformed YAML), pluglets, include_dir, macros `make_extension`, and error/verbose paths

### Changed

- PyPI publish workflow no longer mutates `pyproject.toml`; release tag must match the version already in the repo (bump version, commit, push, then create a release with tag `vX.Y.Z`)
- Dependabot schedule set back to `monthly`; Zensical `site_url` set to GitHub Pages URL
- Docs: note that local build may 404 on Changelog page; path safety documented in configuration

### Fixed

- Path safety: `include_yaml` and `module_name` file paths must resolve under `project_root`; paths that escape (e.g. `../../outside`) are ignored and no longer loaded
- Pluglet macros added to template context so `modules=` (pluglets) can provide callable macros as well as variables
- Malformed YAML in front matter now covered by test (tab-indented line triggers exception path)

## [0.3.2] - 2026-03-07

### Fixed

- Dependabot auto-merge workflow: run on all successful test workflow completions (not only `main`); resolve PR head branch via Actions API so PR-triggered runs are detected; add checkout and `contents: write` so merge step succeeds
- Fixed PyPi docs link to use GitHub Pages

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
