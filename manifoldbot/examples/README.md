# ManifoldBot Examples

This directory contains example scripts for using ManifoldBot.

## Quick Start

**Most users should start here:**

- `bot/simple_trade_all.py` - Trade all markets with GPT-5 (recommended)
- `bot/run_llm_bot.py` - Simple LLM trading bot

## Browse All Examples

For a complete overview of all available examples, see:

**https://github.com/microprediction/manifoldbot/tree/main/manifoldbot/examples**

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API keys**:
   ```bash
   export MANIFOLD_API_KEY="your_manifold_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Run an example**:
   ```bash
   python -m manifoldbot.examples.bot.simple_trade_all
   ```
