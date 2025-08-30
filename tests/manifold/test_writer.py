"""
Unit tests for ManifoldWriter.
"""

import pytest
from unittest.mock import patch, MagicMock

from manifoldbot.manifold.writer import ManifoldWriter


class TestManifoldWriter:
    """Test cases for ManifoldWriter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.writer = ManifoldWriter(api_key="test_key")

    def test_init(self):
        """Test ManifoldWriter initialization."""
        writer = ManifoldWriter(api_key="test_key")
        assert writer.api_key == "test_key"
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
        mock_request.assert_called_once_with("POST", "bet", data={"contractId": "market123", "outcome": "YES", "amount": 10})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_place_bet_limit_order(self, mock_request):
        """Test placing a limit order bet."""
        mock_response = {"id": "bet456", "amount": 10, "outcome": "NO", "limitProb": 0.3}
        mock_request.return_value = mock_response

        result = self.writer.place_bet("market123", "NO", 10, probability=0.3)

        expected_data = {
            "contractId": "market123",
            "outcome": "NO", 
            "amount": 10,
            "limitProb": 0.3,
            "expiresMillisAfter": 6 * 60 * 60 * 1000
        }
        assert result == mock_response
        mock_request.assert_called_once_with("POST", "bet", data=expected_data)

    def test_place_bet_validation(self):
        """Test bet placement validation."""
        with pytest.raises(ValueError, match="Outcome must be"):
            self.writer.place_bet("market123", "INVALID", 10)

        with pytest.raises(ValueError, match="Amount must be positive"):
            self.writer.place_bet("market123", "YES", -10)

        with pytest.raises(ValueError, match="Probability must be between"):
            self.writer.place_bet("market123", "YES", 10, probability=1.5)

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
        mock_bet = {"id": "bet123", "amount": 10, "outcome": "YES"}
        mock_request.return_value = mock_bet

        result = self.writer.get_bet("bet123")

        assert result == mock_bet
        mock_request.assert_called_once_with("GET", "bet/bet123")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_create_market(self, mock_request):
        """Test creating a market."""
        mock_market = {"id": "market123", "question": "Test question", "description": "Test description"}
        mock_request.return_value = mock_market

        result = self.writer.create_market("Test question", "Test description")

        expected_data = {"question": "Test question", "description": "Test description", "outcomeType": "BINARY"}
        assert result == mock_market
        mock_request.assert_called_once_with("POST", "market", data=expected_data)

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_create_market_with_options(self, mock_request):
        """Test creating a market with additional options."""
        mock_market = {"id": "market123", "question": "Test question"}
        mock_request.return_value = mock_market

        result = self.writer.create_market(
            "Test question", 
            "Test description", 
            outcome_type="MULTIPLE_CHOICE",
            close_time=1234567890,
            tags=["tag1", "tag2"],
            group_id="group123"
        )

        expected_data = {
            "question": "Test question",
            "description": "Test description", 
            "outcomeType": "MULTIPLE_CHOICE",
            "closeTime": 1234567890,
            "tags": ["tag1", "tag2"],
            "groupId": "group123"
        }
        assert result == mock_market
        mock_request.assert_called_once_with("POST", "market", data=expected_data)

    def test_create_market_validation(self):
        """Test market creation validation."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            self.writer.create_market("", "Description")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.writer.create_market("Question", "")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_close_market(self, mock_request):
        """Test closing a market."""
        mock_response = {"id": "market123", "isResolved": True, "resolution": "YES"}
        mock_request.return_value = mock_response

        result = self.writer.close_market("market123", "YES")

        assert result == mock_response
        mock_request.assert_called_once_with("POST", "market/market123/close", data={"outcome": "YES"})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_close_market_with_probability(self, mock_request):
        """Test closing a market with probability."""
        mock_response = {"id": "market123", "isResolved": True, "resolution": "MULTI"}
        mock_request.return_value = mock_response

        result = self.writer.close_market("market123", "MULTI", probability=0.7)

        assert result == mock_response
        mock_request.assert_called_once_with("POST", "market/market123/close", data={"outcome": "MULTI", "probability": 0.7})

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_me(self, mock_request):
        """Test getting current user info."""
        mock_user = {"id": "user123", "name": "TestUser", "balance": 1000, "totalDeposits": 5000}
        mock_request.return_value = mock_user

        result = self.writer.get_me()

        assert result == mock_user
        mock_request.assert_called_once_with("GET", "me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_balance(self, mock_request):
        """Test getting balance."""
        mock_user = {"id": "user123", "balance": 1000.5}
        mock_request.return_value = mock_user

        result = self.writer.get_balance()

        assert result == 1000.5
        mock_request.assert_called_once_with("GET", "me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_get_total_deposits(self, mock_request):
        """Test getting total deposits."""
        mock_user = {"id": "user123", "totalDeposits": 5000.0}
        mock_request.return_value = mock_user

        result = self.writer.get_total_deposits()

        assert result == 5000.0
        mock_request.assert_called_once_with("GET", "me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_is_authenticated_true(self, mock_request):
        """Test authentication check when authenticated."""
        mock_user = {"id": "user123", "name": "TestUser"}
        mock_request.return_value = mock_user

        result = self.writer.is_authenticated()

        assert result is True
        mock_request.assert_called_once_with("GET", "me")

    @patch.object(ManifoldWriter, "_make_authenticated_request")
    def test_is_authenticated_false(self, mock_request):
        """Test authentication check when not authenticated."""
        from requests.exceptions import RequestException
        mock_request.side_effect = RequestException("Unauthorized")

        result = self.writer.is_authenticated()

        assert result is False
        mock_request.assert_called_once_with("GET", "me")