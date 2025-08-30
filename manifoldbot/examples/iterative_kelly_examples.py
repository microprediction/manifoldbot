"""
Examples of Iterative Fractional Kelly Betting

This module demonstrates how the iterative Kelly Criterion works with market impact,
showing the difference between simple Kelly and iterative Kelly approaches.
"""

import math
from manifoldbot.manifold.bot import KellyCriterionDecisionMaker
from manifoldbot.manifold.lmsr import LMSRCalculator


def example_1_simple_vs_iterative_kelly():
    """Compare simple Kelly vs iterative Kelly with market impact."""
    print("=== Example 1: Simple vs Iterative Kelly ===\n")
    
    # Market parameters
    true_prob = 0.7  # We think the true probability is 70%
    market_prob = 0.5  # Market is trading at 50%
    bankroll = 1000.0  # $1000 bankroll
    market_subsidy = 100.0  # $100 market subsidy
    kelly_fraction = 0.25  # Use 25% of Kelly
    
    print(f"True Probability: {true_prob:.1%}")
    print(f"Market Probability: {market_prob:.1%}")
    print(f"Bankroll: ${bankroll:.0f}")
    print(f"Market Subsidy: ${market_subsidy:.0f}")
    print(f"Kelly Fraction: {kelly_fraction:.1%}\n")
    
    # Simple Kelly (ignoring market impact)
    simple_b = (1 / market_prob) - 1
    simple_kelly = (simple_b * true_prob - (1 - true_prob)) / simple_b
    simple_bet = simple_kelly * kelly_fraction * bankroll
    
    print("Simple Kelly (ignoring market impact):")
    print(f"  Kelly Fraction: {simple_kelly:.1%}")
    print(f"  Bet Size: ${simple_bet:.2f}")
    
    # Calculate actual market impact of simple bet
    calculator = LMSRCalculator(market_subsidy)
    outcome = "YES" if true_prob > market_prob else "NO"
    actual_impact = calculator.calculate_market_impact(simple_bet, market_prob, outcome)
    marginal_prob = calculator.calculate_marginal_probability(simple_bet, market_prob, outcome)
    
    print(f"  Market Impact: {actual_impact:.1%}")
    print(f"  Marginal Probability: {marginal_prob:.1%}")
    print(f"  Effective Edge: {true_prob - marginal_prob:.1%}\n")
    
    # Iterative Kelly (accounting for market impact)
    kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=kelly_fraction, max_prob_impact=0.05)
    iterative_bet = kelly_dm.calculate_kelly_bet(
        true_prob, market_prob, bankroll, market_subsidy
    )
    
    # Calculate impact of iterative bet
    iterative_impact = calculator.calculate_market_impact(iterative_bet, market_prob, outcome)
    iterative_marginal = calculator.calculate_marginal_probability(iterative_bet, market_prob, outcome)
    
    print("Iterative Kelly (accounting for market impact):")
    print(f"  Bet Size: ${iterative_bet:.2f}")
    print(f"  Market Impact: {iterative_impact:.1%}")
    print(f"  Marginal Probability: {iterative_marginal:.1%}")
    print(f"  Effective Edge: {true_prob - iterative_marginal:.1%}\n")
    
    print("Key Insights:")
    print("- Simple Kelly overestimates bet size by ignoring market impact")
    print("- Iterative Kelly finds the optimal bet size where Kelly Criterion is satisfied")
    print("- Iterative approach prevents over-betting due to slippage\n")


def example_2_different_kelly_fractions():
    """Show how different Kelly fractions affect betting behavior."""
    print("=== Example 2: Different Kelly Fractions ===\n")
    
    # Market parameters
    true_prob = 0.65
    market_prob = 0.4
    bankroll = 2000.0
    market_subsidy = 200.0
    
    print(f"True Probability: {true_prob:.1%}")
    print(f"Market Probability: {market_prob:.1%}")
    print(f"Bankroll: ${bankroll:.0f}")
    print(f"Market Subsidy: ${market_subsidy:.0f}\n")
    
    kelly_fractions = [0.1, 0.25, 0.5, 1.0]  # 10%, 25%, 50%, 100% of Kelly
    
    print("Kelly Fraction | Bet Size | Market Impact | Marginal Prob | Effective Edge")
    print("-" * 75)
    
    calculator = LMSRCalculator(market_subsidy)
    outcome = "YES" if true_prob > market_prob else "NO"
    
    for kf in kelly_fractions:
        kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=kf, max_prob_impact=0.1)
        bet = kelly_dm.calculate_kelly_bet(
            true_prob, market_prob, bankroll, market_subsidy
        )
        
        impact = calculator.calculate_market_impact(bet, market_prob, outcome)
        marginal = calculator.calculate_marginal_probability(bet, market_prob, outcome)
        edge = true_prob - marginal
        
        print(f"{kf:>11.0%} | ${bet:>7.2f} | {impact:>11.1%} | {marginal:>11.1%} | {edge:>12.1%}")
    
    print("\nKey Insights:")
    print("- Higher Kelly fractions lead to larger bets and more market impact")
    print("- There's a trade-off between bet size and slippage")
    print("- Fractional Kelly (25%) is often optimal for risk management\n")


def example_3_market_impact_limits():
    """Demonstrate how market impact limits affect Kelly betting."""
    print("=== Example 3: Market Impact Limits ===\n")
    
    # Market parameters
    true_prob = 0.8
    market_prob = 0.3
    bankroll = 5000.0
    market_subsidy = 50.0  # Small market = high impact
    kelly_fraction = 0.25
    
    print(f"True Probability: {true_prob:.1%}")
    print(f"Market Probability: {market_prob:.1%}")
    print(f"Bankroll: ${bankroll:.0f}")
    print(f"Market Subsidy: ${market_subsidy:.0f} (small market)")
    print(f"Kelly Fraction: {kelly_fraction:.1%}\n")
    
    impact_limits = [0.01, 0.02, 0.05, 0.1, 0.2]  # 1%, 2%, 5%, 10%, 20% max impact
    
    print("Max Impact | Bet Size | Actual Impact | Marginal Prob | Kelly Satisfied")
    print("-" * 70)
    
    calculator = LMSRCalculator(market_subsidy)
    outcome = "YES" if true_prob > market_prob else "NO"
    
    for max_impact in impact_limits:
        kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=kelly_fraction, max_prob_impact=max_impact)
        bet = kelly_dm.calculate_kelly_bet(
            true_prob, market_prob, bankroll, market_subsidy
        )
        
        actual_impact = calculator.calculate_market_impact(bet, market_prob, outcome)
        marginal = calculator.calculate_marginal_probability(bet, market_prob, outcome)
        
        # Check if Kelly Criterion is satisfied
        b = (1 / marginal) - 1
        kelly_calc = (b * true_prob - (1 - true_prob)) / b
        desired_bet = kelly_calc * kelly_fraction * bankroll
        kelly_satisfied = abs(bet - desired_bet) < 1.0
        
        print(f"{max_impact:>9.0%} | ${bet:>7.2f} | {actual_impact:>12.1%} | {marginal:>11.1%} | {kelly_satisfied:>13}")
    
    print("\nKey Insights:")
    print("- Stricter impact limits reduce bet sizes")
    print("- Kelly Criterion may not be fully satisfied with tight limits")
    print("- Balance between optimal Kelly sizing and market impact\n")


def example_4_iterative_convergence():
    """Show how the iterative algorithm converges to optimal bet size."""
    print("=== Example 4: Iterative Convergence ===\n")
    
    # Market parameters
    true_prob = 0.6
    market_prob = 0.45
    bankroll = 1000.0
    market_subsidy = 100.0
    kelly_fraction = 0.25
    
    print(f"True Probability: {true_prob:.1%}")
    print(f"Market Probability: {market_prob:.1%}")
    print(f"Bankroll: ${bankroll:.0f}")
    print(f"Market Subsidy: ${market_subsidy:.0f}")
    print(f"Kelly Fraction: {kelly_fraction:.1%}\n")
    
    # Simulate the iterative process
    calculator = LMSRCalculator(market_subsidy)
    outcome = "YES" if true_prob > market_prob else "NO"
    
    print("Iteration | Bet Size | Marginal Prob | Kelly % | Desired Bet | Difference")
    print("-" * 70)
    
    # Binary search simulation
    low, high = 0.0, bankroll
    for iteration in range(10):
        mid = (low + high) / 2
        
        # Calculate marginal probability for this bet size
        marginal_prob = calculator.calculate_marginal_probability(mid, market_prob, outcome)
        
        # Calculate Kelly fraction with marginal probability
        b = (1 / marginal_prob) - 1
        kelly_fraction_calc = (b * true_prob - (1 - true_prob)) / b
        
        # Calculate desired bet size based on Kelly
        desired_bet = kelly_fraction_calc * kelly_fraction * bankroll
        
        difference = abs(mid - desired_bet)
        
        print(f"{iteration:>9} | ${mid:>7.2f} | {marginal_prob:>11.1%} | {kelly_fraction_calc:>6.1%} | ${desired_bet:>10.2f} | ${difference:>9.2f}")
        
        # Binary search logic
        if kelly_fraction_calc <= 0:
            high = mid
        elif abs(mid - desired_bet) < 0.01:
            break
        elif mid < desired_bet:
            low = mid
        else:
            high = mid
    
    print(f"\nFinal optimal bet: ${mid:.2f}")
    print(f"Convergence achieved in {iteration + 1} iterations\n")


def example_5_edge_cases():
    """Test edge cases in iterative Kelly betting."""
    print("=== Example 5: Edge Cases ===\n")
    
    # Test cases: (true_prob, market_prob, bankroll, market_subsidy, description)
    test_cases = [
        (0.55, 0.5, 1000.0, 100.0, "Small edge"),
        (0.9, 0.1, 1000.0, 100.0, "Large edge"),
        (0.51, 0.5, 1000.0, 10.0, "Small market"),
        (0.6, 0.4, 100.0, 1000.0, "Small bankroll"),
        (0.5, 0.5, 1000.0, 100.0, "No edge"),
    ]
    
    kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25)
    
    print("Case | True | Market | Bet Size | Impact | Edge")
    print("-" * 50)
    
    for i, (true_prob, market_prob, bankroll, market_subsidy, description) in enumerate(test_cases, 1):
        bet = kelly_dm.calculate_kelly_bet(
            true_prob, market_prob, bankroll, market_subsidy
        )
        
        if bet > 0:
            calculator = LMSRCalculator(market_subsidy)
            outcome = "YES" if true_prob > market_prob else "NO"
            impact = calculator.calculate_market_impact(bet, market_prob, outcome)
            marginal = calculator.calculate_marginal_probability(bet, market_prob, outcome)
            edge = true_prob - marginal
        else:
            impact = 0.0
            edge = 0.0
        
        print(f"{i:>4} | {true_prob:>4.1%} | {market_prob:>6.1%} | ${bet:>7.2f} | {impact:>6.1%} | {edge:>4.1%}")
    
    print(f"\nTest cases: {', '.join([case[4] for case in test_cases])}")
    print("\nKey Insights:")
    print("- No bet when there's no edge (true_prob = market_prob)")
    print("- Bet size scales with edge size and bankroll")
    print("- Small markets limit bet sizes due to impact\n")


if __name__ == "__main__":
    print("Iterative Fractional Kelly Betting Examples\n")
    print("=" * 50)
    
    example_1_simple_vs_iterative_kelly()
    example_2_different_kelly_fractions()
    example_3_market_impact_limits()
    example_4_iterative_convergence()
    example_5_edge_cases()
    
    print("All examples completed!")
