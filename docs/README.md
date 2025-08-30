# ManifoldBot Documentation

A Python package for interacting with Manifold Markets API.

## Features

- **ManifoldReader**: Read-only access to Manifold Markets data (no API key required)
- **ManifoldWriter**: Authenticated access for trading and market management (API key required)
- **Basic API Coverage**: Markets, users, bets, comments, and portfolio management
- **Error Handling**: Retry logic and graceful error handling
- **Type Safety**: Full type hints throughout

## Installation

```bash
pip install manifoldbot
```

## Quick Start

### Reading Market Data

```python
from manifoldbot.manifold import ManifoldReader

# Initialize reader (no API key needed)
reader = ManifoldReader()

# Get recent markets
markets = reader.get_markets(limit=10)
for market in markets:
    print(f"{market['question']} - {market.get('probability', 0):.1%}")

# Get specific market by ID
market = reader.get_market("market_id_here")
print(f"Current probability: {market['probability']:.1%}")

# Get market by slug
market = reader.get_market_by_slug("market-slug-here")
```

### Trading with Authentication

```python
from manifoldbot.manifold import ManifoldWriter
import os

# Initialize writer (API key required)
api_key = os.getenv("MANIFOLD_API_KEY")
writer = ManifoldWriter(api_key=api_key)

# Check authentication
if writer.is_authenticated():
    print(f"Logged in as: {writer.get_me()['name']}")
    print(f"Balance: {writer.get_balance()}Ṁ")

# Place a market bet
result = writer.place_bet("market_id", "YES", 10)  # 10Ṁ bet
print(f"Bet placed: {result['betId']}")

# Place a limit order
result = writer.place_limit_yes("market_id", 10, 0.7)  # 10Ṁ at 70% probability
print(f"Limit order placed: {result['betId']}")
```

## API Reference

### ManifoldReader

Read-only access to Manifold Markets data (no API key required).

#### Core Methods

- `get_markets(limit=None, filters=None)` - Get list of markets
- `get_market(market_id)` - Get specific market by ID
- `get_market_by_slug(slug)` - Get market by slug
- `search_markets(query, limit=None)` - Search markets by query
- `get_trending_markets(limit=None)` - Get trending markets

#### User Methods

- `get_user(user_id)` - Get user information
- `get_user_markets(user_id, limit=None)` - Get markets created by user
- `get_user_bets(user_id, limit=None)` - Get bets placed by user

#### Market Details

- `get_market_bets(market_id, limit=None)` - Get bets on a market
- `get_market_history(market_id, limit=None)` - Get market price history
- `get_market_probability(market_id)` - Get current probability (0.0-1.0)
- `get_market_probability_percent(market_id)` - Get probability as percentage
- `get_market_basic_info(market_id)` - Get basic market info
- `get_market_liquidity(market_id)` - Get liquidity information

#### Group Methods

- `get_group(group_id)` - Get group information
- `get_group_markets(group_id, limit=None)` - Get markets in group

**Note:** `get_groups()` and `get_market_comments()` raise `NotImplementedError` due to API limitations.

### ManifoldWriter

Authenticated access for trading and market management (API key required).

#### Authentication

- `is_authenticated()` - Check if properly authenticated
- `get_me()` - Get current user information
- `update_user(**kwargs)` - Update user profile

#### Trading

- `place_bet(market_id, outcome, amount, probability=None)` - Place bet (market or limit order)
- `place_limit_yes(market_id, amount, limit_prob)` - Place YES limit order
- `place_limit_no(market_id, amount, limit_prob)` - Place NO limit order
- `cancel_bet(bet_id)` - Cancel pending bet
- `get_bet(bet_id)` - Get bet details

#### Portfolio Management

- `get_balance()` - Get current balance
- `get_total_deposits()` - Get total deposits
- `get_portfolio()` - Get portfolio summary (simplified from user data)
- `get_positions(market_id=None)` - Get user positions (returns empty list - API not available)

#### Market Management

- `create_market(question, description, outcome_type="BINARY", ...)` - Create new market
- `close_market(market_id, outcome, probability=None)` - Close market with resolution

#### Comments

- `post_comment(market_id, text, reply_to=None)` - Post comment on market

#### Advanced Trading

- `calculate_market_impact(market_id, amount, outcome)` - Calculate bet impact
- `place_bet_with_impact_limit(market_id, outcome, amount, max_impact)` - Place bet with impact limit

## Examples

Working examples are available in the `manifoldbot/examples/` directory:

- **[manifold/basic_reader.py](manifoldbot/examples/manifold/basic_reader.py)** - Basic market data fetching
- **[manifold/basic_writer.py](manifoldbot/examples/manifold/basic_writer.py)** - Authenticated operations and account management  
- **[bot/llm_trading_bot.py](manifoldbot/examples/bot/llm_trading_bot.py)** - LLM-powered trading bot
- **[bot/ai_optimist_trading_bot.py](manifoldbot/examples/bot/ai_optimist_trading_bot.py)** - Simple rule-based trading bot

Run examples directly:
```bash
python -m manifoldbot.examples.manifold.basic_reader
python -m manifoldbot.examples.manifold.basic_writer
python -m manifoldbot.examples.bot.llm_trading_bot
python -m manifoldbot.examples.bot.llm_trading_bot --all
```

**Note:** Examples are tested to ensure they stay up-to-date with the API.

## Configuration

### Environment Variables

Set these environment variables for authentication:

```bash
export MANIFOLD_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_openai_key_here"  # For AI features
```

### API Key Setup

1. Go to [Manifold Markets](https://manifold.markets)
2. Sign in and go to your profile
3. Generate an API key
4. Set the `MANIFOLD_API_KEY` environment variable

## Error Handling

The package includes robust error handling:

```python
from manifoldbot.manifold import ManifoldWriter
import requests

writer = ManifoldWriter(api_key="your_key")

try:
    result = writer.place_bet("market_id", "YES", 10)
except requests.RequestException as e:
    print(f"API error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Testing

Run the test suite:

```bash
# Unit tests (mocked API calls)
pytest tests/

# Real API tests (requires API key)
pytest tests/manifold/test_reader_real.py tests/manifold/test_writer_real.py

# Test examples to ensure they stay up-to-date
pytest tests/test_examples.py
```

**Note:** The project is tested on Python 3.12. All examples are tested to ensure they work with the current API.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
