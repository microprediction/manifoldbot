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
        self, market_id: str, outcome: str, amount: float, probability: Optional[float] = None, order_type: str = "market"
    ) -> Dict[str, Any]:
        """
        Place a bet on a market.

        Args:
            market_id: Market ID or slug
            outcome: "YES" or "NO"
            amount: Amount to bet in M$
            probability: Optional limit price (0-1)
            order_type: "market" or "limit"

        Returns:
            Bet placement result
        """
        if outcome not in ["YES", "NO"]:
            raise ValueError("Outcome must be 'YES' or 'NO'")

        if amount <= 0:
            raise ValueError("Amount must be positive")

        if probability is not None and not (0 <= probability <= 1):
            raise ValueError("Probability must be between 0 and 1")

        data = {"contractId": market_id, "outcome": outcome, "amount": amount, "orderType": order_type}

        if probability is not None:
            data["limitProb"] = probability

        return self._make_authenticated_request("POST", "bet", json=data)

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

        return self._make_authenticated_request("POST", "market", json=data)

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

        return self._make_authenticated_request("POST", f"market/{market_id}/close", json=data)

    # Position management

    def get_positions(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user positions.

        Args:
            market_id: Optional market ID to filter positions

        Returns:
            List of positions
        """
        endpoint = "positions"
        if market_id:
            endpoint = f"positions/{market_id}"

        return self._make_authenticated_request("GET", endpoint)

    def get_portfolio(self) -> Dict[str, Any]:
        """
        Get user portfolio summary.

        Returns:
            Portfolio data
        """
        return self._make_authenticated_request("GET", "portfolio")

    # Comment operations

    def post_comment(self, market_id: str, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a comment on a market.

        Args:
            market_id: Market ID
            text: Comment text
            reply_to: Optional parent comment ID

        Returns:
            Posted comment data
        """
        if not text.strip():
            raise ValueError("Comment text cannot be empty")

        data = {"contractId": market_id, "text": text}

        if reply_to:
            data["replyToCommentId"] = reply_to

        return self._make_authenticated_request("POST", "comment", json=data)

    # User operations

    def get_me(self) -> Dict[str, Any]:
        """
        Get current user information.

        Returns:
            User data
        """
        return self._make_authenticated_request("GET", "me")

    def update_user(self, **kwargs) -> Dict[str, Any]:
        """
        Update user profile.

        Args:
            **kwargs: User fields to update

        Returns:
            Updated user data
        """
        return self._make_authenticated_request("POST", "me", json=kwargs)

    # Advanced trading operations

    def calculate_market_impact(self, market_id: str, amount: float, outcome: str) -> Dict[str, Any]:
        """
        Calculate the market impact of a potential bet.

        Args:
            market_id: Market ID
            amount: Bet amount
            outcome: "YES" or "NO"

        Returns:
            Market impact analysis
        """
        # Get current market state
        market = self.get_market(market_id)

        # This is a simplified calculation
        # In practice, you'd want to use the actual market impact formula
        current_prob = market.get("probability", 0.5)
        liquidity = market.get("totalLiquidity", 1000)

        # Simple market impact estimation
        impact = amount / liquidity if liquidity > 0 else 0

        return {
            "current_probability": current_prob,
            "estimated_impact": impact,
            "new_probability": min(1, max(0, current_prob + impact if outcome == "YES" else current_prob - impact)),
            "liquidity": liquidity,
        }

    def place_bet_with_impact_limit(
        self, market_id: str, outcome: str, amount: float, max_impact: float = 0.05
    ) -> Dict[str, Any]:
        """
        Place a bet with a maximum market impact limit.

        Args:
            market_id: Market ID
            outcome: "YES" or "NO"
            amount: Desired bet amount
            max_impact: Maximum allowed market impact (0-1)

        Returns:
            Bet placement result
        """
        impact_analysis = self.calculate_market_impact(market_id, amount, outcome)

        if impact_analysis["estimated_impact"] > max_impact:
            # Reduce bet size to stay within impact limit
            max_amount = max_impact * impact_analysis["liquidity"]
            amount = min(amount, max_amount)
            self.logger.warning(f"Reduced bet size to {amount} to stay within impact limit")

        return self.place_bet(market_id, outcome, amount)

    # Utility methods

    def get_balance(self) -> float:
        """
        Get current user balance.

        Returns:
            Current balance in M$
        """
        user_data = self.get_me()
        return user_data.get("balance", 0.0)

    def get_total_deposits(self) -> float:
        """
        Get total deposits.

        Returns:
            Total deposits in M$
        """
        user_data = self.get_me()
        return user_data.get("totalDeposits", 0.0)

    def is_authenticated(self) -> bool:
        """
        Check if the writer is properly authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        try:
            self.get_me()
            return True
        except requests.RequestException:
            return False
