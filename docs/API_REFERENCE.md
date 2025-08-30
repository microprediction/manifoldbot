# API Reference

## ManifoldReader

The `ManifoldReader` class provides read-only access to Manifold Markets data. No API key is required.

### Constructor

```python
ManifoldReader(timeout=30, retry_config=None)
```

**Parameters:**
- `timeout` (int): Request timeout in seconds (default: 30)
- `retry_config` (dict, optional): Custom retry configuration

### Methods

#### `get_markets(limit=None, before=None)`

Get a list of markets from Manifold Markets.

**Parameters:**
- `limit` (int, optional): Maximum number of markets to return
- `before` (str, optional): Cursor for pagination

**Returns:** `List[Dict[str, Any]]` - List of market dictionaries

**Example:**
```python
reader = ManifoldReader()

# Get 10 most recent markets
markets = reader.get_markets(limit=10)

# Get markets with pagination
markets = reader.get_markets(limit=50, before="cursor_string")
```

#### `get_market(market_id)`

Get detailed information about a specific market.

**Parameters:**
- `market_id` (str): The market ID

**Returns:** `Dict[str, Any]` - Market dictionary

**Example:**
```python
market = reader.get_market("8PLAdy8q8u")
print(f"Question: {market['question']}")
print(f"Probability: {market.get('probability', 0):.1%}")
```

#### `get_market_by_slug(slug)`

Get market information using the market slug.

**Parameters:**
- `slug` (str): The market slug (from the URL)

**Returns:** `Dict[str, Any]` - Market dictionary

**Example:**
```python
market = reader.get_market_by_slug("catl-receives-license-renewal-for-y-qz65RqIZsy")
```

#### `get_user(user_id)`

Get user information.

**Parameters:**
- `user_id` (str): The user ID

**Returns:** `Dict[str, Any]` - User dictionary

**Example:**
```python
user = reader.get_user("user_id_here")
print(f"Username: {user['name']}")
print(f"Total deposits: {user.get('totalDeposits', 0)}Ṁ")
```

#### `get_user_markets(user_id, limit=None)`

Get markets created by a specific user.

**Parameters:**
- `user_id` (str): The user ID
- `limit` (int, optional): Maximum number of markets to return

**Returns:** `List[Dict[str, Any]]` - List of market dictionaries

**Example:**
```python
user_markets = reader.get_user_markets("MikhailTal", limit=20)
print(f"User has created {len(user_markets)} markets")
```

#### `get_market_bets(market_id, limit=None)`

Get bets placed on a specific market.

**Parameters:**
- `market_id` (str): The market ID
- `limit` (int, optional): Maximum number of bets to return

**Returns:** `List[Dict[str, Any]]` - List of bet dictionaries

#### `search_markets(query, limit=None)`

Search for markets by query string.

**Parameters:**
- `query` (str): Search query
- `limit` (int, optional): Maximum number of results

**Returns:** `List[Dict[str, Any]]` - List of matching markets

## ManifoldWriter

The `ManifoldWriter` class provides authenticated access for trading and market management. Requires a valid API key.

### Constructor

```python
ManifoldWriter(api_key, timeout=30, retry_config=None)
```

**Parameters:**
- `api_key` (str): Manifold Markets API key
- `timeout` (int): Request timeout in seconds (default: 30)
- `retry_config` (dict, optional): Custom retry configuration

### Authentication Methods

#### `is_authenticated()`

Check if the writer is properly authenticated.

**Returns:** `bool` - True if authenticated, False otherwise

**Example:**
```python
writer = ManifoldWriter(api_key="your_key")
if writer.is_authenticated():
    print("Successfully authenticated")
else:
    print("Authentication failed")
```

#### `get_me()`

Get information about the authenticated user.

**Returns:** `Dict[str, Any]` - User dictionary

**Example:**
```python
user_info = writer.get_me()
print(f"Username: {user_info['name']}")
print(f"Balance: {user_info['balance']}Ṁ")
```

### Trading Methods

#### `place_bet(market_id, outcome, amount, probability=None)`

Place a bet on a market.

**Parameters:**
- `market_id` (str): Market ID
- `outcome` (str): "YES" or "NO"
- `amount` (int): Amount in M$ (must be positive integer)
- `probability` (float, optional): Limit price (0-1) for limit orders

**Returns:** `Dict[str, Any]` - Bet result dictionary

**Example:**
```python
# Market order
result = writer.place_bet("market_id", "YES", 10)

# Limit order
result = writer.place_bet("market_id", "YES", 10, probability=0.7)
```

#### `place_limit_yes(market_id, amount, limit_prob)`

Place a YES limit order (convenience method).

**Parameters:**
- `market_id` (str): Market ID
- `amount` (int): Amount in M$
- `limit_prob` (float): Limit probability (0.0-1.0)

**Returns:** `Dict[str, Any]` - Bet result dictionary

#### `place_limit_no(market_id, amount, limit_prob)`

Place a NO limit order (convenience method).

**Parameters:**
- `market_id` (str): Market ID
- `amount` (int): Amount in M$
- `limit_prob` (float): Limit probability (0.0-1.0)

**Returns:** `Dict[str, Any]` - Bet result dictionary

#### `cancel_bet(bet_id)`

Cancel a pending bet.

**Parameters:**
- `bet_id` (str): Bet ID to cancel

**Returns:** `Dict[str, Any]` - Cancellation result

#### `get_bet(bet_id)`

Get details of a specific bet.

**Parameters:**
- `bet_id` (str): Bet ID

**Returns:** `Dict[str, Any]` - Bet dictionary

### Portfolio Methods

#### `get_balance()`

Get current balance.

**Returns:** `float` - Balance in M$

#### `get_total_deposits()`

Get total deposits.

**Returns:** `float` - Total deposits in M$

#### `get_portfolio()`

Get portfolio summary.

**Returns:** `Dict[str, Any]` - Portfolio dictionary

#### `get_positions(market_id=None)`

Get user's positions.

**Parameters:**
- `market_id` (str, optional): Filter by specific market

**Returns:** `List[Dict[str, Any]]` - List of positions

### Market Management Methods

#### `create_market(question, outcome_type="BINARY", **kwargs)`

Create a new market.

**Parameters:**
- `question` (str): Market question
- `outcome_type` (str): "BINARY", "FREE_RESPONSE", or "MULTIPLE_CHOICE"
- `**kwargs`: Additional market parameters

**Returns:** `Dict[str, Any]` - Created market dictionary

**Example:**
```python
market = writer.create_market(
    question="Will AI achieve AGI by 2030?",
    outcome_type="BINARY",
    description="This market resolves YES if...",
    initial_probability=0.3,
    close_time=1735689600000,  # Unix timestamp
    tags=["AI", "AGI", "technology"]
)
```

#### `close_market(market_id, outcome, probability=None)`

Close a market with a resolution.

**Parameters:**
- `market_id` (str): Market ID
- `outcome` (str): "YES", "NO", "MKT", or "CANCEL"
- `probability` (float, optional): Resolution probability for "MKT" outcome

**Returns:** `Dict[str, Any]` - Market closure result

### Comment Methods

#### `post_comment(market_id, text, reply_to=None)`

Post a comment on a market.

**Parameters:**
- `market_id` (str): Market ID
- `text` (str): Comment text
- `reply_to` (str, optional): Comment ID to reply to

**Returns:** `Dict[str, Any]` - Comment result

### Advanced Trading Methods

#### `calculate_market_impact(market_id, amount, outcome)`

Calculate the impact of a potential bet on market probability.

**Parameters:**
- `market_id` (str): Market ID
- `amount` (float): Bet amount
- `outcome` (str): "YES" or "NO"

**Returns:** `Dict[str, Any]` - Impact calculation result

**Example:**
```python
impact = writer.calculate_market_impact("market_id", 100, "YES")
print(f"Current probability: {impact['current_probability']:.1%}")
print(f"New probability: {impact['new_probability']:.1%}")
print(f"Impact: {impact['estimated_impact']:.3f}")
```

#### `place_bet_with_impact_limit(market_id, outcome, amount, max_impact)`

Place a bet only if its impact is below a threshold.

**Parameters:**
- `market_id` (str): Market ID
- `outcome` (str): "YES" or "NO"
- `amount` (int): Bet amount
- `max_impact` (float): Maximum allowed impact

**Returns:** `Dict[str, Any]` - Bet result or raises ValueError

**Example:**
```python
try:
    result = writer.place_bet_with_impact_limit(
        "market_id", "YES", 100, max_impact=0.05
    )
    print("Bet placed successfully")
except ValueError as e:
    print(f"Bet rejected: {e}")
```

### User Management Methods

#### `update_user(**kwargs)`

Update user profile information.

**Parameters:**
- `**kwargs`: Fields to update (e.g., "name", "bio")

**Returns:** `Dict[str, Any]` - Updated user data

**Example:**
```python
updated_user = writer.update_user(
    name="New Name",
    bio="Updated bio"
)
```

## Error Handling

### Common Exceptions

#### `requests.RequestException`
Raised for HTTP errors (network issues, API errors, etc.)

#### `ValueError`
Raised for validation errors (invalid parameters, etc.)

#### `NotImplementedError`
Raised for API endpoints that are not available

### Example Error Handling

```python
from manifoldbot.manifold import ManifoldWriter
import requests

writer = ManifoldWriter(api_key="your_key")

try:
    result = writer.place_bet("market_id", "YES", 10)
except requests.RequestException as e:
    if e.response.status_code == 400:
        print("Bad request - check market ID and parameters")
    elif e.response.status_code == 401:
        print("Authentication failed - check API key")
    elif e.response.status_code == 403:
        print("Insufficient permissions")
    else:
        print(f"API error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Rate Limiting

The package includes built-in retry logic for handling rate limits and temporary API issues. By default, it will retry failed requests up to 3 times with exponential backoff.

You can customize the retry behavior:

```python
retry_config = {
    "max_retries": 5,
    "backoff_factor": 2,
    "retry_on": [429, 500, 502, 503, 504]
}

reader = ManifoldReader(retry_config=retry_config)
writer = ManifoldWriter(api_key="your_key", retry_config=retry_config)
```
