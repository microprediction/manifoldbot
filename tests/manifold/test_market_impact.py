"""
Tests for market impact calculations and limits.
"""

import pytest
from manifoldbot.manifold.bot import KellyCriterionDecisionMaker, ConfidenceBasedDecisionMaker


class TestMarketImpact:
    """Test market impact calculations."""
    
    def test_kelly_market_impact_limit(self):
        """Test that Kelly Criterion respects market impact limits."""
        kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25, max_prob_impact=0.05, min_bet=1.0, max_bet=1000.0)
        
        # Test with small market subsidy
        market_subsidy = 100.0  # 100 M$ subsidy
        
        # Calculate Kelly bet with large bankroll (should be limited by market impact)
        kelly_bet = kelly_dm.calculate_kelly_bet(
            true_prob=0.8,  # High confidence
            market_prob=0.5,  # Market at 50%
            bankroll=1000.0,  # Large bankroll
            market_subsidy=market_subsidy
        )
        
        # Should be limited by probability impact, not by Kelly calculation
        assert kelly_bet > 0  # Should still be a positive bet
        
        # Verify the actual impact is within limits
        actual_impact = kelly_dm.calculate_market_impact(
            kelly_bet, 0.5, market_subsidy, "YES"
        )
        assert actual_impact <= 0.05 + 1e-10  # Allow small numerical error
    
    def test_confidence_market_impact_limit(self):
        """Test that ConfidenceBasedDecisionMaker respects 5% market subsidy limit."""
        conf_dm = ConfidenceBasedDecisionMaker(base_bet=10.0, max_bet=1000.0)
        
        # Test with small market subsidy
        market_subsidy = 50.0  # 50 M$ subsidy
        max_allowed_bet = market_subsidy * 0.05  # 2.5 M$
        
        # Calculate bet with high confidence and large probability difference
        bet_amount = conf_dm.calculate_bet_size(
            confidence=0.9,  # High confidence
            probability_diff=0.3,  # Large difference
            market_subsidy=market_subsidy
        )
        
        # Should be limited by 5% of subsidy
        assert bet_amount <= max_allowed_bet
        assert bet_amount > 0  # Should still be a positive bet
    
    def test_market_impact_calculation(self):
        """Test market impact calculation using proper LMSR math."""
        kelly_dm = KellyCriterionDecisionMaker()
        
        # Test impact calculation with proper LMSR math
        impact = kelly_dm.calculate_market_impact(
            bet_amount=10.0, 
            current_prob=0.5, 
            market_subsidy=100.0, 
            outcome="YES"
        )
        assert impact > 0  # Should be positive
        assert impact < 1.0  # Should be less than 100%
        
        # Test with zero subsidy
        impact = kelly_dm.calculate_market_impact(
            bet_amount=10.0, 
            current_prob=0.5, 
            market_subsidy=0.0, 
            outcome="YES"
        )
        assert impact == 0.0
    
    def test_kelly_without_subsidy_data(self):
        """Test Kelly calculation when no subsidy data is available."""
        kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25, max_prob_impact=0.05, min_bet=1.0, max_bet=100.0)
        
        # Calculate Kelly bet without subsidy limit
        kelly_bet = kelly_dm.calculate_kelly_bet(
            true_prob=0.7,
            market_prob=0.5,
            bankroll=100.0,
            market_subsidy=None  # No subsidy data
        )
        
        # Should calculate normally without subsidy limit
        assert kelly_bet > 0
        assert kelly_bet <= 100.0  # Should respect max_bet limit
    
    def test_analyze_market_with_subsidy(self):
        """Test that analyze_market includes subsidy information in metadata."""
        kelly_dm = KellyCriterionDecisionMaker()
        
        # Create market with subsidy data and probability that will trigger a bet
        market = {
            "id": "test123",
            "question": "Test question",
            "probability": 0.2,  # Low probability will trigger YES bet
            "subsidy": 200.0
        }
        
        decision = kelly_dm.analyze_market(market, bankroll=100.0)
        
        # Should include subsidy information in metadata
        assert decision.metadata is not None
        assert decision.metadata["market_subsidy"] == 200.0
        assert decision.metadata["max_bet_by_impact"] == 10.0  # 5% of 200
        assert "market_impact" in decision.metadata
    
    def test_analyze_market_without_subsidy(self):
        """Test that analyze_market works without subsidy data."""
        kelly_dm = KellyCriterionDecisionMaker()
        
        # Create market without subsidy data and probability that will trigger a bet
        market = {
            "id": "test123",
            "question": "Test question",
            "probability": 0.2  # Low probability will trigger YES bet
        }
        
        decision = kelly_dm.analyze_market(market, bankroll=100.0)
        
        # Should still work and include metadata
        assert decision.metadata is not None
        assert decision.metadata["market_subsidy"] == 0
        assert decision.metadata["max_bet_by_impact"] is None
