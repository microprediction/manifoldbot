"""
Advanced example: Different bet sizing strategies.

This shows various approaches to determining bet sizes.
"""

import os
from manifoldbot import ManifoldBot, SimpleRuleDecisionMaker, KellyCriterionDecisionMaker, ConfidenceBasedDecisionMaker


def main():
    # Get API key
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        print("Error: MANIFOLD_API_KEY not set")
        return
    
    # Example 1: Simple rule-based betting
    print("1. Simple Rule-Based Betting:")
    simple_dm = SimpleRuleDecisionMaker(fixed_bet=10)
    bot1 = ManifoldBot(manifold_api_key=api_key, decision_maker=simple_dm)
    
    # Example 2: Kelly Criterion betting
    print("2. Kelly Criterion Betting:")
    kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25, max_prob_impact=0.05)
    bot2 = ManifoldBot(manifold_api_key=api_key, decision_maker=kelly_dm)
    
    # Example 3: Confidence-based betting
    print("3. Confidence-Based Betting:")
    confidence_dm = ConfidenceBasedDecisionMaker(min_confidence=0.7)
    bot3 = ManifoldBot(manifold_api_key=api_key, decision_maker=confidence_dm)
    
    print("All decision makers created successfully!")


if __name__ == "__main__":
    main()
