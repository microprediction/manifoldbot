# ManifoldBot

A Python package for interacting with Manifold Markets API.

## Installation

```bash
pip install manifoldbot
```

## Quick Start

### Read Market Data (No API Key Required)

```python
from manifoldbot.manifold import ManifoldReader

reader = ManifoldReader()
markets = reader.get_markets(limit=10)
for market in markets:
    print(f"{market['question']} - {market.get('probability', 0):.1%}")
```

### Place Bets (API Key Required)

```python
import os
from manifoldbot.manifold import ManifoldWriter

writer = ManifoldWriter(api_key=os.getenv("MANIFOLD_API_KEY"))
result = writer.place_bet("market_id", "YES", 10)  # 10Ṁ bet
print(f"Bet placed: {result['betId']}")
```

## Examples

See `manifoldbot/examples/` for complete working examples:
- `basic_reader.py` - Market data fetching
- `basic_writer.py` - Account management and trading  
- `simple_trading_bot.py` - Complete trading bot

## Documentation

- [Full Documentation](docs/README.md)
- [API Reference](docs/API_REFERENCE.md)
- [Quick Start Guide](docs/QUICKSTART.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.
