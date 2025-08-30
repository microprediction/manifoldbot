"""
ManifoldBot - A self-contained Python module for creating intelligent trading bots.

This package provides a framework for creating bots that monitor data sources,
analyze content with ChatGPT, and automatically trade on Manifold Markets.
"""

__version__ = "0.1.0"
__author__ = "Peter Cotton"
__email__ = "peter@example.com"

from .config.settings import load_config

# Core imports - these will be available when someone does `import manifoldbot`
from .core.bot import Bot
from .manifold.reader import ManifoldReader

# Main exports
__all__ = [
    "Bot",
    "load_config",
    "ManifoldReader",
    "__version__",
    "__author__",
    "__email__",
]
