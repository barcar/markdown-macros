"""
Markdown Macros: MkDocs-Macros–style extension for Python-Markdown.

Jinja2 templating with variables (config + YAML front matter), macros, and
filters. Parses --- YAML --- front matter and exposes md.Meta / md.front_matter.
Use define_env(env) in a module for macros/filters/variables.
"""

from markdown_macros.front_matter import FrontMatterExtension
from markdown_macros.macros import MacrosExtension, make_extension

# Python-Markdown discovers extensions via makeExtension (camelCase)
makeExtension = make_extension

__all__ = ["FrontMatterExtension", "MacrosExtension", "make_extension", "makeExtension"]
