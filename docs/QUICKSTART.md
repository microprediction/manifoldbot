# Quick Start Guide

Get up and running with ManifoldBot in 5 minutes!

## 1. Installation

```bash
pip install manifoldbot
```

## 2. Get Your API Key

1. Go to [Manifold Markets](https://manifold.markets)
2. Sign in → Profile → API Keys
3. Generate a new key
4. Copy it (you'll need it in the next step)

## 3. Set Up Environment

```bash
export MANIFOLD_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```bash
echo "MANIFOLD_API_KEY=your_api_key_here" > .env
```

## 4. Basic Usage

### Read Market Data (No API Key Required)

```python
from manifoldbot.manifold import ManifoldReader

reader = ManifoldReader()
markets = reader.get_markets(limit=5)
for market in markets:
    print(f"{market['question']} - {market.get('probability', 0):.1%}")
```

### Place Bets (API Key Required)

```python
import os
from manifoldbot.manifold import ManifoldWriter

writer = ManifoldWriter(api_key=os.getenv("MANIFOLD_API_KEY"))
result = writer.place_bet("market_id", "YES", 1)  # 1Ṁ bet
print(f"Bet placed: {result['betId']}")
```

## 5. Examples

See the `manifoldbot/examples/` directory for complete working examples:

- **basic_reader.py** - Market data fetching
- **basic_writer.py** - Account management and trading
- **simple_trading_bot.py** - Complete trading bot

Run examples:
```bash
python -m manifoldbot.examples.basic_reader
python -m manifoldbot.examples.basic_writer
```

## 7. Error Handling

```python
try:
    result = writer.place_bet("market_id", "YES", 10)
except Exception as e:
    print(f"Bet failed: {e}")
```

## 8. Next Steps

- Read the [full documentation](README.md)
- Try the [tutorial](TUTORIAL.md)
- Check the [API reference](API_REFERENCE.md)
- Join the [Manifold Markets Discord](https://discord.gg/manifold) for community support

## Need Help?

- **Documentation**: [docs/README.md](README.md)
- **API Reference**: [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Tutorial**: [docs/TUTORIAL.md](TUTORIAL.md)
- **Issues**: [GitHub Issues](https://github.com/petercotton/manifoldbot/issues)

Happy trading! 🚀
