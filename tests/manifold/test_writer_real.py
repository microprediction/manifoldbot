"""
Real API tests for ManifoldWriter.

Tests the authenticated client with actual Manifold Markets API calls.
These tests require a valid MANIFOLD_API_KEY.
"""

import os
import pytest
import requests
from manifoldbot.manifold.writer import ManifoldWriter


class TestManifoldWriterReal:
    """Real API tests for ManifoldWriter."""

    def setup_method(self):
        """Set up test fixtures."""
        api_key = os.getenv("MANIFOLD_API_KEY")
        if not api_key:
            pytest.skip("MANIFOLD_API_KEY not set - skipping real API tests")
        
        self.writer = ManifoldWriter(api_key=api_key)
        
        # Verify authentication works
        if not self.writer.is_authenticated():
            pytest.skip("Authentication failed - check API key")

    def test_authentication(self):
        """Test that authentication works."""
        assert self.writer.is_authenticated()
        
        # Get user info
        user = self.writer.get_me()
        assert isinstance(user, dict)
        assert "id" in user
        assert "name" in user
        assert "balance" in user

    def test_get_balance(self):
        """Test getting user balance."""
        balance = self.writer.get_balance()
        assert isinstance(balance, (int, float))
        assert balance >= 0

    def test_get_portfolio(self):
        """Test getting portfolio."""
        portfolio = self.writer.get_portfolio()
        assert isinstance(portfolio, dict)
        assert "balance" in portfolio

    def test_get_positions(self):
        """Test getting user positions."""
        positions = self.writer.get_positions()
        assert isinstance(positions, list)
        # Positions can be empty, that's fine

    def test_calculate_market_impact(self):
        """Test market impact calculation."""
        # Use a real market for testing
        markets = self.writer.get_markets(limit=1)
        if not markets:
            pytest.skip("No markets available for testing")
        
        market_id = markets[0]["id"]
        impact = self.writer.calculate_market_impact(market_id, 10, "YES")
        
        assert isinstance(impact, dict)
        assert "current_probability" in impact
        assert "estimated_impact" in impact
        assert "new_probability" in impact
        assert "liquidity" in impact

    def test_place_bet_dry_run(self):
        """Test bet placement validation without actually placing bets."""
        # Get a real market
        markets = self.writer.get_markets(limit=1)
        if not markets:
            pytest.skip("No markets available for testing")
        
        market_id = markets[0]["id"]
        
        # Test validation
        with pytest.raises(ValueError, match="Outcome must be 'YES' or 'NO'"):
            self.writer.place_bet(market_id, "INVALID", 10)
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            self.writer.place_bet(market_id, "YES", -5)
        
        with pytest.raises(ValueError, match="Probability must be between 0 and 1"):
            self.writer.place_bet(market_id, "YES", 10, probability=1.5)

    def test_place_bet_with_impact_limit(self):
        """Test placing bet with impact limit (should reduce bet size if needed)."""
        # Get a real market
        markets = self.writer.get_markets(limit=1)
        if not markets:
            pytest.skip("No markets available for testing")
        
        market_id = markets[0]["id"]
        
        # Test with a very small impact limit
        # This should either place a very small bet or skip entirely
        try:
            result = self.writer.place_bet_with_impact_limit(
                market_id, "YES", 100, max_impact=0.001  # 0.1% max impact
            )
            # If it succeeds, it should be a very small bet
            assert isinstance(result, dict)
        except requests.RequestException as e:
            # API errors are acceptable for this test
            # (e.g., insufficient balance, market closed, etc.)
            assert "error" in str(e).lower() or "exception" in str(e).lower()

    def test_create_market_validation(self):
        """Test market creation validation."""
        # Test validation without actually creating markets
        with pytest.raises(ValueError, match="Question cannot be empty"):
            self.writer.create_market("", "Description")
        
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.writer.create_market("Question", "")

    def test_post_comment_validation(self):
        """Test comment posting validation."""
        # Get a real market for testing
        markets = self.writer.get_markets(limit=1)
        if not markets:
            pytest.skip("No markets available for testing")
        
        market_id = markets[0]["id"]
        
        # Test validation
        with pytest.raises(ValueError, match="Comment text cannot be empty"):
            self.writer.post_comment(market_id, "")

    def test_get_bet(self):
        """Test getting bet details (if user has any bets)."""
        # This will only work if the user has placed bets
        # We'll test the method exists and handles errors gracefully
        try:
            # Try to get a non-existent bet
            self.writer.get_bet("non_existent_bet_id")
            assert False, "Should have raised an exception"
        except requests.RequestException:
            # Expected behavior for non-existent bet
            pass

    def test_cancel_bet(self):
        """Test canceling a bet (if user has any pending bets)."""
        # This will only work if the user has pending bets
        # We'll test the method exists and handles errors gracefully
        try:
            # Try to cancel a non-existent bet
            self.writer.cancel_bet("non_existent_bet_id")
            assert False, "Should have raised an exception"
        except requests.RequestException:
            # Expected behavior for non-existent bet
            pass

    def test_close_market(self):
        """Test closing a market (if user owns any markets)."""
        # This will only work if the user owns markets
        # We'll test the method exists and handles errors gracefully
        try:
            # Try to close a market the user doesn't own
            markets = self.writer.get_markets(limit=1)
            if markets:
                market_id = markets[0]["id"]
                self.writer.close_market(market_id, "YES")
                assert False, "Should have raised an exception"
        except requests.RequestException:
            # Expected behavior for market user doesn't own
            pass

    def test_inheritance_from_reader(self):
        """Test that ManifoldWriter inherits all ManifoldReader functionality."""
        # Test that writer can do everything reader can do
        markets = self.writer.get_markets(limit=1)
        assert isinstance(markets, list)
        
        if markets:
            market_id = markets[0]["id"]
            market = self.writer.get_market(market_id)
            assert isinstance(market, dict)
            assert "id" in market

    def test_api_key_security(self):
        """Test that API key is properly set in headers."""
        assert "Authorization" in self.writer.session.headers
        assert self.writer.session.headers["Authorization"].startswith("Key ")
        assert self.writer.api_key is not None
