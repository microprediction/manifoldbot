"""
Real API tests for ManifoldWriter.

These tests require a valid MANIFOLD_API_KEY environment variable.
"""

import os
import pytest
import requests

from manifoldbot.manifold.writer import ManifoldWriter


@pytest.mark.skipif(not os.getenv("MANIFOLD_API_KEY"), reason="MANIFOLD_API_KEY not set")
class TestManifoldWriterReal:
    """Real API tests for ManifoldWriter."""

    def setup_method(self):
        """Set up test fixtures."""
        api_key = os.getenv("MANIFOLD_API_KEY")
        if not api_key:
            pytest.skip("MANIFOLD_API_KEY not set")
        
        self.writer = ManifoldWriter(api_key=api_key)

    def test_authentication(self):
        """Test that authentication works."""
        assert self.writer.is_authenticated()

    def test_get_balance(self):
        """Test getting user balance."""
        balance = self.writer.get_balance()
        assert isinstance(balance, (int, float))
        assert balance >= 0

    def test_place_bet_dry_run(self):
        """Test bet placement validation without actually placing bets."""
        # Get a real market
        markets = self.writer.get_markets(limit=1)
        if not markets:
            pytest.skip("No markets available for testing")
        
        market_id = markets[0]["id"]
        
        # Test validation without placing real bet
        with pytest.raises(ValueError, match="Outcome must be"):
            self.writer.place_bet(market_id, "INVALID", 10)

        with pytest.raises(ValueError, match="Amount must be positive"):
            self.writer.place_bet(market_id, "YES", -10)

        with pytest.raises(ValueError, match="Probability must be between"):
            self.writer.place_bet(market_id, "YES", 10, probability=1.5)

    def test_create_market_validation(self):
        """Test market creation validation."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            self.writer.create_market("", "Description")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.writer.create_market("Question", "")

    def test_get_bet(self):
        """Test getting bet details."""
        # This will likely fail with 404, but that's expected
        try:
            result = self.writer.get_bet("nonexistent_bet_id")
            # If it succeeds, check the structure
            assert isinstance(result, dict)
        except requests.RequestException as e:
            # 404 is expected for nonexistent bet
            assert e.response.status_code == 404

    def test_cancel_bet(self):
        """Test canceling a bet."""
        # This will likely fail with 404, but that's expected
        try:
            result = self.writer.cancel_bet("nonexistent_bet_id")
            # If it succeeds, check the structure
            assert isinstance(result, dict)
        except requests.RequestException as e:
            # 404 is expected for nonexistent bet
            assert e.response.status_code == 404

    def test_close_market(self):
        """Test closing a market."""
        # This will likely fail with 404, but that's expected
        try:
            result = self.writer.close_market("nonexistent_market_id", "YES")
            # If it succeeds, check the structure
            assert isinstance(result, dict)
        except requests.RequestException as e:
            # 400 or 404 is expected for nonexistent market
            assert e.response.status_code in [400, 404]

    def test_inheritance_from_reader(self):
        """Test that ManifoldWriter inherits ManifoldReader functionality."""
        # Test that we can use reader methods
        markets = self.writer.get_markets(limit=1)
        assert isinstance(markets, list)
        
        if markets:
            market = self.writer.get_market(markets[0]["id"])
            assert isinstance(market, dict)
            assert "id" in market

    def test_api_key_security(self):
        """Test that API key is properly set in headers."""
        assert "Authorization" in self.writer.session.headers
        assert self.writer.session.headers["Authorization"].startswith("Key ")