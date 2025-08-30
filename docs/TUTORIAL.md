# ManifoldBot Tutorial

This tutorial shows you how to use ManifoldBot with working examples.

## Prerequisites

- Python 3.9 or higher
- Manifold Markets account (for trading)
- API key from Manifold Markets (for trading)

## Setup

### 1. Installation

```bash
pip install manifoldbot
```

### 2. Get Your API Key (for trading)

1. Go to [Manifold Markets](https://manifold.markets)
2. Sign in to your account
3. Go to your profile settings
4. Generate an API key
5. Copy the key

### 3. Set Environment Variables

```bash
export MANIFOLD_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_openai_key_here"  # For LLM features
```

## Tutorial 1: Reading Market Data

Start with reading market data (no API key required):

```python
from manifoldbot import ManifoldReader

# Initialize the reader
reader = ManifoldReader()

# Get recent markets
markets = reader.get_markets(limit=5)
for market in markets:
    print(f"{market['question']} - {market.get('probability', 0):.1%}")
```

Run this example:
```bash
python -m manifoldbot.examples.manifold.basic_reader
```

## Tutorial 2: Basic Trading

Place bets using your API key:

```python
import os
from manifoldbot import ManifoldWriter

# Initialize writer with API key
writer = ManifoldWriter(api_key=os.getenv("MANIFOLD_API_KEY"))

# Check authentication
if writer.is_authenticated():
    print(f"Balance: {writer.get_balance():.2f} M$")
    
    # Place a small bet
    result = writer.place_bet("market_id", "YES", 1)  # 1 M$ bet
    print(f"Bet placed: {result['betId']}")
```

Run this example:
```bash
python -m manifoldbot.examples.manifold.basic_writer
```

## Tutorial 3: Simple Trading Bot

Use a simple rule-based bot:

```python
import os
from manifoldbot.examples.bot.ai_optimist_trading_bot import main

# Run the AI optimist bot
main()
```

Run this example:
```bash
python -m manifoldbot.examples.bot.ai_optimist_trading_bot
```

## Tutorial 4: LLM Trading Bot

Use an LLM-powered trading bot:

```python
import os
from manifoldbot.examples.bot.llm_trading_bot import main

# Run on recent markets
main(trade_all=False)

# Or run on all markets
main(trade_all=True)
```

Run this example:
```bash
# Trade recent markets
python -m manifoldbot.examples.bot.llm_trading_bot

# Trade all markets
python -m manifoldbot.examples.bot.llm_trading_bot --all
```

## Tutorial 5: Using the Bot Framework

Create custom trading bots using the framework:

```python
import os
from manifoldbot import ManifoldBot, RandomDecisionMaker

# Create a decision maker
decision_maker = RandomDecisionMaker()

# Create bot
bot = ManifoldBot(
    manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
    decision_maker=decision_maker
)

# Run on recent markets
session = bot.run_on_recent_markets(limit=5, bet_amount=5, max_bets=2)

print(f"Markets analyzed: {session.markets_analyzed}")
print(f"Bets placed: {session.bets_placed}")
```

Run this example:
```bash
python -m manifoldbot.examples.bot.generic_bot_example
```

## Best Practices

1. **Start Small**: Begin with small bet amounts (1-5 M$)
2. **Test First**: Use the examples to understand the API
3. **Monitor Balance**: Check your balance regularly
4. **Handle Errors**: Always wrap trading code in try/catch blocks
5. **Rate Limiting**: The package handles rate limits automatically

## Error Handling

```python
import os
from manifoldbot import ManifoldWriter
import requests

writer = ManifoldWriter(api_key=os.getenv("MANIFOLD_API_KEY"))

try:
    result = writer.place_bet("market_id", "YES", 10)
    print(f"Bet placed: {result['betId']}")
except requests.RequestException as e:
    print(f"API error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Next Steps

- Read the [API Reference](API_REFERENCE.md) for detailed method documentation
- Check the [main documentation](README.md) for advanced features
- Join the [Manifold Markets Discord](https://discord.gg/manifold) for community support

Happy trading! 🚀