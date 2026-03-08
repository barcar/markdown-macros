# Contributing

Thanks for your interest in contributing. This project follows common open-source practices; below is what you need to get started.

## Getting started

1. **Fork and clone** the repo (or clone directly if you have push access).

2. **Create a virtual environment** and install the package with dev dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Run the tests** to confirm everything passes:
   ```bash
   pytest tests/ -v
   ```
   The project keeps test coverage at 95% or above; run `pytest tests/ --cov=markdown_macros --cov-fail-under=95 -v` to check.

## Making changes

- **Branch** from `main` (e.g. `git checkout -b fix/short-description`).
- **Make your changes** and add or update tests as needed.
- **Commit** with clear, present-tense messages (e.g. `Add test for include_dir`, `Fix path escape when module_name has slash`).
- **Push** your branch and open a **pull request** against `main`.

In the PR, briefly describe what changed and why. CI runs tests (and coverage); the PR should be green before merge.

## Reporting issues

Open a [GitHub issue](https://github.com/barcar/markdown-macros/issues) with:

- A short summary and steps to reproduce (for bugs).
- Your environment (Python version, OS) if relevant.
- A minimal example (config snippet, markdown, or code) when it helps.

## Code and docs

- **Style:** Keep the existing style in the codebase (formatting, naming). No formal style guide is enforced.
- **Tests:** New behavior should have tests; avoid dropping coverage.
- **Docs:** The docs live under `docs/` and are built with [Zensical](https://zensical.org). Update them for user-facing changes.

## Releases

Releases are cut by the maintainers. The version in `pyproject.toml` and [CHANGELOG.md](CHANGELOG.md) is the source of truth; the release tag (e.g. `v0.4.0`) must match. You don’t need to do anything special for a release when contributing.

---

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
