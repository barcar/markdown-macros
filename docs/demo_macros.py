"""
Demo module for the documentation site. Defines macros and filters
used on the Live demo page. Only used when building the docs.
"""


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
