# Installation

## Prerequisites

- **Python** ≥ 3.8
- **Python-Markdown** ≥ 3.4
- **PyYAML** ≥ 6.0
- **Jinja2** ≥ 3.0

## Standard installation

```bash
pip install markdown-macros
```

This installs `markdown-macros` and its dependencies (`markdown`, `pyyaml`, `jinja2`).

## Enabling the extension

The extension must be registered with Python-Markdown. How you do that depends on your environment.

### By name (recommended)

Most Markdown-based tools accept extension names. Add `markdown_macros` to the list of Markdown extensions.

**Zensical** (`zensical.toml`):

```toml
[project.markdown_extensions.markdown_macros]
# optional: module_name = "main", variables = { ... }
```

**MkDocs** (`mkdocs.yml`):

```yaml
markdown_extensions:
  - markdown_macros
  # or with options:
  # - markdown_macros:
  #     module_name: main
  #     variables:
  #       unit_price: 10
```

**Python**:

```python
import markdown

html = markdown.markdown(
    source,
    extensions=["markdown_macros"]
)
```

### By class (with options)

For full control over options, use the extension class:

```python
import markdown
from markdown_macros import MacrosExtension

md = markdown.Markdown(extensions=[
    MacrosExtension(
        module_name="main",
        variables={"unit_price": 10},
        include_yaml=["data/vars.yaml"],
        project_root="/path/to/project",
    )
])
html = md.convert(source)
```

## Front-matter only (no Jinja2)

If you only want YAML front matter parsed and exposed as `md.Meta` / `md.front_matter` **without** any Jinja2 templating, use the lighter extension:

```python
from markdown_macros import FrontMatterExtension

md = markdown.Markdown(extensions=[FrontMatterExtension()])
```

Or by name:

```python
extensions=["markdown_macros.front_matter:FrontMatterExtension"]
```

## Check that it works

1. Create a Markdown file with front matter and a variable:

   ```markdown
   ---
   title: Test
   ---

   # {{ title }}

   If you see "Test" above, the extension is working.
   ```

2. Convert it with the extension enabled (e.g. `zensical serve`, or the Python snippet above).

3. In the output, the heading should show **Test** and the variable line should show the sentence with **Test** in it—not the literal `{{ title }}`.

If you see raw `{{ title }}`, the extension is not in the Markdown pipeline or Jinja2 failed (check that `jinja2` is installed).

## Python-Markdown extension API

This project follows the [Python-Markdown extension API](https://python-markdown.github.io/extensions/api/):

- **Entry point**: Registered under `markdown.extensions` as `markdown_macros` (so `extensions=['markdown_macros']` works after `pip install`).
- **Config**: Options use the standard `self.config = {key: [default, description]}` format; `getConfigs()` is passed to the preprocessor.
- **Registration**: `md.registerExtension(self)` and `md.preprocessors.register(..., priority=...)` (higher priority runs first).
- **Preprocessor**: `run(self, lines)` receives and returns a list of lines (Unicode strings).
- **Discovery**: The package provides `makeExtension(**kwargs)` so the extension can be loaded by module name without a class suffix.
