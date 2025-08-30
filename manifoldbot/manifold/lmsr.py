"""
Logarithmic Market Scoring Rule (LMSR) calculations for Manifold Markets.

This module provides accurate calculations for:
- Market impact of bets
- Probability changes
- Optimal bet sizing with impact limits
"""

import math
from typing import Tuple, Optional


class LMSRCalculator:
    """
    Calculator for Logarithmic Market Scoring Rule operations.
    
    Manifold Markets uses LMSR with the formula:
    P = 1 / (1 + exp(-(q_yes - q_no) / b))
    
    where:
    - P is the market probability
    - q_yes is the total amount bet on YES
    - q_no is the total amount bet on NO  
    - b is the liquidity parameter (market subsidy)
    """
    
    def __init__(self, liquidity_parameter: float):
        """
        Initialize LMSR calculator.
        
        Args:
            liquidity_parameter: The 'b' parameter in LMSR (market subsidy)
        """
        self.b = liquidity_parameter
    
    def probability_to_log_odds(self, prob: float) -> float:
        """
        Convert probability to log-odds.
        
        Args:
            prob: Probability (0.0 to 1.0)
            
        Returns:
            Log-odds value
        """
        if prob <= 0 or prob >= 1:
            raise ValueError(f"Probability must be between 0 and 1, got {prob}")
        return math.log(prob / (1 - prob))
    
    def log_odds_to_probability(self, log_odds: float) -> float:
        """
        Convert log-odds to probability.
        
        Args:
            log_odds: Log-odds value
            
        Returns:
            Probability (0.0 to 1.0)
        """
        return 1 / (1 + math.exp(-log_odds))
    
    def calculate_market_impact(self, bet_amount: float, current_prob: float, outcome: str) -> float:
        """
        Calculate the actual price impact of a bet on the LMSR market.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            Absolute change in probability (0.0 to 1.0)
        """
        if bet_amount <= 0:
            return 0.0
        
        if outcome not in ["YES", "NO"]:
            raise ValueError(f"Outcome must be 'YES' or 'NO', got {outcome}")
        
        # Convert current probability to log-odds
        current_log_odds = self.probability_to_log_odds(current_prob)
        
        # Calculate the change in log-odds from the bet
        if outcome == "YES":
            # Betting YES increases the log-odds
            log_odds_change = bet_amount / self.b
        else:  # NO
            # Betting NO decreases the log-odds
            log_odds_change = -bet_amount / self.b
        
        # New log-odds
        new_log_odds = current_log_odds + log_odds_change
        
        # Convert back to probability
        new_prob = self.log_odds_to_probability(new_log_odds)
        
        # Return absolute change in probability
        return abs(new_prob - current_prob)
    
    def calculate_new_probability(self, bet_amount: float, current_prob: float, outcome: str) -> float:
        """
        Calculate the new market probability after placing a bet.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            New market probability after the bet
        """
        if bet_amount <= 0:
            return current_prob
        
        if outcome not in ["YES", "NO"]:
            raise ValueError(f"Outcome must be 'YES' or 'NO', got {outcome}")
        
        # Convert current probability to log-odds
        current_log_odds = self.probability_to_log_odds(current_prob)
        
        # Calculate the change in log-odds from the bet
        if outcome == "YES":
            log_odds_change = bet_amount / self.b
        else:  # NO
            log_odds_change = -bet_amount / self.b
        
        # New log-odds
        new_log_odds = current_log_odds + log_odds_change
        
        # Convert back to probability
        return self.log_odds_to_probability(new_log_odds)
    
    def find_max_bet_by_impact(self, current_prob: float, outcome: str, max_impact: float) -> float:
        """
        Find the maximum bet size that doesn't exceed the probability impact limit.
        
        Args:
            current_prob: Current market probability
            outcome: "YES" or "NO"
            max_impact: Maximum allowed probability change (0.0 to 1.0)
            
        Returns:
            Maximum bet amount that stays within impact limit
        """
        if max_impact <= 0 or max_impact >= 1:
            raise ValueError(f"Max impact must be between 0 and 1, got {max_impact}")
        
        # Binary search to find max bet
        low, high = 0.0, self.b * 10  # Start with 10x liquidity as upper bound
        
        for _ in range(50):  # More iterations for precision
            mid = (low + high) / 2
            impact = self.calculate_market_impact(mid, current_prob, outcome)
            
            if impact <= max_impact:
                low = mid
            else:
                high = mid
        
        return low
    
    def calculate_bet_cost(self, bet_amount: float, current_prob: float, outcome: str) -> float:
        """
        Calculate the cost of placing a bet (including slippage).
        
        For LMSR, this is the integral of the price function from current to new probability.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            Total cost of the bet
        """
        if bet_amount <= 0:
            return 0.0
        
        new_prob = self.calculate_new_probability(bet_amount, current_prob, outcome)
        
        # For LMSR, the cost is: b * ln(1 + exp((q_yes - q_no) / b))
        # This is a simplified approximation
        current_log_odds = self.probability_to_log_odds(current_prob)
        new_log_odds = self.probability_to_log_odds(new_prob)
        
        # Cost is proportional to the change in log-odds
        cost = self.b * abs(new_log_odds - current_log_odds)
        
        return cost
    
    def calculate_marginal_probability(self, bet_amount: float, current_prob: float, outcome: str) -> float:
        """
        Calculate the marginal probability (price at the end of the bet).
        
        This is the probability we get for the last unit of the bet,
        which is what Kelly Criterion should use.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            Marginal probability (price at end of bet)
        """
        if bet_amount <= 0:
            return current_prob
        
        # The marginal probability is simply the new probability after the bet
        return self.calculate_new_probability(bet_amount, current_prob, outcome)
    
    def calculate_effective_probability(self, bet_amount: float, current_prob: float, outcome: str) -> float:
        """
        Calculate the effective probability we get when placing a bet.
        
        This is the average probability we pay, accounting for slippage.
        It's the integral of the price function divided by the bet amount.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            Effective probability (average price paid)
        """
        if bet_amount <= 0:
            return current_prob
        
        new_prob = self.calculate_new_probability(bet_amount, current_prob, outcome)
        
        # For small bets, the effective probability is approximately the midpoint
        # For larger bets, we need to integrate the price function
        # This is a simplified approximation using the average
        if outcome == "YES":
            # For YES bets, we pay prices from current_prob to new_prob
            # The average is approximately the midpoint
            effective_prob = (current_prob + new_prob) / 2
        else:
            # For NO bets, we pay (1 - probability) from (1 - current_prob) to (1 - new_prob)
            # The average is approximately the midpoint
            effective_prob = (current_prob + new_prob) / 2
        
        return effective_prob


def calculate_market_impact(bet_amount: float, current_prob: float, liquidity: float, outcome: str) -> float:
    """
    Convenience function to calculate market impact.
    
    Args:
        bet_amount: Amount of the bet
        current_prob: Current market probability
        liquidity: Market liquidity parameter
        outcome: "YES" or "NO"
        
    Returns:
        Absolute change in probability
    """
    calculator = LMSRCalculator(liquidity)
    return calculator.calculate_market_impact(bet_amount, current_prob, outcome)


def find_max_bet_by_impact(current_prob: float, liquidity: float, outcome: str, max_impact: float) -> float:
    """
    Convenience function to find max bet by impact.
    
    Args:
        current_prob: Current market probability
        liquidity: Market liquidity parameter
        outcome: "YES" or "NO"
        max_impact: Maximum allowed probability change
        
    Returns:
        Maximum bet amount
    """
    calculator = LMSRCalculator(liquidity)
    return calculator.find_max_bet_by_impact(current_prob, outcome, max_impact)
