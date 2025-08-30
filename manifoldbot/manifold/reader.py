"""
ManifoldReader - Read-only client for Manifold Markets API.

No API key required - uses public endpoints only.
Based on oreacle-bot client patterns with improved pagination handling.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class ManifoldReader:
    """
    Read-only client for Manifold Markets API.

    No API key required - uses public endpoints only.
    Handles pagination automatically for all list endpoints.
    """

    BASE_URL = "https://api.manifold.markets/v0"

    def __init__(self, timeout: int = 30, retry_config: Optional[Dict] = None):
        """
        Initialize ManifoldReader.

        Args:
            timeout: Request timeout in seconds
            retry_config: Retry configuration dict
        """
        self.timeout = timeout
        self.retry_config = retry_config or {"max_retries": 3, "backoff_factor": 2, "retry_on": [429, 500, 502, 503, 504]}

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ManifoldBot/0.1.0", "Accept": "application/json"})

        logger.info("ManifoldReader initialized (no API key required)")

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data

        Returns:
            JSON response data

        Raises:
            requests.RequestException: On request failure
        """
        # Build URL like oreacle-bot does
        url = f"{self.BASE_URL}/{endpoint}"

        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                response = self.session.request(method=method, url=url, params=params, json=data, timeout=self.timeout)

                # Check for retryable status codes
                if response.status_code in self.retry_config["retry_on"]:
                    if attempt < self.retry_config["max_retries"]:
                        wait_time = self.retry_config["backoff_factor"] ** attempt
                        logger.warning(f"Retrying request after {wait_time}s (status: {response.status_code})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries exceeded, raise exception
                        raise requests.RequestException("Max retries exceeded")

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                if attempt < self.retry_config["max_retries"]:
                    wait_time = self.retry_config["backoff_factor"] ** attempt
                    logger.warning(f"Retrying request after {wait_time}s (error: {e})")
                    time.sleep(wait_time)
                    continue
                raise

        raise requests.RequestException("Max retries exceeded")

    def _paginate(self, endpoint: str, params: Optional[Dict] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Handle pagination for list endpoints.

        Args:
            endpoint: API endpoint
            params: Query parameters
            limit: Maximum number of items to return (None for all)

        Returns:
            List of all items across all pages
        """
        all_items = []
        page_params = params.copy() if params else {}

        while True:
            response = self._make_request("GET", endpoint, params=page_params)

            # Handle different response formats
            if isinstance(response, list):
                items = response
            elif isinstance(response, dict) and "data" in response:
                items = response["data"]
            else:
                items = [response] if response else []

            all_items.extend(items)

            # Check if we've hit the limit
            if limit and len(all_items) >= limit:
                return all_items[:limit]

            # Check for pagination token/cursor
            if isinstance(response, dict):
                # Look for common pagination fields
                next_cursor = response.get("nextCursor") or response.get("next_cursor")
                if next_cursor:
                    page_params["cursor"] = next_cursor
                    continue

                # Check if there are more pages
                has_more = response.get("hasMore", False)
                if not has_more:
                    break

            # If no pagination info, assume single page
            break

        return all_items

    # Market endpoints

    def get_market(self, market_id: str) -> Dict[str, Any]:
        """
        Get market by ID or slug.

        Args:
            market_id: Market ID or slug

        Returns:
            Market data
        """
        return self._make_request("GET", f"market/{market_id}")

    def get_market_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get market by slug.

        Args:
            slug: Market slug (from URL)

        Returns:
            Market data
        """
        return self._make_request("GET", f"slug/{slug}")

    def search_markets(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search markets by query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching markets
        """
        params = {"term": query}
        return self._paginate("search-markets", params=params, limit=limit)

    def get_markets(self, limit: Optional[int] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get markets with optional filters.

        Args:
            limit: Maximum number of markets
            filters: Filter parameters (creator, category, etc.)

        Returns:
            List of markets
        """
        params = filters or {}
        return self._paginate("markets", params=params, limit=limit)

    def get_all_markets(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ALL markets by a specific user (defaults to MikhailTal).
        
        Since the API doesn't support filtering by creator, this method fetches
        all markets and filters them client-side by creator name.
        
        Args:
            username: Username to filter by. Defaults to "MikhailTal" if not provided
            
        Returns:
            List of ALL markets created by the specified user
        """
        if username is None:
            username = "MikhailTal"
        
        print(f"Fetching markets by {username}...")
        
        # Get all markets using proper pagination with 'before' parameter
        all_markets = []
        page = 1
        limit = 1000
        before_cursor = None
        
        while True:
            # Build params for this page
            params = {"limit": limit}
            if before_cursor:
                params["before"] = before_cursor
            
            # Get markets for this page
            response = self._make_request("GET", "markets", params=params)
            
            if isinstance(response, list):
                markets = response
            elif isinstance(response, dict) and "data" in response:
                markets = response["data"]
            else:
                markets = []
            
            if not markets:
                break
                
            all_markets.extend(markets)
            
            # Show progress every 10 pages
            if page % 10 == 0:
                print(f"  Fetched {len(all_markets)} markets so far...")
            
            # If we got fewer than the limit, we've reached the end
            if len(markets) < limit:
                break
                
            # Use the last market's ID as the cursor for next request
            before_cursor = markets[-1]["id"]
            page += 1
            
            # Safety check to avoid infinite loops
            if page > 100:  # Max 100 pages = 100k markets
                break
        
        # Filter by creator name - be more precise
        user_markets = [
            m for m in all_markets 
            if m.get('creatorUsername') == username
        ]
        
        # If no matches by username, try by creator name
        if not user_markets:
            user_markets = [
                m for m in all_markets 
                if m.get('creatorName') == username
            ]
        
        print(f"✅ Found {len(user_markets)} markets by {username} out of {len(all_markets)} total markets")
        return user_markets



    def get_trending_markets(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get trending markets.

        Args:
            limit: Maximum number of markets

        Returns:
            List of trending markets
        """
        return self._paginate("markets", params={"sort": "trending"}, limit=limit)

    def get_market_history(self, market_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get market price history.

        Args:
            market_id: Market ID
            limit: Maximum number of data points

        Returns:
            List of price history data points
        """
        return self._paginate(f"market/{market_id}/history", limit=limit)

    def get_market_comments(self, market_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get market comments.
        Note: This endpoint may not be available in the current API.

        Args:
            market_id: Market ID
            limit: Maximum number of comments

        Returns:
            List of comments
        """
        # This endpoint doesn't exist in the current API
        raise NotImplementedError("Market comments endpoint not available in current API")

    def get_market_bets(self, market_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get market bets.

        Args:
            market_id: Market ID
            limit: Maximum number of bets

        Returns:
            List of bets
        """
        return self._paginate(f"market/{market_id}/bets", limit=limit)

    # User endpoints

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user by ID or username.

        Args:
            user_id: User ID or username

        Returns:
            User data
        """
        return self._make_request("GET", f"user/{user_id}")

    def get_user_markets(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get markets created by user.

        Args:
            user_id: User ID or username
            limit: Maximum number of markets

        Returns:
            List of user's markets
        """
        return self._paginate(f"user/{user_id}/markets", limit=limit)

    def get_user_bets(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get bets placed by user.

        Args:
            user_id: User ID or username
            limit: Maximum number of bets

        Returns:
            List of user's bets
        """
        return self._paginate(f"user/{user_id}/bets", limit=limit)

    # Group endpoints

    def get_groups(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all groups.
        Note: This endpoint has database issues in the current API.

        Args:
            limit: Maximum number of groups

        Returns:
            List of groups
        """
        # This endpoint has database errors in the current API
        raise NotImplementedError("Groups endpoint has database issues in current API")

    def get_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get group by ID or slug.

        Args:
            group_id: Group ID or slug

        Returns:
            Group data
        """
        return self._make_request("GET", f"group/{group_id}")

    def get_group_markets(self, group_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get markets in group.

        Args:
            group_id: Group ID or slug
            limit: Maximum number of markets

        Returns:
            List of group markets
        """
        return self._paginate(f"group/{group_id}/markets", limit=limit)

    # Utility methods

    def get_market_probability(self, market_id: str) -> float:
        """
        Get current market probability.

        Args:
            market_id: Market ID

        Returns:
            Current probability (0.0 to 1.0)
        """
        market = self.get_market(market_id)
        return market.get("probability", 0.0)

    def get_market_probability_percent(self, market_id: str) -> float:
        """
        Get current market probability as percentage.

        Args:
            market_id: Market ID

        Returns:
            Current probability as percentage (0.0 to 100.0)
        """
        probability = self.get_market_probability(market_id)
        return probability * 100.0

    def get_market_basic_info(self, market_id: str) -> Dict[str, Any]:
        """
        Get basic market information.

        Args:
            market_id: Market ID

        Returns:
            Basic market info (question, probability, volume, etc.)
        """
        market = self.get_market(market_id)
        return {
            "id": market.get("id"),
            "question": market.get("question"),
            "description": market.get("description"),
            "probability": market.get("probability", 0.0),
            "probability_percent": market.get("probability", 0.0) * 100.0,
            "volume": market.get("volume", 0),
            "total_liquidity": market.get("totalLiquidity", 0),
            "yes_liquidity": market.get("yesLiquidity", 0),
            "no_liquidity": market.get("noLiquidity", 0),
            "creator": market.get("creatorName"),
            "created_time": market.get("createdTime"),
            "close_time": market.get("closeTime"),
            "resolution": market.get("resolution"),
            "is_resolved": market.get("isResolved", False),
        }

    def get_market_liquidity(self, market_id: str) -> Dict[str, Any]:
        """
        Get market liquidity information.

        Args:
            market_id: Market ID

        Returns:
            Liquidity data
        """
        market = self.get_market(market_id)
        return {
            "total": market.get("totalLiquidity", 0),
            "yes": market.get("yesLiquidity", 0),
            "no": market.get("noLiquidity", 0),
        }

    def get_market_depth(self, market_id: str, levels: int = 10) -> Dict[str, Any]:
        """
        Get market depth at different price levels.

        Args:
            market_id: Market ID
            levels: Number of price levels

        Returns:
            Market depth data
        """
        # This would need to be implemented based on actual API
        # For now, return basic liquidity info
        return self.get_market_liquidity(market_id)

    def get_market_risk_metrics(self, market_id: str) -> Dict[str, Any]:
        """
        Get market risk metrics.

        Args:
            market_id: Market ID

        Returns:
            Risk metrics
        """
        # This would need to be implemented based on actual API
        # For now, return basic market info
        market = self.get_market(market_id)
        return {
            "volatility": 0.0,  # Would need to calculate from history
            "max_drawdown": 0.0,  # Would need to calculate from history
            "sharpe_ratio": 0.0,  # Would need to calculate from history
        }
