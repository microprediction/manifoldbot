"""
Tests for LMSR (Logarithmic Market Scoring Rule) calculations.
"""

import pytest
import math
from manifoldbot.manifold.lmsr import LMSRCalculator, calculate_market_impact, find_max_bet_by_impact


class TestLMSRCalculator:
    """Test cases for LMSRCalculator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = LMSRCalculator(liquidity_parameter=100.0)
    
    def test_probability_to_log_odds(self):
        """Test probability to log-odds conversion."""
        # Test edge cases
        assert abs(self.calculator.probability_to_log_odds(0.5) - 0.0) < 1e-10
        assert self.calculator.probability_to_log_odds(0.1) < 0
        assert self.calculator.probability_to_log_odds(0.9) > 0
        
        # Test round-trip conversion
        prob = 0.3
        log_odds = self.calculator.probability_to_log_odds(prob)
        converted_back = self.calculator.log_odds_to_probability(log_odds)
        assert abs(converted_back - prob) < 1e-10
    
    def test_log_odds_to_probability(self):
        """Test log-odds to probability conversion."""
        # Test edge cases
        assert abs(self.calculator.log_odds_to_probability(0.0) - 0.5) < 1e-10
        assert self.calculator.log_odds_to_probability(-10.0) < 0.1
        assert self.calculator.log_odds_to_probability(10.0) > 0.9
        
        # Test round-trip conversion
        log_odds = 1.0
        prob = self.calculator.log_odds_to_probability(log_odds)
        converted_back = self.calculator.probability_to_log_odds(prob)
        assert abs(converted_back - log_odds) < 1e-10
    
    def test_invalid_probability(self):
        """Test that invalid probabilities raise errors."""
        with pytest.raises(ValueError):
            self.calculator.probability_to_log_odds(0.0)
        
        with pytest.raises(ValueError):
            self.calculator.probability_to_log_odds(1.0)
        
        with pytest.raises(ValueError):
            self.calculator.probability_to_log_odds(-0.1)
        
        with pytest.raises(ValueError):
            self.calculator.probability_to_log_odds(1.1)
    
    def test_calculate_market_impact_yes_bet(self):
        """Test market impact calculation for YES bets."""
        current_prob = 0.5
        bet_amount = 10.0
        
        impact = self.calculator.calculate_market_impact(bet_amount, current_prob, "YES")
        
        # YES bet should increase probability, so impact should be positive
        assert impact > 0
        assert impact < 1.0  # Impact should be less than 100%
        
        # Larger bet should have larger impact
        larger_impact = self.calculator.calculate_market_impact(bet_amount * 2, current_prob, "YES")
        assert larger_impact > impact
    
    def test_calculate_market_impact_no_bet(self):
        """Test market impact calculation for NO bets."""
        current_prob = 0.5
        bet_amount = 10.0
        
        impact = self.calculator.calculate_market_impact(bet_amount, current_prob, "NO")
        
        # NO bet should decrease probability, so impact should be positive (absolute value)
        assert impact > 0
        assert impact < 1.0
        
        # Larger bet should have larger impact
        larger_impact = self.calculator.calculate_market_impact(bet_amount * 2, current_prob, "NO")
        assert larger_impact > impact
    
    def test_calculate_market_impact_symmetry(self):
        """Test that YES and NO bets have symmetric impact."""
        current_prob = 0.5
        bet_amount = 10.0
        
        yes_impact = self.calculator.calculate_market_impact(bet_amount, current_prob, "YES")
        no_impact = self.calculator.calculate_market_impact(bet_amount, current_prob, "NO")
        
        # At 50% probability, YES and NO bets should have equal impact
        assert abs(yes_impact - no_impact) < 1e-10
    
    def test_calculate_market_impact_zero_bet(self):
        """Test that zero bet has zero impact."""
        current_prob = 0.5
        impact = self.calculator.calculate_market_impact(0.0, current_prob, "YES")
        assert impact == 0.0
    
    def test_calculate_new_probability(self):
        """Test new probability calculation."""
        current_prob = 0.5
        bet_amount = 10.0
        
        # YES bet should increase probability
        new_prob_yes = self.calculator.calculate_new_probability(bet_amount, current_prob, "YES")
        assert new_prob_yes > current_prob
        
        # NO bet should decrease probability
        new_prob_no = self.calculator.calculate_new_probability(bet_amount, current_prob, "NO")
        assert new_prob_no < current_prob
        
        # Impact should match the difference
        yes_impact = self.calculator.calculate_market_impact(bet_amount, current_prob, "YES")
        assert abs(yes_impact - (new_prob_yes - current_prob)) < 1e-10
    
    def test_find_max_bet_by_impact(self):
        """Test finding maximum bet by impact limit."""
        current_prob = 0.5
        max_impact = 0.05  # 5% impact limit
        
        max_bet_yes = self.calculator.find_max_bet_by_impact(current_prob, "YES", max_impact)
        max_bet_no = self.calculator.find_max_bet_by_impact(current_prob, "NO", max_impact)
        
        # Should be positive
        assert max_bet_yes > 0
        assert max_bet_no > 0
        
        # Should be symmetric at 50% probability
        assert abs(max_bet_yes - max_bet_no) < 1e-10
        
        # Should respect impact limit
        actual_impact_yes = self.calculator.calculate_market_impact(max_bet_yes, current_prob, "YES")
        actual_impact_no = self.calculator.calculate_market_impact(max_bet_no, current_prob, "NO")
        
        assert actual_impact_yes <= max_impact + 1e-10  # Allow small numerical error
        assert actual_impact_no <= max_impact + 1e-10
    
    def test_find_max_bet_by_impact_edge_cases(self):
        """Test max bet calculation at edge probabilities."""
        max_impact = 0.01  # 1% impact limit
        
        # At very low probability, YES bets should be more impactful
        low_prob = 0.01
        max_bet_low = self.calculator.find_max_bet_by_impact(low_prob, "YES", max_impact)
        
        # At very high probability, NO bets should be more impactful
        high_prob = 0.99
        max_bet_high = self.calculator.find_max_bet_by_impact(high_prob, "NO", max_impact)
        
        # Both should be positive and respect limits
        assert max_bet_low > 0
        assert max_bet_high > 0
        
        # Verify impact limits are respected
        impact_low = self.calculator.calculate_market_impact(max_bet_low, low_prob, "YES")
        impact_high = self.calculator.calculate_market_impact(max_bet_high, high_prob, "NO")
        
        assert impact_low <= max_impact + 1e-10
        assert impact_high <= max_impact + 1e-10
    
    def test_invalid_outcome(self):
        """Test that invalid outcomes raise errors."""
        with pytest.raises(ValueError):
            self.calculator.calculate_market_impact(10.0, 0.5, "MAYBE")
        
        with pytest.raises(ValueError):
            self.calculator.calculate_new_probability(10.0, 0.5, "INVALID")
    
    def test_invalid_max_impact(self):
        """Test that invalid max impact values raise errors."""
        with pytest.raises(ValueError):
            self.calculator.find_max_bet_by_impact(0.5, "YES", 0.0)
        
        with pytest.raises(ValueError):
            self.calculator.find_max_bet_by_impact(0.5, "YES", 1.0)
        
        with pytest.raises(ValueError):
            self.calculator.find_max_bet_by_impact(0.5, "YES", -0.1)
        
        with pytest.raises(ValueError):
            self.calculator.find_max_bet_by_impact(0.5, "YES", 1.1)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_calculate_market_impact_function(self):
        """Test the convenience function for market impact."""
        bet_amount = 10.0
        current_prob = 0.5
        liquidity = 100.0
        outcome = "YES"
        
        impact = calculate_market_impact(bet_amount, current_prob, liquidity, outcome)
        
        # Should return positive impact
        assert impact > 0
        assert impact < 1.0
    
    def test_find_max_bet_by_impact_function(self):
        """Test the convenience function for max bet by impact."""
        current_prob = 0.5
        liquidity = 100.0
        outcome = "YES"
        max_impact = 0.05
        
        max_bet = find_max_bet_by_impact(current_prob, liquidity, outcome, max_impact)
        
        # Should return positive bet amount
        assert max_bet > 0
        
        # Should respect impact limit
        calculator = LMSRCalculator(liquidity)
        actual_impact = calculator.calculate_market_impact(max_bet, current_prob, outcome)
        assert actual_impact <= max_impact + 1e-10


class TestLMSRProperties:
    """Test mathematical properties of LMSR."""
    
    def test_liquidity_scaling(self):
        """Test that higher liquidity reduces impact."""
        bet_amount = 10.0
        current_prob = 0.5
        
        # Low liquidity
        low_liquidity_calc = LMSRCalculator(50.0)
        low_impact = low_liquidity_calc.calculate_market_impact(bet_amount, current_prob, "YES")
        
        # High liquidity
        high_liquidity_calc = LMSRCalculator(200.0)
        high_impact = high_liquidity_calc.calculate_market_impact(bet_amount, current_prob, "YES")
        
        # Higher liquidity should result in lower impact
        assert high_impact < low_impact
    
    def test_probability_sensitivity(self):
        """Test that impact varies with current probability."""
        bet_amount = 10.0
        liquidity = 100.0
        calculator = LMSRCalculator(liquidity)
        
        # Test at different probabilities
        probs = [0.1, 0.3, 0.5, 0.7, 0.9]
        impacts = []
        
        for prob in probs:
            impact = calculator.calculate_market_impact(bet_amount, prob, "YES")
            impacts.append(impact)
        
        # Impact should vary with probability (LMSR is actually more sensitive near 50%)
        # This is because the derivative of the sigmoid is highest at 0.5
        assert impacts[2] > impacts[0]  # 50% > 10%
        assert impacts[2] > impacts[4]  # 50% > 90%
        
        # All impacts should be positive
        for impact in impacts:
            assert impact > 0
    
    def test_bet_size_scaling(self):
        """Test that impact scales with bet size."""
        current_prob = 0.5
        liquidity = 100.0
        calculator = LMSRCalculator(liquidity)
        
        bet_sizes = [1.0, 5.0, 10.0, 20.0]
        impacts = []
        
        for bet_size in bet_sizes:
            impact = calculator.calculate_market_impact(bet_size, current_prob, "YES")
            impacts.append(impact)
        
        # Impact should increase with bet size
        for i in range(1, len(impacts)):
            assert impacts[i] > impacts[i-1]
    
    def test_marginal_vs_effective_probability(self):
        """Test that marginal probability is different from effective probability."""
        current_prob = 0.5
        liquidity = 100.0
        bet_amount = 20.0
        calculator = LMSRCalculator(liquidity)
        
        # Calculate both marginal and effective probabilities
        marginal_prob = calculator.calculate_marginal_probability(bet_amount, current_prob, "YES")
        effective_prob = calculator.calculate_effective_probability(bet_amount, current_prob, "YES")
        
        # Marginal should be higher than effective for YES bets (we pay more at the end)
        assert marginal_prob > effective_prob
        assert marginal_prob > current_prob  # YES bet increases probability
        
        # Both should be between current and new probability
        new_prob = calculator.calculate_new_probability(bet_amount, current_prob, "YES")
        assert current_prob <= effective_prob <= marginal_prob <= new_prob
    
    def test_marginal_probability_for_no_bets(self):
        """Test marginal probability calculation for NO bets."""
        current_prob = 0.5
        liquidity = 100.0
        bet_amount = 20.0
        calculator = LMSRCalculator(liquidity)
        
        # Calculate marginal and effective probabilities for NO bet
        marginal_prob = calculator.calculate_marginal_probability(bet_amount, current_prob, "NO")
        effective_prob = calculator.calculate_effective_probability(bet_amount, current_prob, "NO")
        
        # Marginal should be lower than effective for NO bets (we pay less at the end)
        assert marginal_prob < effective_prob
        assert marginal_prob < current_prob  # NO bet decreases probability
        
        # Both should be between new and current probability
        new_prob = calculator.calculate_new_probability(bet_amount, current_prob, "NO")
        assert new_prob <= marginal_prob <= effective_prob <= current_prob
