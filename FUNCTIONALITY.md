# ManifoldBot Functionality Specification

## Overview

ManifoldBot is designed as a comprehensive Python package for creating intelligent trading bots that interact with Manifold Markets. The package provides a robust client for Manifold Markets API operations, AI-powered analysis capabilities, and automated trading functionality.

The package is generic and can be used for any type of market monitoring and trading. Specific use cases (like Chinese regulatory monitoring) are provided as examples in the `/examples` folder.

## Architecture: Reader/Writer Separation

ManifoldBot uses a clean separation of concerns with two main client classes:

### ManifoldReader (No API Key Required)
- **Purpose**: Read public market data, analyze markets, calculate metrics
- **Use Cases**: Market research, analysis, monitoring
- **API Key**: Not required - uses public endpoints only
- **Rate Limits**: Higher rate limits for public data access

### ManifoldWriter (API Key Required)
- **Purpose**: Place bets, manage positions, post comments, trading operations
- **Use Cases**: Automated trading, position management, market making
- **API Key**: Required - uses authenticated endpoints
- **Rate Limits**: Lower rate limits for trading operations

This separation allows users to:
- **Analyze markets** without needing an API key
- **Develop and test strategies** using only the reader
- **Deploy trading bots** with the writer when ready
- **Scale analysis** across many markets without API key limits

## Core Manifold Markets Client Functionality

### 1. Market Information Retrieval (ManifoldReader)

#### 1.1 Market Discovery and Search
```python
from manifoldbot import ManifoldReader

# No API key needed for reading public data
reader = ManifoldReader()

# Search markets by query
markets = reader.search_markets("CATL lithium mine")
for market in markets:
    print(f"{market.question} - {market.probability}%")

# Get market by slug
market = reader.get_market("MikhailTal/catl-receives-license-renewal-for-y")
```

#### 1.2 Market Data Access
- **Market Details**: Question, description, probability, volume, liquidity
- **Market History**: Price history, volume history, resolution history
- **Market Comments**: All comments with pagination support
- **Market Positions**: Current positions and position history (public data only)
- **Market Trades**: Recent trades and trade history (public data only)

#### 1.3 Pagination Handling
Based on the [oreacle-bot implementation](https://github.com/microprediction/oreacle-bot), the reader will properly handle pagination for:
- Market lists (search results, trending markets, etc.)
- Comments (with proper pagination tokens)
- Trade history
- Position history
- User data

```python
# Automatic pagination handling
all_comments = reader.get_market_comments(market_id, limit=None)  # Gets all comments
recent_comments = reader.get_market_comments(market_id, limit=50)  # Gets first 50
```

### 2. Trading Operations (ManifoldWriter)

#### 2.1 Placing Bets
```python
from manifoldbot import ManifoldWriter

# API key required for trading operations
writer = ManifoldWriter(api_key="your_manifold_api_key")

# Simple bet placement
bet = writer.place_bet(
    market_id="market_id",
    outcome="YES",  # or "NO"
    amount=10,      # M$
    probability=0.6  # Optional: limit order at 60%
)

# Market order (immediate execution)
bet = writer.place_bet(
    market_id="market_id",
    outcome="YES",
    amount=10,
    order_type="market"
)
```

#### 2.2 Advanced Trading Features
- **Limit Orders**: Place bets at specific probability levels
- **Market Orders**: Immediate execution at current market price
- **Partial Fills**: Handle partial order execution
- **Order Management**: Cancel pending orders, modify orders
- **Position Sizing**: Calculate optimal bet sizes

#### 2.3 Market Impact Calculation

One of the key features is the ability to calculate how much to bet to move the market by a specific percentage:

```python
# Calculate bet size to move market 1% (uses reader for market data)
bet_amount = writer.calculate_market_impact(
    market_id="market_id",
    target_probability_change=0.01,  # 1% change
    outcome="YES"
)
print(f"Need to bet {bet_amount} M$ to move market 1%")

# More sophisticated impact calculation
impact_analysis = writer.analyze_market_impact(
    market_id="market_id",
    bet_amount=50,
    outcome="YES"
)
print(f"Expected probability change: {impact_analysis.expected_change}")
print(f"Confidence interval: {impact_analysis.confidence_interval}")
```

### 3. Market Analysis and Metrics (ManifoldReader)

#### 3.1 Liquidity Analysis
```python
# Get market liquidity metrics (no API key needed)
liquidity = reader.get_market_liquidity(market_id)
print(f"Total liquidity: {liquidity.total} M$")
print(f"YES liquidity: {liquidity.yes} M$")
print(f"NO liquidity: {liquidity.no} M$")

# Calculate liquidity depth at different price levels
depth = reader.get_market_depth(market_id, levels=10)
```

#### 3.2 Market Efficiency Metrics
- **Bid-Ask Spread**: Current spread and historical spread analysis
- **Volume Analysis**: Trading volume patterns and trends
- **Price Discovery**: How quickly prices adjust to new information
- **Arbitrage Opportunities**: Cross-market arbitrage detection

#### 3.3 Risk Metrics
```python
# Calculate market risk metrics (no API key needed)
risk_metrics = reader.get_market_risk_metrics(market_id)
print(f"Volatility: {risk_metrics.volatility}")
print(f"Max drawdown: {risk_metrics.max_drawdown}")
print(f"Sharpe ratio: {risk_metrics.sharpe_ratio}")
```

## AI-Powered Analysis Integration

### 4. Content Analysis Pipeline

#### 4.1 Document Processing
```python
from manifoldbot import Bot, AIClient

# Initialize AI client
ai_client = AIClient(api_key="openai_key")

# Analyze document content
analysis = ai_client.analyze_document(
    content="Document content here...",
    market_context="CATL lithium mine license renewal",
    analysis_type="regulatory_document"
)

print(f"Confidence: {analysis.confidence}")
print(f"Recommendation: {analysis.recommendation}")
print(f"Key evidence: {analysis.evidence}")
```

#### 4.2 Market-Specific Analysis
- **Regulatory Documents**: SEC filings, regulatory announcements
- **News Articles**: Financial news, company announcements
- **Social Media**: Twitter, Reddit sentiment analysis
- **Technical Analysis**: Chart patterns, technical indicators
- **Custom Sources**: Any data source can be integrated via the data source framework

### 5. Automated Trading Logic

#### 5.1 Decision Engine
```python
# Configure trading rules
trading_rules = {
    "min_confidence": 0.75,
    "max_position_size": 50,  # M$
    "stop_loss": 0.1,        # 10% loss
    "take_profit": 0.2,      # 20% gain
    "risk_per_trade": 0.02   # 2% of portfolio
}

# Automated trading decision
decision = bot.make_trading_decision(
    market_id="market_id",
    analysis_result=analysis,
    trading_rules=trading_rules
)

if decision.should_trade:
    bet = writer.place_bet(
        market_id=decision.market_id,
        outcome=decision.outcome,
        amount=decision.amount,
        probability=decision.probability
    )
```

#### 5.2 Risk Management
- **Position Sizing**: Kelly criterion, fixed fractional, volatility-based
- **Portfolio Management**: Diversification, correlation analysis
- **Stop Losses**: Dynamic stop losses based on volatility
- **Take Profits**: Profit-taking strategies

## Data Source Integration

### 6. Multi-Source Data Collection

#### 6.1 Web Scraping
```python
# Configure web scraping source
web_source = WebSource(
    name="SEC Filings",
    url="https://www.sec.gov/edgar/search/",
    selector=".filing-item",
    poll_interval=900  # 15 minutes
)

# Monitor for new content
new_items = web_source.get_new_items()
for item in new_items:
    analysis = ai_client.analyze_document(item.content)
    # Process analysis...
```

#### 6.2 RSS Feeds
```python
# RSS feed monitoring
rss_source = RSSSource(
    name="Financial News",
    url="https://feeds.finance.yahoo.com/rss/2.0/headline",
    poll_interval=300  # 5 minutes
)
```

#### 6.3 API Integrations
```python
# API-based data sources
api_source = APISource(
    name="SEC Filings",
    base_url="https://api.sec.gov",
    endpoint="/filings",
    auth_type="api_key"
)
```

## Configuration and Deployment

### 7. Bot Configuration

#### 7.1 YAML Configuration
```yaml
# bot_config.yaml
name: "Market Monitor Bot"
description: "Monitors data sources and trades on Manifold Markets"

# Data sources
data_sources:
  - type: "web"
    name: "SEC Filings"
    url: "https://www.sec.gov/edgar/search/"
    selector: ".filing-item"
    poll_interval: 900
    
  - type: "rss"
    name: "Financial News"
    url: "https://feeds.finance.yahoo.com/rss/2.0/headline"
    poll_interval: 300

# AI configuration
ai:
  model: "gpt-4o-mini"
  confidence_threshold: 0.75
  max_tokens: 2000

# Manifold configuration
manifold:
  market_slug: "username/your-market-slug"
  comment_only: false
  max_position_size: 50
  default_probability: 0.55

# Trading rules
trading:
  min_confidence: 0.8
  max_risk_per_trade: 0.02
  stop_loss: 0.1
  take_profit: 0.2
```

#### 7.2 Programmatic Configuration
```python
from manifoldbot import Bot, BotConfig, DataSourceConfig

# Create configuration programmatically
config = BotConfig(
    name="My Trading Bot",
    data_sources=[
        DataSourceConfig(
            type="web",
            name="News Source",
            url="https://example.com/news",
            selector=".news-item",
            poll_interval=900
        )
    ],
    manifold=ManifoldConfig(
        market_slug="username/market-slug",
        comment_only=False,
        max_position_size=25
    )
)

# Create and run bot
bot = Bot(config)
bot.run()
```

### 8. Deployment Options

#### 8.1 Local Development
```bash
# Install package
pip install -e .

# Run bot
manifoldbot start --config bot_config.yaml
```

#### 8.2 Docker Deployment
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["manifoldbot", "start", "--config", "bot_config.yaml"]
```

#### 8.3 GitHub Actions
```yaml
name: ManifoldBot
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run ManifoldBot
        env:
          MANIFOLD_API_KEY: ${{ secrets.MANIFOLD_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pip install -e .
          manifoldbot start --config bot_config.yaml
```

## Advanced Features

### 9. Portfolio Management

#### 9.1 Multi-Market Trading
```python
# Monitor multiple markets
markets = [
    "market1-slug",
    "market2-slug",
    "market3-slug"
]

# Portfolio-level risk management
portfolio = Portfolio(
    max_total_exposure=100,  # M$
    max_correlation=0.7,
    rebalance_frequency="daily"
)

for market_id in markets:
    analysis = bot.analyze_market(market_id)
    position = portfolio.calculate_position(analysis)
    if position.should_trade:
        client.place_bet(market_id, position.outcome, position.amount)
```

#### 9.2 Cross-Market Arbitrage
```python
# Find arbitrage opportunities (uses reader for analysis)
arbitrage_ops = reader.find_arbitrage_opportunities(
    markets=["market1", "market2"],
    min_profit=0.01  # 1% minimum profit
)

for op in arbitrage_ops:
    # Execute arbitrage trades (uses writer for trading)
    writer.place_bet(op.market1_id, op.outcome1, op.amount1)
    writer.place_bet(op.market2_id, op.outcome2, op.amount2)
```

### 10. Monitoring and Alerting

#### 10.1 Real-time Monitoring
```python
# Set up monitoring (uses reader for data collection)
monitor = MarketMonitor(
    reader=reader,  # No API key needed for monitoring
    markets=["market1", "market2"],
    alert_thresholds={
        "price_change": 0.05,  # 5% price change
        "volume_spike": 2.0,   # 2x volume increase
        "liquidity_drop": 0.3  # 30% liquidity drop
    }
)

# Start monitoring
monitor.start()
```

#### 10.2 Alert System
```python
# Configure alerts
alerts = AlertSystem(
    channels=["email", "slack", "discord"],
    rules={
        "large_trade": {"threshold": 100, "action": "notify"},
        "market_resolution": {"action": "close_positions"},
        "api_error": {"action": "retry", "max_retries": 3}
    }
)
```

## Error Handling and Resilience

### 11. Robust Error Handling

#### 11.1 API Error Handling
```python
# Automatic retry with exponential backoff
reader = ManifoldReader(
    retry_config={
        "max_retries": 3,
        "backoff_factor": 2,
        "retry_on": [429, 500, 502, 503, 504]
    }
)

writer = ManifoldWriter(
    api_key="key",
    retry_config={
        "max_retries": 3,
        "backoff_factor": 2,
        "retry_on": [429, 500, 502, 503, 504]
    }
)
```

#### 11.2 Network Resilience
- **Connection Pooling**: Reuse HTTP connections
- **Timeout Handling**: Configurable timeouts for different operations
- **Circuit Breaker**: Stop making requests if service is down
- **Graceful Degradation**: Continue operating with reduced functionality

### 12. Data Persistence

#### 12.1 SQLite Database
```python
# Automatic data persistence
storage = SQLiteStorage("bot_data.db")

# Store market data
storage.store_market_data(market_id, data)

# Store trade history
storage.store_trade(trade)

# Store analysis results
storage.store_analysis(analysis)
```

#### 12.2 Backup and Recovery
- **Automatic Backups**: Regular database backups
- **Data Export**: Export data to CSV/JSON
- **State Recovery**: Resume from last known state

## Performance Optimization

### 13. Efficient Data Processing

#### 13.1 Caching
```python
# Redis caching for frequently accessed data
cache = RedisCache(host="localhost", port=6379)

# Cache market data (reader)
cached_market = cache.get_or_set(
    f"market:{market_id}",
    lambda: reader.get_market(market_id),
    ttl=300  # 5 minutes
)
```

#### 13.2 Batch Operations
```python
# Batch API calls for efficiency (reader)
markets_data = reader.get_multiple_markets([
    "market1", "market2", "market3"
])

# Batch trade execution (writer)
trades = writer.place_multiple_bets([
    {"market_id": "m1", "outcome": "YES", "amount": 10},
    {"market_id": "m2", "outcome": "NO", "amount": 15},
    {"market_id": "m3", "outcome": "YES", "amount": 20}
])
```

## Testing and Quality Assurance

### 14. Comprehensive Testing

#### 14.1 Unit Tests
```python
# Test individual components
def test_market_impact_calculation():
    client = ManifoldClient(api_key="test_key")
    impact = client.calculate_market_impact(
        market_id="test_market",
        target_probability_change=0.01,
        outcome="YES"
    )
    assert impact > 0
    assert impact < 1000  # Reasonable upper bound
```

#### 14.2 Integration Tests
```python
# Test full bot functionality
def test_bot_trading_cycle():
    bot = Bot(test_config)
    result = bot.run_single_cycle()
    assert result.success
    assert result.trades_placed >= 0
```

#### 14.3 Strategy Testing
```python
# Test strategies with live market data
reader = ManifoldReader()
strategy = MyTradingStrategy(reader)

# Test on multiple markets
test_results = strategy.test_strategy([
    "market1", "market2", "market3"
])

print(f"Strategy performance: {test_results.performance}")
print(f"Success rate: {test_results.success_rate}")
print(f"Average confidence: {test_results.avg_confidence}")
```

## Security and Compliance

### 15. Security Features

#### 15.1 API Key Management
- **Environment Variables**: Secure storage of API keys
- **Key Rotation**: Support for API key rotation
- **Access Logging**: Log all API access for audit

#### 15.2 Rate Limiting
```python
# Built-in rate limiting
client = ManifoldClient(
    api_key="key",
    rate_limit={
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    }
)
```

### 16. Compliance and Audit

#### 16.1 Trade Logging
```python
# Comprehensive trade logging
trade_log = TradeLogger(
    log_file="trades.log",
    include_analysis=True,
    include_market_data=True
)

# Log every trade
trade_log.log_trade(trade, analysis, market_data)
```

#### 16.2 Risk Reporting
```python
# Generate risk reports
risk_report = RiskReporter()
report = risk_report.generate_report(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(f"Total exposure: {report.total_exposure} M$")
print(f"Risk-adjusted return: {report.risk_adjusted_return}")
print(f"VaR (95%): {report.var_95} M$")
```

## Usage Patterns

### Research and Analysis (No API Key Required)
```python
from manifoldbot import ManifoldReader

# Analyze markets without needing an API key
reader = ManifoldReader()

# Research multiple markets
markets = reader.search_markets("AI regulation")
for market in markets:
    liquidity = reader.get_market_liquidity(market.id)
    risk_metrics = reader.get_market_risk_metrics(market.id)
    print(f"{market.question}: {market.probability}% (Liquidity: {liquidity.total} M$)")
```

### Automated Trading (API Key Required)
```python
from manifoldbot import ManifoldReader, ManifoldWriter, Bot

# Set up both reader and writer
reader = ManifoldReader()  # No API key needed
writer = ManifoldWriter(api_key="your_key")  # API key required

# Create bot with both components
bot = Bot(
    reader=reader,
    writer=writer,
    config=bot_config
)

# Bot uses reader for analysis, writer for trading
bot.run()
```

### Development and Testing
```python
# Test strategies without placing real bets
reader = ManifoldReader()
strategy = MyTradingStrategy(reader)

# Test with live market data (no trades placed)
strategy.analyze_markets(["market1", "market2", "market3"])

# When ready, add writer for live trading
writer = ManifoldWriter(api_key="your_key")
strategy.set_writer(writer)
strategy.run_live()
```

## Conclusion

This functionality specification outlines a comprehensive ManifoldBot package that provides:

1. **Clean Architecture**: Reader/Writer separation for better security and scalability
2. **Robust Manifold Markets Client**: Full API coverage with proper pagination handling
3. **Advanced Trading Capabilities**: Market impact calculation, position sizing, risk management
4. **AI-Powered Analysis**: Document analysis, market prediction, automated decision making
5. **Multi-Source Data Integration**: Web scraping, RSS feeds, API integrations
6. **Enterprise-Grade Features**: Monitoring, alerting, security, compliance
7. **Easy Deployment**: Local, Docker, and cloud deployment options

The Reader/Writer separation provides several key benefits:
- **Security**: API keys only needed for trading operations
- **Scalability**: Analyze many markets without API key rate limits
- **Development**: Test strategies without placing real bets
- **Flexibility**: Use reader-only for research, add writer when ready to trade
- **Cost Efficiency**: Reduce API costs by using public endpoints for analysis

The package is designed to be both powerful for advanced users and simple for beginners, with comprehensive documentation and examples for all use cases.

## Examples and Use Cases

The `/examples` folder will contain specific implementations demonstrating how to use ManifoldBot for different scenarios:

### Example 1: Chinese Regulatory Monitoring
- **File**: `examples/chinese_regulatory_bot.py`
- **Description**: Monitors Chinese regulatory sources for specific company updates
- **Data Sources**: CNINFO, SZSE, Jiangxi Natural Resources
- **Use Case**: Based on the oreacle-bot implementation for CATL lithium mine monitoring

### Example 2: SEC Filings Monitor
- **File**: `examples/sec_filings_bot.py`
- **Description**: Monitors SEC EDGAR database for company filings
- **Data Sources**: SEC EDGAR API, company websites
- **Use Case**: Track 8-K filings, 10-Q reports, proxy statements

### Example 3: News Sentiment Bot
- **File**: `examples/news_sentiment_bot.py`
- **Description**: Monitors financial news and trades based on sentiment
- **Data Sources**: RSS feeds, news APIs
- **Use Case**: Trade on news sentiment for specific companies or sectors

### Example 4: Social Media Bot
- **File**: `examples/social_media_bot.py`
- **Description**: Monitors social media for market-moving information
- **Data Sources**: Twitter API, Reddit API
- **Use Case**: Track social sentiment and viral information

Each example will include:
- Complete configuration files
- Data source implementations
- AI analysis prompts
- Trading logic
- Deployment instructions

## Implementation Priority

1. **Phase 1**: Core Manifold Markets client with basic trading
2. **Phase 2**: Market impact calculation and advanced trading features
3. **Phase 3**: AI integration and document analysis
4. **Phase 4**: Data source integration and monitoring
5. **Phase 5**: Example implementations and documentation
6. **Phase 6**: Advanced features (portfolio management, arbitrage)
7. **Phase 7**: Enterprise features (security, compliance, monitoring)

This phased approach ensures that core functionality is available early while examples and advanced features are added incrementally based on user feedback and requirements.
