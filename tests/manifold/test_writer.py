"""
Unit tests for ManifoldWriter.

Tests the authenticated client for Manifold Markets API.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from manifoldbot.manifold.writer import ManifoldWriter


class TestManifoldWriter:
    """Test cases for ManifoldWriter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_123"
        self.writer = ManifoldWriter(api_key=self.api_key)

    def test_init(self):
        """Test ManifoldWriter initialization."""
        writer = ManifoldWriter(api_key="test_key", timeout=60)

        assert writer.api_key == "test_key"
        assert writer.timeout == 60
        assert writer.BASE_URL == "https://api.manifold.markets/v0"
        assert "Authorization" in writer.session.headers
        assert writer.session.headers["Authorization"] == "Key test_key"

    def test_init_inherits_from_reader(self):
        """Test that ManifoldWriter inherits from ManifoldReader."""
        writer = ManifoldWriter(api_key="test_key")

        # Should have all reader methods
        assert hasattr(writer, "get_market")
        assert hasattr(writer, "search_markets")
        assert hasattr(writer, "get_markets")

        # Should have writer-specific methods
        assert hasattr(writer, "place_bet")
        assert hasattr(writer, "create_market")
        assert hasattr(writer, "get_me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_place_bet_market_order(self, mock_request):
        """Test placing a market order bet."""
        mock_response = {"id": "bet123", "amount": 10, "outcome": "YES", "probBefore": 0.5, "probAfter": 0.52}
        mock_request.return_value = mock_response

        result = self.writer.place_bet("market123", "YES", 10)

        assert result == mock_response
        mock_request.assert_called_once_with(
            "POST", "bet", json={"contractId": "market123", "outcome": "YES", "amount": 10, "orderType": "market"}
        )

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_place_bet_limit_order(self, mock_request):
        """Test placing a limit order bet."""
        mock_response = {"id": "bet123", "status": "pending"}
        mock_request.return_value = mock_response

        result = self.writer.place_bet("market123", "NO", 5, probability=0.6)

        assert result == mock_response
        mock_request.assert_called_once_with(
            "POST",
            "bet",
            json={"contractId": "market123", "outcome": "NO", "amount": 5, "orderType": "market", "limitProb": 0.6},
        )

    def test_place_bet_validation(self):
        """Test bet placement validation."""
        # Invalid outcome
        with pytest.raises(ValueError, match="Outcome must be 'YES' or 'NO'"):
            self.writer.place_bet("market123", "MAYBE", 10)

        # Invalid amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            self.writer.place_bet("market123", "YES", -5)

        with pytest.raises(ValueError, match="Amount must be positive"):
            self.writer.place_bet("market123", "YES", 0)

        # Invalid probability
        with pytest.raises(ValueError, match="Probability must be between 0 and 1"):
            self.writer.place_bet("market123", "YES", 10, probability=1.5)

        with pytest.raises(ValueError, match="Probability must be between 0 and 1"):
            self.writer.place_bet("market123", "YES", 10, probability=-0.1)

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_cancel_bet(self, mock_request):
        """Test canceling a bet."""
        mock_response = {"id": "bet123", "status": "cancelled"}
        mock_request.return_value = mock_response

        result = self.writer.cancel_bet("bet123")

        assert result == mock_response
        mock_request.assert_called_once_with("POST", "bet/bet123/cancel")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_bet(self, mock_request):
        """Test getting bet details."""
        mock_bet = {"id": "bet123", "amount": 10, "outcome": "YES", "probBefore": 0.5, "probAfter": 0.52}
        mock_request.return_value = mock_bet

        result = self.writer.get_bet("bet123")

        assert result == mock_bet
        mock_request.assert_called_once_with("GET", "bet/bet123")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_create_market(self, mock_request):
        """Test creating a market."""
        mock_market = {
            "id": "market123",
            "question": "Will this test pass?",
            "description": "A test market",
            "outcomeType": "BINARY",
        }
        mock_request.return_value = mock_market

        result = self.writer.create_market(question="Will this test pass?", description="A test market")

        assert result == mock_market
        mock_request.assert_called_once_with(
            "POST",
            "market",
            json={"question": "Will this test pass?", "description": "A test market", "outcomeType": "BINARY"},
        )

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_create_market_with_options(self, mock_request):
        """Test creating a market with additional options."""
        mock_market = {"id": "market123"}
        mock_request.return_value = mock_market

        result = self.writer.create_market(
            question="Test question",
            description="Test description",
            outcome_type="MULTIPLE_CHOICE",
            close_time=1234567890,
            tags=["test", "example"],
            group_id="group123",
        )

        mock_request.assert_called_once_with(
            "POST",
            "market",
            json={
                "question": "Test question",
                "description": "Test description",
                "outcomeType": "MULTIPLE_CHOICE",
                "closeTime": 1234567890,
                "tags": ["test", "example"],
                "groupId": "group123",
            },
        )

    def test_create_market_validation(self):
        """Test market creation validation."""
        # Empty question
        with pytest.raises(ValueError, match="Question cannot be empty"):
            self.writer.create_market("", "Description")

        with pytest.raises(ValueError, match="Question cannot be empty"):
            self.writer.create_market("   ", "Description")

        # Empty description
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.writer.create_market("Question", "")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.writer.create_market("Question", "   ")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_close_market(self, mock_request):
        """Test closing a market."""
        mock_response = {"id": "market123", "isResolved": True, "resolution": "YES"}
        mock_request.return_value = mock_response

        result = self.writer.close_market("market123", "YES")

        assert result == mock_response
        mock_request.assert_called_once_with("POST", "market/market123/close", json={"outcome": "YES"})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_close_market_with_probability(self, mock_request):
        """Test closing a market with probability."""
        mock_response = {"id": "market123", "isResolved": True, "resolution": "MULTI"}
        mock_request.return_value = mock_response

        result = self.writer.close_market("market123", "MULTI", probability=0.7)

        mock_request.assert_called_once_with("POST", "market/market123/close", json={"outcome": "MULTI", "probability": 0.7})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_positions(self, mock_request):
        """Test getting positions."""
        mock_positions = [
            {"contractId": "market1", "shares": 10, "outcome": "YES"},
            {"contractId": "market2", "shares": 5, "outcome": "NO"},
        ]
        mock_request.return_value = mock_positions

        result = self.writer.get_positions()

        assert result == mock_positions
        mock_request.assert_called_once_with("GET", "positions")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_positions_for_market(self, mock_request):
        """Test getting positions for specific market."""
        mock_position = {"contractId": "market1", "shares": 10, "outcome": "YES"}
        mock_request.return_value = mock_position

        result = self.writer.get_positions("market1")

        assert result == mock_position
        mock_request.assert_called_once_with("GET", "positions/market1")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_portfolio(self, mock_request):
        """Test getting portfolio."""
        mock_portfolio = {"balance": 1000, "totalDeposits": 5000, "totalValue": 6000}
        mock_request.return_value = mock_portfolio

        result = self.writer.get_portfolio()

        assert result == mock_portfolio
        mock_request.assert_called_once_with("GET", "portfolio")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_post_comment(self, mock_request):
        """Test posting a comment."""
        mock_comment = {"id": "comment123", "text": "Great market!", "contractId": "market123"}
        mock_request.return_value = mock_comment

        result = self.writer.post_comment("market123", "Great market!")

        assert result == mock_comment
        mock_request.assert_called_once_with("POST", "comment", json={"contractId": "market123", "text": "Great market!"})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_post_comment_reply(self, mock_request):
        """Test posting a reply comment."""
        mock_comment = {"id": "comment456", "text": "I agree", "replyToCommentId": "comment123"}
        mock_request.return_value = mock_comment

        result = self.writer.post_comment("market123", "I agree", reply_to="comment123")

        mock_request.assert_called_once_with(
            "POST", "comment", json={"contractId": "market123", "text": "I agree", "replyToCommentId": "comment123"}
        )

    def test_post_comment_validation(self):
        """Test comment validation."""
        with pytest.raises(ValueError, match="Comment text cannot be empty"):
            self.writer.post_comment("market123", "")

        with pytest.raises(ValueError, match="Comment text cannot be empty"):
            self.writer.post_comment("market123", "   ")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_me(self, mock_request):
        """Test getting current user info."""
        mock_user = {"id": "user123", "name": "TestUser", "balance": 1000, "totalDeposits": 5000}
        mock_request.return_value = mock_user

        result = self.writer.get_me()

        assert result == mock_user
        mock_request.assert_called_once_with("GET", "me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_update_user(self, mock_request):
        """Test updating user profile."""
        mock_user = {"id": "user123", "name": "UpdatedName"}
        mock_request.return_value = mock_user

        result = self.writer.update_user(name="UpdatedName", bio="New bio")

        assert result == mock_user
        mock_request.assert_called_once_with("POST", "me", json={"name": "UpdatedName", "bio": "New bio"})

    @patch.object(ManifoldWriter, "get_market")
    def test_calculate_market_impact(self, mock_get_market):
        """Test market impact calculation."""
        mock_market = {"probability": 0.5, "totalLiquidity": 1000}
        mock_get_market.return_value = mock_market

        result = self.writer.calculate_market_impact("market123", 50, "YES")

        assert result["current_probability"] == 0.5
        assert result["estimated_impact"] == 0.05  # 50/1000
        assert result["new_probability"] == 0.55  # 0.5 + 0.05
        assert result["liquidity"] == 1000

    @patch.object(ManifoldWriter, "calculate_market_impact")
    @patch.object(ManifoldWriter, "place_bet")
    def test_place_bet_with_impact_limit(self, mock_place_bet, mock_calculate_impact):
        """Test placing bet with impact limit."""
        mock_calculate_impact.return_value = {"estimated_impact": 0.1, "liquidity": 1000}  # 10% impact
        mock_place_bet.return_value = {"id": "bet123"}

        # Impact exceeds limit, should reduce bet size
        result = self.writer.place_bet_with_impact_limit("market123", "YES", 100, max_impact=0.05)

        # Should have reduced bet size to 50 (0.05 * 1000)
        mock_place_bet.assert_called_once_with("market123", "YES", 50)
        assert result == {"id": "bet123"}

    @patch.object(ManifoldWriter, "calculate_market_impact")
    @patch.object(ManifoldWriter, "place_bet")
    def test_place_bet_with_impact_limit_within_limit(self, mock_place_bet, mock_calculate_impact):
        """Test placing bet with impact limit when within limit."""
        mock_calculate_impact.return_value = {"estimated_impact": 0.02, "liquidity": 1000}  # 2% impact
        mock_place_bet.return_value = {"id": "bet123"}

        # Impact within limit, should use original amount
        result = self.writer.place_bet_with_impact_limit("market123", "YES", 20, max_impact=0.05)

        mock_place_bet.assert_called_once_with("market123", "YES", 20)
        assert result == {"id": "bet123"}

    @patch.object(ManifoldWriter, "get_me")
    def test_get_balance(self, mock_get_me):
        """Test getting balance."""
        mock_get_me.return_value = {"balance": 1500.50}

        result = self.writer.get_balance()

        assert result == 1500.50
        mock_get_me.assert_called_once()

    @patch.object(ManifoldWriter, "get_me")
    def test_get_total_deposits(self, mock_get_me):
        """Test getting total deposits."""
        mock_get_me.return_value = {"totalDeposits": 10000.0}

        result = self.writer.get_total_deposits()

        assert result == 10000.0
        mock_get_me.assert_called_once()

    @patch.object(ManifoldWriter, "get_me")
    def test_is_authenticated_true(self, mock_get_me):
        """Test authentication check when authenticated."""
        mock_get_me.return_value = {"id": "user123"}

        result = self.writer.is_authenticated()

        assert result is True
        mock_get_me.assert_called_once()

    @patch.object(ManifoldWriter, "get_me")
    def test_is_authenticated_false(self, mock_get_me):
        """Test authentication check when not authenticated."""
        mock_get_me.side_effect = requests.RequestException("Unauthorized")

        result = self.writer.is_authenticated()

        assert result is False
        mock_get_me.assert_called_once()
