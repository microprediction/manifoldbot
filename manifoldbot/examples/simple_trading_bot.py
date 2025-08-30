"""
Simple trading bot example.

This example demonstrates a basic trading strategy that looks for
undervalued markets and places small bets.

Requires MANIFOLD_API_KEY environment variable.
"""

import os
import time
from typing import Any, Dict, List

from manifoldbot.manifold import ManifoldReader, ManifoldWriter


class SimpleTradingBot:
    """A simple trading bot that looks for undervalued markets."""

    def __init__(self, api_key: str):
        """Initialize the trading bot."""
        self.reader = ManifoldReader()
        self.writer = ManifoldWriter(api_key=api_key)
        self.max_bet_size = 5  # Maximum bet size in M$
        self.min_balance = 20  # Minimum balance to keep

    def find_undervalued_markets(
        self, keywords: List[str], max_probability: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Find markets that might be undervalued."""
        markets = self.reader.get_markets(limit=50)

        undervalued = []
        for market in markets:
            if market.get("isResolved", True):
                continue

            question = market.get("question", "").lower()
            probability = market.get("probability", 0)
            volume = market.get("volume", 0)

            # Check if market contains keywords and is below threshold
            if (
                any(keyword.lower() in question for keyword in keywords)
                and probability <= max_probability
                and volume > 100
            ):  # Some trading activity

                undervalued.append(market)

        return undervalued

    def should_place_bet(self, market: Dict[str, Any]) -> bool:
        """Determine if we should bet on this market."""
        # Check balance
        if self.writer.get_balance() < self.min_balance:
            return False

        # Check market conditions
        probability = market.get("probability", 0)
        volume = market.get("volume", 0)

        # Only bet on markets with reasonable activity
        return volume > 50 and probability < 0.4

    def run_trading_cycle(self, keywords: List[str]):
        """Run one trading cycle."""
        print("🔍 Searching for undervalued markets...")

        undervalued = self.find_undervalued_markets(keywords)
        print(f"Found {len(undervalued)} potentially undervalued markets")

        for market in undervalued[:3]:  # Limit to top 3
            if self.should_place_bet(market):
                try:
                    market_id = market["id"]
                    question = market["question"]
                    probability = market.get("probability", 0)

                    print(f"🎯 Considering: {question[:50]}...")
                    print(f"   Current probability: {probability:.1%}")

                    # Place a small bet
                    result = self.writer.place_bet(market_id, "YES", 2)
                    print(f"   ✅ Bet placed: {result.get('betId', 'unknown')}")

                    # Wait between bets to avoid rate limits
                    time.sleep(2)

                except Exception as e:
                    print(f"   ❌ Bet failed: {e}")
            else:
                print("⏭️  Skipping market (insufficient balance or conditions)")


def main():
    """Run the simple trading bot."""
    # Check for API key
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        print("❌ MANIFOLD_API_KEY environment variable not set")
        return

    # Initialize bot
    bot = SimpleTradingBot(api_key=api_key)

    # Check authentication
    if not bot.writer.is_authenticated():
        print("❌ Authentication failed")
        return

    print("✅ Trading bot initialized successfully!")
    print(f"💰 Current balance: {bot.writer.get_balance():.2f}Ṁ")

    # Run trading cycle for AI-related markets
    print("\n🤖 Running trading cycle for AI-related markets...")
    keywords = ["AI", "artificial intelligence", "machine learning"]
    bot.run_trading_cycle(keywords)

    print("\n🎉 Trading cycle complete!")


if __name__ == "__main__":
    main()
