"""
Simple AI module for ManifoldBot.

Just handles OpenAI API calls cleanly.
"""

from .openai_client import analyze_market_with_gpt

__all__ = [
    "analyze_market_with_gpt",
]
