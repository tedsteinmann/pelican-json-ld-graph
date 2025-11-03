"""
Pelican JSON-LD Graph Generator Plugin

A Pelican plugin that generates Schema.org JSON-LD structured data
from Markdown frontmatter metadata.
"""

from .generator import register

__all__ = ['register']
