"""
ManifoldBot - A self-contained Python module for creating intelligent trading bots.

This package provides a framework for creating bots that monitor data sources,
analyze content with ChatGPT, and automatically trade on Manifold Markets.
"""

__version__ = "0.2.1"
__author__ = "Peter Cotton"
__email__ = "peter@example.com"

from .config.settings import load_config

# Core imports - these will be available when someone does `import manifoldbot`
from .manifold.reader import ManifoldReader
from .manifold.writer import ManifoldWriter
from .manifold.bot import (
    ManifoldBot, DecisionMaker, MarketDecision, TradingSession,
    RandomDecisionMaker, KellyCriterionDecisionMaker, ConfidenceBasedDecisionMaker, LLMDecisionMaker
)

# Main exports
__all__ = [
    "load_config",
    "ManifoldReader",
    "ManifoldWriter",
    "ManifoldBot",
    "DecisionMaker",
    "MarketDecision",
    "TradingSession",
    "RandomDecisionMaker",
    "KellyCriterionDecisionMaker",
    "ConfidenceBasedDecisionMaker",
    "LLMDecisionMaker",
    "__version__",
    "__author__",
    "__email__",
]
