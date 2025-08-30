#!/usr/bin/env python3
"""
Simple script to run the LLM trading bot.

Usage:
    python -m manifoldbot.examples.run_llm_bot

Make sure to set your API keys:
    export MANIFOLD_API_KEY="your_manifold_api_key"
    export OPENAI_API_KEY="your_openai_api_key"
"""

import os
import sys
from manifoldbot.examples.llm_trading_bot import main

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("MANIFOLD_API_KEY"):
        print("Error: MANIFOLD_API_KEY environment variable not set")
        print("Get your API key from: https://manifold.markets/")
        sys.exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Get your API key from: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    # Run the bot
    main()
