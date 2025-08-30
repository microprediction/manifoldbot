"""
Basic ManifoldWriter examples.

This example demonstrates how to use ManifoldWriter for authenticated
operations like placing bets and managing your account.

Requires MANIFOLD_API_KEY environment variable.
"""

import os

from manifoldbot.manifold import ManifoldWriter


def main():
    """Demonstrate basic ManifoldWriter functionality."""
    # Check for API key
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        print("❌ MANIFOLD_API_KEY environment variable not set")
        print("Please set your API key: export MANIFOLD_API_KEY='your_key'")
        return

    # Initialize writer
    writer = ManifoldWriter(api_key=api_key)

    # Check authentication
    if not writer.is_authenticated():
        print("❌ Authentication failed - check your API key")
        return

    print("✅ Successfully authenticated!")

    # Get user info
    user_info = writer.get_me()
    print(f"👤 Logged in as: {user_info.get('name', 'Unknown')}")
    print(f"💰 Balance: {writer.get_balance():.2f}Ṁ")
    print(f"📊 Total deposits: {writer.get_total_deposits():.2f}Ṁ")

    # Get portfolio
    try:
        portfolio = writer.get_portfolio()
        print(f"📈 Portfolio: {portfolio}")
    except Exception as e:
        print(f"⚠️  Could not fetch portfolio: {e}")

    # Get positions
    try:
        positions = writer.get_positions()
        print(f"🎯 Active positions: {len(positions)}")
    except Exception as e:
        print(f"⚠️  Could not fetch positions: {e}")

    # Example: Calculate market impact (without placing bet)
    print("\n📊 Market impact calculation example:")
    try:
        # Use a real market ID for demonstration
        market_id = "gnQtgc926u"  # Example market ID
        impact = writer.calculate_market_impact(market_id, 10, "YES")
        print("Market impact for 10Ṁ YES bet:")
        print(f"  Current probability: {impact['current_probability']:.1%}")
        print(f"  Estimated impact: {impact['estimated_impact']:.3f}")
        print(f"  New probability: {impact['new_probability']:.1%}")
    except Exception as e:
        print(f"⚠️  Could not calculate market impact: {e}")

    print("\n💡 To place actual bets, use:")
    print("  writer.place_bet(market_id, 'YES', 1)  # 1Ṁ market bet")
    print("  writer.place_limit_yes(market_id, 10, 0.7)  # 10Ṁ at 70%")


if __name__ == "__main__":
    main()
