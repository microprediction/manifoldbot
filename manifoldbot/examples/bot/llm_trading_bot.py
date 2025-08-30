"""
LLM Trading Bot Example

This example shows how to create an LLM-powered trading bot using
the ManifoldBot framework. Use --all flag to trade all markets.
"""

import os
from manifoldbot import ManifoldBot, LLMDecisionMaker, ManifoldReader


def main(trade_all=False):
    """Run the LLM trading bot."""
    # Get API keys
    manifold_api_key = os.getenv("MANIFOLD_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not manifold_api_key:
        print("Error: MANIFOLD_API_KEY environment variable not set")
        return
    
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Create decision maker
    decision_maker = LLMDecisionMaker(
        openai_api_key=openai_api_key,
        min_confidence=0.6,
        model="gpt-4"
    )
    
    # Create bot
    bot = ManifoldBot(
        manifold_api_key=manifold_api_key,
        decision_maker=decision_maker
    )
    
    if trade_all:
        # Trade ALL markets
        reader = ManifoldReader()
        print("Fetching ALL markets (this will take a moment)...")
        markets = reader.get_all_markets()
        print(f"Found {len(markets)} total markets")
        session = bot.run_on_markets(
            markets=markets,
            bet_amount=5,
            max_bets=50
        )
    else:
        # Run on recent markets
        session = bot.run_on_recent_markets(
            limit=10,
            bet_amount=5,
            max_bets=3
        )
    
    # Print results
    print(f"Markets analyzed: {session.markets_analyzed}")
    print(f"Bets placed: {session.bets_placed}")
    print(f"Initial balance: {session.initial_balance:.2f} M$")
    print(f"Final balance: {session.final_balance:.2f} M$")
    print(f"Balance change: {session.final_balance - session.initial_balance:+.2f} M$")


if __name__ == "__main__":
    import sys
    trade_all = "--all" in sys.argv
    main(trade_all=trade_all)