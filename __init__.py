"""
Pelican JSON-LD Graph Generator Plugin

A Pelican plugin that generates Schema.org JSON-LD structured data
from Markdown frontmatter metadata.
"""

from .generator import register


def register():
    """Register the plugin with Pelican."""
    from .generator import register as gen_register
    gen_register()
