"""
MkDocs-Macros–style extension for Python-Markdown.

Treats the document as a Jinja2 template: parses YAML front matter for
page-level variables, merges with config variables and optional module
(macros/filters/variables via define_env(env)), then renders the body.
Exposes md.Meta and md.front_matter for downstream use.
"""

import importlib.util
import logging
from pathlib import Path

from markdown import Extension
from markdown.preprocessors import Preprocessor

from markdown_macros.utils import FRONT_MATTER_RE, meta_from_dict

try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

logger = logging.getLogger("markdown_macros")


class MacroEnv:
    """Minimal env object for define_env(env) compatibility with MkDocs Macros."""

    def __init__(self):
        self.variables = {}
        self._macros = {}
        self._filters = {}

    def macro(self, fn=None, name=None):
        """Register a macro. Use as @env.macro or env.macro(func) or env.macro(func, 'name')."""
        if fn is None:
            return lambda f: self.macro(f, name)
        self._macros[name or fn.__name__] = fn
        return fn

    def filter(self, fn=None, name=None):
        """Register a filter. Use as @env.filter or env.filter(func)."""
        if fn is None:
            return lambda f: self.filter(f, name)
        self._filters[name or fn.__name__] = fn
        return fn


def _path_under_root(path: Path, root: Path) -> bool:
    """Return True if path resolves to a location under root (or equals root)."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _load_module(module_name, project_root=None):
    """Load a module by name (e.g. 'main') and return (variables, macros, filters) from define_env."""
    root = Path(project_root or ".").resolve()
    for candidate in [root / f"{module_name}.py", root / module_name / "__init__.py"]:
        if not candidate.exists():
            continue
        if not _path_under_root(candidate, root):
            continue
        spec = importlib.util.spec_from_file_location(module_name, candidate)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "define_env"):
                env = MacroEnv()
                mod.define_env(env)
                return env.variables, env._macros, env._filters
        break
    # Only try import for package-like names (no path separators or "..")
    if "/" in module_name or "\\" in module_name or ".." in module_name:
        return {}, {}, {}
    try:
        mod = __import__(module_name)
        if hasattr(mod, "define_env"):  # pragma: no cover - need installed package with define_env
            env = MacroEnv()
            mod.define_env(env)
            return env.variables, env._macros, env._filters
    except ImportError:
        pass
    return {}, {}, {}


def _load_pluglets(module_names):
    """Load pluglet modules by package name; return merged (variables, macros, filters)."""
    all_vars = {}
    all_macros = {}
    all_filters = {}
    for name in module_names or []:
        name = (name or "").strip()
        if not name:
            continue
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "define_env"):
                env = MacroEnv()
                mod.define_env(env)
                all_vars.update(env.variables)
                all_macros.update(env._macros)
                all_filters.update(env._filters)
        except ImportError as e:
            logger.warning("markdown_macros: could not load pluglet %r: %s", name, e)
    return all_vars, all_macros, all_filters


def _load_one_yaml(path, project_root=None):
    """Load a single YAML file; return dict or None. Paths must resolve under project_root."""
    if not yaml:  # pragma: no cover
        return None
    root = Path(project_root or ".").resolve()
    p = (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not p.exists() or not _path_under_root(p, root):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _merge_include_yaml(include_yaml, project_root, variables):
    """
    Merge include_yaml into variables.
    include_yaml can be: list of paths (flat merge) or dict of key -> path (merge under key).
    """
    if not include_yaml:
        return
    if isinstance(include_yaml, dict):
        for key, path in include_yaml.items():
            data = _load_one_yaml(path, project_root)
            if data is not None:
                variables[key] = data
    else:
        for path in include_yaml:
            data = _load_one_yaml(path, project_root)
            if isinstance(data, dict):
                variables.update(data)


class MacrosPreprocessor(Preprocessor):
    """Parse front matter, build Jinja2 context, render body."""

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, lines):
        text = "\n".join(lines)
        project_root = self.config.get("project_root") or "."
        verbose = self.config.get("verbose", False)

        # 1) Parse and strip front matter
        match = FRONT_MATTER_RE.match(text)
        if match:
            raw_block = match.group(1).strip()
            if yaml:
                try:
                    data = yaml.safe_load(raw_block)
                    if data is None:
                        data = {}
                    if not isinstance(data, dict):
                        data = {"content": data}
                except Exception:
                    data = {}
            else:  # pragma: no cover - yaml not installed
                data = {}
            self.md.Meta = getattr(self.md, "Meta", None) or {}
            self.md.Meta.update(meta_from_dict(data))
            self.md.front_matter = data
            body = text[match.end() :]
        else:
            self.md.Meta = getattr(self.md, "Meta", None) or {}
            if not hasattr(self.md, "front_matter") or self.md.front_matter is None:
                self.md.front_matter = {}
            body = text

        # render_by_default: if False, only render when front matter has render_macros: true
        render_by_default = self.config.get("render_by_default", True)
        page_render_macros = self.md.front_matter.get("render_macros")
        if not render_by_default and not page_render_macros:
            if verbose:
                logger.debug("markdown_macros: skipping Jinja2 (render_by_default=False, no render_macros)")
            return body.split("\n")

        # 2) Build context: config variables + include_yaml + module + pluglets + front matter
        variables = dict(self.config.get("variables") or {})
        _merge_include_yaml(
            self.config.get("include_yaml"),
            project_root,
            variables,
        )
        module_name = (self.config.get("module_name") or "").strip()
        if module_name:
            if verbose:
                logger.debug("markdown_macros: loading module %r", module_name)
            mod_vars, macros, filters = _load_module(module_name, project_root)
            variables.update(mod_vars)
        else:
            macros = {}
            filters = {}
        # Pluglets (preinstalled modules)
        pluglet_names = self.config.get("modules") or []
        if pluglet_names:
            if verbose:
                logger.debug("markdown_macros: loading pluglets %s", pluglet_names)
            pv, pm, pf = _load_pluglets(pluglet_names)
            variables.update(pv)
            if not module_name:
                macros = {}
                filters = {}
            macros.update(pm)
            filters.update(pf)
        variables.update(macros)  # so template can call macros (from module or pluglets)
        if match:
            variables.update(self.md.front_matter)

        if not jinja2:
            return body.split("\n")  # pragma: no cover - jinja2 not installed

        # 3) Build Jinja2 environment
        include_dir = self.config.get("include_dir") or ""
        include_dir_path = (Path(project_root) / include_dir).resolve() if include_dir else None
        env_kw = {
            "block_start_string": self.config.get("j2_block_start_string") or "{%",
            "block_end_string": self.config.get("j2_block_end_string") or "%}",
            "variable_start_string": self.config.get("j2_variable_start_string") or "{{",
            "variable_end_string": self.config.get("j2_variable_end_string") or "}}",
        }
        comment_start = self.config.get("j2_comment_start_string")
        comment_end = self.config.get("j2_comment_end_string")
        if comment_start is not None:  # pragma: no cover - set via config file, not constructor
            env_kw["comment_start_string"] = comment_start
        if comment_end is not None:  # pragma: no cover
            env_kw["comment_end_string"] = comment_end
        on_undefined = self.config.get("on_undefined", "keep")
        if on_undefined == "strict":
            env_kw["undefined"] = jinja2.StrictUndefined
        j2_extensions = self.config.get("j2_extensions") or []
        if j2_extensions:
            env_kw["extensions"] = list(j2_extensions)
        if include_dir_path and include_dir_path.exists():
            env_kw["loader"] = jinja2.FileSystemLoader(str(include_dir_path))
        env = jinja2.Environment(**env_kw)
        env.filters.update(filters)

        # MkDocs Macros compatibility: expand Jinja2 in the YAML "title" field (plugin exception since 1.0.2)
        title_val = variables.get("title")
        if isinstance(title_val, str) and ("{{" in title_val or "{%" in title_val):
            try:
                title_template = env.from_string(title_val)
                variables["title"] = title_template.render(**variables)
                self.md.front_matter["title"] = variables["title"]
                self.md.Meta["title"] = [variables["title"]]
            except Exception:
                pass

        try:
            if verbose:
                logger.debug("markdown_macros: rendering template")
            template = env.from_string(body)
            rendered = template.render(**variables)
        except Exception as e:
            if self.config.get("on_error_fail", False):
                raise
            if verbose:
                logger.debug("markdown_macros: render error (swallowing): %s", e)
            rendered = body
        return rendered.split("\n")


class MacrosExtension(Extension):
    """Python-Markdown extension: Jinja2 templating with variables, macros, and filters (MkDocs-Macros style)."""

    def __init__(self, **kwargs):
        self.config = {
            "variables": [{}, "Global variables merged into Jinja2 context"],
            "module_name": ["", "Python module name (e.g. main) with define_env(env)"],
            "modules": [[], "List of pluglet package names (e.g. mkdocs_macros_plugin.include)"],
            "include_yaml": [[], "Paths to YAML files (list) or key: path (dict) to merge into variables"],
            "include_dir": ["", "Directory for {% include 'file' %} (relative to project_root)"],
            "project_root": [".", "Project root for resolving module, YAML, and include_dir paths"],
            "render_by_default": [True, "If False, only render when front matter has render_macros: true"],
            "on_error_fail": [False, "If True, raise on Jinja2 error instead of returning unchanged body"],
            "on_undefined": ["keep", "Undefined vars: 'keep' (leave/empty) or 'strict' (raise)"],
            "verbose": [False, "Log debug messages"],
            "j2_block_start_string": ["{%", "Jinja2 block start"],
            "j2_block_end_string": ["%}", "Jinja2 block end"],
            "j2_variable_start_string": ["{{", "Jinja2 variable start"],
            "j2_variable_end_string": ["}}", "Jinja2 variable end"],
            "j2_comment_start_string": [None, "Jinja2 comment start (default {#)"],
            "j2_comment_end_string": [None, "Jinja2 comment end (default #})"],
            "j2_extensions": [[], "List of Jinja2 extension names or classes"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(
            MacrosPreprocessor(md, self.getConfigs()),
            "macros",
            priority=20,
        )


def make_extension(**kwargs):
    return MacrosExtension(**kwargs)
