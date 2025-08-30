"""
Basic example: Read market data from Manifold.

This shows how to fetch and display market information.
"""

from manifoldbot import ManifoldReader


def main():
    # Create reader
    reader = ManifoldReader()
    
    # Get recent markets
    markets = reader.get_markets(limit=5)
    
    print("Recent Markets:")
    for market in markets:
        print(f"- {market['question']}")
        print(f"  Probability: {market['probability']:.1%}")
        print(f"  Liquidity: {market.get('totalLiquidity', 0):.1f} M$")
        print()


if __name__ == "__main__":
    main()
