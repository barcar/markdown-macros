# Configuration

All options for the **MacrosExtension** (the main extension that runs Jinja2).

## Option reference

| Option | Default | Description |
|--------|---------|-------------|
| `variables` | `{}` | Global variables merged into the Jinja2 context. Keys are available as `{{ key }}` in every page. |
| `module_name` | `""` | Name of the Python module (e.g. `main`) that defines `define_env(env)` to register macros, filters, and variables. Resolved relative to `project_root`. |
| `modules` | `[]` | List of **pluglet** package names (e.g. `mkdocs_macros_plugin.include`) to load. Each must be importable and define `define_env(env)`. Variables, macros, and filters are merged after the local module. |
| `include_yaml` | `[]` | **List:** paths to YAML files; each is loaded and merged flat into variables. **Dict:** `key: path`; each file is loaded and stored under `variables[key]`. Paths are relative to `project_root`. |
| `include_dir` | `""` | Directory (relative to `project_root`) used for `{% include 'path/to/file.md' %}`. If set, Jinja2 uses a `FileSystemLoader` so includes resolve from this directory. |
| `project_root` | `"."` | Directory used to resolve `module_name`, `include_yaml` paths, and `include_dir`. |
| `render_by_default` | `true` | If `false`, Jinja2 is only run on pages whose front matter has `render_macros: true`. Other pages get front matter parsed but body unchanged. |
| `on_error_fail` | `false` | If `true`, a Jinja2 (or template) error is re-raised and the build fails. If `false`, the body is returned unchanged on error. |
| `on_undefined` | `"keep"` | How to treat undefined variables: `"keep"` (Jinja2 default: empty or leave as-is) or `"strict"` (raise on undefined). |
| `verbose` | `false` | If `true`, log debug messages (e.g. module/pluglet load, render) to the `markdown_macros` logger. |
| `j2_block_start_string` | `"{%"` | Jinja2 block start delimiter. |
| `j2_block_end_string` | `"%}"` | Jinja2 block end delimiter. |
| `j2_variable_start_string` | `"{{"` | Jinja2 variable start delimiter. |
| `j2_variable_end_string` | `"}}"` | Jinja2 variable end delimiter. |
| `j2_comment_start_string` | *(Jinja2 default)* | Jinja2 comment start (default `{#`). Set to customize. |
| `j2_comment_end_string` | *(Jinja2 default)* | Jinja2 comment end (default `#}`). Set to customize. |
| `j2_extensions` | `[]` | List of Jinja2 extension names or classes (e.g. `["jinja2.ext.loopcontrols"]`) to enable on the environment. |

Change the `j2_*` options only if you need to avoid clashes with other syntax (e.g. a different templating system that also uses `{{` and `}}`).

## Examples

### Zensical (`zensical.toml`)

```toml
[project.markdown_extensions.markdown_macros]
module_name = "main"
project_root = "."
variables = { unit_price = 10, currency = "EUR" }
include_yaml = ["data/glossary.yaml"]
# Optional:
# render_by_default = false
# on_undefined = "strict"
# include_dir = "snippets"
# modules = ["my_pluglet"]
```

### MkDocs (`mkdocs.yml`)

```yaml
markdown_extensions:
  - markdown_macros:
      module_name: main
      variables:
        unit_price: 10
        currency: EUR
      include_yaml:
        - data/glossary.yaml
      # Optional: include_dir for {% include %}
      include_dir: snippets
      # Optional: pluglets (preinstalled packages)
      modules:
        - my_pluglet
      on_error_fail: true
      on_undefined: strict
```

### include_yaml as key→path

Merge YAML under a key instead of flat:

```yaml
markdown_extensions:
  - markdown_macros:
      include_yaml:
        glossary: data/glossary.yaml
        team: data/team.yaml
```

Then in templates: `{{ glossary.term }}`, `{{ team.members }}`, etc.

### Python

```python
from markdown_macros import MacrosExtension

MacrosExtension(
    variables={"unit_price": 10, "currency": "EUR"},
    module_name="main",
    include_yaml=["data/glossary.yaml"],
    include_dir="snippets",
    project_root="/path/to/project",
    render_by_default=True,
    on_error_fail=False,
    on_undefined="keep",
    verbose=False,
    modules=["my_pluglet"],
    j2_extensions=["jinja2.ext.loopcontrols"],
)
```

## Variable precedence

When the same key appears in multiple places, the **last** one wins when building the Jinja2 context. Order is:

1. Config `variables`
2. Variables from `include_yaml` (list: flat merge; dict: under key)
3. Variables and macros from the local `module_name` module
4. Variables and macros from `modules` (pluglets)
5. Page YAML front matter

So front matter overrides pluglets and the local module; the local module overrides pluglets and config.
