# ManifoldBot Examples

This directory contains example scripts showing how to use ManifoldBot.

## LLM Trading Bot

The `llm_trading_bot.py` script demonstrates how to create an intelligent trading bot that uses an LLM (GPT-4) to analyze markets and place bets when it thinks the probability is off by at least 5%.

### Features

- **Market Analysis**: Uses GPT-4 to analyze market questions and estimate true probabilities
- **Confidence Threshold**: Only places bets when confidence is above a minimum threshold (default 60%)
- **Probability Difference**: Only bets when LLM estimate differs from market by at least 5%
- **Risk Management**: Configurable bet amounts and maximum number of bets per session
- **Logging**: Detailed logging of all decisions and reasoning

### Setup

1. **Install dependencies**:
   ```bash
   pip install openai
   ```

2. **Set API keys**:
   ```bash
   export MANIFOLD_API_KEY="your_manifold_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Run the bot**:
   ```bash
   python -m manifoldbot.examples.run_llm_bot
   ```

### How it Works

1. **Market Discovery**: Fetches recent markets from Manifold
2. **LLM Analysis**: For each market, sends the question and description to GPT-4
3. **Decision Making**: Compares LLM's probability estimate with current market probability
4. **Betting**: Places bets when:
   - Probability difference ≥ 5%
   - LLM confidence ≥ 60%
   - Within bet limits

### Example Output

```
2024-01-30 10:30:15 - INFO - Bot initialized with balance: 100.00 M$
2024-01-30 10:30:16 - INFO - Analyzing 10 markets...
2024-01-30 10:30:17 - INFO - Analyzing market 1/10: Will it rain tomorrow in NYC?
2024-01-30 10:30:20 - INFO - Decision: YES | Current: 45.0% | LLM: 65.0% | Diff: 20.0% | Confidence: 80.0%
2024-01-30 10:30:21 - INFO - Placed YES bet of 5 M$ on: Will it rain tomorrow in NYC?...
```

### Configuration

You can customize the bot by modifying the parameters in `main()`:

```python
bot = LLMTradingBot(
    manifold_api_key=manifold_api_key,
    openai_api_key=openai_api_key,
    min_confidence=0.6  # Minimum confidence threshold
)

# Run on recent markets
summary = bot.run_on_recent_markets(
    limit=10,      # Number of markets to analyze
    bet_amount=5,  # Amount to bet per market (M$)
    max_bets=3     # Maximum number of bets to place
)

# Run on specific user's markets (default: MikhailTal)
user_summary = bot.run_on_user_markets(
    username="MikhailTal",  # Username to analyze
    limit=10,               # Number of markets to analyze
    bet_amount=5,           # Amount to bet per market (M$)
    max_bets=3              # Maximum number of bets to place
)
```

### Safety Features

- **Rate Limiting**: Built-in delays between API calls
- **Error Handling**: Graceful handling of API errors
- **Bet Limits**: Configurable maximum number of bets per session
- **Balance Checking**: Verifies sufficient balance before betting

## Generic Bot Framework

The `manifoldbot.manifold.bot` module provides a flexible, generic trading bot framework that allows you to inject different decision-making strategies.

### Key Components

- **`ManifoldBot`** - Generic bot that handles market analysis and betting
- **`DecisionMaker`** - Abstract base class for decision-making strategies
- **`MarketDecision`** - Data structure for trading decisions
- **`TradingSession`** - Results of a trading session

### Usage Patterns

#### 1. Using Inheritance

```python
from manifoldbot import ManifoldBot, DecisionMaker, MarketDecision

class MyDecisionMaker(DecisionMaker):
    def analyze_market(self, market):
        # Your custom logic here
        return MarketDecision(
            market_id=market["id"],
            question=market["question"],
            current_probability=market["probability"],
            decision="YES",  # or "NO" or "SKIP"
            confidence=0.8,
            reasoning="My analysis"
        )

bot = ManifoldBot(
    manifold_api_key="your_key",
    decision_maker=MyDecisionMaker()
)

session = bot.run_on_recent_markets(limit=10, bet_amount=5, max_bets=3)
```

#### 2. Using Callback Functions

```python
def my_decision_function(market):
    return MarketDecision(
        market_id=market["id"],
        question=market["question"],
        current_probability=market["probability"],
        decision="YES" if market["probability"] < 0.3 else "SKIP",
        confidence=0.7,
        reasoning="Simple rule"
    )

bot = ManifoldBot(
    manifold_api_key="your_key",
    decision_maker=my_decision_function
)
```

#### 3. Built-in Decision Makers

```python
from manifoldbot.manifold.bot import SimpleRuleDecisionMaker

bot = ManifoldBot(
    manifold_api_key="your_key",
    decision_maker=SimpleRuleDecisionMaker(min_probability_diff=0.1)
)
```

### Available Methods

- `run_on_recent_markets()` - Analyze recent markets
- `run_on_user_markets()` - Analyze markets by specific user (default: MikhailTal)
- `run_on_market_by_slug()` - Analyze a specific market
- `run_on_markets()` - Analyze a custom list of markets

### Other Examples

- `basic_reader.py` - Simple market browsing
- `basic_writer.py` - Basic betting operations  
- `simple_trading_bot.py` - Rule-based trading bot
- `generic_bot_example.py` - Demonstrates the generic framework
- `llm_bot_refactored.py` - LLM bot using the generic framework
