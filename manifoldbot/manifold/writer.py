"""
ManifoldWriter - Authenticated client for Manifold Markets API.

This module provides the ManifoldWriter class for authenticated operations
like placing bets, creating markets, managing positions, etc.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from .reader import ManifoldReader
from .comments import Comment, CommentReply


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

        try:
            return self._make_authenticated_request("POST", "bet", data=data)
        except requests.RequestException as e:
            # Log detailed error information
            self.logger.error(f"Bet placement failed for market {market_id}:")
            self.logger.error(f"  Request data: {data}")
            self.logger.error(f"  Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"  Response status: {e.response.status_code}")
                self.logger.error(f"  Response text: {e.response.text}")
            raise

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

    # Comment operations

    def post_comment(self, comment: Comment) -> Dict[str, Any]:
        """
        Post a comment to a market.

        Args:
            comment: Comment object to post

        Returns:
            API response with comment details

        Raises:
            requests.RequestException: If request fails
            ValueError: If comment validation fails
        """
        comment.validate()
        
        self.logger.info(f"Posting comment to market {comment.contractId}")
        
        response = self._make_authenticated_request(
            "POST", 
            "/comment", 
            json=comment.to_dict()
        )
        
        self.logger.info(f"Successfully posted comment: {response.get('id', 'unknown_id')}")
        return response

    def post_comment_reply(self, reply: CommentReply) -> Dict[str, Any]:
        """
        Post a reply to an existing comment.

        Args:
            reply: CommentReply object to post

        Returns:
            API response with reply details

        Raises:
            requests.RequestException: If request fails
            ValueError: If reply validation fails
        """
        reply.validate()
        
        self.logger.info(f"Posting reply to comment {reply.replyToCommentId} on market {reply.contractId}")
        
        response = self._make_authenticated_request(
            "POST",
            "/comment",
            json=reply.to_dict()
        )
        
        self.logger.info(f"Successfully posted reply: {response.get('id', 'unknown_id')}")
        return response

    def get_market_comments(self, market_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get comments for a specific market.

        Args:
            market_id: Market ID or slug
            limit: Maximum number of comments to retrieve

        Returns:
            List of comment dictionaries

        Raises:
            requests.RequestException: If request fails
        """
        self.logger.info(f"Retrieving comments for market {market_id}")
        
        params = {}
        if limit:
            params["limit"] = limit
            
        response = self._make_authenticated_request(
            "GET",
            f"/comments",
            params={**params, "contractId": market_id}
        )
        
        # Handle both direct list and wrapped response formats
        comments = response if isinstance(response, list) else response.get('comments', [])
        
        self.logger.info(f"Retrieved {len(comments)} comments for market {market_id}")
        return comments

    def edit_comment(self, comment_id: str, new_content: str) -> Dict[str, Any]:
        """
        Edit an existing comment.

        Args:
            comment_id: ID of the comment to edit
            new_content: New content for the comment

        Returns:
            API response with updated comment details

        Raises:
            requests.RequestException: If request fails
            ValueError: If content is invalid
        """
        if not new_content or not new_content.strip():
            raise ValueError("Comment content cannot be empty")

        self.logger.info(f"Editing comment {comment_id}")
        
        response = self._make_authenticated_request(
            "POST",
            f"/comment/{comment_id}/edit",
            json={"content": new_content}
        )
        
        self.logger.info(f"Successfully edited comment {comment_id}")
        return response

    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Delete a comment.

        Args:
            comment_id: ID of the comment to delete

        Returns:
            API response confirming deletion

        Raises:
            requests.RequestException: If request fails
        """
        self.logger.info(f"Deleting comment {comment_id}")
        
        response = self._make_authenticated_request(
            "POST",
            f"/comment/{comment_id}/delete"
        )
        
        self.logger.info(f"Successfully deleted comment {comment_id}")
        return response

    def hide_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Hide a comment (moderator action).

        Args:
            comment_id: ID of the comment to hide

        Returns:
            API response confirming hide action

        Raises:
            requests.RequestException: If request fails
        """
        self.logger.info(f"Hiding comment {comment_id}")
        
        response = self._make_authenticated_request(
            "POST",
            f"/comment/{comment_id}/hide"
        )
        
        self.logger.info(f"Successfully hid comment {comment_id}")
        return response

    def like_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Like/unlike a comment.

        Args:
            comment_id: ID of the comment to like

        Returns:
            API response with like status

        Raises:
            requests.RequestException: If request fails
        """
        self.logger.info(f"Toggling like on comment {comment_id}")
        
        response = self._make_authenticated_request(
            "POST",
            f"/comment/{comment_id}/like"
        )
        
        self.logger.info(f"Successfully toggled like on comment {comment_id}")
        return response

    # Convenience methods for common comment patterns

    def post_simple_comment(self, market_id: str, content: str) -> Dict[str, Any]:
        """
        Post a simple text comment to a market.

        Args:
            market_id: Market ID or slug
            content: Comment content in markdown

        Returns:
            API response with comment details
        """
        comment = Comment(contractId=market_id, content=content)
        return self.post_comment(comment)

    def post_analysis_comment(
        self, 
        market_id: str, 
        probability_estimate: float, 
        reasoning: str = "",
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Post a formatted analysis comment.

        Args:
            market_id: Market ID or slug
            probability_estimate: Your probability estimate (0.0 to 1.0)
            reasoning: Optional reasoning for the estimate
            confidence: Optional confidence level (0.0 to 1.0)

        Returns:
            API response with comment details
        """
        # Format analysis comment
        content_parts = [f"📊 **Analysis**: {probability_estimate:.1%} probability"]
        
        if confidence is not None:
            content_parts.append(f"**Confidence**: {confidence:.1%}")
            
        if reasoning:
            content_parts.append(f"**Reasoning**: {reasoning}")
            
        content_parts.append("*Analysis via ManifoldBot*")
        
        content = "\n\n".join(content_parts)
        return self.post_simple_comment(market_id, content)

    def post_ai_analysis_comment(
        self,
        market_id: str,
        market_question: str,
        market_description: str = "",
        current_probability: float = 0.5,
        model: str = "gpt-4",
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """
        Post an AI-generated analysis comment using OpenAI.

        Args:
            market_id: Market ID or slug
            market_question: The market question
            market_description: Optional market description
            current_probability: Current market probability
            model: OpenAI model to use for analysis
            include_reasoning: Whether to include AI reasoning

        Returns:
            Dict with 'comment_response' (API response) and 'analysis' (AI analysis results)
        """
        try:
            # Import here to avoid circular imports and handle missing dependencies
            from ..ai.openai_client import analyze_market_with_gpt
            from .comments import CommentGenerator
            
            self.logger.info(f"Generating AI analysis comment for market {market_id}")
            
            # Get AI analysis
            analysis_result = analyze_market_with_gpt(
                question=market_question,
                description=market_description,
                current_probability=current_probability,
                model=model
            )
            
            if not analysis_result.get('success', False):
                self.logger.warning(f"AI analysis failed: {analysis_result.get('error', 'Unknown error')}")
                # Post a simple fallback comment
                fallback_content = (
                    f"📊 **Market Analysis** for: {market_question}\n\n"
                    f"Current probability: {current_probability:.1%}\n\n"
                    f"*AI analysis temporarily unavailable - ManifoldBot*"
                )
                comment_response = self.post_simple_comment(market_id, fallback_content)
                return {
                    'comment_response': comment_response,
                    'analysis': analysis_result
                }
            
            # Generate comment using AI analysis
            comment_generator = CommentGenerator()
            comment_content = comment_generator.generate_analysis_comment(
                market_question=market_question,
                current_probability=current_probability,
                analysis_result=analysis_result,
                include_reasoning=include_reasoning
            )
            
            # Post the AI-generated comment
            comment_response = self.post_simple_comment(market_id, comment_content)
            
            self.logger.info(f"Successfully posted AI analysis comment: {comment_response.get('id', 'unknown_id')}")
            
            return {
                'comment_response': comment_response,
                'analysis': analysis_result
            }
            
        except ImportError as e:
            self.logger.error(f"OpenAI client not available: {e}")
            fallback_content = (
                f"📊 **Market Analysis** for: {market_question}\n\n"
                f"Current probability: {current_probability:.1%}\n\n"
                f"*AI analysis requires OpenAI integration - ManifoldBot*"
            )
            comment_response = self.post_simple_comment(market_id, fallback_content)
            return {
                'comment_response': comment_response,
                'analysis': {'success': False, 'error': 'OpenAI not available'}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post AI analysis comment: {e}")
            raise

    def post_trading_update_comment(
        self,
        market_id: str,
        action: str,
        probability_before: float,
        probability_after: float,
        amount: Optional[int] = None,
        reasoning: str = ""
    ) -> Dict[str, Any]:
        """
        Post a comment explaining a trading action and its market impact.

        Args:
            market_id: Market ID or slug
            action: Trading action ("BUY_YES", "BUY_NO", "SELL", etc.)
            probability_before: Market probability before trade
            probability_after: Market probability after trade
            amount: Amount traded (optional)
            reasoning: Reasoning for the trade

        Returns:
            API response with comment details
        """
        from .comments import CommentGenerator
        
        # Map actions to display names
        action_map = {
            "BUY_YES": "📈 YES",
            "BUY_NO": "📉 NO", 
            "SELL": "💰 SELL",
            "BUY": "📈 BUY"
        }
        
        display_action = action_map.get(action, action)
        prob_change = probability_after - probability_before
        
        content_parts = [f"🤖 **Trade Update**: {display_action}"]
        
        if amount:
            content_parts.append(f"Amount: M${amount}")
            
        content_parts.extend([
            f"**Market Impact**:",
            f"- Before: {probability_before:.1%}",
            f"- After: {probability_after:.1%}",
            f"- Change: {prob_change:+.1%}"
        ])
        
        if reasoning:
            content_parts.append(f"**Reasoning**: {reasoning}")
            
        content_parts.append("*Automated trading via ManifoldBot*")
        
        content = "\n".join(content_parts)
        return self.post_simple_comment(market_id, content)
