"""
Basic ManifoldReader examples.

This example demonstrates how to use ManifoldReader to fetch market data
without requiring an API key.
"""

from manifoldbot.manifold import ManifoldReader


def main():
    """Demonstrate basic ManifoldReader functionality."""
    # Initialize reader (no API key needed)
    reader = ManifoldReader()

    print("🔍 Fetching recent markets...")

    # Get recent markets
    markets = reader.get_markets(limit=5)
    print(f"Found {len(markets)} markets")

    for i, market in enumerate(markets, 1):
        question = market.get("question", "Unknown")
        probability = market.get("probability", 0)
        volume = market.get("volume", 0)

        print(f"{i}. {question[:60]}...")
        print(f"   Probability: {probability:.1%}")
        print(f"   Volume: {volume}Ṁ")
        print()

    # Get a specific market by slug
    print("🎯 Fetching market by slug...")
    try:
        market = reader.get_market_by_slug(
            "catl-receives-license-renewal-for-y-qz65RqIZsy"
        )
        print(f"Market: {market.get('question', 'Unknown')}")
        print(f"Current probability: {market.get('probability', 0):.1%}")
        print(f"Volume: {market.get('volume', 0)}Ṁ")
    except Exception as e:
        print(f"Error fetching market: {e}")

    # Search for markets
    print("\n🔍 Searching for AI-related markets...")
    try:
        ai_markets = reader.search_markets("AI", limit=3)
        print(f"Found {len(ai_markets)} AI-related markets")

        for market in ai_markets:
            print(f"- {market.get('question', 'Unknown')[:50]}...")
    except Exception as e:
        print(f"Error searching markets: {e}")


if __name__ == "__main__":
    main()
