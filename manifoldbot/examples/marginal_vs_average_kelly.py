"""
Example demonstrating the difference between using marginal vs average probability
in Kelly Criterion calculations for LMSR markets.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manifoldbot.manifold.lmsr import LMSRCalculator


def compare_kelly_calculations():
    """Compare Kelly Criterion using marginal vs average probability."""
    
    # Market parameters
    current_prob = 0.5  # Market at 50%
    true_prob = 0.6     # We think it should be 60%
    liquidity = 100.0   # Market liquidity
    bankroll = 1000.0   # Our bankroll
    kelly_fraction = 0.25  # 25% of Kelly
    
    calculator = LMSRCalculator(liquidity)
    
    print("=== Kelly Criterion: Marginal vs Average Probability ===\n")
    print(f"Market Probability: {current_prob:.1%}")
    print(f"Our True Probability: {true_prob:.1%}")
    print(f"Market Liquidity: {liquidity:.0f} M$")
    print(f"Our Bankroll: {bankroll:.0f} M$")
    print(f"Kelly Fraction: {kelly_fraction:.1%}\n")
    
    # Test different bet sizes
    bet_sizes = [5.0, 10.0, 20.0, 50.0]
    
    print("Bet Size | Marginal Prob | Average Prob | Kelly (Marginal) | Kelly (Average)")
    print("-" * 80)
    
    for bet_size in bet_sizes:
        # Calculate probabilities
        marginal_prob = calculator.calculate_marginal_probability(bet_size, current_prob, "YES")
        average_prob = calculator.calculate_effective_probability(bet_size, current_prob, "YES")
        
        # Calculate Kelly fractions
        # Kelly = (bp - q) / b, where b = (1/p - 1)
        marginal_b = (1 / marginal_prob) - 1
        marginal_kelly = (marginal_b * true_prob - (1 - true_prob)) / marginal_b
        
        average_b = (1 / average_prob) - 1
        average_kelly = (average_b * true_prob - (1 - true_prob)) / average_b
        
        # Calculate bet amounts
        marginal_bet = marginal_kelly * kelly_fraction * bankroll
        average_bet = average_kelly * kelly_fraction * bankroll
        
        print(f"{bet_size:8.1f} | {marginal_prob:12.1%} | {average_prob:11.1%} | {marginal_bet:15.1f} | {average_bet:13.1f}")
    
    print("\n=== Key Insights ===")
    print("1. Marginal probability is higher than average (we pay more at the end)")
    print("2. Kelly with marginal probability is more conservative (smaller bets)")
    print("3. Kelly with average probability overestimates our edge")
    print("4. Using marginal probability is mathematically correct for Kelly Criterion")
    
    # Show the optimal bet size using marginal probability
    print(f"\n=== Optimal Bet Size Calculation ===")
    
    # Find the bet size where Kelly Criterion is satisfied with marginal probability
    optimal_bet = find_optimal_kelly_bet(calculator, true_prob, current_prob, bankroll, kelly_fraction)
    
    if optimal_bet > 0:
        marginal_prob_optimal = calculator.calculate_marginal_probability(optimal_bet, current_prob, "YES")
        impact = calculator.calculate_market_impact(optimal_bet, current_prob, "YES")
        
        print(f"Optimal Bet Size: {optimal_bet:.2f} M$")
        print(f"Marginal Probability: {marginal_prob_optimal:.1%}")
        print(f"Market Impact: {impact:.1%}")
        
        # Verify Kelly Criterion
        b = (1 / marginal_prob_optimal) - 1
        kelly = (b * true_prob - (1 - true_prob)) / b
        print(f"Kelly Fraction: {kelly:.1%}")
        print(f"Desired Bet: {kelly * kelly_fraction * bankroll:.2f} M$")
    else:
        print("No positive edge found with marginal probability")


def find_optimal_kelly_bet(calculator, true_prob, current_prob, bankroll, kelly_fraction, max_iterations=50):
    """Find the bet size where Kelly Criterion is satisfied with marginal probability."""
    
    low, high = 0.0, bankroll
    
    for _ in range(max_iterations):
        mid = (low + high) / 2
        
        # Calculate marginal probability for this bet size
        marginal_prob = calculator.calculate_marginal_probability(mid, current_prob, "YES")
        
        # Calculate Kelly fraction with marginal probability
        b = (1 / marginal_prob) - 1
        kelly_fraction_calc = (b * true_prob - (1 - true_prob)) / b
        
        # Calculate desired bet size based on Kelly
        desired_bet = kelly_fraction_calc * kelly_fraction * bankroll
        
        if kelly_fraction_calc <= 0:
            # No positive edge
            high = mid
        elif abs(mid - desired_bet) < 0.01:  # Close enough
            return mid
        elif mid < desired_bet:
            low = mid
        else:
            high = mid
    
    return mid


if __name__ == "__main__":
    compare_kelly_calculations()
