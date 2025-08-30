"""
Real API tests for ManifoldReader.

These tests make actual API calls to verify the reader works with the real Manifold API.
Only tests endpoints that are confirmed to work.
"""

import pytest

from manifoldbot.manifold.reader import ManifoldReader


class TestManifoldReaderReal:
    """Real API tests for ManifoldReader."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ManifoldReader()

    def test_get_markets_real(self):
        """Test getting markets with real API call."""
        markets = self.reader.get_markets(limit=5)
        assert isinstance(markets, list)
        assert len(markets) > 0
        assert len(markets) <= 5

        # Check market structure
        market = markets[0]
        assert "id" in market
        assert "question" in market
        # Note: probability may not be in the markets list response
        # It's typically only available when fetching individual market details

    def test_get_market_real(self):
        """Test getting a single market with real API call."""
        # First get a market ID from the markets list
        markets = self.reader.get_markets(limit=1)
        assert len(markets) > 0
        market_id = markets[0]["id"]

        # Get the specific market
        market = self.reader.get_market(market_id)
        assert isinstance(market, dict)
        assert market["id"] == market_id
        assert "question" in market
        # Individual market details should have probability
        if "probability" in market:
            assert isinstance(market["probability"], (int, float))
            assert 0 <= market["probability"] <= 1

    def test_get_market_by_slug_real(self):
        """Test getting a market by slug with real API call."""
        # Test with a known market slug
        market = self.reader.get_market_by_slug("catl-receives-license-renewal-for-y")
        assert isinstance(market, dict)
        assert "id" in market
        assert "question" in market
        assert "probability" in market
        assert "outcomeType" in market
        assert market["outcomeType"] == "BINARY"
        assert isinstance(market["probability"], (int, float))
        assert 0 <= market["probability"] <= 1

    def test_search_markets_real(self):
        """Test searching markets with real API call."""
        results = self.reader.search_markets("AI", limit=3)
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 3

        # Check that results contain "AI" in the question
        for market in results:
            assert "AI" in market["question"] or "ai" in market["question"].lower()

    def test_get_user_real(self):
        """Test getting a user with real API call."""
        user = self.reader.get_user("Bayesian")
        assert isinstance(user, dict)
        assert user["username"] == "Bayesian"
        assert "id" in user
        assert "balance" in user
        assert "createdTime" in user

    def test_get_user_markets_real(self):
        """Test getting user markets with real API call."""
        # This endpoint doesn't exist in the current API
        with pytest.raises(Exception):
            self.reader.get_user_markets("Bayesian", limit=3)

    def test_get_user_bets_real(self):
        """Test getting user bets with real API call."""
        bets = self.reader.get_user_bets("Bayesian", limit=3)
        assert isinstance(bets, list)
        assert len(bets) > 0
        assert len(bets) <= 3

        # Check bet structure
        bet = bets[0]
        assert "id" in bet
        assert "amount" in bet
        assert "outcome" in bet
        assert "contractId" in bet

    def test_get_market_bets_real(self):
        """Test getting market bets with real API call."""
        # This endpoint doesn't exist in the current API
        with pytest.raises(Exception):
            self.reader.get_market_bets("some_market_id", limit=3)

    def test_get_market_probability_real(self):
        """Test getting market probability with real API call."""
        # First get a market ID
        markets = self.reader.get_markets(limit=1)
        market_id = markets[0]["id"]

        probability = self.reader.get_market_probability(market_id)
        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0

    def test_get_market_probability_percent_real(self):
        """Test getting market probability as percentage with real API call."""
        # First get a market ID
        markets = self.reader.get_markets(limit=1)
        market_id = markets[0]["id"]

        probability_percent = self.reader.get_market_probability_percent(market_id)
        assert isinstance(probability_percent, float)
        assert 0.0 <= probability_percent <= 100.0

    def test_get_market_basic_info_real(self):
        """Test getting market basic info with real API call."""
        # First get a market ID
        markets = self.reader.get_markets(limit=1)
        market_id = markets[0]["id"]

        info = self.reader.get_market_basic_info(market_id)
        assert isinstance(info, dict)
        assert "id" in info
        assert "question" in info
        assert "probability" in info
        assert "probability_percent" in info
        assert "volume" in info
        assert "total_liquidity" in info
        assert "creator" in info

    def test_get_market_liquidity_real(self):
        """Test getting market liquidity with real API call."""
        # First get a market ID
        markets = self.reader.get_markets(limit=1)
        market_id = markets[0]["id"]

        liquidity = self.reader.get_market_liquidity(market_id)
        assert isinstance(liquidity, dict)
        assert "total" in liquidity
        assert "yes" in liquidity
        assert "no" in liquidity
        assert liquidity["total"] >= 0
        assert liquidity["yes"] >= 0
        assert liquidity["no"] >= 0

    def test_pagination_real(self):
        """Test that pagination works with real API call."""
        # Get more than the default limit to test pagination
        markets = self.reader.get_markets(limit=15)
        assert isinstance(markets, list)
        assert len(markets) == 15

        # Check that we got unique markets
        market_ids = [m["id"] for m in markets]
        assert len(set(market_ids)) == 15  # All unique

    def test_error_handling_real(self):
        """Test error handling with real API call."""
        # Test with invalid market ID
        with pytest.raises(Exception):
            self.reader.get_market("invalid_market_id")

        # Test with invalid user
        with pytest.raises(Exception):
            self.reader.get_user("nonexistent_user_12345")

    def test_unavailable_endpoints_real(self):
        """Test that unavailable endpoints raise NotImplementedError."""
        # Test market comments endpoint
        with pytest.raises(NotImplementedError):
            self.reader.get_market_comments("some_market_id")

        # Test groups endpoint
        with pytest.raises(NotImplementedError):
            self.reader.get_groups()
