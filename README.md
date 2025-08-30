# ManifoldBot

A Python package for creating intelligent trading bots for Manifold Markets.

## Quick Start

### 1. Installation

```bash
pip install manifoldbot
```

### 2. Set API Keys

```bash
export MANIFOLD_API_KEY="your_manifold_api_key"
export OPENAI_API_KEY="your_openai_key"
```

### 3. Run the LLM Trading Bot

Trade all markets with AI:

```bash
python -m manifoldbot.examples.bot.llm_trading_bot --all
```

Or trade recent markets only:

```bash
python -m manifoldbot.examples.bot.llm_trading_bot
```

## What It Does

The LLM trading bot:
- Analyzes market questions using GPT
- Compares AI probability vs current market probability  
- Places bets when there's a significant difference (≥5%)
- Only bets when confidence is high (≥60%)

## More Examples

See `manifoldbot/examples/` for additional examples:
- `manifold/basic_reader.py` - Read market data (no API key needed)
- `manifold/basic_writer.py` - Place bets manually
- `bot/ai_optimist_trading_bot.py` - Simple rule-based bot

## Documentation

- [Full Documentation](docs/README.md)
- [Tutorial](docs/TUTORIAL.md)
- [API Reference](docs/API_REFERENCE.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.