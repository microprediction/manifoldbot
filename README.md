# ManifoldBot

A self-contained Python module for creating intelligent trading bots that monitor data sources, analyze content with ChatGPT, and automatically trade on Manifold Markets.

## Quick Start

### 1. Install the Package

**Option A: Using the installation script (recommended)**
```bash
./install.sh
```

**Option B: Manual installation**
```bash
pip install -e .
```

**Option C: Install from PyPI (when published)**
```bash
pip install manifoldbot
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Manifold Markets API Configuration
MANIFOLD_API_KEY=your_manifold_api_key_here
```

### 3. Create a Bot Configuration

Create a `bot_config.yaml` file (see examples in PLAN.md):
```yaml
name: "My Trading Bot"
description: "Monitors data sources and trades on Manifold Markets"

data_sources:
  - type: "web"
    name: "Example Source"
    url: "https://example.com"
    selector: ".content"
    poll_interval: 900  # 15 minutes

ai:
  model: "gpt-4o-mini"
  confidence_threshold: 0.75

manifold:
  market_slug: "your-market-slug"
  comment_only: true  # Start with comments only
```

### 4. Run the Bot

```bash
manifoldbot start --config bot_config.yaml
```

Or create a config file first:
```bash
manifoldbot init --output my_bot.yaml
# Edit my_bot.yaml with your settings
manifoldbot start --config my_bot.yaml
```

## Features

- 🤖 **AI-Powered Analysis**: Uses ChatGPT to analyze content and make trading decisions
- 📊 **Multiple Data Sources**: Web scraping, RSS feeds, and API integrations
- 🎯 **Manifold Integration**: Full Manifold Markets API support
- ⚙️ **Easy Configuration**: YAML-based configuration system
- 🔒 **Secure**: Environment variables for API keys
- 🚀 **Deploy Anywhere**: Local, Docker, or GitHub Actions

## Requirements

- Python 3.8+
- OpenAI API key
- Manifold Markets API key

## Documentation

For detailed documentation, examples, and architecture information, see [PLAN.md](PLAN.md).

## Development

This project is based on the [oreacle-bot](https://github.com/microprediction/oreacle-bot) architecture but with cleaner separation of concerns and a more generic, reusable design.

## License

See [LICENSE](LICENSE) file for details.
