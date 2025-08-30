"""
ManifoldBot Framework Example

This example shows how to use the ManifoldBot class with different
decision makers for a more modular approach.
"""

import os
from manifoldbot import ManifoldBot, RandomDecisionMaker


def main():
    # Get API key
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        print("Error: MANIFOLD_API_KEY not set")
        return
    
    # Create a decision maker
    decision_maker = RandomDecisionMaker()
    
    # Create bot with the decision maker
    bot = ManifoldBot(
        manifold_api_key=api_key,
        decision_maker=decision_maker
    )
    
    # Run on recent markets
    session = bot.run_on_recent_markets(
        limit=5,
        bet_amount=5,
        max_bets=2
    )
    
    print(f"Markets analyzed: {session.markets_analyzed}")
    print(f"Bets placed: {session.bets_placed}")


if __name__ == "__main__":
    main()
