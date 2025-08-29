# ManifoldBot - Self-Contained Manifold Markets Trading Bot

## Overview

ManifoldBot is a self-contained Python module for creating intelligent trading bots that monitor data sources, analyze content with ChatGPT, and automatically trade on Manifold Markets. Based on the oreacle-bot architecture but with cleaner separation of concerns and a more generic, reusable design.

## Core Architecture

### Package Structure
```
manifoldbot/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── bot.py              # Main Bot class
│   ├── monitor.py          # Monitoring loop
│   └── decision.py         # Trading decision logic
├── data/
│   ├── __init__.py
│   ├── sources/            # Data source adapters
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract base source
│   │   ├── web.py          # Web scraping source
│   │   ├── rss.py          # RSS feed source
│   │   └── api.py          # API-based source
│   ├── storage.py          # SQLite storage
│   └── filters.py          # Content filtering
├── ai/
│   ├── __init__.py
│   ├── client.py           # OpenAI client
│   ├── models.py           # Pydantic schemas
│   ├── prompts.py          # Prompt templates
│   └── analysis.py         # Analysis pipeline
├── manifold/
│   ├── __init__.py
│   ├── client.py           # Manifold API client
│   ├── markets.py          # Market utilities
│   └── comments.py         # Comment formatting
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuration management
│   └── schemas.py          # Config validation
└── utils/
    ├── __init__.py
    ├── logging.py          # Logging setup
    ├── validation.py       # Input validation
    └── helpers.py          # Utility functions
```

## Key Features

### 1. Modular Data Sources
- **Base Source Class**: Abstract interface for all data sources
- **Web Scraping**: BeautifulSoup-based web content extraction
- **RSS Feeds**: Standard RSS/Atom feed monitoring
- **API Sources**: REST API integration with rate limiting
- **Custom Sources**: Easy to extend with new data sources

### 2. AI-Powered Analysis
- **ChatGPT Integration**: GPT-4o-mini for content analysis
- **Structured Output**: Pydantic models for consistent data
- **Confidence Scoring**: 0.0-1.0 confidence with evidence
- **Multi-language Support**: Chinese, English, and other languages
- **Custom Prompts**: Configurable analysis prompts per bot

### 3. Manifold Markets Integration
- **API Client**: Full Manifold Markets API wrapper
- **Market Monitoring**: Track specific markets by slug
- **Comment System**: Rich, formatted comments with evidence
- **Trading Logic**: Conservative position sizing and risk management
- **Deduplication**: Prevent duplicate actions

### 4. Configuration Management
- **Environment Variables**: Secure credential management
- **YAML Config**: Bot-specific configuration files
- **Validation**: Pydantic-based config validation
- **Defaults**: Sensible defaults for all settings

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
1. **Package Setup**
   - Create `manifoldbot` package structure
   - Set up `pyproject.toml` with dependencies
   - Add `__init__.py` files and basic imports
   - Create `README.md` with usage examples

2. **Configuration System**
   - Implement `config/settings.py` with environment variable loading
   - Create `config/schemas.py` for validation
   - Add support for YAML configuration files
   - Set up logging configuration

3. **Base Classes**
   - Create `data/sources/base.py` abstract base class
   - Implement `data/storage.py` SQLite database
   - Add `utils/validation.py` for input validation
   - Create `utils/logging.py` for consistent logging

### Phase 2: Data Sources (Week 2)
1. **Web Scraping Source**
   - Implement `data/sources/web.py` with BeautifulSoup
   - Add support for CSS selectors and XPath
   - Include retry logic and error handling
   - Add content filtering and deduplication

2. **RSS Source**
   - Create `data/sources/rss.py` for feed monitoring
   - Support RSS 2.0 and Atom feeds
   - Add feed validation and error recovery
   - Implement content extraction from feed items

3. **API Source**
   - Build `data/sources/api.py` for REST APIs
   - Add rate limiting and authentication
   - Support pagination and incremental updates
   - Include response caching

4. **Content Filtering**
   - Implement `data/filters.py` for content preprocessing
   - Add keyword matching and regex filtering
   - Support boolean logic for complex filters
   - Include content deduplication

### Phase 3: AI Integration (Week 3)
1. **OpenAI Client**
   - Create `ai/client.py` with OpenAI API integration
   - Add retry logic and error handling
   - Implement token counting and cost tracking
   - Support multiple models (GPT-4o-mini, GPT-4, etc.)

2. **Analysis Models**
   - Define Pydantic schemas in `ai/models.py`
   - Create structured output formats for analysis
   - Add confidence scoring and evidence extraction
   - Support multi-language content analysis

3. **Prompt System**
   - Implement `ai/prompts.py` with template system
   - Create default prompts for common use cases
   - Add support for custom prompts per bot
   - Include prompt versioning and validation

4. **Analysis Pipeline**
   - Build `ai/analysis.py` for content processing
   - Add pre-filtering to reduce API costs
   - Implement structured output parsing
   - Include fallback analysis for API failures

### Phase 4: Manifold Integration (Week 4)
1. **API Client**
   - Create `manifold/client.py` with full API coverage
   - Add authentication and rate limiting
   - Support all Manifold API endpoints
   - Include error handling and retries

2. **Market Utilities**
   - Implement `manifold/markets.py` for market operations
   - Add market discovery and validation
   - Support market monitoring and updates
   - Include position tracking

3. **Comment System**
   - Build `manifold/comments.py` for rich formatting
   - Support markdown, emojis, and structured content
   - Add evidence display and confidence indicators
   - Include source attribution and links

4. **Trading Logic**
   - Create `manifold/trading.py` for position management
   - Add conservative risk management
   - Implement position sizing algorithms
   - Include stop-loss and take-profit logic

### Phase 5: Bot Framework (Week 5)
1. **Main Bot Class**
   - Implement `core/bot.py` as the main interface
   - Add configuration loading and validation
   - Support multiple data sources per bot
   - Include monitoring and alerting

2. **Monitoring Loop**
   - Create `core/monitor.py` for continuous operation
   - Add configurable polling intervals
   - Support graceful shutdown and restart
   - Include health checks and status reporting

3. **Decision Engine**
   - Build `core/decision.py` for trading decisions
   - Add confidence thresholds and safety gates
   - Implement multi-factor decision making
   - Include backtesting and simulation support

4. **CLI Interface**
   - Create command-line interface for bot management
   - Add commands for start, stop, status, and config
   - Support multiple bot instances
   - Include logging and debugging options

### Phase 6: Testing & Documentation (Week 6)
1. **Unit Tests**
   - Add comprehensive test suite
   - Test all core components
   - Include mock data and API responses
   - Add integration tests

2. **Documentation**
   - Create comprehensive README
   - Add API documentation
   - Include usage examples and tutorials
   - Create configuration reference

3. **Examples**
   - Build example bots for common use cases
   - Add configuration templates
   - Include deployment guides
   - Create troubleshooting guides

## Configuration Example

```yaml
# bot_config.yaml
name: "CATL Mining Monitor"
description: "Monitors Chinese regulatory sources for CATL lithium mine updates"

data_sources:
  - type: "web"
    name: "CNINFO"
    url: "https://www.cninfo.com.cn/new/disclosure/stock?plate=szse&stock=300750"
    selector: ".disclosure-list-item"
    poll_interval: 900  # 15 minutes
    
  - type: "web"
    name: "Jiangxi Natural Resources"
    url: "https://jxt.jiangxi.gov.cn/ycsrmzf/gytdsyqhkyqcr/"
    selector: ".list-item"
    poll_interval: 900

ai:
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.1
  confidence_threshold: 0.75
  
manifold:
  market_slug: "MikhailTal/catl-receives-license-renewal-for-y"
  comment_only: false
  max_position_size: 5  # M$
  default_probability: 0.55

filters:
  keywords:
    include: ["CATL", "宜春", "枧下窝", "采矿许可证", "锂云母"]
    exclude: ["勘探", "暂停", "取消"]
  
  confidence_gates:
    entity_match: true
    action_required: true
    evidence_required: true
```

## Usage Example

```python
from manifoldbot import Bot
from manifoldbot.config import load_config

# Load configuration
config = load_config("bot_config.yaml")

# Create and run bot
bot = Bot(config)
bot.run()
```

## Dependencies

### Core Dependencies
- `requests` - HTTP client for API calls
- `beautifulsoup4` - Web scraping
- `feedparser` - RSS feed parsing
- `sqlite3` - Database storage (built-in)
- `pydantic` - Data validation and settings
- `pyyaml` - Configuration file parsing
- `openai` - ChatGPT integration
- `python-dotenv` - Environment variable loading

### Optional Dependencies
- `deepl` - Alternative translation service
- `googletrans` - Google Translate integration
- `schedule` - Advanced scheduling
- `rich` - Enhanced console output
- `click` - CLI interface

## Deployment Options

### 1. Local Development
```bash
pip install -e .
python -m manifoldbot.cli start --config bot_config.yaml
```

### 2. Docker Container
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["python", "-m", "manifoldbot.cli", "start"]
```

### 3. GitHub Actions
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
          python -m manifoldbot.cli start --config bot_config.yaml
```

## Migration from Oreacle-Bot

### Key Differences
1. **Package Name**: `oreacle-bot` → `manifoldbot`
2. **Modular Design**: Cleaner separation of concerns
3. **Generic Sources**: Not tied to specific Chinese regulatory sites
4. **Configuration**: YAML-based instead of hardcoded
5. **Extensibility**: Easy to add new data sources and analysis types
6. **Testing**: Comprehensive test suite
7. **Documentation**: Better documentation and examples

### Migration Steps
1. Extract core logic from oreacle-bot
2. Refactor into modular components
3. Add configuration system
4. Implement generic data sources
5. Add comprehensive testing
6. Create documentation and examples

## Success Metrics

### Technical Metrics
- [ ] All core components implemented and tested
- [ ] 90%+ test coverage
- [ ] Documentation complete
- [ ] Example bots working
- [ ] Performance benchmarks met

### Functional Metrics
- [ ] Successfully monitors multiple data sources
- [ ] Accurate AI analysis with high confidence
- [ ] Reliable Manifold Markets integration
- [ ] Conservative trading with risk management
- [ ] Zero false positive trades

### User Experience Metrics
- [ ] Easy setup and configuration
- [ ] Clear documentation and examples
- [ ] Helpful error messages and logging
- [ ] Flexible deployment options
- [ ] Active community and support

## Future Enhancements

### Phase 7: Advanced Features
- **Multi-Market Support**: Monitor and trade multiple markets
- **Portfolio Management**: Advanced position sizing and risk management
- **Backtesting**: Historical performance analysis
- **Machine Learning**: Custom models for specific use cases
- **Real-time Alerts**: Slack, Discord, email notifications

### Phase 8: Enterprise Features
- **Multi-User Support**: Team collaboration and permissions
- **API Server**: REST API for external integrations
- **Dashboard**: Web-based monitoring and control
- **Analytics**: Advanced reporting and insights
- **Compliance**: Audit trails and regulatory compliance

This plan provides a comprehensive roadmap for creating a self-contained, modular Manifold trading bot that improves upon the oreacle-bot architecture while maintaining its core functionality and reliability.
