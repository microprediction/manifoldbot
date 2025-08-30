"""
ManifoldWriter - Authenticated client for Manifold Markets API.

This module provides the ManifoldWriter class for authenticated operations
like placing bets, creating markets, managing positions, etc.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from .reader import ManifoldReader


class ManifoldWriter(ManifoldReader):
    """
    Authenticated client for Manifold Markets API.

    Extends ManifoldReader to add authenticated operations like:
    - Placing bets
    - Creating markets
    - Managing positions
    - Posting comments
    - User account operations

    Requires a Manifold API key for authentication.
    """

    def __init__(self, api_key: str, timeout: int = 30, retry_config: Optional[Dict[str, Any]] = None):
        """
        Initialize ManifoldWriter with API key.

        Args:
            api_key: Manifold Markets API key
            timeout: Request timeout in seconds
            retry_config: Custom retry configuration
        """
        super().__init__(timeout=timeout, retry_config=retry_config)

        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

        # Add authentication header
        self.session.headers.update({"Authorization": f"Key {api_key}"})

        self.logger.info("ManifoldWriter initialized with API key")

    def _make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an authenticated request to the Manifold API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            API response data

        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request(method, endpoint, **kwargs)

    # Betting operations

    def place_bet(
        self, market_id: str, outcome: str, amount: int, probability: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a bet on a market.

        Args:
            market_id: Market ID or slug
            outcome: "YES" or "NO"
            amount: Amount to bet in M$ (integer)
            probability: Optional limit price (0-1) for limit orders

        Returns:
            Bet placement result
        """
        if outcome not in ["YES", "NO"]:
            raise ValueError("Outcome must be 'YES' or 'NO'")

        if amount <= 0:
            raise ValueError("Amount must be positive")

        if probability is not None and not (0 <= probability <= 1):
            raise ValueError("Probability must be between 0 and 1")

        data = {"contractId": market_id, "outcome": outcome, "amount": amount}

        if probability is not None:
            data["limitProb"] = probability
            # Add default expiration for limit orders (6 hours)
            data["expiresMillisAfter"] = 6 * 60 * 60 * 1000

        return self._make_authenticated_request("POST", "bet", data=data)

    def place_limit_yes(self, market_id: str, amount: int, limit_prob: float) -> Dict[str, Any]:
        """
        Place a YES limit order (convenience method).
        
        Args:
            market_id: The market contract ID
            amount: Order amount in M$
            limit_prob: Limit probability (0.0-1.0)
            
        Returns:
            Order response from API
        """
        return self.place_bet(market_id, "YES", amount, probability=limit_prob)

    def place_limit_no(self, market_id: str, amount: int, limit_prob: float) -> Dict[str, Any]:
        """
        Place a NO limit order (convenience method).
        
        Args:
            market_id: The market contract ID
            amount: Order amount in M$
            limit_prob: Limit probability (0.0-1.0)
            
        Returns:
            Order response from API
        """
        return self.place_bet(market_id, "NO", amount, probability=limit_prob)

    def cancel_bet(self, bet_id: str) -> Dict[str, Any]:
        """
        Cancel a pending bet.

        Args:
            bet_id: Bet ID to cancel

        Returns:
            Cancellation result
        """
        return self._make_authenticated_request("POST", f"bet/{bet_id}/cancel")

    def get_bet(self, bet_id: str) -> Dict[str, Any]:
        """
        Get bet details.

        Args:
            bet_id: Bet ID

        Returns:
            Bet details
        """
        return self._make_authenticated_request("GET", f"bet/{bet_id}")

    # Market creation operations

    def create_market(
        self,
        question: str,
        description: str,
        outcome_type: str = "BINARY",
        close_time: Optional[int] = None,
        tags: Optional[List[str]] = None,
        group_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new market.

        Args:
            question: Market question
            description: Market description
            outcome_type: "BINARY", "MULTIPLE_CHOICE", "FREE_RESPONSE", etc.
            close_time: Close time as Unix timestamp
            tags: List of tags
            group_id: Optional group ID

        Returns:
            Created market data
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if not description.strip():
            raise ValueError("Description cannot be empty")

        data = {"question": question, "description": description, "outcomeType": outcome_type}

        if close_time is not None:
            data["closeTime"] = close_time

        if tags:
            data["tags"] = tags

        if group_id:
            data["groupId"] = group_id

        return self._make_authenticated_request("POST", "market", data=data)

    def close_market(self, market_id: str, outcome: str, probability: Optional[float] = None) -> Dict[str, Any]:
        """
        Close a market with a resolution.

        Args:
            market_id: Market ID
            outcome: Resolution outcome
            probability: Optional probability for partial resolution

        Returns:
            Market closure result
        """
        data = {"outcome": outcome}

        if probability is not None:
            data["probability"] = probability

        return self._make_authenticated_request("POST", f"market/{market_id}/close", data=data)



    def get_me(self) -> Dict[str, Any]:
        """Get current user information."""
        return self._make_authenticated_request("GET", "me")

    def get_balance(self) -> float:
        """Get current user balance."""
        user_data = self.get_me()
        return user_data.get("balance", 0.0)

    def get_total_deposits(self) -> float:
        """Get total deposits."""
        user_data = self.get_me()
        return user_data.get("totalDeposits", 0.0)

    def is_authenticated(self) -> bool:
        """Check if properly authenticated."""
        try:
            self.get_me()
            return True
        except requests.RequestException:
            return False
