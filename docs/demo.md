---
title: Live demo
author: Docs
features:
  - Front matter
  - Config variables
  - include_yaml
  - Macros and filters
---

# Live demo

This page is built **with** the Markdown Macros extension. Each section shows **markdown source** (the template with macros/variables) and the **rendered** result. Where the template uses data from other files, those **sources** are shown too (YAML file, Python module).

## Front matter

Variables from this page’s YAML header (or from config when the host strips the header first).

**Markdown source:**

```markdown
---
title: Live demo
author: Docs
features:
  - Front matter
  - Config variables
---

- **title:** {{ title }}
- **author:** {{ author }}
- **features:** {{ features | join(', ') }}
```

**Rendered:**

- **title:** {{ title }}
- **author:** {{ author }}
- **features:** {{ features | join(', ') }}

## Config variables

Set in `zensical.toml` (or your tool’s config).

**Markdown source:**

```markdown
- **site_name:** {{ site_name }}
- **version:** {{ version }}
```

**Rendered:**

- **site_name:** {{ site_name }}
- **version:** {{ version }}

## include_yaml

Variables are loaded from `docs/demo_vars.yaml`. The YAML source defines the data; the markdown source references it.

**YAML source** (`docs/demo_vars.yaml`):

```yaml
# Variables loaded via include_yaml for the Live demo page
project_url: https://github.com/barcar/markdown-macros
tagline: Variables, macros, and filters in your Markdown
```

**Markdown source:**

```markdown
- **tagline:** {{ tagline }}
- **project_url:** [Repository]({{ project_url }})
```

**Rendered:**

- **tagline:** {{ tagline }}
- **project_url:** [Repository]({{ project_url }})

## Module (define_env)

Variables, macros, and filters come from `docs/demo_macros.py`. The Python module source defines them; the markdown source calls them.

**Python module source** (`docs/demo_macros.py`):

```python
def define_env(env):
    env.variables["from_module"] = "set in docs/demo_macros.py"

    @env.macro
    def greet(name):
        """Return a greeting string."""
        return f"Hello, **{name}**!"

    @env.filter
    def double(x):
        """Double a number (string or int)."""
        n = int(x) if isinstance(x, str) and x.isdigit() else x
        return 2 * n
```

**Markdown source:**

```markdown
- **from_module:** {{ from_module }}
- **Macro** `greet("reader")`: {{ greet("reader") }}
- **Filter** `21 | double`: {{ 21 | double }}
```

**Rendered:**

- **from_module:** {{ from_module }}
- **Macro** `greet("reader")`: {{ greet("reader") }}
- **Filter** `21 | double`: {{ 21 | double }}

## Page-level set and conditionals

**Markdown source:**

```markdown
{% set local_var = "I was set in the page with the set tag." %}
- **local_var:** {{ local_var }}

{% if version %}
- **Conditional:** This line appears because `version` is defined (current: {{ version }}).
{% endif %}
```

**Rendered:**

{% set local_var = "I was set in the page with the set tag." %}
- **local_var:** {{ local_var }}

{% if version %}
- **Conditional:** This line appears because `version` is defined (current: {{ version }}).
{% endif %}

---

*The "Rendered" blocks above were produced by the extension at build time.*
