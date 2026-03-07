# Writing modules

Modules are Python files (or packages) that register **variables**, **macros**, and **filters** for use in your Markdown templates. The API is compatible with [MkDocs Macros](https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/) so you can reuse the same `define_env(env)` pattern.

## The `define_env(env)` function

Every module **must** define a function named `define_env` that takes one argument, `env`:

```python
def define_env(env):
    """
    Hook for variables, macros, and filters.
    """
    # variables
    env.variables["site_name"] = "My Docs"

    @env.macro
    def hello(name):
        return f"Hello, {name}!"

    @env.filter
    def reverse(s):
        return s[::-1]
```

This function is called once when the extension loads. Use it to fill `env.variables` and to register macros and filters with `@env.macro` and `@env.filter`.

## Location of the module

By default, the extension looks for a module named `main` (e.g. `main.py`) in the **project root** (the directory given by `project_root`, which defaults to `"."`).

- **Single file**: `main.py` in the project root.
- **Custom name**: set `module_name` in config, e.g. `module_name: "mymacros"` → `mymacros.py` or `mymacros/__init__.py`.
- **Subpath**: e.g. `module_name: "include/macros"` → `include/macros.py` or `include/macros/__init__.py` under `project_root`.

The extension tries, in order:

1. `project_root / f"{module_name}.py"`
2. `project_root / module_name / "__init__.py"`
3. `importlib.import_module(module_name)` (if the module is on the Python path)

If no module is found or it has no `define_env`, the extension still runs; it just has no extra variables, macros, or filters from that module.

### Pluglets (preinstalled modules)

You can also load **pluglets**: Python packages installed in the environment (e.g. via `pip`) that define `define_env(env)`. Set the **`modules`** config option to a list of package names:

```yaml
# mkdocs.yml
markdown_extensions:
  - markdown_macros:
      modules:
        - my_pluglet
        - another_pluglet
```

Each pluglet is imported with `importlib.import_module(name)`; its variables, macros, and filters are merged. The local `module_name` module is loaded first, then pluglets, so the local module can override pluglet names. Pluglets are useful for sharing macros across projects.

## Registering variables, macros, and filters

### Variables

Add key/value pairs to `env.variables`. They become available in every page as `{{ key }}`.

```python
def define_env(env):
    env.variables["author"] = "Alice"
    env.variables["version"] = "1.0"
    # or with dot notation (same thing):
    env.variables.author = "Alice"
```

Values can be strings, numbers, lists, or dicts; Jinja2 will use them as usual.

### Macros

Macros are callable in the template, e.g. `{{ price(10, 5) }}`. Register them with the `@env.macro` decorator or by calling `env.macro(func, name)`.

```python
def define_env(env):
    @env.macro
    def price(unit_price, quantity):
        return unit_price * quantity

    # Custom name
    def square(x):
        return x * x
    env.macro(square, "sq")
```

In Markdown:

```markdown
Total: {{ price(10, 5) }}
{{ sq(4) }} is 16.
```

Macros can return a string (including Markdown or HTML). They are executed at render time.

### Filters

Filters are used with the pipe syntax: `{{ value | filter_name }}`. Register them with `@env.filter`.

```python
def define_env(env):
    @env.filter
    def double(x):
        n = int(x) if isinstance(x, str) and x.isdigit() else x
        return 2 * n

    @env.filter
    def reverse(s):
        return s[::-1]
```

In Markdown:

```markdown
{{ 21 | double }} is 42.
{{ "hello" | reverse }} is olleh.
```

The first argument to the filter is the value on the left of `|`; additional arguments can be passed in parentheses in Jinja2.

## The `env` object (Markdown Macros)

In this extension, `env` only provides what’s needed for the MkDocs-Macros–compatible API:

| Attribute / method | Description |
|-------------------|-------------|
| `env.variables` | Dict of variables merged into the Jinja2 context. Add or change keys here. |
| `env.macro(fn, name=None)` | Register a macro. Use as `@env.macro` or `env.macro(func)` or `env.macro(func, "name")`. |
| `env.filter(fn, name=None)` | Register a filter. Use as `@env.filter` or `env.filter(func)`. |

There is **no** `env.conf`, `env.config`, or `env.page` in this extension (those exist in the MkDocs Macros *plugin* because it has access to the MkDocs config and current page). Here, page-level data comes only from **YAML front matter**, which is parsed and merged into the template variables automatically.

## Implementing the module as a package

You can use a package (a directory with `__init__.py`) instead of a single file:

```
main/
├── __init__.py   # define_env(env) here
├── util.py
└── ...
```

In `main/__init__.py`:

```python
from .util import format_price

def define_env(env):
    env.variables["site"] = "My Docs"

    @env.macro
    def price(unit, qty):
        return format_price(unit * qty)
```

Set `module_name: "main"` and the extension will load `main/__init__.py`.

## Notes

- **Imports**: Use normal Python imports at the top of your module; `define_env` can use any code you need.
- **Security**: Macros and filters run with the same privileges as the process that builds the docs. Avoid exposing sensitive data or running arbitrary code from untrusted content.
- **Errors**: If `define_env` raises an exception, the extension may fail to load. Validate config or variables inside `define_env` if needed.
