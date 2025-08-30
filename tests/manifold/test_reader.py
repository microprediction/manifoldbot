"""
Unit tests for ManifoldReader.

Tests the read-only client for Manifold Markets API.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from manifoldbot.manifold.reader import ManifoldReader


class TestManifoldReader:
    """Test cases for ManifoldReader."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ManifoldReader()

    def test_init(self):
        """Test ManifoldReader initialization."""
        reader = ManifoldReader(timeout=60)

        assert reader.timeout == 60
        assert reader.BASE_URL == "https://api.manifold.markets/v0"
        assert reader.retry_config["max_retries"] == 3
        assert "User-Agent" in reader.session.headers
        assert reader.session.headers["User-Agent"] == "ManifoldBot/0.1.0"

    def test_init_custom_retry_config(self):
        """Test initialization with custom retry config."""
        custom_config = {"max_retries": 5, "backoff_factor": 3, "retry_on": [500, 502]}
        reader = ManifoldReader(retry_config=custom_config)

        assert reader.retry_config == custom_config

    @patch("manifoldbot.manifold.reader.requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test", "question": "Test market?"}
        mock_request.return_value = mock_response

        result = self.reader._make_request("GET", "market/test123")

        assert result == {"id": "test", "question": "Test market?"}
        mock_request.assert_called_once()

    @patch("manifoldbot.manifold.reader.requests.Session.request")
    def test_make_request_with_params(self, mock_request):
        """Test API request with parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1"}, {"id": "2"}]
        mock_request.return_value = mock_response

        params = {"q": "test query", "limit": 10}
        result = self.reader._make_request("GET", "search-markets", params=params)

        assert result == [{"id": "1"}, {"id": "2"}]
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"] == params

    @patch("manifoldbot.manifold.reader.requests.Session.request")
    def test_make_request_retry_on_429(self, mock_request):
        """Test retry logic on 429 status code."""
        # First call returns 429, second call succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"success": True}

        mock_request.side_effect = [mock_response_429, mock_response_200]

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = self.reader._make_request("GET", "test")

        assert result == {"success": True}
        assert mock_request.call_count == 2

    @patch("manifoldbot.manifold.reader.requests.Session.request")
    def test_make_request_max_retries_exceeded(self, mock_request):
        """Test behavior when max retries exceeded."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response

        with patch("time.sleep"):  # Mock sleep to speed up test
            with pytest.raises(requests.RequestException, match="Max retries exceeded"):
                self.reader._make_request("GET", "test")

        # Should try max_retries + 1 times (initial + retries)
        assert mock_request.call_count == 4  # 1 initial + 3 retries

    @patch.object(ManifoldReader, "_make_request")
    def test_paginate_list_response(self, mock_make_request):
        """Test pagination with list response."""
        mock_make_request.return_value = [{"id": "1", "question": "Market 1?"}, {"id": "2", "question": "Market 2?"}]

        result = self.reader._paginate("markets")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"
        mock_make_request.assert_called_once()

    @patch.object(ManifoldReader, "_make_request")
    def test_paginate_dict_response(self, mock_make_request):
        """Test pagination with dict response containing data field."""
        mock_make_request.return_value = {"data": [{"id": "1", "question": "Market 1?"}, {"id": "2", "question": "Market 2?"}]}

        result = self.reader._paginate("markets")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    @patch.object(ManifoldReader, "_make_request")
    def test_paginate_with_cursor(self, mock_make_request):
        """Test pagination with cursor-based pagination."""
        # First call returns data with next cursor
        first_response = {"data": [{"id": "1"}], "nextCursor": "cursor123"}

        # Second call returns final data
        second_response = {"data": [{"id": "2"}]}

        mock_make_request.side_effect = [first_response, second_response]

        result = self.reader._paginate("markets")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"
        assert mock_make_request.call_count == 2

        # Check that cursor was passed in second call
        second_call_args = mock_make_request.call_args_list[1]
        assert second_call_args[1]["params"]["cursor"] == "cursor123"

    @patch.object(ManifoldReader, "_make_request")
    def test_paginate_with_limit(self, mock_make_request):
        """Test pagination with limit."""
        mock_make_request.return_value = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]

        result = self.reader._paginate("markets", limit=2)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    @patch.object(ManifoldReader, "_make_request")
    def test_get_market(self, mock_make_request):
        """Test get_market method."""
        mock_market = {"id": "test123", "question": "Will this test pass?", "probability": 0.75}
        mock_make_request.return_value = mock_market

        result = self.reader.get_market("test123")

        assert result == mock_market
        mock_make_request.assert_called_once_with("GET", "market/test123")

    @patch.object(ManifoldReader, "_make_request")
    def test_get_market_by_slug(self, mock_make_request):
        """Test get_market_by_slug method."""
        mock_market = {"id": "test123", "question": "Will this test pass?", "probability": 0.75, "outcomeType": "BINARY"}
        mock_make_request.return_value = mock_market

        result = self.reader.get_market_by_slug("test-slug")

        assert result == mock_market
        mock_make_request.assert_called_once_with("GET", "slug/test-slug")

    @patch.object(ManifoldReader, "_paginate")
    def test_search_markets(self, mock_paginate):
        """Test search_markets method."""
        mock_markets = [{"id": "1", "question": "AI market?"}, {"id": "2", "question": "AI regulation?"}]
        mock_paginate.return_value = mock_markets

        result = self.reader.search_markets("AI", limit=10)

        assert result == mock_markets
        mock_paginate.assert_called_once_with("search-markets", params={"term": "AI"}, limit=10)

    @patch.object(ManifoldReader, "_paginate")
    def test_get_markets(self, mock_paginate):
        """Test get_markets method."""
        mock_markets = [{"id": "1"}, {"id": "2"}]
        mock_paginate.return_value = mock_markets

        filters = {"creator": "testuser", "category": "politics"}
        result = self.reader.get_markets(limit=20, filters=filters)

        assert result == mock_markets
        mock_paginate.assert_called_once_with("markets", params=filters, limit=20)

    @patch.object(ManifoldReader, "_paginate")
    def test_get_trending_markets(self, mock_paginate):
        """Test get_trending_markets method."""
        mock_markets = [{"id": "1", "trending": True}]
        mock_paginate.return_value = mock_markets

        result = self.reader.get_trending_markets(limit=5)

        assert result == mock_markets
        mock_paginate.assert_called_once_with("markets", params={"sort": "trending"}, limit=5)

    def test_get_market_comments(self):
        """Test get_market_comments method."""
        # This method is not implemented due to API issues
        with pytest.raises(NotImplementedError, match="Market comments endpoint not available"):
            self.reader.get_market_comments("market123", limit=50)

    @patch.object(ManifoldReader, "_make_request")
    def test_get_user(self, mock_make_request):
        """Test get_user method."""
        mock_user = {"id": "user123", "name": "TestUser", "totalDeposits": 1000}
        mock_make_request.return_value = mock_user

        result = self.reader.get_user("user123")

        assert result == mock_user
        mock_make_request.assert_called_once_with("GET", "user/user123")

    @patch.object(ManifoldReader, "_paginate")
    def test_get_user_markets(self, mock_paginate):
        """Test get_user_markets method."""
        mock_markets = [{"id": "1", "creator": "user123"}]
        mock_paginate.return_value = mock_markets

        result = self.reader.get_user_markets("user123", limit=10)

        assert result == mock_markets
        mock_paginate.assert_called_once_with("user/user123/markets", limit=10)

    @patch.object(ManifoldReader, "_paginate")
    def test_get_user_bets(self, mock_paginate):
        """Test get_user_bets method."""
        mock_bets = [{"id": "1", "userId": "user123", "amount": 10}]
        mock_paginate.return_value = mock_bets

        result = self.reader.get_user_bets("user123", limit=25)

        assert result == mock_bets
        mock_paginate.assert_called_once_with("user/user123/bets", limit=25)

    def test_get_groups(self):
        """Test get_groups method."""
        # This method is not implemented due to API database issues
        with pytest.raises(NotImplementedError, match="Groups endpoint has database issues"):
            self.reader.get_groups(limit=5)

    @patch.object(ManifoldReader, "_make_request")
    def test_get_group(self, mock_make_request):
        """Test get_group method."""
        mock_group = {"id": "group123", "name": "Test Group"}
        mock_make_request.return_value = mock_group

        result = self.reader.get_group("group123")

        assert result == mock_group
        mock_make_request.assert_called_once_with("GET", "group/group123")

    @patch.object(ManifoldReader, "_paginate")
    def test_get_group_markets(self, mock_paginate):
        """Test get_group_markets method."""
        mock_markets = [{"id": "1", "groupId": "group123"}]
        mock_paginate.return_value = mock_markets

        result = self.reader.get_group_markets("group123", limit=15)

        assert result == mock_markets
        mock_paginate.assert_called_once_with("group/group123/markets", limit=15)

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_liquidity(self, mock_get_market):
        """Test get_market_liquidity method."""
        mock_market = {"id": "market123", "totalLiquidity": 1000, "yesLiquidity": 600, "noLiquidity": 400}
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_liquidity("market123")

        expected = {"total": 1000, "yes": 600, "no": 400}
        assert result == expected
        mock_get_market.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market_liquidity")
    def test_get_market_depth(self, mock_get_liquidity):
        """Test get_market_depth method."""
        mock_liquidity = {"total": 1000, "yes": 600, "no": 400}
        mock_get_liquidity.return_value = mock_liquidity

        result = self.reader.get_market_depth("market123", levels=5)

        assert result == mock_liquidity
        mock_get_liquidity.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_risk_metrics(self, mock_get_market):
        """Test get_market_risk_metrics method."""
        mock_market = {"id": "market123", "probability": 0.75}
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_risk_metrics("market123")

        expected = {"volatility": 0.0, "max_drawdown": 0.0, "sharpe_ratio": 0.0}
        assert result == expected
        mock_get_market.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_probability(self, mock_get_market):
        """Test get_market_probability method."""
        mock_market = {"id": "market123", "probability": 0.75}
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_probability("market123")

        assert result == 0.75
        mock_get_market.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_probability_default(self, mock_get_market):
        """Test get_market_probability with missing probability field."""
        mock_market = {"id": "market123"}  # No probability field
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_probability("market123")

        assert result == 0.0  # Default value
        mock_get_market.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market_probability")
    def test_get_market_probability_percent(self, mock_get_probability):
        """Test get_market_probability_percent method."""
        mock_get_probability.return_value = 0.75

        result = self.reader.get_market_probability_percent("market123")

        assert result == 75.0
        mock_get_probability.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_basic_info(self, mock_get_market):
        """Test get_market_basic_info method."""
        mock_market = {
            "id": "market123",
            "question": "Will this test pass?",
            "description": "A test market",
            "probability": 0.75,
            "volume": 1000,
            "totalLiquidity": 500,
            "yesLiquidity": 300,
            "noLiquidity": 200,
            "creatorName": "TestUser",
            "createdTime": 1234567890,
            "closeTime": 1234567890,
            "resolution": None,
            "isResolved": False,
        }
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_basic_info("market123")

        expected = {
            "id": "market123",
            "question": "Will this test pass?",
            "description": "A test market",
            "probability": 0.75,
            "probability_percent": 75.0,
            "volume": 1000,
            "total_liquidity": 500,
            "yes_liquidity": 300,
            "no_liquidity": 200,
            "creator": "TestUser",
            "created_time": 1234567890,
            "close_time": 1234567890,
            "resolution": None,
            "is_resolved": False,
        }
        assert result == expected
        mock_get_market.assert_called_once_with("market123")

    @patch.object(ManifoldReader, "get_market")
    def test_get_market_basic_info_missing_fields(self, mock_get_market):
        """Test get_market_basic_info with missing fields."""
        mock_market = {"id": "market123"}  # Minimal market data
        mock_get_market.return_value = mock_market

        result = self.reader.get_market_basic_info("market123")

        expected = {
            "id": "market123",
            "question": None,
            "description": None,
            "probability": 0.0,
            "probability_percent": 0.0,
            "volume": 0,
            "total_liquidity": 0,
            "yes_liquidity": 0,
            "no_liquidity": 0,
            "creator": None,
            "created_time": None,
            "close_time": None,
            "resolution": None,
            "is_resolved": False,
        }
        assert result == expected


class TestManifoldReaderReal:
    """Real API tests for ManifoldReader."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ManifoldReader()

    def test_get_markets_real(self):
        """Test getting markets with real API call."""
        markets = self.reader.get_markets(limit=5)

        assert isinstance(markets, list)
        assert len(markets) <= 5

        if markets:  # If we got results
            market = markets[0]
            assert "id" in market
            assert "question" in market
            # Note: probability is not in the markets list, only in individual market details

    def test_search_markets_real(self):
        """Test searching markets with real API call."""
        markets = self.reader.search_markets("AI", limit=3)

        assert isinstance(markets, list)
        assert len(markets) <= 3

        if markets:
            market = markets[0]
            assert "id" in market
            assert "question" in market
            # Search results should contain the search term
            assert "AI" in market["question"].upper()

    def test_get_market_by_id_real(self):
        """Test getting a specific market by ID."""
        # First get a market ID from the markets list
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market_id = markets[0]["id"]

        # Now get the specific market
        market = self.reader.get_market(market_id)

        assert isinstance(market, dict)
        assert market["id"] == market_id
        assert "question" in market
        # Individual market details should have probability
        if "probability" in market:
            assert isinstance(market["probability"], (int, float))
            assert 0 <= market["probability"] <= 1

    def test_get_market_probability_real(self):
        """Test getting market probability with real API call."""
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market_id = markets[0]["id"]
        probability = self.reader.get_market_probability(market_id)

        assert isinstance(probability, (int, float))
        assert 0 <= probability <= 1

    def test_get_market_probability_percent_real(self):
        """Test getting market probability as percentage."""
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market_id = markets[0]["id"]
        probability_percent = self.reader.get_market_probability_percent(market_id)

        assert isinstance(probability_percent, (int, float))
        assert 0 <= probability_percent <= 100

    def test_get_market_basic_info_real(self):
        """Test getting basic market info with real API call."""
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

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

        # Check probability conversion
        assert info["probability_percent"] == info["probability"] * 100

    def test_get_market_liquidity_real(self):
        """Test getting market liquidity with real API call."""
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market_id = markets[0]["id"]
        liquidity = self.reader.get_market_liquidity(market_id)

        assert isinstance(liquidity, dict)
        assert "total" in liquidity
        assert "yes" in liquidity
        assert "no" in liquidity

        # Liquidity values should be non-negative
        assert liquidity["total"] >= 0
        assert liquidity["yes"] >= 0
        assert liquidity["no"] >= 0

    def test_get_market_comments_real(self):
        """Test getting market comments with real API call."""
        # This method is not implemented due to API issues
        with pytest.raises(NotImplementedError, match="Market comments endpoint not available"):
            self.reader.get_market_comments("test_market_id", limit=3)

    def test_get_user_real(self):
        """Test getting user info with real API call."""
        # First get a market to find a user
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market = markets[0]
        creator_id = market.get("creatorId")

        if not creator_id:
            pytest.skip("No creator ID found in market")

        # Some user IDs may not be accessible (404 errors)
        try:
            user = self.reader.get_user(creator_id)
            assert isinstance(user, dict)
            assert "id" in user
            assert "name" in user
        except requests.RequestException as e:
            if "404" in str(e):
                pytest.skip(f"User {creator_id} not accessible (404 error)")
            else:
                raise

    def test_get_user_markets_real(self):
        """Test getting user markets with real API call."""
        # First get a market to find a user
        markets = self.reader.get_markets(limit=1)

        if not markets:
            pytest.skip("No markets available for testing")

        market = markets[0]
        creator_id = market.get("creatorId")

        if not creator_id:
            pytest.skip("No creator ID found in market")

        # Some user IDs may not be accessible (404 errors)
        try:
            user_markets = self.reader.get_user_markets(creator_id, limit=3)
            assert isinstance(user_markets, list)
            assert len(user_markets) <= 3

            if user_markets:
                user_market = user_markets[0]
                assert "id" in user_market
                assert "question" in user_market
                assert user_market.get("creatorId") == creator_id
        except requests.RequestException as e:
            if "404" in str(e):
                pytest.skip(f"User {creator_id} markets not accessible (404 error)")
            else:
                raise

    def test_get_groups_real(self):
        """Test getting groups with real API call."""
        # This method is not implemented due to API database issues
        with pytest.raises(NotImplementedError, match="Groups endpoint has database issues"):
            self.reader.get_groups(limit=3)

    def test_pagination_real(self):
        """Test pagination with real API call."""
        # Get first page
        markets_page1 = self.reader.get_markets(limit=2)

        assert isinstance(markets_page1, list)
        assert len(markets_page1) <= 2

        if len(markets_page1) == 2:
            # Get more markets to test pagination
            markets_page2 = self.reader.get_markets(limit=4)

            assert isinstance(markets_page2, list)
            assert len(markets_page2) <= 4
            assert len(markets_page2) >= len(markets_page1)

    def test_error_handling_real(self):
        """Test error handling with real API call."""
        # Test with invalid market ID
        with pytest.raises(requests.RequestException):
            self.reader.get_market("invalid_market_id_12345")

        # Test with invalid user ID
        with pytest.raises(requests.RequestException):
            self.reader.get_user("invalid_user_id_12345")
