"""
Basic example: Place bets on Manifold.

This shows how to place bets (requires API key).
"""

import os
from manifoldbot import ManifoldWriter


def main():
    # Create writer (requires API key)
    writer = ManifoldWriter(api_key=os.getenv("MANIFOLD_API_KEY"))
    
    if not writer.is_authenticated():
        print("Error: Invalid API key")
        return
    
    # Get balance
    balance = writer.get_balance()
    print(f"Current balance: {balance:.2f} M$")
    
    # Example: Place a bet (uncomment to actually place)
    # result = writer.place_bet(
    #     market_id="your_market_id",
    #     outcome="YES",
    #     amount=10
    # )
    # print(f"Bet placed: {result}")


if __name__ == "__main__":
    main()
